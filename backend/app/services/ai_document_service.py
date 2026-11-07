import hashlib
import logging
import re
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_document import AIDocument, AIDocumentChunk, AIChunkEmbedding
from app.models.heritage_site import HeritageSite
from app.schemas.ai import AIDocumentIngestRequest, AIDocumentIngestResponse
from app.services.ai_embedding_service import (
    compute_sha256,
    generate_batch_embeddings,
    is_embedding_ready,
)

logger = logging.getLogger("3d_bharat.ai_document")


def chunk_text(
    text: str,
    target_chunk_size: int = 400,
    min_chunk_size: int = 50,
) -> List[str]:
    """
    Sentence and paragraph-aware text chunker.
    Preserves semantic boundaries without arbitrary slicing.
    """
    clean_text = text.replace("\r\n", "\n").strip()
    if not clean_text:
        return []

    # First split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", clean_text) if p.strip()]
    chunks: List[str] = []

    for para in paragraphs:
        if len(para) <= target_chunk_size:
            chunks.append(para)
        else:
            # Split paragraph by sentences
            sentences = re.split(r"(?<=[.!?])\s+", para)
            current_chunk = []
            current_len = 0

            for sent in sentences:
                sent_len = len(sent)
                if current_len + sent_len > target_chunk_size and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sent]
                    current_len = sent_len
                else:
                    current_chunk.append(sent)
                    current_len += sent_len + 1

            if current_chunk:
                chunks.append(" ".join(current_chunk))

    # Filter out tiny fragments
    return [c for c in chunks if len(c) >= min_chunk_size]


def ingest_document(
    db: Session,
    request: AIDocumentIngestRequest,
) -> AIDocument:
    """
    Idempotent document ingestion with content hashing, chunking, and vector embedding.
    """
    content_hash = compute_sha256(request.text_content)

    # 1. Idempotency Check: if identical content hash exists, return existing document
    existing_doc = db.execute(
        select(AIDocument).where(AIDocument.content_hash == content_hash)
    ).scalar_one_or_none()
    if existing_doc:
        logger.info("Document with content hash %s already ingested as %s", content_hash, existing_doc.document_id)
        return existing_doc

    # Check document_id uniqueness
    doc_by_id = db.execute(
        select(AIDocument).where(AIDocument.document_id == request.document_id)
    ).scalar_one_or_none()
    if doc_by_id:
        raise ValueError(f"Document with ID '{request.document_id}' already exists.")

    # Validate site if linked
    if request.heritage_site_id:
        site = db.execute(
            select(HeritageSite).where(HeritageSite.id == request.heritage_site_id)
        ).scalar_one_or_none()
        if not site:
            raise ValueError(f"HeritageSite with id {request.heritage_site_id} does not exist.")

    # 2. Create Document record
    doc = AIDocument(
        document_id=request.document_id,
        title=request.title,
        document_type=request.document_type,
        source_url=request.source_url,
        publisher_institution=request.publisher_institution,
        author=request.author,
        publication_date=request.publication_date,
        content_hash=content_hash,
        permission_classification=request.permission_classification,
        heritage_site_id=request.heritage_site_id,
    )
    db.add(doc)
    db.flush()

    # 3. Chunk text
    raw_chunks = chunk_text(request.text_content)
    if not raw_chunks:
        raw_chunks = [request.text_content.strip()]

    doc.total_chunks = len(raw_chunks)

    # 4. Generate embeddings in batch if embedding model is ready
    chunk_embeddings = generate_batch_embeddings(raw_chunks)
    embedding_model_name = settings.AI_EMBEDDING_MODEL or "all-MiniLM-L6-v2"

    for idx, chunk_str in enumerate(raw_chunks):
        c_hash = compute_sha256(chunk_str)
        token_estimate = int(len(chunk_str.split()) * 1.3)

        chunk_record = AIDocumentChunk(
            document_id=doc.id,
            chunk_index=idx,
            chunk_text=chunk_str,
            chunk_hash=c_hash,
            token_count=token_estimate,
        )
        db.add(chunk_record)
        db.flush()

        emb_vector = chunk_embeddings[idx] if idx < len(chunk_embeddings) else None
        if emb_vector is not None:
            emb_record = AIChunkEmbedding(
                chunk_id=chunk_record.id,
                embedding_model=embedding_model_name,
                dimensions=len(emb_vector),
                embedding_json=emb_vector,
                content_hash=c_hash,
            )
            db.add(emb_record)

    db.commit()
    db.refresh(doc)
    return doc


def get_document_by_id(db: Session, doc_id: int) -> Optional[AIDocument]:
    return db.execute(select(AIDocument).where(AIDocument.id == doc_id)).scalar_one_or_none()


def count_documents_and_chunks(db: Session) -> tuple[int, int]:
    from sqlalchemy import func
    total_docs = db.scalar(select(func.count(AIDocument.id))) or 0
    total_chunks = db.scalar(select(func.count(AIDocumentChunk.id))) or 0
    return total_docs, total_chunks
