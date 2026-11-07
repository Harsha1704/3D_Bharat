from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.heritage_site import (
    HeritageSiteCreate,
    HeritageSiteResponse,
    HeritageSiteUpdate,
    HeritageSiteNearbyResponse,
    HeritageSiteSearchResponse,
    HeritageSiteRecommendationResponse,
    HeritageSiteDetailResponse,
    HeritageRelatedSitesResponse,
)

from app.services.heritage_site_service import (
    create_heritage_site,
    get_heritage_site,
    get_heritage_sites,
    update_heritage_site,
    delete_heritage_site,
    get_nearby_heritage_sites,
    search_heritage_sites,
    get_heritage_recommendations,
    get_heritage_sites_in_bbox,
    get_comprehensive_site_details,
    get_related_heritage_sites,
)


router = APIRouter(
    prefix="/heritage-sites",
    tags=["Heritage Sites & Discovery"],
)


# =========================================================
# CREATE
# POST /api/v1/heritage-sites
# =========================================================

@router.post(
    "",
    response_model=HeritageSiteResponse,
    status_code=201,
    summary="Register a new heritage site",
)
def create_site(
    site_data: HeritageSiteCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_heritage_site(
            db,
            site_data,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Heritage site with external_id '{site_data.external_id}' already exists.",
        )


# =========================================================
# LIST
# GET /api/v1/heritage-sites
# =========================================================

@router.get(
    "",
    response_model=List[HeritageSiteResponse],
    summary="List all heritage sites with basic pagination",
)
def list_sites(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    return get_heritage_sites(
        db,
        skip=skip,
        limit=limit,
    )


# =========================================================
# ADVANCED SEARCH
# GET /api/v1/heritage-sites/search
# =========================================================

@router.get(
    "/search",
    response_model=HeritageSiteSearchResponse,
    summary="Advanced multi-field heritage search with pagination and sorting",
)
def search_sites(
    query: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Search text across name, description, significance, architecture, and external ID",
    ),

    state: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter by Indian state or union territory",
    ),

    district: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter by administrative district",
    ),

    city: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter by city or town",
    ),

    category: list[str] | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter by heritage category (e.g. Temple, Fort, Monument)",
    ),

    period: str | None = Query(
        default=None,
        min_length=1,
        max_length=200,
        description="Filter by historical period or era",
    ),

    architecture: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter by architectural style (e.g. Dravidian, Nagara, Indo-Islamic)",
    ),

    dynasty: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter by associated dynasty or historical figures",
    ),

    tag: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter by keyword tag",
    ),

    sort_by: str = Query(
        default="id",
        pattern="^(id|name|state|city|district|category|period|created_at)$",
        description="Sort attribute",
    ),

    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort direction",
    ),

    skip: int = Query(
        default=0,
        ge=0,
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    db: Session = Depends(get_db),
):
    return search_heritage_sites(
        db=db,
        query=query,
        state=state,
        district=district,
        city=city,
        category=category,
        period=period,
        architecture=architecture,
        dynasty=dynasty,
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )


# =========================================================
# BOUNDING-BOX GEOGRAPHICAL DISCOVERY
# GET /api/v1/heritage-sites/bbox
# =========================================================

@router.get(
    "/bbox",
    response_model=List[HeritageSiteResponse],
    summary="Search heritage sites within a geographical bounding box viewport",
)
def search_sites_in_bbox(
    min_lat: float = Query(
        ...,
        ge=-90.0,
        le=90.0,
        description="Minimum latitude (southern bound)",
    ),
    min_lon: float = Query(
        ...,
        ge=-180.0,
        le=180.0,
        description="Minimum longitude (western bound)",
    ),
    max_lat: float = Query(
        ...,
        ge=-90.0,
        le=90.0,
        description="Maximum latitude (northern bound)",
    ),
    max_lon: float = Query(
        ...,
        ge=-180.0,
        le=180.0,
        description="Maximum longitude (eastern bound)",
    ),
    category: list[str] | None = Query(
        default=None,
        description="Optional category filters",
    ),
    state: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Optional state filter",
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
):
    if min_lat > max_lat:
        raise HTTPException(
            status_code=422,
            detail="Invalid bounding box coordinates: min_lat cannot be greater than max_lat.",
        )
    if min_lon > max_lon:
        raise HTTPException(
            status_code=422,
            detail="Invalid bounding box coordinates: min_lon cannot be greater than max_lon.",
        )

    return get_heritage_sites_in_bbox(
        db=db,
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
        category=category,
        state=state,
        skip=skip,
        limit=limit,
    )


