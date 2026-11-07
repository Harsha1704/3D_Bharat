from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
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


class HeritageMedia(Base):
    """
    Metadata for archival photographs, historical documents, audio guides,
    and preservation media linked to heritage sites.
    """
    __tablename__ = "heritage_media"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    heritage_site_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("heritage_sites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    source_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("heritage_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    media_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        # ARCHIVAL_PHOTOGRAPH, HISTORICAL_DOCUMENT, AUDIO_GUIDE, DOCUMENTARY_VIDEO, ARCHITECTURAL_DRAWING
    )

    storage_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    checksum_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    attribution: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    license: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    capture_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="UNVERIFIED",
        nullable=False,
        index=True,
        # VERIFIED, UNVERIFIED, COMMUNITY_SUBMITTED
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
