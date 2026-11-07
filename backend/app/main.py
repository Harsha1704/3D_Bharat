import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import check_database_connection
from app.api.v1.heritage_sites import (
    router as heritage_sites_router,
)
from app.api.v1.heritage_connections import (
    router as heritage_connections_router,
)
from app.api.v1.heritage_graph import (
    router as heritage_graph_router,
)
from app.api.v1.heritage_sources import (
    router as heritage_sources_router,
)
from app.api.v1.heritage_media import (
    router as heritage_media_router,
)
from app.api.v1.heritage_3d_assets import (
    router as heritage_3d_assets_router,
)
from app.api.v1.heritage_ingestion import (
    router as heritage_ingestion_router,
)

logger = logging.getLogger("3d_bharat")

app = FastAPI(
    title="3D BHARAT API",
    description=(
        "AI-powered heritage intelligence and digital preservation "
        "platform for India's cultural heritage."
    ),
    version=settings.PROJECT_VERSION,
)


# =========================================================
# CORS SECURITY
# Configurable origin whitelist without wildcards
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# =========================================================
# GLOBAL EXCEPTION HANDLER
# Protect internal details, SQL errors, and credentials
# =========================================================

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled error processing {request.method} {request.url.path}: {exc}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# =========================================================
# API V1 ROUTERS
# =========================================================

app.include_router(
    heritage_sites_router,
    prefix="/api/v1",
)

app.include_router(
    heritage_connections_router,
    prefix="/api/v1",
)

app.include_router(
    heritage_graph_router,
    prefix="/api/v1",
)

app.include_router(
    heritage_sources_router,
    prefix="/api/v1",
)

app.include_router(
    heritage_media_router,
    prefix="/api/v1",
)

app.include_router(
    heritage_3d_assets_router,
    prefix="/api/v1",
)

app.include_router(
    heritage_ingestion_router,
    prefix="/api/v1",
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "message": "Heritage Intelligence Platform",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():
    is_connected = check_database_connection()

    if not is_connected:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
            },
        )

    return {
        "status": "healthy",
        "service": "3D BHARAT API",
        "database": "connected",
    }
