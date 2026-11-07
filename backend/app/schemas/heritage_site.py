from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# BASE SCHEMA
# =========================================================

class HeritageSiteBase(BaseModel):
    external_id: str
    name: str
    state: str
    district: Optional[str] = None
    city: Optional[str] = None
    category: str
    period: Optional[str] = None
    description: str
    significance: Optional[str] = None
    architecture: Optional[str] = None

    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )

    tags: Optional[List[str]] = None
    historical_events: Optional[List[str]] = None
    associated_people: Optional[List[str]] = None
    traditions: Optional[List[str]] = None


# =========================================================
# CREATE
# =========================================================

class HeritageSiteCreate(HeritageSiteBase):
    pass


# =========================================================
# UPDATE
# =========================================================

class HeritageSiteUpdate(BaseModel):
    external_id: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None
    significance: Optional[str] = None
    architecture: Optional[str] = None

    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )

    tags: Optional[List[str]] = None
    historical_events: Optional[List[str]] = None
    associated_people: Optional[List[str]] = None
    traditions: Optional[List[str]] = None


# =========================================================
# NORMAL RESPONSE
# =========================================================

class HeritageSiteResponse(HeritageSiteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# NEARBY RESPONSE
# =========================================================

class HeritageSiteNearbyResponse(HeritageSiteResponse):
    distance_km: float


# =========================================================
# PAGINATED SEARCH RESPONSE
# =========================================================

class HeritageSiteSearchResponse(BaseModel):
    items: List[HeritageSiteResponse]

    total: int

    skip: int

    limit: int

    has_next: bool


class HeritageSiteRecommendationResponse(HeritageSiteResponse):
    structured_score: Optional[float] = None
    semantic_score: Optional[float] = None
    recommendation_score: float
    recommendation_reasons: List[str]