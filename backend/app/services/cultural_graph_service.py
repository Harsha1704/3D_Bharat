import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.cultural_graph import (
    CulturalEntityType,
    CulturalRelationshipType,
    CulturalEvidenceStatus,
    CulturalGraphEntity,
    CulturalGraphRelationship,
)
from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.schemas.cultural_graph import (
    CulturalGraphEntityCreate,
    CulturalGraphEntityUpdate,
    CulturalGraphEntityResponse,
    CulturalGraphRelationshipCreate,
    CulturalGraphRelationshipUpdate,
    CulturalGraphRelationshipResponse,
    CulturalGraphExploreResponse,
    CulturalGraphStatisticsResponse,
    RelationshipProvenanceItem,
    CulturalGraphProvenanceResponse,
)


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", cleaned).strip("-")


# =========================================================
# ENTITY SERVICES
# =========================================================

def get_entity_by_id(db: Session, entity_id: int) -> Optional[CulturalGraphEntity]:
    stmt = select(CulturalGraphEntity).where(CulturalGraphEntity.id == entity_id)
    return db.execute(stmt).scalar_one_or_none()


def get_entity_by_site_id(db: Session, site_id: int) -> Optional[CulturalGraphEntity]:
    stmt = select(CulturalGraphEntity).where(CulturalGraphEntity.heritage_site_id == site_id)
    return db.execute(stmt).scalar_one_or_none()


def get_entity_by_slug(db: Session, slug: str) -> Optional[CulturalGraphEntity]:
    stmt = select(CulturalGraphEntity).where(CulturalGraphEntity.slug == slug)
    return db.execute(stmt).scalar_one_or_none()


def get_entities(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    entity_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    search: Optional[str] = None,
) -> Tuple[List[CulturalGraphEntity], int]:
    limit = min(max(1, limit), 200)
    skip = max(0, skip)

    conditions = []
    if entity_type:
        conditions.append(CulturalGraphEntity.entity_type == entity_type)
    if verification_status:
        conditions.append(CulturalGraphEntity.verification_status == verification_status)
    if search:
        search_pattern = f"%{search.strip()}%"
        conditions.append(
            or_(
                CulturalGraphEntity.canonical_name.ilike(search_pattern),
                CulturalGraphEntity.geographical_context.ilike(search_pattern),
                CulturalGraphEntity.period.ilike(search_pattern),
            )
        )

    count_stmt = select(func.count(CulturalGraphEntity.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = db.scalar(count_stmt) or 0

    query = select(CulturalGraphEntity)
    if conditions:
        query = query.where(*conditions)
    query = query.order_by(CulturalGraphEntity.canonical_name.asc()).offset(skip).limit(limit)

    results = list(db.execute(query).scalars().all())
    return results, total


def create_entity(db: Session, entity_data: CulturalGraphEntityCreate) -> CulturalGraphEntity:
    # Validate entity_type
    valid_types = {t.value for t in CulturalEntityType}
    if entity_data.entity_type not in valid_types:
        raise ValueError(
            f"Invalid entity_type '{entity_data.entity_type}'. Must be one of: {sorted(valid_types)}"
        )

    # Validate verification_status
    valid_status = {s.value for s in CulturalEvidenceStatus}
    if entity_data.verification_status not in valid_status:
        raise ValueError(
            f"Invalid verification_status '{entity_data.verification_status}'. Must be one of: {sorted(valid_status)}"
        )

    # Validate heritage site association if provided
    if entity_data.heritage_site_id is not None:
        site = db.execute(
            select(HeritageSite).where(HeritageSite.id == entity_data.heritage_site_id)
        ).scalar_one_or_none()
        if site is None:
            raise ValueError(f"Heritage site with id {entity_data.heritage_site_id} does not exist.")

        existing_entity = get_entity_by_site_id(db, entity_data.heritage_site_id)
        if existing_entity is not None:
            raise ValueError(
                f"Heritage site {entity_data.heritage_site_id} is already mapped to CulturalGraphEntity {existing_entity.id} ({existing_entity.canonical_name}). Duplicate site mappings are forbidden."
            )

    # Generate or validate slug
    slug = entity_data.slug or _slugify(entity_data.canonical_name)
    existing_slug = get_entity_by_slug(db, slug)
    if existing_slug is not None:
        counter = 2
        while get_entity_by_slug(db, f"{slug}-{counter}") is not None:
            counter += 1
        slug = f"{slug}-{counter}"

    data_dict = entity_data.model_dump()
    data_dict["slug"] = slug

    entity = CulturalGraphEntity(**data_dict)
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


# =========================================================
# RELATIONSHIP SERVICES
# =========================================================

def get_relationship_by_id(db: Session, relationship_id: int) -> Optional[CulturalGraphRelationship]:
    stmt = select(CulturalGraphRelationship).where(CulturalGraphRelationship.id == relationship_id)
    return db.execute(stmt).scalar_one_or_none()


def enrich_relationship_response(
    rel: CulturalGraphRelationship,
    entity_map: Optional[Dict[int, CulturalGraphEntity]] = None,
) -> CulturalGraphRelationshipResponse:
    source_name = None
    target_name = None
    source_type = None
    target_type = None

    if entity_map:
        source_ent = entity_map.get(rel.source_entity_id)
        target_ent = entity_map.get(rel.target_entity_id)
        if source_ent:
            source_name = source_ent.canonical_name
            source_type = source_ent.entity_type
        if target_ent:
            target_name = target_ent.canonical_name
            target_type = target_ent.entity_type

    res = CulturalGraphRelationshipResponse.model_validate(rel)
    res.source_entity_name = source_name
    res.target_entity_name = target_name
    res.source_entity_type = source_type
    res.target_entity_type = target_type
    return res


def get_relationships_for_entity(
    db: Session,
    entity_id: int,
    relationship_type: Optional[str] = None,
    evidence_status: Optional[str] = None,
) -> List[CulturalGraphRelationshipResponse]:
    conditions = [
        or_(
            CulturalGraphRelationship.source_entity_id == entity_id,
            CulturalGraphRelationship.target_entity_id == entity_id,
        )
    ]
    if relationship_type:
        conditions.append(CulturalGraphRelationship.relationship_type == relationship_type)
    if evidence_status:
        conditions.append(CulturalGraphRelationship.evidence_status == evidence_status)

    stmt = select(CulturalGraphRelationship).where(*conditions)
    relationships = list(db.execute(stmt).scalars().all())

    # Build entity map for name resolution
    entity_ids = set()
    for r in relationships:
        entity_ids.add(r.source_entity_id)
        entity_ids.add(r.target_entity_id)

    entity_map = {}
    if entity_ids:
        ents = db.execute(
            select(CulturalGraphEntity).where(CulturalGraphEntity.id.in_(entity_ids))
        ).scalars().all()
        entity_map = {e.id: e for e in ents}

    return [enrich_relationship_response(r, entity_map) for r in relationships]


def create_relationship(
    db: Session,
    rel_data: CulturalGraphRelationshipCreate,
) -> CulturalGraphRelationshipResponse:
    if rel_data.source_entity_id == rel_data.target_entity_id:
        raise ValueError("Self-referential relationships are not permitted.")

    # Validate source and target entity existence
    source = get_entity_by_id(db, rel_data.source_entity_id)
    if not source:
        raise ValueError(f"Source entity {rel_data.source_entity_id} does not exist.")

    target = get_entity_by_id(db, rel_data.target_entity_id)
    if not target:
        raise ValueError(f"Target entity {rel_data.target_entity_id} does not exist.")

    # Validate relationship type
    valid_rel_types = {t.value for t in CulturalRelationshipType}
    if rel_data.relationship_type not in valid_rel_types:
        raise ValueError(
            f"Invalid relationship_type '{rel_data.relationship_type}'. Must be one of: {sorted(valid_rel_types)}"
        )

    # Validate evidence status
    valid_evidence = {s.value for s in CulturalEvidenceStatus}
    if rel_data.evidence_status not in valid_evidence:
        raise ValueError(
            f"Invalid evidence_status '{rel_data.evidence_status}'. Must be one of: {sorted(valid_evidence)}"
        )

    # Check for existing duplicate relationship
    duplicate_stmt = select(CulturalGraphRelationship).where(
        CulturalGraphRelationship.source_entity_id == rel_data.source_entity_id,
        CulturalGraphRelationship.target_entity_id == rel_data.target_entity_id,
        CulturalGraphRelationship.relationship_type == rel_data.relationship_type,
    )
    if db.execute(duplicate_stmt).scalar_one_or_none() is not None:
        raise ValueError(
            f"Relationship '{rel_data.relationship_type}' already exists between entity {rel_data.source_entity_id} and {rel_data.target_entity_id}."
        )

    # Validate primary source if provided
    if rel_data.primary_source_id is not None:
        source_rec = db.execute(
            select(HeritageSource).where(HeritageSource.id == rel_data.primary_source_id)
        ).scalar_one_or_none()
        if source_rec is None:
            raise ValueError(f"HeritageSource with id {rel_data.primary_source_id} does not exist.")

    rel = CulturalGraphRelationship(**rel_data.model_dump())
    db.add(rel)
    db.commit()
    db.refresh(rel)

    entity_map = {source.id: source, target.id: target}
    return enrich_relationship_response(rel, entity_map)


# =========================================================
# BOUNDED GRAPH EXPLORATION & TRAVERSAL
# =========================================================

def explore_graph(
    db: Session,
    center_entity_id: int,
    max_depth: int = 1,
    entity_types: Optional[List[str]] = None,
    relationship_types: Optional[List[str]] = None,
    evidence_status: Optional[str] = None,
    limit: int = 50,
) -> CulturalGraphExploreResponse:
    center_entity = get_entity_by_id(db, center_entity_id)
    if center_entity is None:
        raise ValueError(f"Entity with id {center_entity_id} not found.")

    # Guard bounds
    bounded_depth = min(max(1, max_depth), 3)
    bounded_limit = min(max(1, limit), 100)

    visited_entity_ids: Set[int] = {center_entity_id}
    current_frontier: Set[int] = {center_entity_id}
    collected_rel_ids: Set[int] = set()
    collected_relationships: List[CulturalGraphRelationship] = []

    for depth_step in range(bounded_depth):
        if not current_frontier or len(visited_entity_ids) >= bounded_limit:
            break

        # Query all edges connecting to current frontier
        edge_conditions = [
            or_(
                CulturalGraphRelationship.source_entity_id.in_(current_frontier),
                CulturalGraphRelationship.target_entity_id.in_(current_frontier),
            )
        ]
        if relationship_types:
            edge_conditions.append(CulturalGraphRelationship.relationship_type.in_(relationship_types))
        if evidence_status:
            edge_conditions.append(CulturalGraphRelationship.evidence_status == evidence_status)

        stmt = select(CulturalGraphRelationship).where(*edge_conditions)
        edges = list(db.execute(stmt).scalars().all())

        next_frontier: Set[int] = set()

        for edge in edges:
            if edge.id in collected_rel_ids:
                continue

            # Determine the neighbor entity
            if edge.source_entity_id in current_frontier:
                neighbor_id = edge.target_entity_id
            else:
                neighbor_id = edge.source_entity_id

            # If neighbor not visited yet, check limit
            if neighbor_id not in visited_entity_ids:
                if len(visited_entity_ids) >= bounded_limit:
                    continue
                # Entity type filter check on neighbor
                neighbor_entity = get_entity_by_id(db, neighbor_id)
                if neighbor_entity is None:
                    continue
                if entity_types and neighbor_entity.entity_type not in entity_types:
                    continue

                visited_entity_ids.add(neighbor_id)
                next_frontier.add(neighbor_id)

            collected_rel_ids.add(edge.id)
            collected_relationships.append(edge)

        current_frontier = next_frontier

    # Fetch all collected entities
    nodes_stmt = select(CulturalGraphEntity).where(CulturalGraphEntity.id.in_(visited_entity_ids))
    nodes = list(db.execute(nodes_stmt).scalars().all())
    entity_map = {n.id: n for n in nodes}

    enriched_edges = [enrich_relationship_response(r, entity_map) for r in collected_relationships]
    nodes_response = [CulturalGraphEntityResponse.model_validate(n) for n in nodes]

    return CulturalGraphExploreResponse(
        center_entity_id=center_entity_id,
        center_entity=CulturalGraphEntityResponse.model_validate(center_entity),
        depth=bounded_depth,
        total_nodes=len(nodes_response),
        total_edges=len(enriched_edges),
        nodes=nodes_response,
        edges=enriched_edges,
    )


# =========================================================
# GRAPH STATISTICS
# =========================================================

def get_graph_statistics(db: Session) -> CulturalGraphStatisticsResponse:
    total_entities = db.scalar(select(func.count(CulturalGraphEntity.id))) or 0
    total_relationships = db.scalar(select(func.count(CulturalGraphRelationship.id))) or 0

    # Group entities by type
    ent_type_rows = db.execute(
        select(CulturalGraphEntity.entity_type, func.count(CulturalGraphEntity.id)).group_by(
            CulturalGraphEntity.entity_type
        )
    ).all()
    entities_by_type = {row[0]: row[1] for row in ent_type_rows}

    # Group relationships by type
    rel_type_rows = db.execute(
        select(CulturalGraphRelationship.relationship_type, func.count(CulturalGraphRelationship.id)).group_by(
            CulturalGraphRelationship.relationship_type
        )
    ).all()
    relationships_by_type = {row[0]: row[1] for row in rel_type_rows}

    # Group relationships by evidence status
    evidence_rows = db.execute(
        select(CulturalGraphRelationship.evidence_status, func.count(CulturalGraphRelationship.id)).group_by(
            CulturalGraphRelationship.evidence_status
        )
    ).all()
    relationships_by_evidence = {row[0]: row[1] for row in evidence_rows}

    return CulturalGraphStatisticsResponse(
        total_entities=total_entities,
        total_relationships=total_relationships,
        entities_by_type=entities_by_type,
        relationships_by_type=relationships_by_type,
        relationships_by_evidence=relationships_by_evidence,
    )


# =========================================================
# ENTITY PROVENANCE
# =========================================================

def get_entity_provenance(db: Session, entity_id: int) -> CulturalGraphProvenanceResponse:
    entity = get_entity_by_id(db, entity_id)
    if entity is None:
        raise ValueError(f"Entity with id {entity_id} not found.")

    # Query all relationships where entity is source or target
    stmt = select(CulturalGraphRelationship).where(
        or_(
            CulturalGraphRelationship.source_entity_id == entity_id,
            CulturalGraphRelationship.target_entity_id == entity_id,
        )
    )
    relationships = list(db.execute(stmt).scalars().all())

    # Collect connected entity IDs and primary source IDs
    connected_ids = set()
    source_ids = set()
    for rel in relationships:
        other_id = rel.target_entity_id if rel.source_entity_id == entity_id else rel.source_entity_id
        connected_ids.add(other_id)
        if rel.primary_source_id:
            source_ids.add(rel.primary_source_id)

    connected_map = {}
    if connected_ids:
        ents = db.execute(
            select(CulturalGraphEntity).where(CulturalGraphEntity.id.in_(connected_ids))
        ).scalars().all()
        connected_map = {e.id: e for e in ents}

    source_map = {}
    if source_ids:
        sources = db.execute(
            select(HeritageSource).where(HeritageSource.id.in_(source_ids))
        ).scalars().all()
        source_map = {s.id: s for s in sources}

    items: List[RelationshipProvenanceItem] = []
    for rel in relationships:
        other_id = rel.target_entity_id if rel.source_entity_id == entity_id else rel.source_entity_id
        connected_ent = connected_map.get(other_id)
        if not connected_ent:
            continue

        src_record = source_map.get(rel.primary_source_id) if rel.primary_source_id else None

        items.append(
            RelationshipProvenanceItem(
                relationship_id=rel.id,
                relationship_type=rel.relationship_type,
                connected_entity_id=connected_ent.id,
                connected_entity_name=connected_ent.canonical_name,
                connected_entity_type=connected_ent.entity_type,
                evidence_status=rel.evidence_status,
                confidence_score=rel.confidence_score,
                primary_source_id=rel.primary_source_id,
                source_title=src_record.title if src_record else None,
                source_citation=rel.source_citation or (src_record.citation if src_record else None),
                source_url=src_record.url if src_record else None,
            )
        )

    return CulturalGraphProvenanceResponse(
        entity_id=entity.id,
        entity_name=entity.canonical_name,
        entity_type=entity.entity_type,
        verification_status=entity.verification_status,
        heritage_site_id=entity.heritage_site_id,
        relationships_provenance=items,
    )
