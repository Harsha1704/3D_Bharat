from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.models.heritage_connection import HeritageConnection

from app.services.heritage_recommendation_service import (
    build_heritage_profile,
    calculate_structured_similarity,
    _model,
    SEMANTIC_WEIGHT,
    STRUCTURED_WEIGHT,
)


# =========================================================
# GRAPH SETTINGS
# =========================================================

DEFAULT_MINIMUM_SCORE = 20.0


# =========================================================
# RELATIONSHIP TYPE
# =========================================================

def determine_relationship_type(
    source: HeritageSite,
    candidate: HeritageSite,
) -> str:

    # -----------------------------------------------------
    # SAME REGION + CATEGORY
    # -----------------------------------------------------

    if (
        source.state
        and candidate.state
        and source.state.strip().lower()
        == candidate.state.strip().lower()
    ):

        if (
            source.category
            and candidate.category
            and source.category.strip().lower()
            == candidate.category.strip().lower()
        ):
            return "SAME_REGION_AND_CATEGORY"

        return "SAME_REGION"

    # -----------------------------------------------------
    # SAME CATEGORY
    # -----------------------------------------------------

    if (
        source.category
        and candidate.category
        and source.category.strip().lower()
        == candidate.category.strip().lower()
    ):
        return "SAME_HERITAGE_CATEGORY"

    # -----------------------------------------------------
    # HISTORICAL PERIOD
    # -----------------------------------------------------

    if (
        source.period
        and candidate.period
    ):

        source_period = source.period.strip().lower()
        candidate_period = candidate.period.strip().lower()

        if (
            source_period in candidate_period
            or candidate_period in source_period
        ):
            return "SIMILAR_HISTORICAL_PERIOD"

    # -----------------------------------------------------
    # SHARED TAGS
    # -----------------------------------------------------

    source_tags = {
        x.strip().lower()
        for x in (source.tags or [])
        if x
    }

    candidate_tags = {
        x.strip().lower()
        for x in (candidate.tags or [])
        if x
    }

    if source_tags & candidate_tags:
        return "SHARED_HERITAGE_TAGS"

    # -----------------------------------------------------
    # SHARED TRADITIONS
    # -----------------------------------------------------

    source_traditions = {
        x.strip().lower()
        for x in (source.traditions or [])
        if x
    }

    candidate_traditions = {
        x.strip().lower()
        for x in (candidate.traditions or [])
        if x
    }

    if source_traditions & candidate_traditions:
        return "SHARED_TRADITIONS"

    # -----------------------------------------------------
    # SHARED PEOPLE
    # -----------------------------------------------------

    source_people = {
        x.strip().lower()
        for x in (source.associated_people or [])
        if x
    }

    candidate_people = {
        x.strip().lower()
        for x in (candidate.associated_people or [])
        if x
    }

    if source_people & candidate_people:
        return "SHARED_HISTORICAL_FIGURES"

    # -----------------------------------------------------
    # SHARED EVENTS
    # -----------------------------------------------------

    source_events = {
        x.strip().lower()
        for x in (source.historical_events or [])
        if x
    }

    candidate_events = {
        x.strip().lower()
        for x in (candidate.historical_events or [])
        if x
    }

    if source_events & candidate_events:
        return "SHARED_HISTORICAL_EVENTS"

    # -----------------------------------------------------
    # FALLBACK
    # -----------------------------------------------------

    return "SEMANTICALLY_RELATED"


# =========================================================
# HYBRID RELATIONSHIP SCORE
# =========================================================

def calculate_relationship_score(
    source: HeritageSite,
    candidate: HeritageSite,
) -> tuple[float, list[str]]:

    # -----------------------------------------------------
    # STRUCTURED SCORE
    # -----------------------------------------------------

    structured_score, structured_reasons = (
        calculate_structured_similarity(
            source,
            candidate,
        )
    )

    # -----------------------------------------------------
    # SEMANTIC PROFILES
    # -----------------------------------------------------

    source_profile = build_heritage_profile(
        source
    )

    candidate_profile = build_heritage_profile(
        candidate
    )

    # -----------------------------------------------------
    # EMBEDDINGS
    # -----------------------------------------------------

    source_embedding = _model.encode(
        source_profile,
        normalize_embeddings=True,
    )

    candidate_embedding = _model.encode(
        candidate_profile,
        normalize_embeddings=True,
    )

    # -----------------------------------------------------
    # COSINE SIMILARITY
    # -----------------------------------------------------

    similarity = (
        candidate_embedding @ source_embedding
    )

    semantic_score = (
        max(0.0, float(similarity))
        * 100
    )

    semantic_score = min(
        semantic_score,
        100.0,
    )

    # -----------------------------------------------------
    # HYBRID SCORE
    # -----------------------------------------------------

    final_score = (
        structured_score
        * STRUCTURED_WEIGHT
        +
        semantic_score
        * SEMANTIC_WEIGHT
    )

    final_score = min(
        final_score,
        100.0,
    )

    # -----------------------------------------------------
    # REASONS
    # -----------------------------------------------------

    reasons = list(
        structured_reasons
    )

    if semantic_score >= 60:

        reasons.append(
            "Strong semantic similarity"
        )

    elif semantic_score >= 40:

        reasons.append(
            "Moderate semantic similarity"
        )

    elif semantic_score >= 25:

        reasons.append(
            "Some semantic similarity"
        )

    # -----------------------------------------------------
    # ADD SCORE INFORMATION
    # -----------------------------------------------------

    reasons.append(
        f"Hybrid intelligence score: {round(final_score, 2)}"
    )

    return (
        round(final_score, 2),
        reasons,
    )


# =========================================================
# GENERATE CONNECTIONS FOR ONE SITE
# =========================================================

def generate_connections_for_site(
    db: Session,
    site_id: int,
    minimum_score: float = DEFAULT_MINIMUM_SCORE,
) -> list[dict] | None:

    # -----------------------------------------------------
    # SOURCE SITE
    # -----------------------------------------------------

    source_site = db.execute(
        select(HeritageSite).where(
            HeritageSite.id == site_id
        )
    ).scalar_one_or_none()

    if source_site is None:
        return None

    # -----------------------------------------------------
    # CANDIDATES
    # -----------------------------------------------------

    candidates = list(
        db.execute(
            select(HeritageSite).where(
                HeritageSite.id != site_id
            )
        )
        .scalars()
        .all()
    )

    if not candidates:
        return []

    generated = []

    # -----------------------------------------------------
    # PROCESS CANDIDATES
    # -----------------------------------------------------

    for candidate in candidates:

        score, reasons = calculate_relationship_score(
            source_site,
            candidate,
        )

        # -------------------------------------------------
        # FILTER WEAK RELATIONSHIPS
        # -------------------------------------------------

        if score < minimum_score:
            continue

        # -------------------------------------------------
        # RELATIONSHIP TYPE
        # -------------------------------------------------

        relationship_type = determine_relationship_type(
            source_site,
            candidate,
        )

        # -------------------------------------------------
        # CHECK EXISTING CONNECTION
        # -------------------------------------------------

        existing = db.execute(
            select(HeritageConnection).where(
                HeritageConnection.source_site_id
                == source_site.id,

                HeritageConnection.target_site_id
                == candidate.id,

                HeritageConnection.relationship_type
                == relationship_type,
            )
        ).scalar_one_or_none()

        # -------------------------------------------------
        # UPDATE EXISTING
        # -------------------------------------------------

        if existing is not None:

            existing.confidence_score = (
                score / 100.0
            )

            existing.description = (
                "Automatically generated relationship: "
                + "; ".join(reasons)
            )

            generated.append(
                {
                    "connection": existing,
                    "score": score,
                    "reasons": reasons,
                    "created": False,
                }
            )

            continue

        # -------------------------------------------------
        # CREATE NEW CONNECTION
        # -------------------------------------------------

        connection = HeritageConnection(
            source_site_id=source_site.id,
            target_site_id=candidate.id,
            relationship_type=relationship_type,
            description=(
                "Automatically generated relationship: "
                + "; ".join(reasons)
            ),
            confidence_score=score / 100.0,
        )

        db.add(connection)

        generated.append(
            {
                "connection": connection,
                "score": score,
                "reasons": reasons,
                "created": True,
            }
        )

    # -----------------------------------------------------
    # COMMIT
    # -----------------------------------------------------

    db.commit()

    # -----------------------------------------------------
    # REFRESH
    # -----------------------------------------------------

    for item in generated:

        db.refresh(
            item["connection"]
        )

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    generated.sort(
        key=lambda item: (
            item["score"],
            item["connection"].target_site_id,
        ),
        reverse=True,
    )

    return generated


# =========================================================
# GENERATE COMPLETE HERITAGE GRAPH
# =========================================================

def generate_heritage_graph(
    db: Session,
    minimum_score: float = DEFAULT_MINIMUM_SCORE,
) -> list[dict]:

    sites = list(
        db.execute(
            select(HeritageSite)
            .order_by(HeritageSite.id)
        )
        .scalars()
        .all()
    )

    results = []

    for site in sites:

        connections = generate_connections_for_site(
            db=db,
            site_id=site.id,
            minimum_score=minimum_score,
        )

        if connections:

            results.extend(
                connections
            )

    return results