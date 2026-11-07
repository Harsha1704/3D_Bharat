from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class HeritageSourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., min_length=1, max_length=100)
    author: Optional[str] = Field(default=None, max_length=255)
    institution: Optional[str] = Field(default=None, max_length=255)
    publication_date: Optional[str] = Field(default=None, max_length=100)
    citation: Optional[str] = None
    url: Optional[str] = Field(default=None, max_length=500)
    license: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
    verification_status: str = Field(default="UNVERIFIED", max_length=50)


class HeritageSourceCreate(HeritageSourceBase):
    heritage_site_id: Optional[int] = Field(default=None, gt=0)


class HeritageSourceUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    source_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    author: Optional[str] = Field(default=None, max_length=255)
    institution: Optional[str] = Field(default=None, max_length=255)
    publication_date: Optional[str] = Field(default=None, max_length=100)
    citation: Optional[str] = None
    url: Optional[str] = Field(default=None, max_length=500)
    license: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None
    verification_status: Optional[str] = Field(default=None, max_length=50)


class HeritageSourceResponse(HeritageSourceBase):
    id: int
    heritage_site_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
