from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, List, Optional, Set
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.ai_document import AIDocument, AIDocumentChunk, AIChunkEmbedding
from app.models.cultural_graph import (
    CulturalGraphEntity,
    CulturalGraphRelationship,
    CulturalEvidenceStatus,
)
from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.services.ai_embedding_service import (
    cosine_similarity,
    generate_embedding,
    is_embedding_ready,
)

logger = logging.getLogger("3d_bharat.ai_retrieval")


@dataclass
class EvidenceItem:
    citation_id: str
    title: str
    content: str
    source_id: Optional[int] = None
    source_url: Optional[str] = None
    institution: Optional[str] = None
    publication_date: Optional[str] = None
    associated_site_id: Optional[int] = None
    associated_site_name: Optional[str] = None
    associated_graph_entity_id: Optional[int] = None
    associated_graph_entity_name: Optional[str] = None
    evidence_classification: str = "DOCUMENTED"
    score: float = 1.0


def extract_keywords(query: str) -> List[str]:
    cleaned = re.sub(r"[^\w\s]", " ", query.lower())
    words = [w for w in cleaned.split() if len(w) >= 3]
    stopwords = {
        "the", "was", "were", "are", "is", "been", "being", "and", "but", "for", "not", "with",
        "from", "about", "into", "over", "after", "before", "between", "under", "above", "below",
        "what", "which", "where", "when", "who", "whom", "whose", "why", "how", "that", "this",
        "these", "those", "there", "their", "have", "has", "had", "having", "does", "did", "doing",
        "associated", "built", "show", "give", "list", "tell", "explain", "describe",
        "dynasty", "dynasties", "architecture", "architectural", "style", "styles",
        "period", "history", "historical", "monument", "monuments", "site", "sites",
        "evidence", "records", "record", "details", "information", "association", "significance",
        "king", "queen", "emperor", "ruler", "fortress", "underground", "secret", "ancient", "medieval"
    }
    return [w for w in words if w not in stopwords]


def retrieve_heritage_sites_evidence(
    db: Session,
    query: str,
    selected_site_id: Optional[int] = None,
    limit: int = 4,
) -> List[EvidenceItem]:
    """
    Retrieve matching monuments from the verified heritage_sites database.
    """
    items: List[EvidenceItem] = []
    seen_site_ids: Set[int] = set()
    query_lower = query.lower()

    # 1. If explicit site selected, prioritize it
    if selected_site_id:
        site = db.execute(select(HeritageSite).where(HeritageSite.id == selected_site_id)).scalar_one_or_none()
        if site:
            seen_site_ids.add(site.id)
            desc_parts = [
                f"{site.name} is a {site.category or 'monument'} located in {site.district or site.city or ''}, {site.state or ''}.",
                f"Historical Period: {site.period or 'Documented Historical Era'}.",
            ]
            if site.description:
                desc_parts.append(site.description[:350])
            if site.architecture:
                desc_parts.append(f"Architecture: {site.architecture}.")

            items.append(
                EvidenceItem(
                    citation_id="",
                    title=f"{site.name} Baseline Record",
                    content=" ".join(desc_parts),
                    associated_site_id=site.id,
                    associated_site_name=site.name,
                    evidence_classification="DOCUMENTED",
                    institution="Archaeological Survey of India (ASI) / UNESCO",
                    score=2.0,
                )
            )

    # 2. Exact phrase / substring match against monument names
    all_sites = db.execute(select(HeritageSite)).scalars().all()
    for site in all_sites:
        if site.id in seen_site_ids:
            continue
        # Check if site name appears in query, or query appears in site name
        if site.name.lower() in query_lower or (len(query_lower) > 4 and query_lower in site.name.lower()):
            seen_site_ids.add(site.id)
            desc_parts = [
                f"{site.name} ({site.category or 'Monument'}) in {site.state or 'India'}.",
                f"Historical Period: {site.period or 'Documented'}.",
            ]
            if site.description:
                desc_parts.append(site.description[:350])
            if site.architecture:
                desc_parts.append(f"Architecture: {site.architecture}.")

            items.append(
                EvidenceItem(
                    citation_id="",
                    title=f"National Heritage Register: {site.name}",
                    content=" ".join(desc_parts),
                    associated_site_id=site.id,
                    associated_site_name=site.name,
                    evidence_classification="DOCUMENTED",
                    institution="Archaeological Survey of India (ASI)",
                    score=1.8,
                )
            )
            if len(items) >= limit:
                return items

    # 3. Fallback: Specific keywords match across name or state
    keywords = extract_keywords(query)
    if keywords and len(items) < limit:
        conditions = []
        for kw in keywords[:4]:
            pattern = f"%{kw}%"
            conditions.append(HeritageSite.name.ilike(pattern))
            conditions.append(HeritageSite.state.ilike(pattern))

        if conditions:
            query_stmt = select(HeritageSite).where(or_(*conditions)).limit(limit)
            matching_sites = db.execute(query_stmt).scalars().all()

            for site in matching_sites:
                if site.id in seen_site_ids:
                    continue
                seen_site_ids.add(site.id)

                snippet = (
                    f"{site.name} ({site.category or 'Heritage Site'}) in {site.state or 'India'}. "
                    f"Period: {site.period or 'Documented'}. {site.description[:250] if site.description else ''}"
                )
                items.append(
                    EvidenceItem(
                        citation_id="",
                        title=f"National Heritage Register: {site.name}",
                        content=snippet.strip(),
                        associated_site_id=site.id,
                        associated_site_name=site.name,
                        evidence_classification="DOCUMENTED",
                        institution="Archaeological Survey of India (ASI)",
                        score=1.1,
                    )
                )

    return items


