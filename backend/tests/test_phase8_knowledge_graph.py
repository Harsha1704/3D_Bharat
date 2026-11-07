import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.cultural_graph import CulturalGraphEntity, CulturalGraphRelationship
from sqlalchemy import select, or_, delete

client = TestClient(app)


@pytest.fixture(autouse=True, scope="module")
def cleanup_test_graph_data():
    yield
    # Clean up any test entities or relationships created during tests
    db = SessionLocal()
    try:
        test_ents = db.execute(
            select(CulturalGraphEntity).where(
                or_(
                    CulturalGraphEntity.canonical_name.ilike("Test%"),
                    CulturalGraphEntity.canonical_name.ilike("Authorized%"),
                )
            )
        ).scalars().all()
        if test_ents:
            test_ids = [e.id for e in test_ents]
            db.execute(
                delete(CulturalGraphRelationship).where(
                    or_(
                        CulturalGraphRelationship.source_entity_id.in_(test_ids),
                        CulturalGraphRelationship.target_entity_id.in_(test_ids),
                    )
                )
            )
            db.execute(
                delete(CulturalGraphEntity).where(CulturalGraphEntity.id.in_(test_ids))
            )
            db.commit()
    finally:
        db.close()


# =========================================================
# 1. ENTITY LISTING & FILTERING
# =========================================================

