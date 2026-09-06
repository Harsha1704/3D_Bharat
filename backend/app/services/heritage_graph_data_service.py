from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.models.heritage_connection import HeritageConnection


# =========================================================
# GENERATE FRONTEND-READY HERITAGE GRAPH
# =========================================================

def get_heritage_graph(
    db: Session,
) -> dict:

    # -----------------------------------------------------
    # GET ALL HERITAGE SITES
    # -----------------------------------------------------

    sites = list(
        db.execute(
            select(HeritageSite)
            .order_by(HeritageSite.id)
        )
        .scalars()
        .all()
    )

    # -----------------------------------------------------
    # GET ALL CONNECTIONS
    # -----------------------------------------------------

    connections = list(
        db.execute(
            select(HeritageConnection)
            .order_by(HeritageConnection.id)
        )
        .scalars()
        .all()
    )

    # -----------------------------------------------------
    # BUILD NODES
    # -----------------------------------------------------

    nodes = []

    for site in sites:

        nodes.append(
            {
                "id": site.id,
                "name": site.name,
                "state": site.state,
                "district": site.district,
                "city": site.city,
                "category": site.category,
                "period": site.period,
                "latitude": site.latitude,
                "longitude": site.longitude,
            }
        )

    # -----------------------------------------------------
    # BUILD EDGES
    # -----------------------------------------------------

    edges = []

    for connection in connections:

        edges.append(
            {
                "id": connection.id,
                "source": connection.source_site_id,
                "target": connection.target_site_id,
                "relationship_type": (
                    connection.relationship_type
                ),
                "description": connection.description,
                "confidence_score": (
                    connection.confidence_score
                ),
            }
        )

    # -----------------------------------------------------
    # RETURN GRAPH
    # -----------------------------------------------------

    return {
        "nodes": nodes,
        "edges": edges,
    }