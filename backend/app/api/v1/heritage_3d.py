import os
from typing import List, Optional
from fastapi import (
    APIRouter,
    Body,
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
from app.models.heritage_3d_asset import Heritage3DAsset
from app.models.heritage_site import HeritageSite
from app.schemas.heritage_3d_asset import (
    Heritage3DAssetCreate,
    Heritage3DAssetUpdate,
    Heritage3DAssetResponse,
    Heritage3DAssetResponseWithUrl,
    Heritage3DAssetDiscoveryResponse,
    AssetValidationResult,
)
from app.services.heritage_3d_service import (
    create_heritage_3d_asset,
    get_heritage_3d_asset,
    get_pilot_asset,
    list_heritage_3d_assets_by_site,
    list_all_heritage_3d_assets,
    update_heritage_3d_asset,
    validate_heritage_3d_asset,
    publish_heritage_3d_asset,
    archive_heritage_3d_asset,
    delete_heritage_3d_asset,
)
from app.services.storage_service import storage_service

router = APIRouter(prefix="/heritage-3d", tags=["Phase 10: Interactive 3D Heritage Exploration"])


def _format_asset_response(asset: Heritage3DAsset) -> Heritage3DAssetResponseWithUrl:
    data = {c.name: getattr(asset, c.name) for c in asset.__table__.columns}
    data["file_url"] = f"/api/v1/heritage-3d/assets/{asset.id}/file"
    return Heritage3DAssetResponseWithUrl(**data)


# =========================================================
# PUBLIC ENDPOINTS
# =========================================================

@router.get(
    "/assets",
    response_model=Heritage3DAssetDiscoveryResponse,
    summary="List and filter 3D heritage assets",
)
def list_3d_assets(
    site_id: Optional[int] = Query(default=None, description="Filter by heritage site ID"),
    asset_format: Optional[str] = Query(default=None, description="Filter by format (e.g. GLB, GLTF)"),
    asset_origin: Optional[str] = Query(default=None, description="Filter by asset origin"),
    visibility_status: Optional[str] = Query(default="PUBLIC", description="Filter by visibility (PUBLIC, UNLISTED, ARCHIVED)"),
    is_pilot: Optional[bool] = Query(default=None, description="Filter pilot monument asset"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = list_all_heritage_3d_assets(
        db=db,
        site_id=site_id,
        asset_format=asset_format,
        visibility_status=visibility_status,
        is_pilot=is_pilot,
        skip=skip,
        limit=limit,
    )
    if asset_origin:
        items = [i for i in items if i.asset_origin.lower() == asset_origin.lower()]

    formatted = [_format_asset_response(i) for i in items]
    return Heritage3DAssetDiscoveryResponse(
        items=formatted,
        total=total,
        skip=skip,
        limit=limit,
        has_next=(skip + len(items)) < total,
    )


@router.get(
    "/pilot",
    response_model=Heritage3DAssetResponseWithUrl,
    summary="Get active pilot monument 3D asset",
)
def get_pilot_monument_asset(
    db: Session = Depends(get_db),
):
    pilot = get_pilot_asset(db)
    if not pilot:
        # Fallback to the first public 3D asset if not explicitly flagged as pilot
        items, _ = list_all_heritage_3d_assets(db=db, visibility_status="PUBLIC", limit=1)
        if items:
            pilot = items[0]
    if not pilot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No published 3D pilot monument asset found.",
        )
    return _format_asset_response(pilot)


@router.get(
    "/assets/{asset_id}",
    response_model=Heritage3DAssetResponseWithUrl,
    summary="Get details of a single 3D asset",
)
def get_asset_details(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = get_heritage_3d_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"3D asset with ID {asset_id} not found.",
        )
    return _format_asset_response(asset)


@router.get(
    "/assets/{asset_id}/file",
    summary="Download or stream 3D binary file",
)
def download_asset_file(
    asset_id: int,
    db: Session = Depends(get_db),
):
    asset = get_heritage_3d_asset(db, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"3D asset with ID {asset_id} not found.",
        )
    try:
        abs_path = storage_service.get_absolute_path(asset.storage_key)
        if not abs_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Physical asset file missing from storage.",
            )
        return FileResponse(
            path=str(abs_path),
            media_type=asset.mime_type,
            filename=asset.original_filename,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=86400",
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get(
    "/sites/{site_id}",
    response_model=List[Heritage3DAssetResponseWithUrl],
    summary="Get all 3D models available for a specific heritage site",
)
def get_site_3d_assets(
    site_id: int,
    db: Session = Depends(get_db),
):
    site = db.query(HeritageSite).filter(HeritageSite.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Heritage site with ID {site_id} not found.",
        )
    assets = list_heritage_3d_assets_by_site(db, site_id=site_id, public_only=True)
    return [_format_asset_response(a) for a in assets]


# =========================================================
# PROTECTED WORKFLOW ENDPOINTS (API KEY REQUIRED)
# =========================================================

@router.post(
    "/assets",
    response_model=Heritage3DAssetResponseWithUrl,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
    summary="Upload and ingest a verified 3D heritage model",
)
def ingest_3d_asset(
    site_id: int = Form(...),
    title: str = Form(...),
    asset_format: str = Form("GLB"),
    description: Optional[str] = Form(None),
    asset_origin: str = Form("HISTORICAL_RECONSTRUCTION"),
    source_url: Optional[str] = Form(None),
    source_identifier: Optional[str] = Form(None),
    creator: Optional[str] = Form(None),
    publisher: Optional[str] = Form(None),
    licence_name: str = Form("CC-BY-4.0"),
    licence_url: Optional[str] = Form(None),
    rights_status: str = Form("CREATIVE_COMMONS"),
    attribution_text: Optional[str] = Form(None),
    commercial_use_allowed: bool = Form(False),
    modification_allowed: bool = Form(True),
    redistribution_allowed: bool = Form(True),
    poly_count: Optional[int] = Form(None),
    vertex_count: Optional[int] = Form(None),
    texture_resolution: Optional[str] = Form(None),
    coordinate_notes: Optional[str] = Form(None),
    is_pilot: bool = Form(False),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Ingest a 3D digital model with complete provenance, SHA-256 integrity verification,
    and storage abstraction.
    """
    site = db.query(HeritageSite).filter(HeritageSite.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Heritage site with ID {site_id} does not exist.",
        )

    try:
        storage_key, sanitized_name, file_size, checksum = storage_service.save_file_stream(
            stream=file.file,
            original_filename=file.filename or f"model_{site_id}.glb",
            category_dir="3d",
            site_id=site_id,
            is_3d=True,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    content_type = file.content_type or "model/gltf-binary"
    fmt = asset_format.upper()

    asset_create = Heritage3DAssetCreate(
        heritage_site_id=site_id,
        title=title,
        description=description,
        asset_format=fmt,
        original_format=fmt,
        processed_format="GLB",
        storage_key=storage_key,
        original_filename=sanitized_name,
        mime_type=content_type,
        file_size_bytes=file_size,
        checksum_sha256=checksum,
        asset_origin=asset_origin,
        source_url=source_url,
        source_identifier=source_identifier,
        creator=creator,
        publisher=publisher,
        licence_name=licence_name,
        licence_url=licence_url,
        rights_status=rights_status,
        attribution_text=attribution_text or f"Created by {creator or 'Unknown'} under {licence_name}",
        commercial_use_allowed=commercial_use_allowed,
        modification_allowed=modification_allowed,
        redistribution_allowed=redistribution_allowed,
        poly_count=poly_count,
        vertex_count=vertex_count,
        texture_resolution=texture_resolution,
        coordinate_notes=coordinate_notes,
        is_pilot=is_pilot,
        validation_status="PENDING_REVIEW",
        visibility_status="PUBLIC",
    )

    try:
        created = create_heritage_3d_asset(db, asset_create)
        # Auto-validate ingested file
        validate_heritage_3d_asset(db, created.id)
        db.refresh(created)
        return _format_asset_response(created)
    except Exception as exc:
        storage_service.delete_file(storage_key)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/assets/{asset_id}/validate",
    response_model=AssetValidationResult,
    dependencies=[Depends(verify_write_access)],
    summary="Run validation checks on 3D asset file",
)
def validate_asset_endpoint(
    asset_id: int,
    db: Session = Depends(get_db),
):
    try:
        result = validate_heritage_3d_asset(db, asset_id)
        return AssetValidationResult(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "/assets/{asset_id}/publish",
    response_model=Heritage3DAssetResponseWithUrl,
    dependencies=[Depends(verify_write_access)],
    summary="Publish a validated 3D model for public viewing",
)
def publish_asset_endpoint(
    asset_id: int,
    visibility_status: str = Body(default="PUBLIC", embed=True),
    db: Session = Depends(get_db),
):
    try:
        published = publish_heritage_3d_asset(db, asset_id, visibility_status=visibility_status)
        return _format_asset_response(published)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post(
    "/assets/{asset_id}/archive",
    response_model=Heritage3DAssetResponseWithUrl,
    dependencies=[Depends(verify_write_access)],
    summary="Archive a 3D model",
)
def archive_asset_endpoint(
    asset_id: int,
    reason: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
):
    try:
        archived = archive_heritage_3d_asset(db, asset_id, reason=reason)
        return _format_asset_response(archived)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
