from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_write_access
from app.schemas.cultural_graph import (
    CulturalGraphEntityCreate,
    CulturalGraphEntityResponse,
    CulturalGraphRelationshipCreate,
    CulturalGraphRelationshipResponse,
    CulturalGraphExploreResponse,
    CulturalGraphStatisticsResponse,
    CulturalGraphProvenanceResponse,
)
from app.services.cultural_graph_service import (
    get_entity_by_id,
    get_entities,
    create_entity,
    get_relationships_for_entity,
    create_relationship,
    explore_graph,
    get_graph_statistics,
    get_entity_provenance,
)

router = APIRouter(
    prefix="/knowledge-graph",
    tags=["Cultural Knowledge Graph"],
)


# =========================================================
# ENTITIES ENDPOINTS
# =========================================================

@router.get(
    "/entities",
    response_model=List[CulturalGraphEntityResponse],
    summary="List Cultural Graph Entities",
)
def list_entities(
    response: Response,
    entity_type: Optional[str] = Query(None, description="Filter by entity type (HERITAGE_SITE, DYNASTY, etc.)"),
    verification_status: Optional[str] = Query(None, description="Filter by verification status"),
    search: Optional[str] = Query(None, description="Search canonical name or context"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Retrieve cultural entities in the knowledge graph with optional filtering and pagination.
    """
    entities, total = get_entities(
        db=db,
        skip=skip,
        limit=limit,
        entity_type=entity_type,
        verification_status=verification_status,
        search=search,
    )
    response.headers["X-Total-Count"] = str(total)
    return entities


@router.post(
    "/entities",
    response_model=CulturalGraphEntityResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
    summary="Create Cultural Graph Entity",
)
def create_cultural_entity(
    entity_data: CulturalGraphEntityCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new entity in the cultural knowledge graph.
    Requires write authentication.
    """
    try:
        return create_entity(db, entity_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/entities/{entity_id}",
    response_model=CulturalGraphEntityResponse,
    summary="Get Cultural Graph Entity Details",
)
def get_entity_details(
    entity_id: int,
    db: Session = Depends(get_db),
):
    """
    Get detailed information for a specific cultural entity.
    """
    entity = get_entity_by_id(db, entity_id)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found",
        )
    return entity


@router.get(
    "/entities/{entity_id}/relationships",
    response_model=List[CulturalGraphRelationshipResponse],
    summary="Get Relationships for Entity",
)
def get_entity_relationships(
    entity_id: int,
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    evidence_status: Optional[str] = Query(None, description="Filter by evidence status"),
    db: Session = Depends(get_db),
):
    """
    Get all incoming and outgoing relationships for a cultural entity.
    """
    entity = get_entity_by_id(db, entity_id)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity {entity_id} not found",
        )
    return get_relationships_for_entity(
        db=db,
        entity_id=entity_id,
        relationship_type=relationship_type,
        evidence_status=evidence_status,
    )


@router.get(
    "/entities/{entity_id}/provenance",
    response_model=CulturalGraphProvenanceResponse,
    summary="Get Relationship Provenance for Entity",
)
def get_entity_provenance_dossier(
    entity_id: int,
    db: Session = Depends(get_db),
):
    """
    Get full citation, source, and evidence status audit trail for an entity's relationships.
    """
    try:
        return get_entity_provenance(db, entity_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# =========================================================
# RELATIONSHIPS ENDPOINTS
# =========================================================

@router.post(
    "/relationships",
    response_model=CulturalGraphRelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
    summary="Create Cultural Graph Relationship",
)
def create_cultural_relationship(
    rel_data: CulturalGraphRelationshipCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new typed, evidence-tagged relationship between cultural entities.
    Requires write authentication.
    """
    try:
        return create_relationship(db, rel_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# =========================================================
# GRAPH EXPLORATION & SEARCH
# =========================================================

@router.get(
    "/explore/{entity_id}",
    response_model=CulturalGraphExploreResponse,
    summary="Explore Bounded Knowledge Graph",
)
def explore_cultural_graph(
    entity_id: int,
    depth: int = Query(1, ge=1, le=3, description="Exploration depth (1 to 3 hops)"),
    entity_types: Optional[List[str]] = Query(None, description="Filter included neighbor entity types"),
    relationship_types: Optional[List[str]] = Query(None, description="Filter included relationship types"),
    evidence_status: Optional[str] = Query(None, description="Filter by evidence status"),
    limit: int = Query(50, ge=1, le=100, description="Max total nodes returned"),
    db: Session = Depends(get_db),
):
    """
    Explore the cultural knowledge graph outward from a central entity up to 3 hops.
    Bounded traversal ensures response latency and UI performance.
    """
    try:
        return explore_graph(
            db=db,
            center_entity_id=entity_id,
            max_depth=depth,
            entity_types=entity_types,
            relationship_types=relationship_types,
            evidence_status=evidence_status,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/search",
    response_model=List[CulturalGraphEntityResponse],
    summary="Search Cultural Graph Entities",
)
def search_cultural_entities(
    q: str = Query(..., min_length=1, description="Search query string"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Search cultural entities by name, period, or geographical context.
    """
    entities, _ = get_entities(
        db=db,
        skip=0,
        limit=limit,
        entity_type=entity_type,
        search=q,
    )
    return entities


# =========================================================
# STATISTICS
# =========================================================

@router.get(
    "/statistics",
    response_model=CulturalGraphStatisticsResponse,
    summary="Get Cultural Knowledge Graph Statistics",
)
def get_cultural_graph_statistics(
    db: Session = Depends(get_db),
):
    """
    Return global statistics on entity counts by type, relationship counts by type, and evidence breakdowns.
    """
    return get_graph_statistics(db)
