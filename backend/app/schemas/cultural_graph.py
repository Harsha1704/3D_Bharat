from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.cultural_graph import (
    CulturalEntityType,
    CulturalRelationshipType,
    CulturalEvidenceStatus,
)


# =========================================================
# ENTITY SCHEMAS
# =========================================================

class CulturalGraphEntityBase(BaseModel):
    entity_type: str = Field(..., min_length=2, max_length=50)
    canonical_name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255)
    heritage_site_id: Optional[int] = None
    alternative_names: Optional[List[str]] = None
    description: Optional[str] = None
    geographical_context: Optional[str] = Field(default=None, max_length=255)
    period: Optional[str] = Field(default=None, max_length=255)
    metadata_json: Optional[Dict[str, Any]] = None
    verification_status: str = Field(default=CulturalEvidenceStatus.VERIFIED.value, max_length=50)


class CulturalGraphEntityCreate(CulturalGraphEntityBase):
    pass


class CulturalGraphEntityUpdate(BaseModel):
    canonical_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    alternative_names: Optional[List[str]] = None
    description: Optional[str] = None
    geographical_context: Optional[str] = None
    period: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    verification_status: Optional[str] = None


class CulturalGraphEntityResponse(CulturalGraphEntityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# RELATIONSHIP SCHEMAS
# =========================================================

class CulturalGraphRelationshipBase(BaseModel):
    source_entity_id: int = Field(..., gt=0)
    target_entity_id: int = Field(..., gt=0)
    relationship_type: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    directionality: str = Field(default="DIRECTED", max_length=20)
    evidence_status: str = Field(default=CulturalEvidenceStatus.DOCUMENTED.value, max_length=50)
    confidence_score: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    primary_source_id: Optional[int] = None
    source_citation: Optional[str] = None
    historical_period: Optional[str] = Field(default=None, max_length=255)
    legacy_connection_id: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None


class CulturalGraphRelationshipCreate(CulturalGraphRelationshipBase):
    pass


class CulturalGraphRelationshipUpdate(BaseModel):
    relationship_type: Optional[str] = None
    description: Optional[str] = None
    directionality: Optional[str] = None
    evidence_status: Optional[str] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    primary_source_id: Optional[int] = None
    source_citation: Optional[str] = None
    historical_period: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class CulturalGraphRelationshipResponse(CulturalGraphRelationshipBase):
    id: int
    source_entity_name: Optional[str] = None
    target_entity_name: Optional[str] = None
    source_entity_type: Optional[str] = None
    target_entity_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# GRAPH EXPLORATION & SEARCH SCHEMAS
# =========================================================

class CulturalGraphExploreResponse(BaseModel):
    center_entity_id: int
    center_entity: CulturalGraphEntityResponse
    depth: int
    total_nodes: int
    total_edges: int
    nodes: List[CulturalGraphEntityResponse]
    edges: List[CulturalGraphRelationshipResponse]


class CulturalGraphStatisticsResponse(BaseModel):
    total_entities: int
    total_relationships: int
    entities_by_type: Dict[str, int]
    relationships_by_type: Dict[str, int]
    relationships_by_evidence: Dict[str, int]


class RelationshipProvenanceItem(BaseModel):
    relationship_id: int
    relationship_type: str
    connected_entity_id: int
    connected_entity_name: str
    connected_entity_type: str
    evidence_status: str
    confidence_score: Optional[float] = None
    primary_source_id: Optional[int] = None
    source_title: Optional[str] = None
    source_citation: Optional[str] = None
    source_url: Optional[str] = None


class CulturalGraphProvenanceResponse(BaseModel):
    entity_id: int
    entity_name: str
    entity_type: str
    verification_status: str
    heritage_site_id: Optional[int] = None
    relationships_provenance: List[RelationshipProvenanceItem]
