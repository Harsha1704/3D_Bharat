from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_write_access
from app.schemas.heritage_source import (
    HeritageSourceCreate,
    HeritageSourceUpdate,
    HeritageSourceResponse,
)
from app.services.heritage_source_service import (
    create_heritage_source,
    get_heritage_source,
    get_heritage_sources_by_site,
    update_heritage_source,
    delete_heritage_source,
)

router = APIRouter(tags=["Heritage Sources & Provenance"])


@router.post(
    "/heritage-sites/{site_id}/sources",
    response_model=HeritageSourceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
)
def create_source_for_site(
    site_id: int,
    source_data: HeritageSourceCreate,
    db: Session = Depends(get_db),
):
    """
    Register a historical source / provenance record associated with a heritage site.
    """
    source_data.heritage_site_id = site_id
    try:
        return create_heritage_source(db, source_data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/heritage-sites/{site_id}/sources",
    response_model=List[HeritageSourceResponse],
)
def list_sources_for_site(
    site_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List historical sources and citations for a heritage site.
    """
    return get_heritage_sources_by_site(db, site_id, skip=skip, limit=limit)


@router.get(
    "/heritage-sources/{source_id}",
    response_model=HeritageSourceResponse,
)
def get_source_by_id(
    source_id: int,
    db: Session = Depends(get_db),
):
    source = get_heritage_source(db, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heritage source not found.",
        )
    return source


@router.patch(
    "/heritage-sources/{source_id}",
    response_model=HeritageSourceResponse,
    dependencies=[Depends(verify_write_access)],
)
def update_source_by_id(
    source_id: int,
    update_data: HeritageSourceUpdate,
    db: Session = Depends(get_db),
):
    source = update_heritage_source(db, source_id, update_data)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heritage source not found.",
        )
    return source


@router.delete(
    "/heritage-sources/{source_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_write_access)],
)
def delete_source_by_id(
    source_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_heritage_source(db, source_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heritage source not found.",
        )
    return {"message": "Heritage source deleted successfully."}
