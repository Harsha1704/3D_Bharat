from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class Heritage3DAssetBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    asset_format: str = Field(..., min_length=1, max_length=50)  # GLB, GLTF, OBJ, PLY, GAUSSIAN_SPLAT
    units: Optional[str] = Field(default="meters", max_length=50)
    coordinate_system: Optional[str] = Field(default=None, max_length=100)
    companion_files: Optional[List[str]] = None
    bounding_box: Optional[str] = None
    attribution: Optional[str] = Field(default=None, max_length=255)
    license: Optional[str] = Field(default=None, max_length=100)
    processing_status: str = Field(default="READY", max_length=50)
    verification_status: str = Field(default="UNVERIFIED", max_length=50)
    source_id: Optional[int] = Field(default=None, gt=0)

    # Phase 10 Provenance & Pipeline fields
    asset_origin: str = Field(default="HISTORICAL_RECONSTRUCTION", max_length=50)
    original_format: Optional[str] = Field(default=None, max_length=50)
    processed_format: str = Field(default="GLB", max_length=50)
    preview_image_key: Optional[str] = Field(default=None, max_length=255)
    source_url: Optional[str] = Field(default=None, max_length=1000)
    source_identifier: Optional[str] = Field(default=None, max_length=255)
    creator: Optional[str] = Field(default=None, max_length=255)
    publisher: Optional[str] = Field(default=None, max_length=255)
    licence_name: str = Field(default="CC-BY-4.0", max_length=255)
    licence_url: Optional[str] = Field(default=None, max_length=1000)
    rights_status: str = Field(default="CREATIVE_COMMONS", max_length=50)
    attribution_text: Optional[str] = None
    commercial_use_allowed: bool = False
    modification_allowed: bool = True
    redistribution_allowed: bool = True
    poly_count: Optional[int] = None
    vertex_count: Optional[int] = None
    texture_resolution: Optional[str] = Field(default=None, max_length=50)
    lod_levels: int = Field(default=1, ge=1)
    coordinate_notes: Optional[str] = None
    validation_status: str = Field(default="READY", max_length=50)
    validation_report: Optional[str] = None
    visibility_status: str = Field(default="PUBLIC", max_length=50)
    is_pilot: bool = False


class Heritage3DAssetCreate(Heritage3DAssetBase):
    heritage_site_id: Optional[int] = Field(default=None, gt=0)
    storage_key: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    mime_type: str = Field(..., min_length=1, max_length=100)
    file_size_bytes: int = Field(..., ge=0)
    checksum_sha256: str = Field(..., min_length=64, max_length=64)


class Heritage3DAssetUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    asset_format: Optional[str] = Field(default=None, min_length=1, max_length=50)
    units: Optional[str] = Field(default=None, max_length=50)
    coordinate_system: Optional[str] = Field(default=None, max_length=100)
    companion_files: Optional[List[str]] = None
    bounding_box: Optional[str] = None
    attribution: Optional[str] = Field(default=None, max_length=255)
    license: Optional[str] = Field(default=None, max_length=100)
    processing_status: Optional[str] = Field(default=None, max_length=50)
    verification_status: Optional[str] = Field(default=None, max_length=50)
    source_id: Optional[int] = Field(default=None, gt=0)

    asset_origin: Optional[str] = Field(default=None, max_length=50)
    original_format: Optional[str] = Field(default=None, max_length=50)
    processed_format: Optional[str] = Field(default=None, max_length=50)
    preview_image_key: Optional[str] = Field(default=None, max_length=255)
    source_url: Optional[str] = Field(default=None, max_length=1000)
    source_identifier: Optional[str] = Field(default=None, max_length=255)
    creator: Optional[str] = Field(default=None, max_length=255)
    publisher: Optional[str] = Field(default=None, max_length=255)
    licence_name: Optional[str] = Field(default=None, max_length=255)
    licence_url: Optional[str] = Field(default=None, max_length=1000)
    rights_status: Optional[str] = Field(default=None, max_length=50)
    attribution_text: Optional[str] = None
    commercial_use_allowed: Optional[bool] = None
    modification_allowed: Optional[bool] = None
    redistribution_allowed: Optional[bool] = None
    poly_count: Optional[int] = None
    vertex_count: Optional[int] = None
    texture_resolution: Optional[str] = Field(default=None, max_length=50)
    lod_levels: Optional[int] = Field(default=None, ge=1)
    coordinate_notes: Optional[str] = None
    validation_status: Optional[str] = Field(default=None, max_length=50)
    validation_report: Optional[str] = None
    visibility_status: Optional[str] = Field(default=None, max_length=50)
    is_pilot: Optional[bool] = None


class Heritage3DAssetResponse(Heritage3DAssetBase):
    id: int
    heritage_site_id: int
    storage_key: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    checksum_sha256: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Heritage3DAssetResponseWithUrl(Heritage3DAssetResponse):
    file_url: str


class Heritage3DAssetDiscoveryResponse(BaseModel):
    items: List[Heritage3DAssetResponseWithUrl]
    total: int
    skip: int
    limit: int
    has_next: bool


class AssetValidationResult(BaseModel):
    asset_id: int
    is_valid: bool
    magic_bytes_valid: bool
    format_recognized: bool
    file_size_bytes: int
    checksum_sha256: str
    validation_status: str
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
