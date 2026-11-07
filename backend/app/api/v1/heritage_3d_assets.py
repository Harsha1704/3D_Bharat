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
from app.schemas.heritage_3d_asset import (
    Heritage3DAssetCreate,
    Heritage3DAssetUpdate,
    Heritage3DAssetResponse,
)
from app.services.heritage_3d_service import (
    create_heritage_3d_asset,
    get_heritage_3d_asset,
    list_heritage_3d_assets_by_site,
    update_heritage_3d_asset,
    delete_heritage_3d_asset,
    add_companion_file_to_asset,
    verify_3d_asset_companions,
)
from app.services.storage_service import storage_service

router = APIRouter(tags=["Heritage 3D Assets & Digital Reconstruction"])


@router.post(
    "/heritage-sites/{site_id}/3d-assets",
    response_model=Heritage3DAssetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
)
def create_3d_asset_metadata(
    site_id: int,
    asset_data: Heritage3DAssetCreate,
    db: Session = Depends(get_db),
):
    """
    Register 3D digital preservation asset metadata for a heritage site.
    """
    asset_data.heritage_site_id = site_id
    try:
        return create_heritage_3d_asset(db, asset_data)
    except ValueError as exc:
        msg = str(exc)
        if "does not exist" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        elif "already exists" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


@router.post(
    "/heritage-sites/{site_id}/3d-assets/upload",
    response_model=Heritage3DAssetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
)
def upload_3d_asset_file(
    site_id: int,
    title: str = Form(...),
    asset_format: str = Form(...),  # GLB, GLTF, OBJ, PLY, GAUSSIAN_SPLAT
    description: Optional[str] = Form(default=None),
    units: Optional[str] = Form(default="meters"),
    coordinate_system: Optional[str] = Form(default=None),
    attribution: Optional[str] = Form(default=None),
    license: Optional[str] = Form(default=None),
    source_id: Optional[int] = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Stream upload a 3D digital asset (GLB, glTF, OBJ, PLY, or Gaussian Splat)
    and register its preservation metadata with SHA-256 verification.
    """
    try:
        storage_key, sanitized_name, file_size, checksum = storage_service.save_file_stream(
            stream=file.file,
            original_filename=file.filename or "model_asset",
            category_dir="3d",
            site_id=site_id,
            is_3d=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    content_type = file.content_type or "model/gltf-binary"

    asset_create = Heritage3DAssetCreate(
        heritage_site_id=site_id,
        title=title,
        description=description,
        asset_format=asset_format.upper(),
        storage_key=storage_key,
        original_filename=sanitized_name,
        mime_type=content_type,
        file_size_bytes=file_size,
        checksum_sha256=checksum,
        units=units,
        coordinate_system=coordinate_system,
        attribution=attribution,
        license=license,
        source_id=source_id,
        processing_status="READY",
    )

    try:
        return create_heritage_3d_asset(db, asset_create)
    except Exception as exc:
        # Cleanup uploaded file if database persistence fails
        storage_service.delete_file(storage_key)
        msg = str(exc)
        if "does not exist" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


@router.post(
    "/heritage-3d-assets/{asset_id}/companions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
)
def upload_companion_file(
    asset_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and attach a companion material (.mtl), texture image, or binary buffer
    strictly inside the 3D asset's isolated folder.
    """
    try:
        result = add_companion_file_to_asset(
            db=db,
            asset_id=asset_id,
            companion_filename=file.filename or "companion_file",
            stream=file.file,
        )
        return {
            "message": "Companion file attached successfully.",
            "asset_id": asset_id,
            **result,
        }
    except ValueError as exc:
        msg = str(exc)
        if "does not exist" in msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)


@router.get(
    "/heritage-3d-assets/{asset_id}/verify",
)
def verify_asset_companion_integrity(
    asset_id: int,
    db: Session = Depends(get_db),
):
    """
    Inspect model definitions and verify whether referenced companion files exist on disk.
    """
    try:
        return verify_3d_asset_companions(db=db, asset_id=asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get(
    "/heritage-sites/{site_id}/3d-assets",
    response_model=List[Heritage3DAssetResponse],
)
def list_3d_assets_for_site(
    site_id: int,
    asset_format: Optional[str] = Query(default=None),
    processing_status: Optional[str] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    List 3D preservation models for a heritage site.
    """
    return list_heritage_3d_assets_by_site(
        db,
        site_id=site_id,
        asset_format=asset_format.upper() if asset_format else None,
        processing_status=processing_status,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/heritage-3d-assets/{asset_id}",
    response_model=Heritage3DAssetResponse,
)
def get_3d_asset_by_id(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Heritage 3D asset not found.",
        )
    return asset


@router.get(
    "/heritage-3d-assets/{asset_id}/file",
)
def download_3d_asset_file(
    asset_id: int,
    db: Session = Depends(get_db),
):
    """
    Stream 3D preservation asset safely from local storage.
    """
    asset = get_heritage_3d_asset(db, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Heritage 3D asset not found.")

    try:
        abs_path = storage_service.get_absolute_path(asset.storage_key)
        if not abs_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset file missing from storage.")
        return FileResponse(
            path=str(abs_path),
            media_type=asset.mime_type,
            filename=asset.original_filename,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch(
    "/heritage-3d-assets/{asset_id}",
    response_model=Heritage3DAssetResponse,
    dependencies=[Depends(verify_write_access)],
)
def update_3d_asset_by_id(
    asset_id: int,
    update_data: Heritage3DAssetUpdate,
    db: Session = Depends(get_db),
):
    try:
        asset = update_heritage_3d_asset(db, asset_id, update_data)
        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heritage 3D asset not found.",
            )
        return asset
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete(
    "/heritage-3d-assets/{asset_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_write_access)],
)
def delete_3d_asset_by_id(
    asset_id: int,
    db: Session = Depends(get_db),
):
    try:
        deleted = delete_heritage_3d_asset(db, asset_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heritage 3D asset not found.",
            )
        return {"message": "Heritage 3D asset deleted successfully."}
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
