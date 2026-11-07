from datetime import datetime, timezone
from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ImportBatch(Base):
    """
    Audit log and state tracking for batch data ingestion from official
    heritage sources (ASI, UNESCO, State Archaeology departments).
    Ensures idempotency, auditability, and provenance tracking.
    """
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    batch_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    source_organization: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    source_dataset: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    license: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True,
        # PENDING, IN_PROGRESS, COMPLETED, FAILED, PARTIAL
    )

    total_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    accepted_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    rejected_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    duplicate_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    updated_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    inserted_records: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_log: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
