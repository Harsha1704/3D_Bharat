from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "3D BHARAT API"

def test_get_heritage_sites():
    response = client.get("/api/v1/heritage-sites")
    assert response.status_code == 200
    sites = response.json()
    assert isinstance(sites, list)
    assert len(sites) > 0
    first_site = sites[0]
    assert "id" in first_site
    assert "name" in first_site
    assert "latitude" in first_site
    assert "longitude" in first_site
    assert "category" in first_site

def test_get_single_heritage_site():
    response = client.get("/api/v1/heritage-sites/1")
    assert response.status_code == 200
    site = response.json()
    assert site["id"] == 1
    assert "name" in site
    assert "description" in site

def test_get_nonexistent_heritage_site():
    response = client.get("/api/v1/heritage-sites/999999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_search_heritage_sites():
    response = client.get("/api/v1/heritage-sites/search?query=Hampi")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert any("Hampi" in item["name"] for item in data["items"])

def test_nearby_heritage_sites():
    # Hampi coordinates: lat 15.335, lon 76.46
    response = client.get("/api/v1/heritage-sites/nearby?latitude=15.335&longitude=76.46&radius_km=300")
    assert response.status_code == 200
    nearby = response.json()
    assert isinstance(nearby, list)
    assert len(nearby) >= 1
    assert "distance_km" in nearby[0]
    assert nearby[0]["distance_km"] <= 300

def test_nearby_invalid_latitude():
    response = client.get("/api/v1/heritage-sites/nearby?latitude=190&longitude=76.46")
    assert response.status_code == 422

def test_nearby_negative_radius():
    response = client.get("/api/v1/heritage-sites/nearby?latitude=15.335&longitude=76.46&radius_km=-10")
    assert response.status_code == 422

def test_site_recommendations():
    response = client.get("/api/v1/heritage-sites/1/recommendations")
    assert response.status_code == 200
    recs = response.json()
    assert isinstance(recs, list)
    if len(recs) > 0:
        assert "recommendation_score" in recs[0]
        assert "recommendation_reasons" in recs[0]

def test_site_connections():
    response = client.get("/api/v1/heritage-connections/site/1")
    assert response.status_code == 200
    connections = response.json()
    assert isinstance(connections, list)
    if len(connections) > 0:
        assert "relationship_type" in connections[0]
        assert "confidence_score" in connections[0]

def test_self_connection_rejected():
    response = client.post(
        "/api/v1/heritage-connections",
        json={
            "source_site_id": 1,
            "target_site_id": 1,
            "relationship_type": "SAME_SITE",
            "confidence_score": 0.5,
        },
    )
    assert response.status_code == 400
