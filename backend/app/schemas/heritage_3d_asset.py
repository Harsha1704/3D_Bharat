from datetime import datetime
from typing import List, Optional
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
