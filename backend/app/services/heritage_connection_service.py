from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.models.heritage_connection import HeritageConnection
from app.models.heritage_site import HeritageSite


# =========================================================
# CREATE HERITAGE CONNECTION
# =========================================================

def create_heritage_connection(
    db: Session,
    source_site_id: int,
    target_site_id: int,
    relationship_type: str,
    description: str | None = None,
    confidence_score: float | None = None,
) -> HeritageConnection | None:

    # -----------------------------------------------------
    # VALIDATE SOURCE SITE
    # -----------------------------------------------------

    source_site = db.execute(
        select(HeritageSite).where(
            HeritageSite.id == source_site_id
        )
    ).scalar_one_or_none()

    if source_site is None:
        return None

    # -----------------------------------------------------
    # VALIDATE TARGET SITE
    # -----------------------------------------------------

    target_site = db.execute(
        select(HeritageSite).where(
            HeritageSite.id == target_site_id
        )
    ).scalar_one_or_none()

    if target_site is None:
        return None

    # -----------------------------------------------------
    # PREVENT SELF CONNECTION
    # -----------------------------------------------------

    if source_site_id == target_site_id:
        raise ValueError(
            "A heritage site cannot connect to itself."
        )

    # -----------------------------------------------------
    # CHECK DUPLICATE CONNECTION
    # -----------------------------------------------------

    existing = db.execute(
        select(HeritageConnection).where(
            HeritageConnection.source_site_id
            == source_site_id,

            HeritageConnection.target_site_id
            == target_site_id,

            HeritageConnection.relationship_type
            == relationship_type,
        )
    ).scalar_one_or_none()

    if existing is not None:
        return existing

    # -----------------------------------------------------
    # CREATE CONNECTION
    # -----------------------------------------------------

    connection = HeritageConnection(
        source_site_id=source_site_id,
        target_site_id=target_site_id,
        relationship_type=relationship_type,
        description=description,
        confidence_score=confidence_score,
    )

    db.add(connection)
    db.commit()
    db.refresh(connection)

    return connection


# =========================================================
# GET CONNECTION BY ID
# =========================================================

def get_heritage_connection(
    db: Session,
    connection_id: int,
) -> HeritageConnection | None:

    stmt = select(
        HeritageConnection
    ).where(
        HeritageConnection.id == connection_id
    )

    return db.execute(
        stmt
    ).scalar_one_or_none()


# =========================================================
# GET CONNECTIONS FOR A SITE
# =========================================================

def get_heritage_connections(
    db: Session,
    site_id: int,
) -> list[HeritageConnection]:

    stmt = (
        select(HeritageConnection)
        .where(
            or_(
                HeritageConnection.source_site_id
                == site_id,

                HeritageConnection.target_site_id
                == site_id,
            )
        )
        .order_by(
            HeritageConnection.id
        )
    )

    return list(
        db.execute(stmt)
        .scalars()
        .all()
    )


# =========================================================
# GET OUTGOING CONNECTIONS
# =========================================================

def get_outgoing_connections(
    db: Session,
    site_id: int,
) -> list[HeritageConnection]:

    stmt = (
        select(HeritageConnection)
        .where(
            HeritageConnection.source_site_id
            == site_id
        )
        .order_by(
            HeritageConnection.id
        )
    )

    return list(
        db.execute(stmt)
        .scalars()
        .all()
    )


# =========================================================
# GET INCOMING CONNECTIONS
# =========================================================

def get_incoming_connections(
    db: Session,
    site_id: int,
) -> list[HeritageConnection]:

    stmt = (
        select(HeritageConnection)
        .where(
            HeritageConnection.target_site_id
            == site_id
        )
        .order_by(
            HeritageConnection.id
        )
    )

    return list(
        db.execute(stmt)
        .scalars()
        .all()
    )


# =========================================================
# DELETE CONNECTION
# =========================================================

def delete_heritage_connection(
    db: Session,
    connection_id: int,
) -> bool:

    connection = get_heritage_connection(
        db,
        connection_id,
    )

    if connection is None:
        return False

    db.delete(connection)
    db.commit()

    return True