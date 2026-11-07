from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AIDocument(Base):
    """
    Approved research documents, excavation reports, epigraphical records, and historical texts.
    Retains full source provenance and permission classification for RAG ingestion.
    """
    __tablename__ = "ai_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        # e.g. ARCHIVAL_RECORD, RESEARCH_REPORT, INSCRIPTION, HISTORICAL_TEXT
    )

    source_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    publisher_institution: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    author: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    publication_date: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    permission_classification: Mapped[str] = mapped_column(
        String(50),
        default="PUBLIC_HERITAGE_ARCHIVE",
        nullable=False,
    )

    source_identifier: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    rights_status: Mapped[str] = mapped_column(
        String(50),
        default="RIGHTS_REVIEW_REQUIRED",
        nullable=False,
        index=True,
    )

    rights_evidence_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    rights_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    content_origin: Mapped[str] = mapped_column(
        String(50),
        default="CURATED_SUMMARY",
        nullable=False,
        index=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="UNVERIFIED",
        nullable=False,
        index=True,
    )

    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    total_chunks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    heritage_site_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("heritage_sites.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    chunks: Mapped[List["AIDocumentChunk"]] = relationship(
        "AIDocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class AIDocumentChunk(Base):
    """
    Normalized textual chunks extracted from approved research documents.
    Preserves chunk position, section context, and source linkage.
    """
    __tablename__ = "ai_document_chunks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chunk_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    section_heading: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    document: Mapped["AIDocument"] = relationship(
        "AIDocument",
        back_populates="chunks",
    )

    embeddings: Mapped[List["AIChunkEmbedding"]] = relationship(
        "AIChunkEmbedding",
        back_populates="chunk",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_doc_chunk_index"),
    )


class AIChunkEmbedding(Base):
    """
    Model-version-aware vector representations of document chunks.
    Compatible across vector backends (PostgreSQL JSONB / array fallback or pgvector).
    """
    __tablename__ = "ai_chunk_embeddings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    chunk_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    embedding_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    dimensions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    embedding_json: Mapped[List[float]] = mapped_column(
        JSON,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    chunk: Mapped["AIDocumentChunk"] = relationship(
        "AIDocumentChunk",
        back_populates="embeddings",
    )

    __table_args__ = (
        UniqueConstraint("chunk_id", "embedding_model", name="uq_chunk_embedding_model"),
    )
