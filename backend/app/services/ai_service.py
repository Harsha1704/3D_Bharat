import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.heritage_site import HeritageSite
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AISearchRequest,
    AISearchResult,
    AISearchResponse,
    AIStatusResponse,
)
from app.services.ai_citation_service import process_and_validate_citations
from app.services.ai_document_service import count_documents_and_chunks
from app.services.ai_embedding_service import is_embedding_ready
from app.services.ai_grounding_service import (
    SYSTEM_GROUNDING_PROMPT,
    build_grounded_prompt,
    detect_prompt_injection,
    verify_query_grounding,
)
from app.services.ai_provider_adapter import get_ai_provider
from app.services.ai_retrieval_service import hybrid_retrieve_evidence

logger = logging.getLogger("3d_bharat.ai_service")


def execute_ai_chat(
    db: Session,
    request: AIChatRequest,
) -> AIChatResponse:
    """
    Orchestrates the complete RAG execution:
    1. Hybrid evidence retrieval across DB, Knowledge Graph, Archival Sources, and Chunks
    2. Prompt construction with strict grounding instructions
    3. LLM generation via provider adapter
    4. Citation validation and post-processing
    """
    # 0. Prompt Injection & Security Guardrail
    is_adversarial, reason = detect_prompt_injection(request.message)
    if is_adversarial:
        provider = get_ai_provider()
        return AIChatResponse(
            answer=(
                "Request blocked by 3D BHARAT Security Guardrails: Adversarial command or prompt override pattern detected. "
                "The AI Heritage Intelligence system operates exclusively on historical queries grounded in verified evidence."
            ),
            citations=[],
            retrieved_evidence_summary="0 records retrieved (security guardrail triggered).",
            evidence_status="UNVERIFIED",
            limitations=[
                "Prompt injection attempt detected and neutralized.",
                "System instructions and data integrity protected.",
            ],
            conversation_id=request.conversation_id,
            provider_status=provider.get_provider_info(),
            research_mode=request.research_mode,
        )

    max_results = (
        settings.AI_RESEARCH_MODE_MAX_RESULTS
        if request.research_mode
        else settings.AI_MAX_RETRIEVAL_RESULTS
    )

    # Resolve focus monument name if ID provided
    selected_site_name = None
    if request.selected_site_id:
        site = db.query(HeritageSite).filter(HeritageSite.id == request.selected_site_id).first()
        if site:
            selected_site_name = site.name

    # 1. Hybrid Retrieval
    evidence_items = hybrid_retrieve_evidence(
        db=db,
        query=request.message,
        selected_site_id=request.selected_site_id,
        max_results=max_results,
    )

    provider = get_ai_provider()
    provider_info = provider.get_provider_info()

    # 2. Honest handling for insufficient evidence or ungrounded queries
    is_grounded, grounding_reason = verify_query_grounding(request.message, evidence_items) if evidence_items else (False, "No evidence retrieved.")

    if not evidence_items or not is_grounded:
        return AIChatResponse(
            answer=(
                "The 3D BHARAT national heritage database does not contain sufficient documented or verified records "
                "regarding your specific query. In strict accordance with our historical integrity protocol, the AI will "
                "not invent, extrapolate, or hallucinate undocumented dates, dynasties, or claims."
            ),
            citations=[],
            retrieved_evidence_summary=f"0 matching verified records ({grounding_reason}).",
            evidence_status="INSUFFICIENT_EVIDENCE",
            limitations=[
                "Database lacks verified primary sources for this topic.",
                "Hallucination prevention enforced.",
                grounding_reason,
            ],
            conversation_id=request.conversation_id,
            provider_status=provider_info,
            research_mode=request.research_mode,
        )

    # 3. Grounded Prompt Construction
    prompt = build_grounded_prompt(
        user_query=request.message,
        evidence_items=evidence_items,
        selected_site_name=selected_site_name,
        research_mode=request.research_mode,
    )

    # 4. Generate Answer via Provider Adapter
    raw_answer = provider.generate_answer(
        prompt=prompt,
        system_prompt=SYSTEM_GROUNDING_PROMPT,
        max_tokens=settings.AI_MAX_OUTPUT_TOKENS,
    )

    # 5. Citation Validation
    cleaned_answer, valid_citations = process_and_validate_citations(
        raw_answer=raw_answer,
        retrieved_evidence=evidence_items,
    )

    # Determine predominant evidence status
    evidence_status = "DOCUMENTED"
    if any(c.evidence_classification == "VERIFIED" for c in valid_citations):
        evidence_status = "VERIFIED"

    evidence_summary = (
        f"Retrieved {len(evidence_items)} evidence blocks from the National Heritage Register, "
        f"Cultural Knowledge Graph, and ASI/UNESCO records."
    )

    limitations = [
        "Factual claims are strictly constrained to verified repository evidence.",
        "Architectural similarity is not treated as definitive historical dynastic proof.",
    ]

    return AIChatResponse(
        answer=cleaned_answer,
        citations=valid_citations,
        retrieved_evidence_summary=evidence_summary,
        evidence_status=evidence_status,
        limitations=limitations,
        conversation_id=request.conversation_id,
        provider_status=provider_info,
        research_mode=request.research_mode,
    )


def execute_ai_search(
    db: Session,
    request: AISearchRequest,
) -> AISearchResponse:
    """
    Hybrid semantic and keyword search returning ranked evidence snippets.
    """
    evidence_items = hybrid_retrieve_evidence(
        db=db,
        query=request.query,
        max_results=request.limit,
    )

    results: List[AISearchResult] = []
    for item in evidence_items:
        res_type = "ARCHIVAL_SOURCE"
        if item.associated_site_id:
            res_type = "HERITAGE_SITE"
        elif item.associated_graph_entity_id:
            res_type = "KNOWLEDGE_GRAPH_ENTITY"

        results.append(
            AISearchResult(
                id=item.citation_id,
                title=item.title,
                result_type=res_type,
                snippet=item.content[:280],
                score=round(item.score, 3),
                evidence_classification=item.evidence_classification,
                source_url=item.source_url,
                metadata={
                    "institution": item.institution,
                    "publication_date": item.publication_date,
                    "site_id": item.associated_site_id,
                    "site_name": item.associated_site_name,
                    "graph_entity_id": item.associated_graph_entity_id,
                },
            )
        )

    return AISearchResponse(
        query=request.query,
        total_results=len(results),
        results=results,
    )


def get_ai_status(db: Session) -> AIStatusResponse:
    """
    Safe status response reporting capabilities without exposing keys or credentials.
    """
    provider = get_ai_provider()
    provider_info = provider.get_provider_info()
    total_docs, total_chunks = count_documents_and_chunks(db)

    return AIStatusResponse(
        service="3D BHARAT AI Heritage Intelligence",
        provider=provider_info.get("provider", "unknown"),
        model=provider_info.get("model", settings.AI_MODEL),
        provider_configured=provider_info.get("configured", False),
        embedding_service_ready=is_embedding_ready(),
        embedding_model=settings.AI_EMBEDDING_MODEL or "all-MiniLM-L6-v2",
        vector_backend=settings.AI_VECTOR_BACKEND or "postgres_jsonb",
        retrieval_service_ready=True,
        knowledge_graph_integrated=True,
        total_indexed_documents=total_docs,
        total_indexed_chunks=total_chunks,
    )
