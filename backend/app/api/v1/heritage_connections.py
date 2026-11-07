from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.heritage_connection import (
    HeritageConnectionCreate,
    HeritageConnectionResponse,
)

from app.services.heritage_connection_service import (
    create_heritage_connection,
    get_heritage_connection,
    get_heritage_connections,
    get_outgoing_connections,
    get_incoming_connections,
    delete_heritage_connection,
)


router = APIRouter(
    prefix="/heritage-connections",
    tags=["Heritage Connections"],
)




# =========================================================
# CREATE CONNECTION
# POST /api/v1/heritage-connections
# =========================================================

@router.post(
    "",
    response_model=HeritageConnectionResponse,
    status_code=201,
)
def create_connection(
    connection_data: HeritageConnectionCreate,
    db: Session = Depends(get_db),
):
    try:

        connection = create_heritage_connection(
            db=db,
            source_site_id=connection_data.source_site_id,
            target_site_id=connection_data.target_site_id,
            relationship_type=connection_data.relationship_type,
            description=connection_data.description,
            confidence_score=connection_data.confidence_score,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A connection between these sites with this relationship type already exists.",
        )

    if connection is None:

        raise HTTPException(
            status_code=404,
            detail="Source or target heritage site not found.",
        )

    return connection


# =========================================================
# GET ONE CONNECTION
# GET /api/v1/heritage-connections/{connection_id}
# =========================================================

@router.get(
    "/{connection_id}",
    response_model=HeritageConnectionResponse,
)
def get_connection(
    connection_id: int,
    db: Session = Depends(get_db),
):

    connection = get_heritage_connection(
        db=db,
        connection_id=connection_id,
    )

    if connection is None:

        raise HTTPException(
            status_code=404,
            detail="Heritage connection not found.",
        )

    return connection


# =========================================================
# GET ALL CONNECTIONS FOR A SITE
# GET /api/v1/heritage-connections/site/{site_id}
# =========================================================

@router.get(
    "/site/{site_id}",
    response_model=List[HeritageConnectionResponse],
)
def site_connections(
    site_id: int,
    db: Session = Depends(get_db),
):

    connections = get_heritage_connections(
        db=db,
        site_id=site_id,
    )

    return connections


# =========================================================
# OUTGOING CONNECTIONS
# GET /api/v1/heritage-connections/site/{site_id}/outgoing
# =========================================================

@router.get(
    "/site/{site_id}/outgoing",
    response_model=List[HeritageConnectionResponse],
)
def outgoing_connections(
    site_id: int,
    db: Session = Depends(get_db),
):

    return get_outgoing_connections(
        db=db,
        site_id=site_id,
    )


# =========================================================
# INCOMING CONNECTIONS
# GET /api/v1/heritage-connections/site/{site_id}/incoming
# =========================================================

@router.get(
    "/site/{site_id}/incoming",
    response_model=List[HeritageConnectionResponse],
)
def incoming_connections(
    site_id: int,
    db: Session = Depends(get_db),
):

    return get_incoming_connections(
        db=db,
        site_id=site_id,
    )


# =========================================================
# DELETE CONNECTION
# DELETE /api/v1/heritage-connections/{connection_id}
# =========================================================

@router.delete(
    "/{connection_id}",
)
def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db),
):

    deleted = delete_heritage_connection(
        db=db,
        connection_id=connection_id,
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Heritage connection not found.",
        )

    return {
        "message": "Heritage connection deleted successfully"
    }