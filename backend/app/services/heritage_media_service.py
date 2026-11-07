from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.models.heritage_media import HeritageMedia
from app.schemas.heritage_media import HeritageMediaCreate, HeritageMediaUpdate
from app.services.storage_service import storage_service


def create_heritage_media(
    db: Session,
    media_data: HeritageMediaCreate,
) -> HeritageMedia:
    """
    Creates media metadata for an existing heritage site.
    Validates site existence and optional source existence.
    """
    site = db.execute(
        select(HeritageSite).where(HeritageSite.id == media_data.heritage_site_id)
    ).scalar_one_or_none()
    if site is None:
        raise ValueError(f"Heritage site with id {media_data.heritage_site_id} does not exist.")

    if media_data.source_id is not None:
        source = db.execute(
            select(HeritageSource).where(HeritageSource.id == media_data.source_id)
        ).scalar_one_or_none()
        if source is None:
            raise ValueError(f"Heritage source with id {media_data.source_id} does not exist.")

    # Check for duplicate storage_key
    existing_key = db.execute(
        select(HeritageMedia).where(HeritageMedia.storage_key == media_data.storage_key)
    ).scalar_one_or_none()
    if existing_key is not None:
        raise ValueError(f"Media asset with storage key '{media_data.storage_key}' already exists.")

    data = media_data.model_dump()
    media = HeritageMedia(**data)
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def get_heritage_media(
    db: Session,
    media_id: int,
) -> Optional[HeritageMedia]:
    stmt = select(HeritageMedia).where(HeritageMedia.id == media_id)
    return db.execute(stmt).scalar_one_or_none()


def list_heritage_media_by_site(
    db: Session,
    site_id: int,
    media_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[HeritageMedia]:
    stmt = select(HeritageMedia).where(HeritageMedia.heritage_site_id == site_id)
    if media_type:
        stmt = stmt.where(HeritageMedia.media_type == media_type)
    if verification_status:
        stmt = stmt.where(HeritageMedia.verification_status == verification_status)

    stmt = stmt.offset(skip).limit(limit).order_by(HeritageMedia.id)
    return list(db.execute(stmt).scalars().all())


def list_all_heritage_media(
    db: Session,
    site_id: Optional[int] = None,
    media_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> tuple[List[HeritageMedia], int]:
    stmt = select(HeritageMedia)
    count_stmt = select(func.count(HeritageMedia.id))

    if site_id is not None:
        stmt = stmt.where(HeritageMedia.heritage_site_id == site_id)
        count_stmt = count_stmt.where(HeritageMedia.heritage_site_id == site_id)
    if media_type:
        stmt = stmt.where(HeritageMedia.media_type.ilike(f"%{media_type}%"))
        count_stmt = count_stmt.where(HeritageMedia.media_type.ilike(f"%{media_type}%"))
    if verification_status:
        stmt = stmt.where(HeritageMedia.verification_status.ilike(f"%{verification_status}%"))
        count_stmt = count_stmt.where(HeritageMedia.verification_status.ilike(f"%{verification_status}%"))

    total = db.execute(count_stmt).scalar_one()
    items = list(db.execute(stmt.offset(skip).limit(limit).order_by(HeritageMedia.id)).scalars().all())
    return items, total


def update_heritage_media(
    db: Session,
    media_id: int,
    update_data: HeritageMediaUpdate,
) -> Optional[HeritageMedia]:
    media = get_heritage_media(db, media_id)
    if media is None:
        return None

    if update_data.source_id is not None:
        source = db.execute(
            select(HeritageSource).where(HeritageSource.id == update_data.source_id)
        ).scalar_one_or_none()
        if source is None:
            raise ValueError(f"Heritage source with id {update_data.source_id} does not exist.")

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(media, field, value)

    db.commit()
    db.refresh(media)
    return media


def delete_heritage_media(
    db: Session,
    media_id: int,
) -> bool:
    """
    Deletes the media record from the database, then cleans up storage file.
    """
    media = get_heritage_media(db, media_id)
    if media is None:
        return False

    storage_key = media.storage_key
    db.delete(media)
    db.commit()

    # Clean up physical file after successful DB deletion
    try:
        storage_service.delete_file(storage_key)
    except Exception as exc:
        raise RuntimeError(f"Database record deleted, but physical file cleanup failed: {exc}")

    return True
