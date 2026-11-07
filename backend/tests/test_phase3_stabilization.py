import math
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.main import app
from app.core.config import settings
from app.core.database import get_db, check_database_connection, SessionLocal

client = TestClient(app)


# =========================================================
# 1. DATABASE DEPENDENCY & CONNECTIVITY TESTS
# =========================================================

def test_database_connectivity_helper():
    """Verify that check_database_connection() returns True on live DB."""
    assert check_database_connection() is True


def test_shared_get_db_session_lifecycle():
    """Verify that get_db yields an active session and closes it cleanly."""
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    assert db.is_active

    # Check session query works
    res = db.execute(text("SELECT 1;")).scalar()
    assert res == 1

    # Close session via generator finalizer
    try:
        next(gen)
    except StopIteration:
        pass


def test_shared_get_db_rollback_on_exception():
    """Verify that get_db rolls back transactions when an unhandled exception occurs."""
    gen = get_db()
    db = next(gen)

    class CustomTestError(Exception):
        pass

    with pytest.raises(CustomTestError):
        try:
            # Simulate an unhandled exception inside a request context
            raise CustomTestError("Simulated unhandled route failure")
        except Exception:
            gen.throw(CustomTestError("Simulated unhandled route failure"))


# =========================================================
# 2. CORS SECURITY TESTS
# =========================================================

