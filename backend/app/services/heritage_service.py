from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.schemas.heritage_site import (
    HeritageSiteCreate,
    HeritageSiteResponse,
    HeritageSiteUpdate,
    HeritageSiteNearbyResponse,
)

from app.services.heritage_site_service import (
    create_heritage_site,
    get_heritage_site,
    get_heritage_sites,
    update_heritage_site,
    delete_heritage_site,
    get_nearby_heritage_sites,
)


router = APIRouter(
    prefix="/heritage-sites",
    tags=["Heritage Sites"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "",
    response_model=HeritageSiteResponse,
    status_code=201,
)
def create_site(
    site_data: HeritageSiteCreate,
    db: Session = Depends(get_db),
):
    return create_heritage_site(
        db,
        site_data,
    )


@router.get(
    "",
    response_model=List[HeritageSiteResponse],
)
def list_sites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return get_heritage_sites(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/nearby",
    response_model=List[HeritageSiteNearbyResponse],
)
def nearby_sites(
    latitude: float,
    longitude: float,
    radius_km: float = 10,
    db: Session = Depends(get_db),
):
    return get_nearby_heritage_sites(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )


@router.get(
    "/{site_id}",
    response_model=HeritageSiteResponse,
)
def get_site(
    site_id: int,
    db: Session = Depends(get_db),
):
    site = get_heritage_site(
        db,
        site_id,
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    return site


@router.put(
    "/{site_id}",
    response_model=HeritageSiteResponse,
)
def update_site(
    site_id: int,
    site_data: HeritageSiteUpdate,
    db: Session = Depends(get_db),
):
    site = update_heritage_site(
        db,
        site_id,
        site_data,
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    return site


@router.delete(
    "/{site_id}",
)
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_heritage_site(
        db,
        site_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    return {
        "message": "Heritage site deleted successfully"
    }