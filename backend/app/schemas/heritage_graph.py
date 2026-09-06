from pydantic import BaseModel, ConfigDict


# =========================================================
# GRAPH NODE
# =========================================================

class HeritageGraphNode(BaseModel):
    id: int
    name: str
    state: str | None = None
    district: str | None = None
    city: str | None = None
    category: str | None = None
    period: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# GRAPH EDGE
# =========================================================

class HeritageGraphEdge(BaseModel):
    id: int
    source: int
    target: int
    relationship_type: str
    description: str | None = None
    confidence_score: float | None = None


# =========================================================
# COMPLETE GRAPH
# =========================================================

class HeritageGraphResponse(BaseModel):
    nodes: list[HeritageGraphNode]
    edges: list[HeritageGraphEdge]