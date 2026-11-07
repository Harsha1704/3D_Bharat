from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class HeritageMediaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    media_type: str = Field(..., min_length=1, max_length=50)
    attribution: Optional[str] = Field(default=None, max_length=255)
    license: Optional[str] = Field(default=None, max_length=100)
    capture_date: Optional[str] = Field(default=None, max_length=100)
    verification_status: str = Field(default="UNVERIFIED", max_length=50)
    source_id: Optional[int] = Field(default=None, gt=0)


class HeritageMediaCreate(HeritageMediaBase):
    heritage_site_id: Optional[int] = Field(default=None, gt=0)
    storage_key: str = Field(..., min_length=1, max_length=255)
    original_filename: str = Field(..., min_length=1, max_length=255)
    mime_type: str = Field(..., min_length=1, max_length=100)
    file_size_bytes: int = Field(..., ge=0)
    checksum_sha256: str = Field(..., min_length=64, max_length=64)


class HeritageMediaUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    media_type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    attribution: Optional[str] = Field(default=None, max_length=255)
    license: Optional[str] = Field(default=None, max_length=100)
    capture_date: Optional[str] = Field(default=None, max_length=100)
    verification_status: Optional[str] = Field(default=None, max_length=50)
    source_id: Optional[int] = Field(default=None, gt=0)


class HeritageMediaResponse(HeritageMediaBase):
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


class HeritageMediaResponseWithUrl(HeritageMediaResponse):
    file_url: str


class HeritageMediaDiscoveryResponse(BaseModel):
    items: List[HeritageMediaResponseWithUrl]
    total: int
    skip: int
    limit: int
    has_next: bool
