from datetime import datetime, timezone
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HeritageSource(Base):
    """
    Historical sources, academic citations, archival records, and provenance metadata.
    Preserves strict demarcation between verified historical facts, community submissions,
    and AI-derived suggestions.
    """
    __tablename__ = "heritage_sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    heritage_site_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("heritage_sites.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        # e.g. ACADEMIC_JOURNAL, ARCHAEOLOGICAL_SURVEY, ARCHIVAL_RECORD, INSCRIPTION, ORAL_TRADITION, AI_DERIVED
    )

    author: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    institution: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    publication_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    citation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    license: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="UNVERIFIED",
        nullable=False,
        index=True,
        # VERIFIED, UNVERIFIED, COMMUNITY_SUBMITTED, AI_DERIVED
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )
