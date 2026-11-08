from datetime import datetime, timezone
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Heritage3DAsset(Base):
    """
    Metadata for 3D digital preservation models, point clouds, Gaussian Splats,
    and architectural reconstructions.
    """
    __tablename__ = "heritage_3d_assets"

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

    asset_format: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        # GLB, GLTF, OBJ, PLY, GAUSSIAN_SPLAT
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

    units: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="meters",
    )

    coordinate_system: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    companion_files: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    bounding_box: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    attribution: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    license: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(50),
        default="READY",
        nullable=False,
        index=True,
        # PENDING, PROCESSING, READY, FAILED
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="UNVERIFIED",
        nullable=False,
        index=True,
        # VERIFIED, UNVERIFIED, COMMUNITY_SUBMITTED
    )

    # -------------------------------------------------------------
    # Phase 10: Provenance, Rigor & Viewer Pipeline Fields
    # -------------------------------------------------------------
    asset_origin: Mapped[str] = mapped_column(
        String(50),
        default="HISTORICAL_RECONSTRUCTION",
        nullable=False,
        index=True,
        # PHOTOGRAMMETRY_SCAN, LASER_SCAN, INSTITUTIONAL_3D_MODEL,
        # HISTORICAL_RECONSTRUCTION, ARTIST_INTERPRETATION, ARCHITECTURAL_VISUALIZATION
    )

    original_format: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    processed_format: Mapped[str] = mapped_column(
        String(50),
        default="GLB",
        nullable=False,
    )

    preview_image_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    source_identifier: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    creator: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    publisher: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    licence_name: Mapped[str] = mapped_column(
        String(255),
        default="CC-BY-4.0",
        nullable=False,
    )

    licence_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    rights_status: Mapped[str] = mapped_column(
        String(50),
        default="CREATIVE_COMMONS",
        nullable=False,
        index=True,
        # PUBLIC_DOMAIN, CREATIVE_COMMONS, RESTRICTED_RESEARCH_ONLY, COPYRIGHT_RESERVED
    )

    attribution_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    commercial_use_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    modification_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    redistribution_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    poly_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    vertex_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    texture_resolution: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    lod_levels: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    coordinate_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    validation_status: Mapped[str] = mapped_column(
        String(50),
        default="READY",
        nullable=False,
        index=True,
        # PENDING_REVIEW, VALIDATING, PROCESSING, READY, REJECTED, FAILED, ARCHIVED
    )

    validation_report: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    visibility_status: Mapped[str] = mapped_column(
        String(50),
        default="PUBLIC",
        nullable=False,
        index=True,
        # PUBLIC, UNLISTED, ARCHIVED
    )

    is_pilot: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
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
