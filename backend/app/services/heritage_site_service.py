from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from sqlalchemy import select, func, or_, asc, desc
from app.models.heritage_site import HeritageSite

from app.schemas.heritage_site import (
    HeritageSiteCreate,
    HeritageSiteUpdate,
)

from app.services.heritage_recommendation_service import (
    get_semantic_recommendations,
)

# =========================================================
# CREATE
# =========================================================

def create_heritage_site(
    db: Session,
    site_data: HeritageSiteCreate,
) -> HeritageSite:

    data = site_data.model_dump()

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # Create PostGIS POINT(longitude latitude)
    if latitude is not None and longitude is not None:
        data["location"] = WKTElement(
            f"POINT({longitude} {latitude})",
            srid=4326,
        )

    site = HeritageSite(**data)

    db.add(site)
    db.commit()
    db.refresh(site)

    return site


# =========================================================
# GET ONE
# =========================================================

def get_heritage_site(
    db: Session,
    site_id: int,
) -> HeritageSite | None:

    stmt = select(HeritageSite).where(
        HeritageSite.id == site_id
    )

    return db.execute(
        stmt
    ).scalar_one_or_none()


# =========================================================
# GET ALL
# =========================================================

def get_heritage_sites(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[HeritageSite]:

    stmt = (
        select(HeritageSite)
        .order_by(HeritageSite.id)
        .offset(skip)
        .limit(limit)
    )

    return list(
        db.execute(stmt)
        .scalars()
        .all()
    )


# =========================================================
# ADVANCED SEARCH + PAGINATION
# =========================================================

def search_heritage_sites(
    db: Session,
    query: str | None = None,
    state: str | None = None,
    district: str | None = None,
    city: str | None = None,
    category: list[str] | None = None,
    period: str | None = None,
    tag: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    skip: int = 0,
    limit: int = 20,
) -> dict:

    filters = []

    # =====================================================
    # ADVANCED TEXT SEARCH
    # =====================================================

    if query:
        search_pattern = f"%{query}%"

        filters.append(
            or_(
                # Basic information
                HeritageSite.name.ilike(search_pattern),
                HeritageSite.description.ilike(search_pattern),
                HeritageSite.significance.ilike(search_pattern),
                HeritageSite.architecture.ilike(search_pattern),

                # Location
                HeritageSite.state.ilike(search_pattern),
                HeritageSite.district.ilike(search_pattern),
                HeritageSite.city.ilike(search_pattern),

                # Historical information
                HeritageSite.period.ilike(search_pattern),

                # Arrays
                func.array_to_string(
                    HeritageSite.tags,
                    " "
                ).ilike(search_pattern),

                func.array_to_string(
                    HeritageSite.historical_events,
                    " "
                ).ilike(search_pattern),

                func.array_to_string(
                    HeritageSite.associated_people,
                    " "
                ).ilike(search_pattern),

                func.array_to_string(
                    HeritageSite.traditions,
                    " "
                ).ilike(search_pattern),
            )
        )

    # =====================================================
    # STATE
    # =====================================================

    if state:
        filters.append(
            HeritageSite.state.ilike(
                f"%{state}%"
            )
        )

    # =====================================================
    # DISTRICT
    # =====================================================

    if district:
        filters.append(
            HeritageSite.district.ilike(
                f"%{district}%"
            )
        )

    # =====================================================
    # CITY
    # =====================================================

    if city:
        filters.append(
            HeritageSite.city.ilike(
                f"%{city}%"
            )
        )

    # =====================================================
    # MULTIPLE CATEGORIES
    # =====================================================

    if category:
        category_filters = [
            HeritageSite.category.ilike(
                f"%{item}%"
            )
            for item in category
        ]

        filters.append(
            or_(*category_filters)
        )

    # =====================================================
    # PERIOD
    # =====================================================

    if period:
        filters.append(
            HeritageSite.period.ilike(
                f"%{period}%"
            )
        )

    # =====================================================
    # TAG
    # =====================================================

    if tag:
        filters.append(
            func.lower(
                func.array_to_string(
                    HeritageSite.tags,
                    " "
                )
            ).like(
                f"%{tag.lower()}%"
            )
        )

    # =====================================================
    # TOTAL COUNT
    # =====================================================

    count_stmt = select(
        func.count(HeritageSite.id)
    )

    if filters:
        count_stmt = count_stmt.where(
            *filters
        )

    total = db.execute(
        count_stmt
    ).scalar_one()

    # =====================================================
    # SORTING
    # =====================================================

    sort_columns = {
        "id": HeritageSite.id,
        "name": HeritageSite.name,
        "state": HeritageSite.state,
        "city": HeritageSite.city,
        "category": HeritageSite.category,
        "period": HeritageSite.period,
    }

    sort_column = sort_columns.get(
        sort_by,
        HeritageSite.id,
    )

    if sort_order == "desc":
        order_expression = desc(sort_column)
    else:
        order_expression = asc(sort_column)

    # =====================================================
    # DATA QUERY
    # =====================================================

    stmt = (
        select(HeritageSite)
        .order_by(order_expression)
        .offset(skip)
        .limit(limit)
    )

    if filters:
        stmt = stmt.where(
            *filters
        )

    items = list(
        db.execute(stmt)
        .scalars()
        .all()
    )

    # =====================================================
    # PAGINATION
    # =====================================================

    has_next = (
        skip + len(items) < total
    )

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_next": has_next,
    }
# =========================================================
# UPDATE
# =========================================================

def update_heritage_site(
    db: Session,
    site_id: int,
    site_data: HeritageSiteUpdate,
) -> HeritageSite | None:

    site = get_heritage_site(
        db,
        site_id,
    )

    if site is None:
        return None

    update_data = site_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            site,
            field,
            value,
        )

    # -----------------------------------------------------
    # REBUILD POSTGIS LOCATION
    # -----------------------------------------------------

    latitude = update_data.get(
        "latitude",
        site.latitude,
    )

    longitude = update_data.get(
        "longitude",
        site.longitude,
    )

    if (
        latitude is not None
        and longitude is not None
    ):
        site.location = WKTElement(
            f"POINT({longitude} {latitude})",
            srid=4326,
        )

    db.commit()
    db.refresh(site)

    return site


# =========================================================
# DELETE
# =========================================================

def delete_heritage_site(
    db: Session,
    site_id: int,
) -> bool:

    site = get_heritage_site(
        db,
        site_id,
    )

    if site is None:
        return False

    db.delete(site)
    db.commit()

    return True


# =========================================================
# NEARBY HERITAGE SITES
# =========================================================

def get_nearby_heritage_sites(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 10,
):

    radius_m = radius_km * 1000

    # POINT(longitude latitude)
    search_point = WKTElement(
        f"POINT({longitude} {latitude})",
        srid=4326,
    )

    # Distance in meters
    distance_m = func.ST_Distance(
        HeritageSite.location,
        search_point,
    )

    stmt = (
        select(
            HeritageSite,
            (
                distance_m / 1000.0
            ).label("distance_km"),
        )
        .where(
            HeritageSite.location.is_not(None),
            func.ST_DWithin(
                HeritageSite.location,
                search_point,
                radius_m,
            ),
        )
        .order_by(distance_m)
    )

    results = db.execute(
        stmt
    ).all()

    nearby_sites = []

    for site, distance_km in results:

        nearby_sites.append(
            {
                "external_id": site.external_id,
                "name": site.name,
                "state": site.state,
                "district": site.district,
                "city": site.city,
                "category": site.category,
                "period": site.period,
                "description": site.description,
                "significance": site.significance,
                "architecture": site.architecture,
                "latitude": site.latitude,
                "longitude": site.longitude,
                "tags": site.tags,
                "historical_events": site.historical_events,
                "associated_people": site.associated_people,
                "traditions": site.traditions,
                "id": site.id,
                "created_at": site.created_at,
                "updated_at": site.updated_at,
                "distance_km": round(
                    float(distance_km),
                    3,
                ),
            }
        )

    return nearby_sites

# =========================================================
# HERITAGE INTELLIGENCE / RECOMMENDATIONS
# =========================================================
# =========================================================
# HYBRID HERITAGE INTELLIGENCE
# =========================================================

def get_heritage_recommendations(
    db: Session,
    site_id: int,
    limit: int = 5,
):

    # -----------------------------------------------------
    # SOURCE SITE
    # -----------------------------------------------------

    source_site = get_heritage_site(
        db,
        site_id,
    )

    if source_site is None:
        return None

    # -----------------------------------------------------
    # GET SEMANTIC RECOMMENDATIONS
    # -----------------------------------------------------

    semantic_results = get_semantic_recommendations(
        db=db,
        site_id=site_id,
        limit=50,
    )

    if semantic_results is None:
        return None

    semantic_map = {
        item["site"].id: item
        for item in semantic_results
    }

    # -----------------------------------------------------
    # GET ALL CANDIDATES
    # -----------------------------------------------------

    stmt = (
        select(HeritageSite)
        .where(
            HeritageSite.id != site_id
        )
    )

    candidates = list(
        db.execute(stmt)
        .scalars()
        .all()
    )

    # -----------------------------------------------------
    # NORMALIZE SOURCE ARRAYS
    # -----------------------------------------------------

    source_tags = {
        item.lower()
        for item in (source_site.tags or [])
    }

    source_traditions = {
        item.lower()
        for item in (source_site.traditions or [])
    }

    source_people = {
        item.lower()
        for item in (source_site.associated_people or [])
    }

    source_events = {
        item.lower()
        for item in (source_site.historical_events or [])
    }

    recommendations = []

    # =====================================================
    # SCORE CANDIDATES
    # =====================================================

    for candidate in candidates:

        structured_score = 0.0
        reasons = []

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        if (
            candidate.category
            and source_site.category
            and candidate.category.lower()
            == source_site.category.lower()
        ):
            structured_score += 30

            reasons.append(
                "Same heritage category"
            )

        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        if (
            candidate.state
            and source_site.state
            and candidate.state.lower()
            == source_site.state.lower()
        ):
            structured_score += 20

            reasons.append(
                "Same state"
            )

        # -------------------------------------------------
        # DISTRICT
        # -------------------------------------------------

        if (
            candidate.district
            and source_site.district
            and candidate.district.lower()
            == source_site.district.lower()
        ):
            structured_score += 15

            reasons.append(
                "Same district"
            )

        # -------------------------------------------------
        # CITY
        # -------------------------------------------------

        if (
            candidate.city
            and source_site.city
            and candidate.city.lower()
            == source_site.city.lower()
        ):
            structured_score += 15

            reasons.append(
                "Same city"
            )

        # -------------------------------------------------
        # PERIOD
        # -------------------------------------------------

        if (
            candidate.period
            and source_site.period
        ):

            source_period = (
                source_site.period.lower()
            )

            candidate_period = (
                candidate.period.lower()
            )

            if (
                source_period in candidate_period
                or candidate_period in source_period
            ):
                structured_score += 10

                reasons.append(
                    "Similar historical period"
                )

        # -------------------------------------------------
        # SHARED TAGS
        # -------------------------------------------------

        candidate_tags = {
            item.lower()
            for item in (candidate.tags or [])
        }

        shared_tags = (
            source_tags
            & candidate_tags
        )

        if shared_tags:

            score = min(
                len(shared_tags) * 5,
                20,
            )

            structured_score += score

            reasons.append(
                "Shared tags: "
                + ", ".join(
                    sorted(shared_tags)
                )
            )

        # -------------------------------------------------
        # SHARED TRADITIONS
        # -------------------------------------------------

        candidate_traditions = {
            item.lower()
            for item in (candidate.traditions or [])
        }

        shared_traditions = (
            source_traditions
            & candidate_traditions
        )

        if shared_traditions:

            score = min(
                len(shared_traditions) * 5,
                15,
            )

            structured_score += score

            reasons.append(
                "Shared traditions"
            )

        # -------------------------------------------------
        # SHARED PEOPLE
        # -------------------------------------------------

        candidate_people = {
            item.lower()
            for item in (candidate.associated_people or [])
        }

        shared_people = (
            source_people
            & candidate_people
        )

        if shared_people:

            score = min(
                len(shared_people) * 5,
                15,
            )

            structured_score += score

            reasons.append(
                "Shared historical figures"
            )

        # -------------------------------------------------
        # SHARED EVENTS
        # -------------------------------------------------

        candidate_events = {
            item.lower()
            for item in (candidate.historical_events or [])
        }

        shared_events = (
            source_events
            & candidate_events
        )

        if shared_events:

            score = min(
                len(shared_events) * 5,
                15,
            )

            structured_score += score

            reasons.append(
                "Shared historical events"
            )

        # =================================================
        # SEMANTIC SCORE
        # =================================================

        semantic_score = semantic_map.get(
            candidate.id,
            {},
        ).get(
            "semantic_score",
            0.0,
        )

        # =================================================
        # HYBRID SCORE
        # =================================================

        hybrid_score = (
            structured_score * 0.4
            + semantic_score * 0.6
        )

        # -------------------------------------------------
        # SEMANTIC REASON
        # -------------------------------------------------

        if semantic_score >= 70:

            reasons.append(
                "Strong semantic similarity"
            )

        elif semantic_score >= 50:

            reasons.append(
                "Moderate semantic similarity"
            )

        # -------------------------------------------------
        # INCLUDE
        # -------------------------------------------------

        if hybrid_score > 0:

            recommendations.append(
                {
                    "site": candidate,

                    "recommendation_score": round(
                        hybrid_score,
                        2,
                    ),

                    "recommendation_reasons": reasons,
                }
            )

    # =====================================================
    # SORT
    # =====================================================

    recommendations.sort(
        key=lambda item: (
            item["recommendation_score"],
            item["site"].name.lower(),
        ),
        reverse=True,
    )

    return recommendations[:limit]