import re
from typing import BinaryIO, Dict, List, Optional, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.models.heritage_3d_asset import Heritage3DAsset
from app.schemas.heritage_3d_asset import Heritage3DAssetCreate, Heritage3DAssetUpdate
from app.services.storage_service import storage_service


def create_heritage_3d_asset(
    db: Session,
    asset_data: Heritage3DAssetCreate,
) -> Heritage3DAsset:
    site = db.execute(
        select(HeritageSite).where(HeritageSite.id == asset_data.heritage_site_id)
    ).scalar_one_or_none()
    if site is None:
        raise ValueError(f"Heritage site with id {asset_data.heritage_site_id} does not exist.")

    if asset_data.source_id is not None:
        source = db.execute(
            select(HeritageSource).where(HeritageSource.id == asset_data.source_id)
        ).scalar_one_or_none()
        if source is None:
            raise ValueError(f"Heritage source with id {asset_data.source_id} does not exist.")

    existing_key = db.execute(
        select(Heritage3DAsset).where(Heritage3DAsset.storage_key == asset_data.storage_key)
    ).scalar_one_or_none()
    if existing_key is not None:
        raise ValueError(f"3D asset with storage key '{asset_data.storage_key}' already exists.")

    data = asset_data.model_dump()
    asset = Heritage3DAsset(**data)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def get_heritage_3d_asset(
    db: Session,
    asset_id: int,
) -> Optional[Heritage3DAsset]:
    stmt = select(Heritage3DAsset).where(Heritage3DAsset.id == asset_id)
    return db.execute(stmt).scalar_one_or_none()


def list_heritage_3d_assets_by_site(
    db: Session,
    site_id: int,
    asset_format: Optional[str] = None,
    processing_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Heritage3DAsset]:
    stmt = select(Heritage3DAsset).where(Heritage3DAsset.heritage_site_id == site_id)
    if asset_format:
        stmt = stmt.where(Heritage3DAsset.asset_format == asset_format)
    if processing_status:
        stmt = stmt.where(Heritage3DAsset.processing_status == processing_status)

    stmt = stmt.offset(skip).limit(limit).order_by(Heritage3DAsset.id)
    return list(db.execute(stmt).scalars().all())


def list_all_heritage_3d_assets(
    db: Session,
    site_id: Optional[int] = None,
    asset_format: Optional[str] = None,
    processing_status: Optional[str] = None,
    verification_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[Heritage3DAsset], int]:
    stmt = select(Heritage3DAsset)
    count_stmt = select(func.count(Heritage3DAsset.id))

    if site_id is not None:
        stmt = stmt.where(Heritage3DAsset.heritage_site_id == site_id)
        count_stmt = count_stmt.where(Heritage3DAsset.heritage_site_id == site_id)
    if asset_format:
        stmt = stmt.where(Heritage3DAsset.asset_format.ilike(f"%{asset_format}%"))
        count_stmt = count_stmt.where(Heritage3DAsset.asset_format.ilike(f"%{asset_format}%"))
    if processing_status:
        stmt = stmt.where(Heritage3DAsset.processing_status.ilike(f"%{processing_status}%"))
        count_stmt = count_stmt.where(Heritage3DAsset.processing_status.ilike(f"%{processing_status}%"))
    if verification_status:
        stmt = stmt.where(Heritage3DAsset.verification_status.ilike(f"%{verification_status}%"))
        count_stmt = count_stmt.where(Heritage3DAsset.verification_status.ilike(f"%{verification_status}%"))

    total = db.execute(count_stmt).scalar_one()
    items = list(db.execute(stmt.offset(skip).limit(limit).order_by(Heritage3DAsset.id)).scalars().all())
    return items, total


def update_heritage_3d_asset(
    db: Session,
    asset_id: int,
    update_data: Heritage3DAssetUpdate,
) -> Optional[Heritage3DAsset]:
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        return None

    if update_data.source_id is not None:
        source = db.execute(
            select(HeritageSource).where(HeritageSource.id == update_data.source_id)
        ).scalar_one_or_none()
        if source is None:
            raise ValueError(f"Heritage source with id {update_data.source_id} does not exist.")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


def add_companion_file_to_asset(
    db: Session,
    asset_id: int,
    companion_filename: str,
    stream: BinaryIO,
) -> Dict[str, str]:
    """
    Saves a companion file strictly inside the 3D asset's isolated folder
    and records it in the asset's companion_files list in the database.
    """
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        raise ValueError(f"Heritage 3D asset with id {asset_id} does not exist.")

    rel_key, sanitized, size, checksum = storage_service.save_companion_file(
        parent_storage_key=asset.storage_key,
        companion_filename=companion_filename,
        stream=stream,
    )

    current_companions = list(asset.companion_files or [])
    if sanitized not in current_companions:
        current_companions.append(sanitized)
        asset.companion_files = current_companions
        db.commit()
        db.refresh(asset)

    return {
        "storage_key": rel_key,
        "companion_filename": sanitized,
        "size_bytes": str(size),
        "checksum_sha256": checksum,
    }


def verify_3d_asset_companions(
    db: Session,
    asset_id: int,
) -> Dict[str, object]:
    """
    Inspects model file and checks whether referenced companion files
    (e.g. mtllib in OBJ) exist on disk. Reports any missing companion files.
    """
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        raise ValueError(f"Heritage 3D asset with id {asset_id} does not exist.")

    abs_path = storage_service.get_absolute_path(asset.storage_key)
    if not abs_path.exists():
        return {
            "status": "PRIMARY_FILE_MISSING",
            "model_format": asset.asset_format,
            "referenced_companions": [],
            "found_companions": [],
            "missing_companions": [],
        }

    referenced = []
    # If OBJ, parse mtllib statements
    if asset.asset_format.upper() == "OBJ" or abs_path.suffix.lower() == ".obj":
        try:
            with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    match = re.match(r"^\s*mtllib\s+(.+)$", line)
                    if match:
                        ref_file = match.group(1).strip()
                        # Sanitize reference to prevent directory traversal
                        ref_file = storage_service.sanitize_filename(ref_file)
                        referenced.append(ref_file)
        except Exception:
            pass

    # Check companion folder
    companions_dir = abs_path.parent / "companions"
    found = []
    missing = []

    for ref in referenced:
        target = companions_dir / ref
        if target.exists():
            found.append(ref)
        else:
            missing.append(ref)

    # Also check registered companion_files list from DB
    registered = list(asset.companion_files or [])
    for reg in registered:
        target = companions_dir / reg
        if target.exists():
            if reg not in found:
                found.append(reg)
        else:
            if reg not in missing:
                missing.append(reg)

    status = "COMPLETE" if not missing else "INCOMPLETE"
    return {
        "status": status,
        "model_format": asset.asset_format,
        "registered_companions": registered,
        "referenced_companions": referenced,
        "found_companions": found,
        "missing_companions": missing,
    }


def delete_heritage_3d_asset(
    db: Session,
    asset_id: int,
) -> bool:
    """
    Deletes 3D asset record from database, then cleans up storage files.
    If storage cleanup fails, logs error and raises RuntimeError.
    """
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        return False

    storage_key = asset.storage_key

    # DB transaction first
    db.delete(asset)
    db.commit()

    # Physical cleanup after successful DB commit
    try:
        storage_service.delete_file(storage_key)
    except Exception as exc:
        raise RuntimeError(f"Database record deleted, but physical file cleanup failed: {exc}")

    return True
