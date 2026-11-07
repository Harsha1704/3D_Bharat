from typing import List, Optional
from sqlalchemy import select
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
    """
    Creates 3D asset metadata for an existing heritage site.
    Validates site existence and optional source existence.
    """
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

    # Check for duplicate storage_key
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


def delete_heritage_3d_asset(
    db: Session,
    asset_id: int,
) -> bool:
    """
    Deletes 3D asset record from database and cleans up primary file and companion files.
    """
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        return False

    storage_key = asset.storage_key
    companion_keys = asset.companion_files or []

    db.delete(asset)
    db.commit()

    # Clean up physical files
    storage_service.delete_file(storage_key)
    for c_key in companion_keys:
        storage_service.delete_file(c_key)

    return True
