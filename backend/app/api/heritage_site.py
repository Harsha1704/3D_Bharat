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
    HeritageSiteResponse,
    HeritageSiteRecommendationResponse,
)

from app.services.heritage_site_service import (
    get_heritage_site,
    get_heritage_recommendations,
)


router = APIRouter(
    prefix="/heritage-sites",
    tags=["Heritage Intelligence"],
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
# HERITAGE RECOMMENDATIONS
# GET /api/v1/heritage-sites/{site_id}/recommendations
# =========================================================

@router.get(
    "/{site_id}/recommendations",
    response_model=List[
        HeritageSiteRecommendationResponse
    ],
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

    Recommendations are generated using:
    - Same category
    - Same state
    - Same district
    - Same city
    - Similar historical period
    - Shared tags
    - Shared traditions
    - Shared historical people
    - Shared historical events
    """

    recommendations = get_heritage_recommendations(
        db=db,
        site_id=site_id,
        limit=limit,
    )

    # -----------------------------------------------------
    # SOURCE SITE DOES NOT EXIST
    # -----------------------------------------------------

    if recommendations is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found.",
        )

    # -----------------------------------------------------
    # FORMAT RESPONSE
    # -----------------------------------------------------

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
# GET HERITAGE SITE
# GET /api/v1/heritage-sites/{site_id}
# =========================================================

@router.get(
    "/{site_id}",
    response_model=HeritageSiteResponse,
)
def heritage_details(
    site_id: int,
    db: Session = Depends(get_db),
):
    """
    Return detailed information about a heritage site.
    """

    site = get_heritage_site(
        db=db,
        site_id=site_id,
    )

    if site is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found.",
        )

    return site