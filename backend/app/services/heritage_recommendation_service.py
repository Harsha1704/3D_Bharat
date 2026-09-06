from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.heritage_site import HeritageSite


# =========================================================
# EMBEDDING MODEL
# =========================================================

_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# =========================================================
# WEIGHTS
# =========================================================

SEMANTIC_WEIGHT = 0.60
STRUCTURED_WEIGHT = 0.40


# =========================================================
# TEXT PROFILE
# =========================================================

def build_heritage_profile(
    site: HeritageSite,
) -> str:

    parts = [
        site.name,
        site.category,
        site.period,
        site.state,
        site.district,
        site.city,
        site.description,
        site.significance,
        site.architecture,
    ]

    if site.tags:
        parts.extend(site.tags)

    if site.historical_events:
        parts.extend(site.historical_events)

    if site.associated_people:
        parts.extend(site.associated_people)

    if site.traditions:
        parts.extend(site.traditions)

    return " ".join(
        str(part)
        for part in parts
        if part
    )


# =========================================================
# NORMALIZE ARRAY VALUES
# =========================================================

def normalize_values(
    values: list[str] | None,
) -> set[str]:

    return {
        value.strip().lower()
        for value in (values or [])
        if value and value.strip()
    }


# =========================================================
# STRUCTURED SIMILARITY
# =========================================================

def calculate_structured_similarity(
    source: HeritageSite,
    candidate: HeritageSite,
) -> tuple[float, list[str]]:

    score = 0.0
    reasons = []

    # -----------------------------------------------------
    # SAME CATEGORY
    # -----------------------------------------------------

    if (
        source.category
        and candidate.category
        and source.category.strip().lower()
        == candidate.category.strip().lower()
    ):
        score += 30

        reasons.append(
            "Same heritage category"
        )

    # -----------------------------------------------------
    # SAME STATE
    # -----------------------------------------------------

    if (
        source.state
        and candidate.state
        and source.state.strip().lower()
        == candidate.state.strip().lower()
    ):
        score += 20

        reasons.append(
            "Same state"
        )

    # -----------------------------------------------------
    # SAME DISTRICT
    # -----------------------------------------------------

    if (
        source.district
        and candidate.district
        and source.district.strip().lower()
        == candidate.district.strip().lower()
    ):
        score += 15

        reasons.append(
            "Same district"
        )

    # -----------------------------------------------------
    # SAME CITY
    # -----------------------------------------------------

    if (
        source.city
        and candidate.city
        and source.city.strip().lower()
        == candidate.city.strip().lower()
    ):
        score += 15

        reasons.append(
            "Same city"
        )

    # -----------------------------------------------------
    # SIMILAR HISTORICAL PERIOD
    # -----------------------------------------------------

    if (
        source.period
        and candidate.period
    ):

        source_period = (
            source.period.strip().lower()
        )

        candidate_period = (
            candidate.period.strip().lower()
        )

        if (
            source_period in candidate_period
            or candidate_period in source_period
        ):
            score += 10

            reasons.append(
                "Similar historical period"
            )

    # -----------------------------------------------------
    # SHARED TAGS
    # -----------------------------------------------------

    source_tags = normalize_values(
        source.tags
    )

    candidate_tags = normalize_values(
        candidate.tags
    )

    shared_tags = (
        source_tags & candidate_tags
    )

    if shared_tags:

        tag_score = min(
            len(shared_tags) * 5,
            20,
        )

        score += tag_score

        reasons.append(
            "Shared tags: "
            + ", ".join(
                sorted(shared_tags)
            )
        )

    # -----------------------------------------------------
    # SHARED TRADITIONS
    # -----------------------------------------------------

    source_traditions = normalize_values(
        source.traditions
    )

    candidate_traditions = normalize_values(
        candidate.traditions
    )

    shared_traditions = (
        source_traditions
        & candidate_traditions
    )

    if shared_traditions:

        tradition_score = min(
            len(shared_traditions) * 5,
            15,
        )

        score += tradition_score

        reasons.append(
            "Shared traditions: "
            + ", ".join(
                sorted(shared_traditions)
            )
        )

    # -----------------------------------------------------
    # SHARED HISTORICAL PEOPLE
    # -----------------------------------------------------

    source_people = normalize_values(
        source.associated_people
    )

    candidate_people = normalize_values(
        candidate.associated_people
    )

    shared_people = (
        source_people & candidate_people
    )

    if shared_people:

        people_score = min(
            len(shared_people) * 5,
            15,
        )

        score += people_score

        reasons.append(
            "Shared historical figures: "
            + ", ".join(
                sorted(shared_people)
            )
        )

    # -----------------------------------------------------
    # SHARED HISTORICAL EVENTS
    # -----------------------------------------------------

    source_events = normalize_values(
        source.historical_events
    )

    candidate_events = normalize_values(
        candidate.historical_events
    )

    shared_events = (
        source_events & candidate_events
    )

    if shared_events:

        event_score = min(
            len(shared_events) * 5,
            15,
        )

        score += event_score

        reasons.append(
            "Shared historical events"
        )

    return (
        min(score, 100.0),
        reasons,
    )