# =========================================================
# NEARBY
# GET /api/v1/heritage-sites/nearby
# =========================================================

@router.get(
    "/nearby",
    response_model=List[HeritageSiteNearbyResponse],
    summary="Find heritage sites within a specified radius using Haversine calculation",
)
def nearby_sites(
    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Target latitude",
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Target longitude",
    ),

    radius_km: float = Query(
        default=10,
        gt=0,
        le=500,
        description="Search radius in kilometers (max 500 km)",
    ),

    db: Session = Depends(get_db),
):
    return get_nearby_heritage_sites(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )


# =========================================================
# HERITAGE RECOMMENDATIONS
# GET /api/v1/heritage-sites/{site_id}/recommendations
# =========================================================

@router.get(
    "/{site_id}/recommendations",
    response_model=List[HeritageSiteRecommendationResponse],
    summary="Hybrid heritage recommendation scores combining structured and semantic signals",
)
def heritage_recommendations(
    site_id: int,

    limit: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Number of recommendations to return",
    ),

    db: Session = Depends(get_db),
):
    recommendations = get_heritage_recommendations(
        db=db,
        site_id=site_id,
        limit=limit,
    )

    if recommendations is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    response = []

    for item in recommendations:
        site = item["site"]

        response.append(
            {
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
                "structured_score": item.get("structured_score", 0.0),
                "semantic_score": item.get("semantic_score", 0.0),
                "recommendation_score": item[
                    "recommendation_score"
                ],
                "recommendation_reasons": item[
                    "recommendation_reasons"
                ],
            }
        )

    return response


# =========================================================
# COMPREHENSIVE SITE DETAILS
# GET /api/v1/heritage-sites/{site_id}/details
# =========================================================

@router.get(
    "/{site_id}/details",
    response_model=HeritageSiteDetailResponse,
    summary="Get comprehensive heritage site details with eager loading (sources, media, 3D assets, connections)",
)
def get_site_details(
    site_id: int,
    db: Session = Depends(get_db),
):
    details = get_comprehensive_site_details(db, site_id)
    if details is None:
        raise HTTPException(
            status_code=404,
            detail=f"Heritage site with id {site_id} not found.",
        )
    return details


# =========================================================
# RELATED HERITAGE DISCOVERY
# GET /api/v1/heritage-sites/{site_id}/related
# =========================================================

@router.get(
    "/{site_id}/related",
    response_model=HeritageRelatedSitesResponse,
    summary="Discover related heritage sites distinguishing documented, structured, and semantic connections",
)
def get_related_sites(
    site_id: int,
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum results per relationship category",
    ),
    db: Session = Depends(get_db),
):
    related = get_related_heritage_sites(db, site_id, limit=limit)
    if related is None:
        raise HTTPException(
            status_code=404,
            detail=f"Heritage site with id {site_id} not found.",
        )
    return related


# =========================================================
# GET ONE
# GET /api/v1/heritage-sites/{site_id}
# =========================================================

@router.get(
    "/{site_id}",
    response_model=HeritageSiteResponse,
    summary="Retrieve a single heritage site by ID",
)
def get_site(
    site_id: int,
    db: Session = Depends(get_db),
):
    site = get_heritage_site(
        db,
        site_id,
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    return site


# =========================================================
# UPDATE
# PUT /api/v1/heritage-sites/{site_id}
# =========================================================

@router.put(
    "/{site_id}",
    response_model=HeritageSiteResponse,
    summary="Update heritage site details",
)
def update_site(
    site_id: int,
    site_data: HeritageSiteUpdate,
    db: Session = Depends(get_db),
):
    site = update_heritage_site(
        db,
        site_id,
        site_data,
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    return site


# =========================================================
# DELETE
# DELETE /api/v1/heritage-sites/{site_id}
# =========================================================

@router.delete(
    "/{site_id}",
    summary="Delete a heritage site by ID",
)
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
):
    deleted = delete_heritage_site(
        db,
        site_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    return {
        "message": "Heritage site deleted successfully"
    }
