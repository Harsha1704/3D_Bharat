from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.heritage_connection import (
    HeritageConnectionResponse,
)

from app.services.heritage_graph_service import (
    generate_connections_for_site,
    generate_heritage_graph,
)

from app.schemas.heritage_graph import (
    HeritageGraphResponse,
)

from app.services.heritage_graph_data_service import (
    get_heritage_graph,
)

router = APIRouter(
    prefix="/heritage-graph",
    tags=["Heritage Graph"],
)




# =========================================================
# GENERATE GRAPH FOR ONE SITE
#
# POST /api/v1/heritage-graph/generate/{site_id}
# =========================================================

@router.post(
    "/generate/{site_id}",
)
def generate_site_graph(
    site_id: int,
    minimum_score: float = Query(
        default=0.20,
        ge=0.0,
        le=1.0,
    ),
    db: Session = Depends(get_db),
):
    results = generate_connections_for_site(
        db=db,
        site_id=site_id,
        minimum_score=minimum_score,
    )

    if results is None:
        raise HTTPException(
            status_code=404,
            detail="Heritage site not found",
        )

    return {
        "site_id": site_id,
        "minimum_score": minimum_score,
        "connections_generated": len(results),
        "connections": [
            {
                "id": item["connection"].id,
                "source_site_id": (
                    item["connection"].source_site_id
                ),
                "target_site_id": (
                    item["connection"].target_site_id
                ),
                "relationship_type": (
                    item["connection"].relationship_type
                ),
                "description": (
                    item["connection"].description
                ),
                "confidence_score": (
                    item["connection"].confidence_score
                ),
                "score": round(
                    item["score"],
                    4,
                ),
                "reasons": item["reasons"],
                "created": item["created"],
            }
            for item in results
        ],
    }


# =========================================================
# GENERATE COMPLETE HERITAGE GRAPH
#
# POST /api/v1/heritage-graph/generate
# =========================================================

@router.post(
    "/generate",
)
def generate_complete_graph(
    minimum_score: float = Query(
        default=0.20,
        ge=0.0,
        le=1.0,
    ),
    db: Session = Depends(get_db),
):
    results = generate_heritage_graph(
        db=db,
        minimum_score=minimum_score,
    )

    return {
        "minimum_score": minimum_score,
        "connections_generated": len(results),
        "connections": [
            {
                "id": item["connection"].id,
                "source_site_id": (
                    item["connection"].source_site_id
                ),
                "target_site_id": (
                    item["connection"].target_site_id
                ),
                "relationship_type": (
                    item["connection"].relationship_type
                ),
                "description": (
                    item["connection"].description
                ),
                "confidence_score": (
                    item["connection"].confidence_score
                ),
                "score": round(
                    item["score"],
                    4,
                ),
                "reasons": item["reasons"],
                "created": item["created"],
            }
            for item in results
        ],
    }


# =========================================================
# GRAPH CONNECTIONS FOR ONE SITE
#
# GET /api/v1/heritage-graph/site/{site_id}
# =========================================================

@router.get(
    "/site/{site_id}",
    response_model=List[HeritageConnectionResponse],
)
def get_site_graph(
    site_id: int,
    db: Session = Depends(get_db),
):
    from app.services.heritage_connection_service import (
        get_heritage_connections,
    )

    connections = get_heritage_connections(
        db=db,
        site_id=site_id,
    )

    return connections


# =========================================================
# GET COMPLETE FRONTEND-READY GRAPH
#
# GET /api/v1/heritage-graph
# =========================================================

@router.get(
    "",
    response_model=HeritageGraphResponse,
)
def get_complete_graph(
    db: Session = Depends(get_db),
):
    return get_heritage_graph(
        db=db,
    )