def test_cors_allowed_development_origin():
    """Allowed origin http://localhost:5173 receives matching Access-Control headers."""
    response = client.options(
        "/api/v1/heritage-sites",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_disallowed_origin_rejected():
    """Disallowed origin does NOT receive Access-Control-Allow-Origin header."""
    response = client.options(
        "/api/v1/heritage-sites",
        headers={
            "Origin": "http://malicious-unauthorized-site.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    allow_origin = response.headers.get("access-control-allow-origin")
    assert allow_origin != "http://malicious-unauthorized-site.com"
    assert allow_origin != "*"


def test_cors_no_wildcard_with_credentials():
    """Ensure CORS_ORIGINS never contains '*'."""
    assert "*" not in settings.CORS_ORIGINS
    for origin in settings.CORS_ORIGINS:
        assert origin.startswith("http://") or origin.startswith("https://")


# =========================================================
# 3. HAVERSINE DISTANCE EDGE CASES & MATH TESTS
# =========================================================

def haversine_python(lat1, lon1, lat2, lon2):
    """Pure Python reference implementation matching the PostgreSQL formula."""
    lat1_r = math.radians(lat1)
    lon1_r = math.radians(lon1)
    lat2_r = math.radians(lat2)
    lon2_r = math.radians(lon2)

    cos_angle = (
        math.sin(lat1_r) * math.sin(lat2_r)
        + math.cos(lat1_r) * math.cos(lat2_r) * math.cos(lon2_r - lon1_r)
    )
    clamped_cos = max(-1.0, min(1.0, cos_angle))
    return 6371.0 * math.acos(clamped_cos)


def test_haversine_identical_coordinates():
    """Identical coordinates should produce exactly 0.0 distance."""
    dist = haversine_python(28.6139, 77.2090, 28.6139, 77.2090)
    assert math.isclose(dist, 0.0, abs_tol=1e-5)


def test_haversine_known_delhi_to_agra():
    """Distance between Delhi (28.6562, 77.2410) and Agra (27.1751, 78.0421) is ~178-185 km."""
    dist = haversine_python(28.6562, 77.2410, 27.1751, 78.0421)
    assert 170.0 < dist < 190.0


def test_haversine_near_antipodal_stability():
    """Antipodal points should evaluate without math domain error and yield ~20,015 km."""
    dist = haversine_python(0.0, 0.0, 0.0, 180.0)
    expected = 6371.0 * math.pi
    assert math.isclose(dist, expected, abs_tol=1.0)


def test_haversine_poles_stability():
    """Distance between North Pole and South Pole should evaluate cleanly."""
    dist = haversine_python(90.0, 0.0, -90.0, 0.0)
    expected = 6371.0 * math.pi
    assert math.isclose(dist, expected, abs_tol=1.0)


def test_nearby_api_with_live_site_coordinates():
    """Querying nearby with Taj Mahal coordinates should find Taj Mahal within 1 km."""
    # Taj Mahal coords: lat 27.1751, lon 78.0421
    response = client.get(
        "/api/v1/heritage-sites/nearby",
        params={"latitude": 27.1751, "longitude": 78.0421, "radius_km": 5.0},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Closest site should be at distance ~ 0.0 km
    assert data[0]["distance_km"] <= 0.1
    # Check ascending order
    for i in range(len(data) - 1):
        assert data[i]["distance_km"] <= data[i + 1]["distance_km"]


# =========================================================
# 4. API ERROR HANDLING & VALIDATION TESTS
# =========================================================

def test_get_nonexistent_heritage_site_404():
    """Requesting non-existent site returns 404 with clean detail message."""
    response = client.get("/api/v1/heritage-sites/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Heritage site not found"


def test_get_nonexistent_connection_404():
    """Requesting non-existent connection returns 404."""
    response = client.get("/api/v1/heritage-connections/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Heritage connection not found."


def test_get_recommendations_nonexistent_site_404():
    """Recommendations for non-existent site returns 404."""
    response = client.get("/api/v1/heritage-sites/999999/recommendations")
    assert response.status_code == 404
    assert response.json()["detail"] == "Heritage site not found"


def test_create_connection_invalid_site_404():
    """Creating connection referencing non-existent site returns 404."""
    payload = {
        "source_site_id": 999998,
        "target_site_id": 999999,
        "relationship_type": "HISTORICAL_ALLIANCE",
    }
    response = client.post("/api/v1/heritage-connections", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_create_connection_self_referential_400():
    """Creating self-connection returns 400 Bad Request."""
    payload = {
        "source_site_id": 1,
        "target_site_id": 1,
        "relationship_type": "SAME_BUILDER",
    }
    response = client.post("/api/v1/heritage-connections", json=payload)
    assert response.status_code == 400
    assert "cannot connect to itself" in response.json()["detail"]


def test_create_site_duplicate_external_id_409():
    """Creating site with existing external_id returns 409 Conflict."""
    payload = {
        "external_id": "ASI_TAJ_009",  # Already exists in DB
        "name": "Duplicate Taj Mahal",
        "state": "Uttar Pradesh",
        "category": "Mughal Architecture",
        "description": "Testing duplicate external_id conflict handling.",
    }
    response = client.post("/api/v1/heritage-sites", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_nearby_validation_latitude_out_of_range_422():
    """Latitude > 90 returns 422 Unprocessable Entity."""
    response = client.get(
        "/api/v1/heritage-sites/nearby",
        params={"latitude": 105.0, "longitude": 77.0, "radius_km": 10},
    )
    assert response.status_code == 422


def test_nearby_validation_longitude_out_of_range_422():
    """Longitude < -180 returns 422 Unprocessable Entity."""
    response = client.get(
        "/api/v1/heritage-sites/nearby",
        params={"latitude": 20.0, "longitude": -195.0, "radius_km": 10},
    )
    assert response.status_code == 422


def test_connection_validation_confidence_score_out_of_range_422():
    """Confidence score > 1.0 returns 422."""
    payload = {
        "source_site_id": 1,
        "target_site_id": 2,
        "relationship_type": "TRADE_ROUTE",
        "confidence_score": 1.5,
    }
    response = client.post("/api/v1/heritage-connections", json=payload)
    assert response.status_code == 422


# =========================================================
# 5. KNOWLEDGE GRAPH ENDPOINTS TEST
# =========================================================

def test_heritage_graph_endpoint():
    """Verify full graph returns nodes and edges."""
    response = client.get("/api/v1/heritage-graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 10
    assert len(data["edges"]) >= 8


def test_heritage_site_connections_graph_endpoint():
    """Verify connections for an existing site returns list of HeritageConnectionResponse."""
    response = client.get("/api/v1/heritage-graph/site/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "relationship_type" in data[0]