def retrieve_knowledge_graph_evidence(
    db: Session,
    query: str,
    target_site_ids: List[int],
    limit: int = 6,
) -> List[EvidenceItem]:
    """
    Retrieve connected historical dynasties, builders, styles, and events from Phase 8 Cultural Knowledge Graph.
    """
    items: List[EvidenceItem] = []
    query_lower = query.lower()

    # 1. Fetch entities matching target sites
    entity_ids = []
    if target_site_ids:
        site_entities = db.execute(
            select(CulturalGraphEntity).where(CulturalGraphEntity.heritage_site_id.in_(target_site_ids))
        ).scalars().all()
        entity_ids.extend([e.id for e in site_entities])

    # 2. Check if query matches any entity canonical name or distinctive root
    all_entities = db.execute(select(CulturalGraphEntity)).scalars().all()
    generic_words = {"architecture", "style", "tradition", "traditions", "empire", "dynasty", "monument", "temple", "group", "caves"}
    for ent in all_entities:
        ent_lower = ent.canonical_name.lower()
        if ent_lower in query_lower:
            if ent.id not in entity_ids:
                entity_ids.append(ent.id)
        else:
            distinctive_tokens = [t for t in ent_lower.split() if len(t) >= 5 and t not in generic_words]
            if any(t in query_lower for t in distinctive_tokens):
                if ent.id not in entity_ids:
                    entity_ids.append(ent.id)

    if not entity_ids:
        return items

    ent_map = {e.id: e for e in all_entities}

    # 3. Query relationships involving these entities
    rel_stmt = (
        select(CulturalGraphRelationship)
        .where(
            or_(
                CulturalGraphRelationship.source_entity_id.in_(entity_ids),
                CulturalGraphRelationship.target_entity_id.in_(entity_ids),
            )
        )
        .limit(limit * 2)
    )
    relationships = db.execute(rel_stmt).scalars().all()

    for rel in relationships[:limit]:
        src = ent_map.get(rel.source_entity_id)
        tgt = ent_map.get(rel.target_entity_id)
        if not src or not tgt:
            continue

        rel_type_clean = rel.relationship_type.replace("_", " ")
        statement = (
            f"Cultural Knowledge Graph Record: {src.canonical_name} ({src.entity_type}) is {rel_type_clean} "
            f"connected to {tgt.canonical_name} ({tgt.entity_type}). Evidence: {rel.evidence_status}. "
            f"{rel.description or ''}"
        )
        if rel.source_citation:
            statement += f" Citation: {rel.source_citation}."

        score = 1.5 if rel.evidence_status in ["DOCUMENTED", "VERIFIED"] else 0.8

        items.append(
            EvidenceItem(
                citation_id="",
                title=f"Knowledge Graph: {src.canonical_name} — {rel_type_clean}",
                content=statement.strip(),
                source_id=rel.primary_source_id,
                associated_graph_entity_id=src.id,
                associated_graph_entity_name=src.canonical_name,
                evidence_classification=rel.evidence_status,
                institution="National Cultural Knowledge Graph",
                score=score,
            )
        )

    return items


