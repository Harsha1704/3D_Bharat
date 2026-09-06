from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.schemas.heritage_site import (
    HeritageSiteCreate,
    HeritageSiteResponse,
    HeritageSiteUpdate,
    HeritageSiteNearbyResponse,
    HeritageSiteSearchResponse,
    HeritageSiteRecommendationResponse,
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
)


router = APIRouter(
    prefix="/heritage-sites",
    tags=["Heritage Sites"],
)


# =========================================================
# DATABASE
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# CREATE
# POST /api/v1/heritage-sites
# =========================================================

@router.post(
    "",
    response_model=HeritageSiteResponse,
    status_code=201,
)
def create_site(
    site_data: HeritageSiteCreate,
    db: Session = Depends(get_db),
):
    return create_heritage_site(
        db,
        site_data,
    )


# =========================================================
# LIST
# GET /api/v1/heritage-sites
# =========================================================

@router.get(
    "",
    response_model=List[HeritageSiteResponse],
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
)
def search_sites(
    query: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),

    state: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),

    district: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),

    city: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),

    category: list[str] | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),

    period: str | None = Query(
        default=None,
        min_length=1,
        max_length=200,
    ),

    tag: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),

    sort_by: str = Query(
        default="id",
        pattern="^(id|name|state|city|category|period)$",
    ),

    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
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
        tag=tag,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )

# =========================================================
# NEARBY
# GET /api/v1/heritage-sites/nearby
# =========================================================

@router.get(
    "/nearby",
    response_model=List[
        HeritageSiteNearbyResponse
    ],
)
def nearby_sites(
    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
    ),

    radius_km: float = Query(
        default=10,
        gt=0,
        le=500,
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
    """
    Return intelligent heritage-site recommendations.
    """

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
# GET ONE
# GET /api/v1/heritage-sites/{site_id}
# =========================================================

@router.get(
    "/{site_id}",
    response_model=HeritageSiteResponse,
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