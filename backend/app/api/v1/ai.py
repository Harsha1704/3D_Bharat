from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_write_access
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AISearchRequest,
    AISearchResponse,
    AIStatusResponse,
    AIDocumentIngestRequest,
    AIDocumentIngestResponse,
)
from app.services.ai_document_service import ingest_document
from app.services.ai_service import (
    execute_ai_chat,
    execute_ai_search,
    get_ai_status,
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Heritage Intelligence"],
)


@router.post(
    "/chat",
    response_model=AIChatResponse,
    summary="Evidence-Grounded AI Heritage Chat",
)
def chat_with_heritage_ai(
    request: AIChatRequest,
    db: Session = Depends(get_db),
):
    """
    Ask natural-language heritage research questions and receive evidence-grounded answers
    supported by traceable citations from the verified national database, Cultural Knowledge Graph,
    and archival sources.
    """
    try:
        return execute_ai_chat(db=db, request=request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Heritage Assistant encountered an error: {str(exc)}",
        )


@router.post(
    "/search",
    response_model=AISearchResponse,
    summary="Hybrid Semantic & Keyword Search",
)
def search_heritage_ai_post(
    request: AISearchRequest,
    db: Session = Depends(get_db),
):
    """
    Perform hybrid vector semantic and keyword search across heritage records, archival sources,
    and knowledge graph entities.
    """
    try:
        return execute_ai_search(db=db, request=request)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search service error: {str(exc)}",
        )


@router.get(
    "/search",
    response_model=AISearchResponse,
    summary="Hybrid Search (GET)",
)
def search_heritage_ai_get(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Convenience GET endpoint for hybrid heritage search.
    """
    req = AISearchRequest(query=q, limit=limit)
    return execute_ai_search(db=db, request=req)


@router.get(
    "/status",
    response_model=AIStatusResponse,
    summary="AI Capability & Service Readiness Status",
)
def get_ai_service_status(
    db: Session = Depends(get_db),
):
    """
    Return safe status regarding LLM provider configuration, vector embedding readiness,
    and knowledge graph integration without exposing credentials.
    """
    return get_ai_status(db=db)


@router.post(
    "/documents/ingest",
    response_model=AIDocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_write_access)],
    summary="Ingest Approved Research Document for RAG",
)
def ingest_research_document(
    request: AIDocumentIngestRequest,
    db: Session = Depends(get_db),
):
    """
    Ingest, chunk, and embed an approved scholarly research document with full provenance tracking.
    Protected by preservation write authorization.
    """
    try:
        doc = ingest_document(db=db, request=request)
        return AIDocumentIngestResponse(
            id=doc.id,
            document_id=doc.document_id,
            title=doc.title,
            total_chunks=doc.total_chunks,
            content_hash=doc.content_hash,
            status="INGESTED",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(exc)}",
        )
