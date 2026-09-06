from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.heritage_sites import (
    router as heritage_sites_router,
)

from app.api.v1.heritage_connections import (
    router as heritage_connections_router,
)

from app.api.v1.heritage_graph import (
    router as heritage_graph_router,
)


app = FastAPI(
    title="3D BHARAT API",
    description=(
        "AI-powered heritage intelligence and digital preservation "
        "platform for India's cultural heritage."
    ),
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HERITAGE SITES ROUTER
# =========================================================

app.include_router(
    heritage_sites_router,
    prefix="/api/v1",
)


# =========================================================
# HERITAGE CONNECTIONS ROUTER
# =========================================================

app.include_router(
    heritage_connections_router,
    prefix="/api/v1",
)


# =========================================================
# HERITAGE GRAPH ROUTER
# =========================================================

app.include_router(
    heritage_graph_router,
    prefix="/api/v1",
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
async def root():
    return {
        "project": "3D BHARAT",
        "message": "Heritage Intelligence Platform",
        "version": "0.1.0",
        "status": "running",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "3D BHARAT API",
    }
