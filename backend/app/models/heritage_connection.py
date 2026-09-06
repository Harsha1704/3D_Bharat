from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class HeritageConnection(Base):
    __tablename__ = "heritage_connections"

    __table_args__ = (
        UniqueConstraint(
            "source_site_id",
            "target_site_id",
            "relationship_type",
            name="uq_heritage_connection",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source_site_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "heritage_sites.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    target_site_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "heritage_sites.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence_score: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )