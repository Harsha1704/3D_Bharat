from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# =========================================================
# CONTROLLED ENUMERATIONS
# =========================================================

class CulturalEntityType(str, Enum):
    HERITAGE_SITE = "HERITAGE_SITE"
    DYNASTY = "DYNASTY"
    HISTORICAL_PERSON = "HISTORICAL_PERSON"
    HISTORICAL_EVENT = "HISTORICAL_EVENT"
    ARCHITECTURAL_STYLE = "ARCHITECTURAL_STYLE"
    CULTURAL_TRADITION = "CULTURAL_TRADITION"


class CulturalRelationshipType(str, Enum):
    BUILT_BY = "BUILT_BY"
    PATRONIZED_BY = "PATRONIZED_BY"
    ASSOCIATED_WITH_DYNASTY = "ASSOCIATED_WITH_DYNASTY"
    ASSOCIATED_WITH_PERSON = "ASSOCIATED_WITH_PERSON"
    ASSOCIATED_WITH_EVENT = "ASSOCIATED_WITH_EVENT"
    HAS_ARCHITECTURAL_STYLE = "HAS_ARCHITECTURAL_STYLE"
    ASSOCIATED_WITH_TRADITION = "ASSOCIATED_WITH_TRADITION"
    CONTEMPORARY_WITH = "CONTEMPORARY_WITH"
    LOCATED_IN_REGION = "LOCATED_IN_REGION"
    RESTORED_BY = "RESTORED_BY"
    HISTORICALLY_CONNECTED_TO = "HISTORICALLY_CONNECTED_TO"


class CulturalEvidenceStatus(str, Enum):
    DOCUMENTED = "DOCUMENTED"
    VERIFIED = "VERIFIED"
    IMPORTED_UNVERIFIED = "IMPORTED_UNVERIFIED"
    EXPLORATORY = "EXPLORATORY"
    AI_SUGGESTED = "AI_SUGGESTED"


# =========================================================
# CULTURAL GRAPH ENTITY MODEL
# =========================================================

class CulturalGraphEntity(Base):
    __tablename__ = "cultural_graph_entities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    canonical_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    heritage_site_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("heritage_sites.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    alternative_names: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    geographical_context: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    period: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default=CulturalEvidenceStatus.VERIFIED.value,
        nullable=False,
        index=True,
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

    # Relationships
    heritage_site = relationship(
        "HeritageSite",
        foreign_keys=[heritage_site_id],
        lazy="joined",
    )


# =========================================================
# CULTURAL GRAPH RELATIONSHIP MODEL
# =========================================================

class CulturalGraphRelationship(Base):
    __tablename__ = "cultural_graph_relationships"

    __table_args__ = (
        CheckConstraint(
            "source_entity_id != target_entity_id",
            name="ck_no_self_relationship",
        ),
        UniqueConstraint(
            "source_entity_id",
            "target_entity_id",
            "relationship_type",
            name="uq_cultural_relationship",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    source_entity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cultural_graph_entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    target_entity_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cultural_graph_entities.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    directionality: Mapped[str] = mapped_column(
        String(20),
        default="DIRECTED",
        nullable=False,
    )

    evidence_status: Mapped[str] = mapped_column(
        String(50),
        default=CulturalEvidenceStatus.DOCUMENTED.value,
        nullable=False,
        index=True,
    )

    confidence_score: Mapped[Optional[float]] = mapped_column(
        nullable=True,
        default=1.0,
    )

    primary_source_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("heritage_sources.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source_citation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    historical_period: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    legacy_connection_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("heritage_connections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
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

    # ORM Navigation
    source_entity = relationship(
        "CulturalGraphEntity",
        foreign_keys=[source_entity_id],
        lazy="joined",
    )
    target_entity = relationship(
        "CulturalGraphEntity",
        foreign_keys=[target_entity_id],
        lazy="joined",
    )
    primary_source = relationship(
        "HeritageSource",
        foreign_keys=[primary_source_id],
        lazy="joined",
    )
