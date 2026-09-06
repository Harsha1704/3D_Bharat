from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# BASE
# =========================================================

class HeritageConnectionBase(BaseModel):

    source_site_id: int = Field(
        ...,
        gt=0,
    )

    target_site_id: int = Field(
        ...,
        gt=0,
    )

    relationship_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    confidence_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


# =========================================================
# CREATE
# =========================================================

class HeritageConnectionCreate(
    HeritageConnectionBase
):
    pass


# =========================================================
# UPDATE
# =========================================================

class HeritageConnectionUpdate(BaseModel):

    relationship_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    confidence_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


# =========================================================
# RESPONSE
# =========================================================

class HeritageConnectionResponse(
    HeritageConnectionBase
):

    id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )