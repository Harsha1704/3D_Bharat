import math
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, asc, desc

from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.models.heritage_media import HeritageMedia
from app.models.heritage_3d_asset import Heritage3DAsset
from app.models.heritage_connection import HeritageConnection

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

    # Create POINT(longitude latitude)
    if latitude is not None and longitude is not None:
        data["location"] = f"POINT({longitude} {latitude})"

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
    architecture: str | None = None,
    dynasty: str | None = None,
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
                HeritageSite.external_id.ilike(search_pattern),
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
    # ARCHITECTURAL STYLE
    # =====================================================

    if architecture:
        filters.append(
            HeritageSite.architecture.ilike(
                f"%{architecture}%"
            )
        )

    # =====================================================
    # DYNASTY / ASSOCIATED PEOPLE
    # =====================================================

    if dynasty:
        filters.append(
            or_(
                func.lower(
                    func.array_to_string(
                        HeritageSite.associated_people,
                        " "
                    )
                ).like(f"%{dynasty.lower()}%"),
                HeritageSite.period.ilike(f"%{dynasty}%"),
                HeritageSite.description.ilike(f"%{dynasty}%"),
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
        "district": HeritageSite.district,
        "category": HeritageSite.category,
        "period": HeritageSite.period,
        "created_at": HeritageSite.created_at,
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
# BOUNDING-BOX SEARCH
# =========================================================

def get_heritage_sites_in_bbox(
    db: Session,
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    category: list[str] | None = None,
    state: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[HeritageSite]:
    """
    Search heritage sites falling within the specified bounding box coordinates.
    """
    filters = [
        HeritageSite.latitude.is_not(None),
        HeritageSite.longitude.is_not(None),
        HeritageSite.latitude >= min_lat,
        HeritageSite.latitude <= max_lat,
        HeritageSite.longitude >= min_lon,
        HeritageSite.longitude <= max_lon,
    ]

    if state:
        filters.append(HeritageSite.state.ilike(f"%{state}%"))

    if category:
        category_filters = [
            HeritageSite.category.ilike(f"%{c}%")
            for c in category
        ]
        filters.append(or_(*category_filters))

    stmt = (
        select(HeritageSite)
        .where(*filters)
        .order_by(HeritageSite.id)
        .offset(skip)
        .limit(limit)
    )

    return list(db.execute(stmt).scalars().all())


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
        site.location = f"POINT({longitude} {latitude})"

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

    lat_r = func.radians(latitude)
    lon_r = func.radians(longitude)
    site_lat_r = func.radians(HeritageSite.latitude)
    site_lon_r = func.radians(HeritageSite.longitude)

    cos_angle = (
        func.sin(lat_r) * func.sin(site_lat_r)
        + func.cos(lat_r) * func.cos(site_lat_r) * func.cos(site_lon_r - lon_r)
    )
    clamped_cos = func.least(1.0, func.greatest(-1.0, cos_angle))
    distance_km = 6371.0 * func.acos(clamped_cos)

    stmt = (
        select(
            HeritageSite,
            distance_km.label("distance_km"),
        )
        .where(
            HeritageSite.latitude.is_not(None),
            HeritageSite.longitude.is_not(None),
            distance_km <= radius_km,
        )
        .order_by(distance_km)
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
# COMPREHENSIVE SITE DETAILS
# =========================================================

def get_comprehensive_site_details(
    db: Session,
    site_id: int,
) -> dict | None:
    """
    Returns complete site details including sources, preservation media, 3D assets,
    and connections using eager single-session batch queries (0 N+1 issues).
    Never exposes raw storage filesystem paths.
    """
    site = get_heritage_site(db, site_id)
    if site is None:
        return None

    # Eager batch queries in the active session
    sources_stmt = select(HeritageSource).where(HeritageSource.heritage_site_id == site_id).order_by(HeritageSource.id)
    sources = list(db.execute(sources_stmt).scalars().all())

    media_stmt = select(HeritageMedia).where(HeritageMedia.heritage_site_id == site_id).order_by(HeritageMedia.id)
    media_items = list(db.execute(media_stmt).scalars().all())

    assets_stmt = select(Heritage3DAsset).where(Heritage3DAsset.heritage_site_id == site_id).order_by(Heritage3DAsset.id)
    asset_items = list(db.execute(assets_stmt).scalars().all())

    conn_stmt = select(HeritageConnection).where(
        or_(
            HeritageConnection.source_site_id == site_id,
            HeritageConnection.target_site_id == site_id,
        )
    ).order_by(HeritageConnection.id)
    connections = list(db.execute(conn_stmt).scalars().all())

    # Resolve connected site names in single query
    connected_site_ids = {
        c.target_site_id if c.source_site_id == site_id else c.source_site_id
        for c in connections
    }
    name_map = {}
    if connected_site_ids:
        names_query = select(HeritageSite.id, HeritageSite.name).where(HeritageSite.id.in_(connected_site_ids))
        name_map = {row[0]: row[1] for row in db.execute(names_query).all()}

    formatted_connections = []
    for c in connections:
        other_id = c.target_site_id if c.source_site_id == site_id else c.source_site_id
        direction = "outgoing" if c.source_site_id == site_id else "incoming"
        formatted_connections.append({
            "connection_id": c.id,
            "connected_site_id": other_id,
            "connected_site_name": name_map.get(other_id, f"Site #{other_id}"),
            "relationship_type": c.relationship_type,
            "confidence_score": c.confidence_score,
            "description": c.description,
            "direction": direction,
        })

    formatted_media = []
    for m in media_items:
        media_dict = {
            "id": m.id,
            "heritage_site_id": m.heritage_site_id,
            "title": m.title,
            "description": m.description,
            "media_type": m.media_type,
            "attribution": m.attribution,
            "license": m.license,
            "capture_date": m.capture_date,
            "verification_status": m.verification_status,
            "source_id": m.source_id,
            "storage_key": m.storage_key,
            "original_filename": m.original_filename,
            "mime_type": m.mime_type,
            "file_size_bytes": m.file_size_bytes,
            "checksum_sha256": m.checksum_sha256,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
            "file_url": f"/api/v1/heritage-media/{m.id}/file",
        }
        formatted_media.append(media_dict)

    formatted_assets = []
    for a in asset_items:
        asset_dict = {
            "id": a.id,
            "heritage_site_id": a.heritage_site_id,
            "title": a.title,
            "description": a.description,
            "asset_format": a.asset_format,
            "units": a.units,
            "coordinate_system": a.coordinate_system,
            "companion_files": a.companion_files,
            "bounding_box": a.bounding_box,
            "attribution": a.attribution,
            "license": a.license,
            "processing_status": a.processing_status,
            "verification_status": a.verification_status,
            "source_id": a.source_id,
            "storage_key": a.storage_key,
            "original_filename": a.original_filename,
            "mime_type": a.mime_type,
            "file_size_bytes": a.file_size_bytes,
            "checksum_sha256": a.checksum_sha256,
            "created_at": a.created_at,
            "updated_at": a.updated_at,
            "file_url": f"/api/v1/heritage-3d-assets/{a.id}/file",
        }
        formatted_assets.append(asset_dict)

    return {
        "id": site.id,
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
        "created_at": site.created_at,
        "updated_at": site.updated_at,
        "sources": sources,
        "media": formatted_media,
        "assets_3d": formatted_assets,
        "connections": formatted_connections,
        "stats": {
            "total_sources": len(sources),
            "total_media": len(formatted_media),
            "total_3d_assets": len(formatted_assets),
            "total_connections": len(formatted_connections),
        },
    }


# =========================================================
# RELATED HERITAGE DISCOVERY
# =========================================================

def _compute_haversine_distance(
    lat1: Optional[float],
    lon1: Optional[float],
    lat2: Optional[float],
    lon2: Optional[float],
) -> Optional[float]:
    if None in (lat1, lon1, lat2, lon2):
        return None
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def get_related_heritage_sites(
    db: Session,
    site_id: int,
    limit: int = 10,
) -> dict | None:
    """
    Discovers related heritage sites by clearly separating:
    1. Documented Connections (archival relationships in the database)
    2. Structured Relations (shared category, period, architecture, or proximity)
    3. Semantic Suggestions (AI recommendation engine with clear exploratory disclaimer)
    """
    site = get_heritage_site(db, site_id)
    if site is None:
        return None

    # 1. Documented Connections
    conn_stmt = select(HeritageConnection).where(
        or_(
            HeritageConnection.source_site_id == site_id,
            HeritageConnection.target_site_id == site_id,
        )
    ).order_by(HeritageConnection.id)
    connections = list(db.execute(conn_stmt).scalars().all())

    connected_peer_ids = {
        c.target_site_id if c.source_site_id == site_id else c.source_site_id
        for c in connections
    }
    name_map = {}
    if connected_peer_ids:
        names_query = select(HeritageSite.id, HeritageSite.name).where(HeritageSite.id.in_(connected_peer_ids))
        name_map = {row[0]: row[1] for row in db.execute(names_query).all()}

    documented = []
    for c in connections:
        peer_id = c.target_site_id if c.source_site_id == site_id else c.source_site_id
        documented.append({
            "connection_id": c.id,
            "connected_site_id": peer_id,
            "connected_site_name": name_map.get(peer_id, f"Site #{peer_id}"),
            "relationship_type": c.relationship_type,
            "confidence_score": c.confidence_score,
            "description": c.description,
            "source": "DOCUMENTED_ARCHIVAL_RECORD",
        })

    # 2. Structured Relations
    candidates = list(
        db.execute(select(HeritageSite).where(HeritageSite.id != site_id)).scalars().all()
    )

    structured_relations = []
    for cand in candidates:
        if cand.id in connected_peer_ids:
            continue

        shared = []
        if site.category and cand.category and site.category.strip().lower() == cand.category.strip().lower():
            shared.append(f"Shared category: {cand.category}")
        if site.period and cand.period and (site.period.lower() in cand.period.lower() or cand.period.lower() in site.period.lower()):
            shared.append(f"Shared period: {cand.period}")
        if site.architecture and cand.architecture and (site.architecture.lower() in cand.architecture.lower() or cand.architecture.lower() in site.architecture.lower()):
            shared.append(f"Shared architectural style: {cand.architecture}")
        if site.state and cand.state and site.state.strip().lower() == cand.state.strip().lower():
            shared.append(f"Same state: {cand.state}")

        dist = _compute_haversine_distance(site.latitude, site.longitude, cand.latitude, cand.longitude)
        if dist is not None and dist <= 150.0:
            shared.append(f"Proximity: {round(dist, 1)} km")

        if shared:
            structured_relations.append({
                "site_id": cand.id,
                "name": cand.name,
                "category": cand.category,
                "state": cand.state,
                "period": cand.period,
                "architecture": cand.architecture,
                "distance_km": round(dist, 1) if dist is not None else None,
                "shared_attributes": shared,
                "_score": len(shared) + (1.0 / (1.0 + (dist or 1000.0) / 100.0)),
            })

    structured_relations.sort(key=lambda x: x["_score"], reverse=True)
    for item in structured_relations:
        item.pop("_score", None)
    structured_relations = structured_relations[:limit]

    # 3. Semantic Suggestions
    semantic_raw = get_heritage_recommendations(db, site_id, limit=limit)
    semantic_suggestions = []
    if semantic_raw:
        for item in semantic_raw:
            s = item["site"]
            semantic_suggestions.append({
                "site_id": s.id,
                "name": s.name,
                "state": s.state,
                "category": s.category,
                "recommendation_score": item.get("recommendation_score", 0.0),
                "reasons": item.get("recommendation_reasons", []),
                "disclaimer": (
                    "AI-generated exploratory recommendation based on semantic similarity of "
                    "architectural descriptions and historical context. Not primary archival evidence."
                ),
            })

    return {
        "site_id": site.id,
        "site_name": site.name,
        "documented_connections": documented,
        "structured_relations": structured_relations,
        "semantic_suggestions": semantic_suggestions,
    }


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
