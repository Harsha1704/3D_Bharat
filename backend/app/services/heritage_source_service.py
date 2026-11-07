from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.schemas.heritage_source import HeritageSourceCreate, HeritageSourceUpdate


def create_heritage_source(
    db: Session,
    source_data: HeritageSourceCreate,
) -> HeritageSource:
    """
    Creates a new historical source / provenance record.
    If heritage_site_id is provided, validates that the referenced heritage site exists.
    """
    if source_data.heritage_site_id is not None:
        site = db.execute(
            select(HeritageSite).where(HeritageSite.id == source_data.heritage_site_id)
        ).scalar_one_or_none()
        if site is None:
            raise ValueError(f"Heritage site with id {source_data.heritage_site_id} does not exist.")

    data = source_data.model_dump()
    source = HeritageSource(**data)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def get_heritage_source(
    db: Session,
    source_id: int,
) -> Optional[HeritageSource]:
    stmt = select(HeritageSource).where(HeritageSource.id == source_id)
    return db.execute(stmt).scalar_one_or_none()


def get_heritage_sources_by_site(
    db: Session,
    site_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[HeritageSource]:
    stmt = (
        select(HeritageSource)
        .where(HeritageSource.heritage_site_id == site_id)
        .offset(skip)
        .limit(limit)
        .order_by(HeritageSource.id)
    )
    return list(db.execute(stmt).scalars().all())


def update_heritage_source(
    db: Session,
    source_id: int,
    update_data: HeritageSourceUpdate,
) -> Optional[HeritageSource]:
    source = get_heritage_source(db, source_id)
    if source is None:
        return None

    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)
    return source


def delete_heritage_source(
    db: Session,
    source_id: int,
) -> bool:
    source = get_heritage_source(db, source_id)
    if source is None:
        return False

    db.delete(source)
    db.commit()
    return True
