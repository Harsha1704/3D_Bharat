from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HeritageSite(Base):
    __tablename__ = "heritage_sites"
    __table_args__ = (
        Index("ix_heritage_sites_lat_lon", "latitude", "longitude"),
        Index("ix_heritage_sites_state_category", "state", "category"),
        Index("ix_heritage_sites_district", "district"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    external_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    alternative_names: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    period: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    dynasty: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    construction_year: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    significance: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    architecture: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    historical_events: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    associated_people: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    traditions: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="OFFICIAL_SOURCE",
        nullable=False,
        index=True,
        # OFFICIAL_SOURCE, DOCUMENTED, COMMUNITY_SUBMITTED, UNVERIFIED, AI_DERIVED
    )

    batch_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    source_reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