def retrieve_archival_sources_evidence(
    db: Session,
    query: str,
    target_site_ids: List[int],
    limit: int = 4,
) -> List[EvidenceItem]:
    """
    Retrieve direct historical sources and citations from heritage_sources.
    """
    items: List[EvidenceItem] = []
    if not target_site_ids:
        return items

    stmt = select(HeritageSource).where(HeritageSource.heritage_site_id.in_(target_site_ids)).limit(limit)
    sources = db.execute(stmt).scalars().all()

    for s in sources:
        excerpt = s.citation or f"Documented archival record titled '{s.title}'"
        if s.notes:
            excerpt += f" Notes: {s.notes}"

        items.append(
            EvidenceItem(
                citation_id="",
                title=s.title,
                content=excerpt.strip(),
                source_id=s.id,
                source_url=s.url,
                institution=s.institution,
                publication_date=s.publication_date,
                associated_site_id=s.heritage_site_id,
                evidence_classification=s.verification_status,
                score=1.4,
            )
        )

    return items


def retrieve_semantic_chunks_evidence(
    db: Session,
    query: str,
    limit: int = 4,
) -> List[EvidenceItem]:
    """
    Semantic vector search across indexed AI research document chunks using cosine similarity.
    """
    items: List[EvidenceItem] = []
    if not is_embedding_ready():
        return items

    query_vec = generate_embedding(query)
    if not query_vec:
        return items

    stmt = (
        select(AIChunkEmbedding, AIDocumentChunk, AIDocument)
        .join(AIDocumentChunk, AIChunkEmbedding.chunk_id == AIDocumentChunk.id)
        .join(AIDocument, AIDocumentChunk.document_id == AIDocument.id)
    )
    results = db.execute(stmt).all()
    if not results:
        return items

    scored_chunks = []
    for emb_rec, chunk_rec, doc_rec in results:
        chunk_vec = emb_rec.embedding_json
        sim = cosine_similarity(query_vec, chunk_vec)
        if sim >= 0.40:  # Confident semantic similarity threshold
            scored_chunks.append((sim, chunk_rec, doc_rec))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    for sim, chunk_rec, doc_rec in scored_chunks[:limit]:
        items.append(
            EvidenceItem(
                citation_id="",
                title=f"{doc_rec.title} (Section: {chunk_rec.section_heading or 'Excerpt'})",
                content=chunk_rec.chunk_text,
                source_url=doc_rec.source_url,
                institution=doc_rec.publisher_institution,
                publication_date=doc_rec.publication_date,
                associated_site_id=doc_rec.heritage_site_id,
                evidence_classification="DOCUMENTED",
                score=float(sim),
            )
        )

    return items


def hybrid_retrieve_evidence(
    db: Session,
    query: str,
    selected_site_id: Optional[int] = None,
    max_results: int = 8,
) -> List[EvidenceItem]:
    """
    Hybrid multi-channel retrieval combining:
    1. Monument databases (HeritageSite)
    2. Phase 8 Cultural Knowledge Graph (Dynasty, Ruler, Style, Tradition)
    3. Archival Sources (HeritageSource)
    4. Semantic vector search (AIDocumentChunk)
    """
    all_evidence: List[EvidenceItem] = []

    # 1. Monument records
    site_evidence = retrieve_heritage_sites_evidence(db, query, selected_site_id)
    all_evidence.extend(site_evidence)

    target_site_ids = [e.associated_site_id for e in site_evidence if e.associated_site_id]
    if selected_site_id and selected_site_id not in target_site_ids:
        target_site_ids.append(selected_site_id)

    # 2. Knowledge Graph traversal
    graph_evidence = retrieve_knowledge_graph_evidence(db, query, target_site_ids)
    all_evidence.extend(graph_evidence)

    # 3. Archival Sources
    source_evidence = retrieve_archival_sources_evidence(db, query, target_site_ids)
    all_evidence.extend(source_evidence)

    # 4. Semantic Chunks
    chunk_evidence = retrieve_semantic_chunks_evidence(db, query)
    all_evidence.extend(chunk_evidence)

    if not all_evidence:
        return []

    # Deduplicate by content hash / snippet
    unique_items: List[EvidenceItem] = []
    seen_texts: Set[str] = set()

    # Sort by relevance score
    all_evidence.sort(key=lambda x: x.score, reverse=True)

    for item in all_evidence:
        content_key = item.content[:100].lower()
        if content_key in seen_texts:
            continue
        seen_texts.add(content_key)
        unique_items.append(item)
        if len(unique_items) >= max_results:
            break

    # Assign sequential citation IDs: [CITATION_1], [CITATION_2], ...
    for idx, item in enumerate(unique_items, start=1):
        item.citation_id = f"[CITATION_{idx}]"

    return unique_items