def test_list_entities_pagination():
    response = client.get("/api/v1/knowledge-graph/entities?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    assert "X-Total-Count" in response.headers
    total = int(response.headers["X-Total-Count"])
    assert total >= 44


def test_list_entities_filter_by_type():
    response = client.get("/api/v1/knowledge-graph/entities?entity_type=DYNASTY")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 9
    for item in data:
        assert item["entity_type"] == "DYNASTY"


def test_list_entities_filter_by_architectural_style():
    response = client.get("/api/v1/knowledge-graph/entities?entity_type=ARCHITECTURAL_STYLE")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    for item in data:
        assert item["entity_type"] == "ARCHITECTURAL_STYLE"


def test_search_entities():
    response = client.get("/api/v1/knowledge-graph/search?q=Chola")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    names = [e["canonical_name"] for e in data]
    assert any("Chola" in name for name in names)


def test_get_entity_by_id():
    # First get an entity from list
    list_res = client.get("/api/v1/knowledge-graph/entities?limit=1")
    assert list_res.status_code == 200
    entity_id = list_res.json()[0]["id"]

    res = client.get(f"/api/v1/knowledge-graph/entities/{entity_id}")
    assert res.status_code == 200
    entity = res.json()
    assert entity["id"] == entity_id
    assert "canonical_name" in entity
    assert "entity_type" in entity


def test_get_entity_not_found():
    res = client.get("/api/v1/knowledge-graph/entities/99999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# =========================================================
# 2. ENTITY CREATION & INTEGRITY CONSTRAINTS
# =========================================================

def test_create_entity_success():
    payload = {
        "entity_type": "HISTORICAL_PERSON",
        "canonical_name": "Test King Vikramaditya",
        "period": "Ancient",
        "geographical_context": "Ujjain, Central India",
        "description": "Legendary emperor associated with the Vikram Samvat era.",
        "verification_status": "VERIFIED",
    }
    res = client.post("/api/v1/knowledge-graph/entities", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["canonical_name"] == "Test King Vikramaditya"
    assert created["entity_type"] == "HISTORICAL_PERSON"
    assert "slug" in created


def test_create_entity_invalid_type():
    payload = {
        "entity_type": "FICTIONAL_REALM",
        "canonical_name": "Atlantis",
    }
    res = client.post("/api/v1/knowledge-graph/entities", json=payload)
    assert res.status_code == 400
    assert "Invalid entity_type" in res.json()["detail"]


def test_create_entity_duplicate_heritage_site_rejection():
    # Attempt to link an entity to heritage_site_id = 1 (already mapped to Taj Mahal)
    payload = {
        "entity_type": "HERITAGE_SITE",
        "canonical_name": "Duplicate Taj Mahal Entry",
        "heritage_site_id": 1,
    }
    res = client.post("/api/v1/knowledge-graph/entities", json=payload)
    assert res.status_code == 400
    assert "already mapped" in res.json()["detail"]


# =========================================================
# 3. RELATIONSHIPS & CONSTRAINTS
# =========================================================

def test_get_entity_relationships():
    # Find Brihadisvara Temple entity
    search_res = client.get("/api/v1/knowledge-graph/search?q=Brihadisvara")
    assert search_res.status_code == 200
    assert len(search_res.json()) > 0
    brihadisvara_id = search_res.json()[0]["id"]

    rel_res = client.get(f"/api/v1/knowledge-graph/entities/{brihadisvara_id}/relationships")
    assert rel_res.status_code == 200
    relationships = rel_res.json()
    assert len(relationships) >= 3

    # Check for Raja Raja Chola I and Chola Dynasty associations
    connected_names = [
        r["target_entity_name"] if r["source_entity_id"] == brihadisvara_id else r["source_entity_name"]
        for r in relationships
    ]
    assert any("Chola" in name for name in connected_names)


def test_create_relationship_success():
    # Create two temporary test entities
    e1_res = client.post(
        "/api/v1/knowledge-graph/entities",
        json={
            "entity_type": "HISTORICAL_PERSON",
            "canonical_name": "Test Patron Queen",
            "period": "Medieval",
        },
    )
    assert e1_res.status_code == 201
    e1_id = e1_res.json()["id"]

    e2_res = client.post(
        "/api/v1/knowledge-graph/entities",
        json={
            "entity_type": "CULTURAL_TRADITION",
            "canonical_name": "Test Temple Inscription Tradition",
            "period": "Medieval",
        },
    )
    assert e2_res.status_code == 201
    e2_id = e2_res.json()["id"]

    # Create relationship
    rel_res = client.post(
        "/api/v1/knowledge-graph/relationships",
        json={
            "source_entity_id": e1_id,
            "target_entity_id": e2_id,
            "relationship_type": "ASSOCIATED_WITH_TRADITION",
            "evidence_status": "DOCUMENTED",
            "confidence_score": 0.95,
            "source_citation": "Epigraphia Indica, Vol. IX",
        },
    )
    assert rel_res.status_code == 201
    rel_data = rel_res.json()
    assert rel_data["relationship_type"] == "ASSOCIATED_WITH_TRADITION"
    assert rel_data["evidence_status"] == "DOCUMENTED"
    assert rel_data["source_entity_name"] == "Test Patron Queen"
    assert rel_data["target_entity_name"] == "Test Temple Inscription Tradition"


def test_create_relationship_self_referential_rejection():
    # Find any entity
    res = client.get("/api/v1/knowledge-graph/entities?limit=1")
    entity_id = res.json()[0]["id"]

    rel_res = client.post(
        "/api/v1/knowledge-graph/relationships",
        json={
            "source_entity_id": entity_id,
            "target_entity_id": entity_id,
            "relationship_type": "CONTEMPORARY_WITH",
        },
    )
    assert rel_res.status_code == 400
    assert "Self-referential" in rel_res.json()["detail"]


def test_create_relationship_duplicate_rejection():
    # Find Brihadisvara and Chola Dynasty specifically
    search_brihadisvara = client.get("/api/v1/knowledge-graph/search?q=Brihadisvara").json()[0]
    chola_entities = client.get("/api/v1/knowledge-graph/entities?entity_type=DYNASTY&search=Chola").json()
    assert len(chola_entities) > 0
    search_chola = chola_entities[0]

    # Attempt to insert identical existing relationship
    rel_res = client.post(
        "/api/v1/knowledge-graph/relationships",
        json={
            "source_entity_id": search_brihadisvara["id"],
            "target_entity_id": search_chola["id"],
            "relationship_type": "ASSOCIATED_WITH_DYNASTY",
        },
    )
    assert rel_res.status_code == 400
    assert "already exists" in rel_res.json()["detail"]


# =========================================================
# 4. BOUNDED EXPLORATION TRAVERSAL
# =========================================================

def test_explore_graph_depth_1():
    search_res = client.get("/api/v1/knowledge-graph/search?q=Taj Mahal")
    assert search_res.status_code == 200
    taj_id = search_res.json()[0]["id"]

    res = client.get(f"/api/v1/knowledge-graph/explore/{taj_id}?depth=1")
    assert res.status_code == 200
    data = res.json()
    assert data["center_entity_id"] == taj_id
    assert data["depth"] == 1
    assert data["total_nodes"] >= 3  # Taj, Mughal Dynasty, Shah Jahan, Mughal Architecture
    assert data["total_edges"] >= 2
    assert len(data["nodes"]) == data["total_nodes"]
    assert len(data["edges"]) == data["total_edges"]


def test_explore_graph_depth_bounding():
    # Requests with depth > 3 must be bounded to 3
    search_res = client.get("/api/v1/knowledge-graph/search?q=Taj Mahal")
    taj_id = search_res.json()[0]["id"]

    res = client.get(f"/api/v1/knowledge-graph/explore/{taj_id}?depth=3")
    assert res.status_code == 200
    data = res.json()
    assert data["depth"] == 3
    assert data["total_nodes"] <= 100


def test_explore_graph_filter_by_entity_type():
    search_res = client.get("/api/v1/knowledge-graph/search?q=Taj Mahal")
    taj_id = search_res.json()[0]["id"]

    res = client.get(f"/api/v1/knowledge-graph/explore/{taj_id}?depth=1&entity_types=DYNASTY")
    assert res.status_code == 200
    data = res.json()
    neighbor_nodes = [n for n in data["nodes"] if n["id"] != taj_id]
    for n in neighbor_nodes:
        assert n["entity_type"] == "DYNASTY"


# =========================================================
# 5. GRAPH STATISTICS
# =========================================================

def test_graph_statistics():
    res = client.get("/api/v1/knowledge-graph/statistics")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_entities"] >= 44
    assert stats["total_relationships"] >= 35

    assert "HERITAGE_SITE" in stats["entities_by_type"]
    assert "DYNASTY" in stats["entities_by_type"]
    assert "HISTORICAL_PERSON" in stats["entities_by_type"]
    assert "ARCHITECTURAL_STYLE" in stats["entities_by_type"]

    assert "BUILT_BY" in stats["relationships_by_type"]
    assert "ASSOCIATED_WITH_DYNASTY" in stats["relationships_by_type"]
    assert "HAS_ARCHITECTURAL_STYLE" in stats["relationships_by_type"]

    assert "DOCUMENTED" in stats["relationships_by_evidence"]


# =========================================================
# 6. RELATIONSHIP PROVENANCE AUDIT TRAIL
# =========================================================

def test_entity_provenance_dossier():
    search_res = client.get("/api/v1/knowledge-graph/search?q=Brihadisvara")
    brihadisvara_id = search_res.json()[0]["id"]

    res = client.get(f"/api/v1/knowledge-graph/entities/{brihadisvara_id}/provenance")
    assert res.status_code == 200
    prov = res.json()
    assert prov["entity_id"] == brihadisvara_id
    assert prov["entity_name"] == "Brihadisvara Temple"
    assert len(prov["relationships_provenance"]) >= 3

    # Check evidence traceability
    for item in prov["relationships_provenance"]:
        assert item["evidence_status"] in ["DOCUMENTED", "VERIFIED", "IMPORTED_UNVERIFIED", "EXPLORATORY", "AI_SUGGESTED"]
        assert item["connected_entity_name"] is not None
        # Must have either primary source ID or citation text
        assert item["primary_source_id"] is not None or item["source_citation"] is not None


# =========================================================
# 7. SECURITY & ACCESS CONTROL
# =========================================================

def test_production_write_protection_entities(monkeypatch):
    """In production mode without API key, write requests must be rejected."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", None)

    res = client.post(
        "/api/v1/knowledge-graph/entities",
        json={"entity_type": "DYNASTY", "canonical_name": "Unauthorized Dynasty"},
    )
    assert res.status_code == 503
    assert "disabled in production" in res.json()["detail"]


def test_production_write_protection_relationships(monkeypatch):
    """In production mode without API key, relationship writes must be rejected."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", None)

    res = client.post(
        "/api/v1/knowledge-graph/relationships",
        json={
            "source_entity_id": 1,
            "target_entity_id": 2,
            "relationship_type": "BUILT_BY",
        },
    )
    assert res.status_code == 503
    assert "disabled in production" in res.json()["detail"]


def test_production_api_key_authorized_write(monkeypatch):
    """In production mode with valid API key, write requests succeed."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", "secure_graph_key_999")

    # 1. Without header -> 401
    res1 = client.post(
        "/api/v1/knowledge-graph/entities",
        json={"entity_type": "DYNASTY", "canonical_name": "Authorized Dynasty"},
    )
    assert res1.status_code == 401

    # 2. With valid header -> 201
    res2 = client.post(
        "/api/v1/knowledge-graph/entities",
        headers={"X-API-Key": "secure_graph_key_999"},
        json={"entity_type": "DYNASTY", "canonical_name": "Authorized Dynasty"},
    )
    assert res2.status_code == 201
    assert res2.json()["canonical_name"] == "Authorized Dynasty"
