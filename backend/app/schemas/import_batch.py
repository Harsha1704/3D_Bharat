from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ImportBatchBase(BaseModel):
    batch_id: str = Field(..., min_length=1, max_length=100)
    source_organization: str = Field(..., min_length=1, max_length=200)
    source_dataset: str = Field(..., min_length=1, max_length=200)
    source_url: Optional[str] = Field(default=None, max_length=500)
    license: Optional[str] = Field(default=None, max_length=100)


class ImportBatchCreate(ImportBatchBase):
    pass


class ImportBatchResponse(ImportBatchBase):
    id: int
    status: str
    total_records: int
    accepted_records: int
    rejected_records: int
    duplicate_records: int
    updated_records: int
    inserted_records: int
    error_log: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ImportRecordSummary(BaseModel):
    batch_id: str
    organization: str
    dataset: str
    total_records: int
    inserted_records: int
    updated_records: int
    duplicate_records: int
    rejected_records: int
    errors: List[str] = Field(default_factory=list)