# =========================================================
# HYBRID HERITAGE RECOMMENDATIONS
# =========================================================

def get_semantic_recommendations(
    db: Session,
    site_id: int,
    limit: int = 5,
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

    # -----------------------------------------------------
    # SOURCE EMBEDDING
    # -----------------------------------------------------

    source_profile = build_heritage_profile(
        source_site
    )

    source_embedding = _model.encode(
        source_profile,
        normalize_embeddings=True,
    )

    # -----------------------------------------------------
    # CANDIDATE EMBEDDINGS
    # -----------------------------------------------------

    candidate_profiles = [
        build_heritage_profile(site)
        for site in candidates
    ]

    candidate_embeddings = _model.encode(
        candidate_profiles,
        normalize_embeddings=True,
    )

    # -----------------------------------------------------
    # COSINE SIMILARITY
    # -----------------------------------------------------

    similarities = (
        candidate_embeddings @ source_embedding
    )

    recommendations = []

    # -----------------------------------------------------
    # SCORE EACH CANDIDATE
    # -----------------------------------------------------

    for site, similarity in zip(
        candidates,
        similarities,
    ):

        # =================================================
        # SEMANTIC SCORE
        # =================================================

        semantic_score = (
            max(0.0, float(similarity))
            * 100
        )

        semantic_score = min(
            semantic_score,
            100.0,
        )

        # =================================================
        # STRUCTURED SCORE
        # =================================================

        structured_score, structured_reasons = (
            calculate_structured_similarity(
                source_site,
                site,
            )
        )

        # =================================================
        # HYBRID SCORE
        # =================================================

        recommendation_score = (
            structured_score
            * STRUCTURED_WEIGHT
            +
            semantic_score
            * SEMANTIC_WEIGHT
        )

        recommendation_score = min(
            recommendation_score,
            100.0,
        )

        # =================================================
        # EXPLAINABILITY
        # =================================================

        reasons = list(
            structured_reasons
        )

        # Semantic explanation threshold
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

        # =================================================
        # ONLY INCLUDE RELEVANT RESULTS
        # =================================================

        if recommendation_score > 0:

            recommendations.append(
                {
                    "site": site,

                    "structured_score": round(
                        structured_score,
                        2,
                    ),

                    "semantic_score": round(
                        semantic_score,
                        2,
                    ),

                    "recommendation_score": round(
                        recommendation_score,
                        2,
                    ),

                    "recommendation_reasons": reasons,
                }
            )

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    recommendations.sort(
        key=lambda item: (
            item["recommendation_score"],
            item["semantic_score"],
            item["site"].name.lower(),
        ),
        reverse=True,
    )

    # -----------------------------------------------------
    # TOP-K
    # -----------------------------------------------------

    return recommendations[:limit]