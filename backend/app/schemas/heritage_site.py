from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.heritage_source import HeritageSourceResponse
from app.schemas.heritage_media import HeritageMediaResponseWithUrl
from app.schemas.heritage_3d_asset import Heritage3DAssetResponseWithUrl


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


# =========================================================
# PHASE 5: COMPREHENSIVE SITE DETAILS RESPONSE
# =========================================================

class HeritageConnectionDetailItem(BaseModel):
    connection_id: int
    connected_site_id: int
    connected_site_name: str
    relationship_type: str
    confidence_score: Optional[float] = None
    description: Optional[str] = None
    direction: str  # "outgoing" or "incoming"


class HeritageSiteDetailResponse(HeritageSiteResponse):
    sources: List[HeritageSourceResponse] = Field(default_factory=list)
    media: List[HeritageMediaResponseWithUrl] = Field(default_factory=list)
    assets_3d: List[Heritage3DAssetResponseWithUrl] = Field(default_factory=list)
    connections: List[HeritageConnectionDetailItem] = Field(default_factory=list)
    stats: Dict[str, int] = Field(default_factory=dict)


# =========================================================
# PHASE 5: RELATED HERITAGE SITES DISCOVERY
# =========================================================

class DocumentedConnectionItem(BaseModel):
    connection_id: int
    connected_site_id: int
    connected_site_name: str
    relationship_type: str
    confidence_score: Optional[float] = None
    description: Optional[str] = None
    source: str = "DOCUMENTED_ARCHIVAL_RECORD"


class StructuredRelationItem(BaseModel):
    site_id: int
    name: str
    category: str
    state: str
    period: Optional[str] = None
    architecture: Optional[str] = None
    distance_km: Optional[float] = None
    shared_attributes: List[str] = Field(default_factory=list)


class SemanticSuggestionItem(BaseModel):
    site_id: int
    name: str
    state: str
    category: str
    recommendation_score: float
    reasons: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "AI-generated exploratory recommendation based on semantic similarity of architectural "
        "descriptions and historical context. Not primary archival evidence."
    )


class HeritageRelatedSitesResponse(BaseModel):
    site_id: int
    site_name: str
    documented_connections: List[DocumentedConnectionItem] = Field(default_factory=list)
    structured_relations: List[StructuredRelationItem] = Field(default_factory=list)
    semantic_suggestions: List[SemanticSuggestionItem] = Field(default_factory=list)
