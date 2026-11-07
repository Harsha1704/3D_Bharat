from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_write_access
from app.schemas.heritage_media import (
    HeritageMediaCreate,
    HeritageMediaUpdate,
    HeritageMediaResponse,
    HeritageMediaDiscoveryResponse,
    HeritageMediaResponseWithUrl,
)
from app.services.heritage_media_service import (
    create_heritage_media,
    get_heritage_media,
    list_heritage_media_by_site,
    list_all_heritage_media,
    update_heritage_media,
    delete_heritage_media,
)
from app.services.storage_service import storage_service

router = APIRouter(tags=["Heritage Media & Preservation"])


@router.post(
    "/heritage-sites/{site_id}/media",
    response_model=HeritageMediaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
)
def create_media_metadata(
    site_id: int,
    media_data: HeritageMediaCreate,
    db: Session = Depends(get_db),
):
    """
    Register heritage media metadata for an existing heritage site.
    """
    media_data.heritage_site_id = site_id
    try:
        return create_heritage_media(db, media_data)
    except ValueError as exc:
        msg = str(exc)
        if "does not exist" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        elif "already exists" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


@router.post(
    "/heritage-sites/{site_id}/media/upload",
    response_model=HeritageMediaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
)
def upload_media_file(
    site_id: int,
    title: str = Form(...),
    media_type: str = Form(...),
    description: Optional[str] = Form(default=None),
    attribution: Optional[str] = Form(default=None),
    license: Optional[str] = Form(default=None),
    capture_date: Optional[str] = Form(default=None),
    source_id: Optional[int] = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Stream upload a media file (archival photo, scan, audio guide, or documentary video)
    and register its metadata with SHA-256 verification.
    """
    try:
        storage_key, sanitized_name, file_size, checksum = storage_service.save_file_stream(
            stream=file.file,
            original_filename=file.filename or "media_asset",
            category_dir="media",
            site_id=site_id,
            is_3d=False,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    content_type = file.content_type or "application/octet-stream"

    media_create = HeritageMediaCreate(
        heritage_site_id=site_id,
        title=title,
        description=description,
        media_type=media_type,
        storage_key=storage_key,
        original_filename=sanitized_name,
        mime_type=content_type,
        file_size_bytes=file_size,
        checksum_sha256=checksum,
        attribution=attribution,
        license=license,
        capture_date=capture_date,
        source_id=source_id,
    )

    try:
        return create_heritage_media(db, media_create)
    except Exception as exc:
        # Cleanup uploaded file if database persistence fails
        storage_service.delete_file(storage_key)
        msg = str(exc)
        if "does not exist" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


@router.get(
    "/heritage-sites/{site_id}/media",
    response_model=List[HeritageMediaResponse],
    summary="List preservation media linked to a heritage site",
)
def list_media_for_site(
    site_id: int,
    media_type: Optional[str] = Query(default=None),
    verification_status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List preservation media linked to a heritage site with filtering and pagination.
    """
    return list_heritage_media_by_site(
        db,
        site_id=site_id,
        media_type=media_type,
        verification_status=verification_status,
        skip=skip,
        limit=limit,
    )


# =========================================================
# GLOBAL MEDIA DISCOVERY (PHASE 5)
# GET /api/v1/heritage-media
# =========================================================

@router.get(
    "/heritage-media",
    response_model=HeritageMediaDiscoveryResponse,
    summary="Global discovery of preservation media assets across all heritage sites",
)
def discover_heritage_media(
    site_id: Optional[int] = Query(default=None, description="Optional heritage site filter"),
    media_type: Optional[str] = Query(default=None, description="Filter by media type (e.g. IMAGE, AUDIO, VIDEO)"),
    verification_status: Optional[str] = Query(default=None, description="Filter by status (e.g. VERIFIED, ARCHIVAL)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = list_all_heritage_media(
        db=db,
        site_id=site_id,
        media_type=media_type,
        verification_status=verification_status,
        skip=skip,
        limit=limit,
    )

    formatted_items = []
    for item in items:
        item_dict = {c.name: getattr(item, c.name) for c in item.__table__.columns}
        item_dict["file_url"] = f"/api/v1/heritage-media/{item.id}/file"
        formatted_items.append(HeritageMediaResponseWithUrl(**item_dict))

    has_next = (skip + len(items)) < total
    return HeritageMediaDiscoveryResponse(
        items=formatted_items,
        total=total,
        skip=skip,
        limit=limit,
        has_next=has_next,
    )


@router.get(
    "/heritage-media/{media_id}",
    response_model=HeritageMediaResponse,
    summary="Get single heritage media metadata record",
)
def get_media_by_id(
    media_id: int,
    db: Session = Depends(get_db),
):
    media = get_heritage_media(db, media_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heritage media asset not found.",
        )
    return media


@router.get(
    "/heritage-media/{media_id}/file",
    summary="Stream verified media file safely from storage",
)
def download_media_file(
    media_id: int,
    db: Session = Depends(get_db),
):
    """
    Stream verified media asset safely from local storage.
    """
    media = get_heritage_media(db, media_id)
    if media is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Heritage media not found.")

    try:
        abs_path = storage_service.get_absolute_path(media.storage_key)
        if not abs_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset file missing from storage.")
        return FileResponse(
            path=str(abs_path),
            media_type=media.mime_type,
            filename=media.original_filename,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch(
    "/heritage-media/{media_id}",
    response_model=HeritageMediaResponse,
    dependencies=[Depends(verify_write_access)],
    summary="Update heritage media metadata",
)
def update_media_by_id(
    media_id: int,
    update_data: HeritageMediaUpdate,
    db: Session = Depends(get_db),
):
    try:
        media = update_heritage_media(db, media_id, update_data)
        if media is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heritage media asset not found.",
            )
        return media
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete(
    "/heritage-media/{media_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_write_access)],
    summary="Delete heritage media asset and remove file from storage",
)
def delete_media_by_id(
    media_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted = delete_heritage_media(db, media_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heritage media asset not found.",
            )
        return {"message": "Heritage media deleted successfully."}
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
