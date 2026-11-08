import json
import logging
import os
import re
import struct
from typing import BinaryIO, Dict, List, Optional, Tuple, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.models.heritage_3d_asset import Heritage3DAsset
from app.schemas.heritage_3d_asset import Heritage3DAssetCreate, Heritage3DAssetUpdate
from app.services.storage_service import storage_service

logger = logging.getLogger("3d_bharat.heritage_3d")


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


def get_pilot_asset(db: Session) -> Optional[Heritage3DAsset]:
    stmt = (
        select(Heritage3DAsset)
        .where(Heritage3DAsset.is_pilot == True)
        .where(Heritage3DAsset.visibility_status == "PUBLIC")
        .order_by(Heritage3DAsset.id)
    )
    return db.execute(stmt).scalars().first()


def list_heritage_3d_assets_by_site(
    db: Session,
    site_id: int,
    asset_format: Optional[str] = None,
    processing_status: Optional[str] = None,
    public_only: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> List[Heritage3DAsset]:
    stmt = select(Heritage3DAsset).where(Heritage3DAsset.heritage_site_id == site_id)
    if asset_format:
        stmt = stmt.where(Heritage3DAsset.asset_format == asset_format)
    if processing_status:
        stmt = stmt.where(Heritage3DAsset.processing_status == processing_status)
    if public_only:
        stmt = stmt.where(Heritage3DAsset.visibility_status == "PUBLIC")

    stmt = stmt.offset(skip).limit(limit).order_by(Heritage3DAsset.id)
    return list(db.execute(stmt).scalars().all())


def list_all_heritage_3d_assets(
    db: Session,
    site_id: Optional[int] = None,
    asset_format: Optional[str] = None,
    processing_status: Optional[str] = None,
    verification_status: Optional[str] = None,
    visibility_status: Optional[str] = None,
    is_pilot: Optional[bool] = None,
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
    if visibility_status:
        stmt = stmt.where(Heritage3DAsset.visibility_status == visibility_status)
        count_stmt = count_stmt.where(Heritage3DAsset.visibility_status == visibility_status)
    if is_pilot is not None:
        stmt = stmt.where(Heritage3DAsset.is_pilot == is_pilot)
        count_stmt = count_stmt.where(Heritage3DAsset.is_pilot == is_pilot)

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


def validate_heritage_3d_asset(
    db: Session,
    asset_id: int,
) -> Dict[str, Any]:
    """
    Rigorously validates a 3D asset file on disk:
    - Path & presence check
    - Checksum SHA-256 match
    - Format-specific validation (GLB header, glTF JSON structure, OBJ geometry tokens)
    - Updates validation_status and validation_report
    """
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        raise ValueError(f"Heritage 3D asset with id {asset_id} does not exist.")

    errors: List[str] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {
        "format": asset.asset_format,
        "storage_key": asset.storage_key,
    }

    try:
        abs_path = storage_service.get_absolute_path(asset.storage_key)
        if not abs_path.exists():
            errors.append(f"Storage file missing at {asset.storage_key}")
            asset.validation_status = "FAILED"
            asset.validation_report = json.dumps({"errors": errors, "warnings": warnings, "details": details})
            db.commit()
            return {
                "asset_id": asset_id,
                "is_valid": False,
                "magic_bytes_valid": False,
                "format_recognized": False,
                "file_size_bytes": 0,
                "checksum_sha256": asset.checksum_sha256,
                "validation_status": asset.validation_status,
                "errors": errors,
                "warnings": warnings,
                "details": details,
            }

        file_size = abs_path.stat().st_size
        details["file_size_bytes"] = file_size

        # Checksum calculation
        import hashlib
        sha = hashlib.sha256()
        with open(abs_path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        actual_checksum = sha.hexdigest()
        details["calculated_checksum"] = actual_checksum

        if actual_checksum.lower() != asset.checksum_sha256.lower():
            errors.append(
                f"Checksum mismatch: expected {asset.checksum_sha256}, calculated {actual_checksum}"
            )

        magic_valid = False
        format_recognized = False

        fmt = asset.asset_format.upper()
        with open(abs_path, "rb") as f:
            header = f.read(64)

        if fmt == "GLB" or abs_path.suffix.lower() == ".glb":
            format_recognized = True
            if header.startswith(b"glTF"):
                magic_valid = True
                if len(header) >= 12:
                    magic, version, length = struct.unpack("<4sII", header[:12])
                    details["gltf_version"] = version
                    details["gltf_header_length"] = length
                    if version != 2:
                        warnings.append(f"glTF version is {version}, recommended is 2.")
                    if length != file_size:
                        warnings.append(f"Header length ({length}) differs from file size ({file_size}).")
            else:
                errors.append("Invalid GLB: missing 'glTF' magic header.")

        elif fmt == "GLTF" or abs_path.suffix.lower() == ".gltf":
            format_recognized = True
            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "asset" in data and "version" in data["asset"]:
                    magic_valid = True
                    details["gltf_version"] = data["asset"]["version"]
                else:
                    errors.append("Malformed glTF: missing asset.version metadata.")
            except Exception as e:
                errors.append(f"glTF JSON parsing error: {e}")

        elif fmt == "OBJ" or abs_path.suffix.lower() == ".obj":
            format_recognized = True
            text_sample = header.decode("utf-8", errors="replace")
            lines = [l.strip() for l in text_sample.splitlines() if l.strip()]
            valid_tokens = ("#", "v ", "vn ", "vt ", "f ", "g ", "o ", "mtllib ")
            if any(l.startswith(valid_tokens) for l in lines):
                magic_valid = True
            else:
                errors.append("Invalid OBJ: missing standard geometric tokens.")
        else:
            format_recognized = True
            magic_valid = True
            warnings.append(f"Generic validation applied for format {fmt}.")

        is_valid = len(errors) == 0
        asset.validation_status = "READY" if is_valid else "FAILED"
        if is_valid and asset.processing_status != "READY":
            asset.processing_status = "READY"

        report = {
            "errors": errors,
            "warnings": warnings,
            "details": details,
            "validated_at": str(asset.updated_at),
        }
        asset.validation_report = json.dumps(report)
        db.commit()
        db.refresh(asset)

        return {
            "asset_id": asset_id,
            "is_valid": is_valid,
            "magic_bytes_valid": magic_valid,
            "format_recognized": format_recognized,
            "file_size_bytes": file_size,
            "checksum_sha256": actual_checksum,
            "validation_status": asset.validation_status,
            "errors": errors,
            "warnings": warnings,
            "details": details,
        }

    except Exception as exc:
        logger.error(f"Error validating asset {asset_id}: {exc}")
        asset.validation_status = "FAILED"
        asset.validation_report = json.dumps({"errors": [str(exc)], "warnings": warnings, "details": details})
        db.commit()
        raise


def publish_heritage_3d_asset(
    db: Session,
    asset_id: int,
    visibility_status: str = "PUBLIC",
) -> Heritage3DAsset:
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        raise ValueError(f"Heritage 3D asset with id {asset_id} does not exist.")

    if asset.validation_status not in ("READY", "VALIDATING"):
        raise ValueError(
            f"Cannot publish asset with validation status '{asset.validation_status}'. "
            "Please validate the asset successfully first."
        )

    asset.visibility_status = visibility_status
    asset.processing_status = "READY"
    db.commit()
    db.refresh(asset)
    return asset


def archive_heritage_3d_asset(
    db: Session,
    asset_id: int,
    reason: Optional[str] = None,
) -> Heritage3DAsset:
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        raise ValueError(f"Heritage 3D asset with id {asset_id} does not exist.")

    asset.visibility_status = "ARCHIVED"
    asset.validation_status = "ARCHIVED"
    if reason:
        current_report = {}
        if asset.validation_report:
            try:
                current_report = json.loads(asset.validation_report)
            except Exception:
                current_report = {"raw": asset.validation_report}
        current_report["archive_reason"] = reason
        asset.validation_report = json.dumps(current_report)

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
                        ref_file = storage_service.sanitize_filename(ref_file)
                        referenced.append(ref_file)
        except Exception:
            pass

    companions_dir = abs_path.parent / "companions"
    found = []
    missing = []

    for ref in referenced:
        target = companions_dir / ref
        if target.exists():
            found.append(ref)
        else:
            missing.append(ref)

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
    """
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        return False

    storage_key = asset.storage_key

    db.delete(asset)
    db.commit()

    try:
        storage_service.delete_file(storage_key)
    except Exception as exc:
        raise RuntimeError(f"Database record deleted, but physical file cleanup failed: {exc}")

    return True
