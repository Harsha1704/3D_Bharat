import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# =========================================================
# 1. GEOGRAPHICAL BOUNDING-BOX DISCOVERY TESTS
# =========================================================

def test_bbox_discovery_valid_coordinates():
    """
    Search bounding box covering northern India (lat 25 to 30, lon 75 to 80).
    Should return sites located in this region (e.g. Taj Mahal, Qutb Minar, Red Fort).
    """
    response = client.get(
        "/api/v1/heritage-sites/bbox",
        params={
            "min_lat": 25.0,
            "min_lon": 75.0,
            "max_lat": 30.0,
            "max_lon": 80.0,
        },
    )
    assert response.status_code == 200
    sites = response.json()
    assert isinstance(sites, list)
    assert len(sites) > 0
    for s in sites:
        assert 25.0 <= s["latitude"] <= 30.0
        assert 75.0 <= s["longitude"] <= 80.0


def test_bbox_discovery_with_category_filter():
    """
    Search bounding box with an explicit category filter.
    """
    response = client.get(
        "/api/v1/heritage-sites/bbox",
        params={
            "min_lat": 8.0,
            "min_lon": 68.0,
            "max_lat": 37.0,
            "max_lon": 97.0,
            "category": ["Fort"],
        },
    )
    assert response.status_code == 200
    sites = response.json()
    assert isinstance(sites, list)
    for s in sites:
        assert "fort" in s["category"].lower()


def test_bbox_discovery_with_state_filter():
    """
    Search bounding box with state filter.
    """
    response = client.get(
        "/api/v1/heritage-sites/bbox",
        params={
            "min_lat": 8.0,
            "min_lon": 68.0,
            "max_lat": 37.0,
            "max_lon": 97.0,
            "state": "Tamil Nadu",
        },
    )
    assert response.status_code == 200
    sites = response.json()
    assert isinstance(sites, list)
    for s in sites:
        assert s["state"].lower() == "tamil nadu"


def test_bbox_discovery_empty_region():
    """
    Search bounding box in an uninhabited region with zero sites (Antarctica).
    """
    response = client.get(
        "/api/v1/heritage-sites/bbox",
        params={
            "min_lat": -85.0,
            "min_lon": -10.0,
            "max_lat": -80.0,
            "max_lon": 0.0,
        },
    )
    assert response.status_code == 200
    sites = response.json()
    assert isinstance(sites, list)
    assert len(sites) == 0


def test_bbox_invalid_lat_ordering_rejected():
    """
    min_lat > max_lat must fail with 422 Unprocessable Entity.
    """
    response = client.get(
        "/api/v1/heritage-sites/bbox",
        params={
            "min_lat": 30.0,
            "min_lon": 75.0,
            "max_lat": 25.0,
            "max_lon": 80.0,
        },
    )
    assert response.status_code == 422
    assert "min_lat cannot be greater than max_lat" in response.json()["detail"]


def test_bbox_invalid_lon_ordering_rejected():
    """
    min_lon > max_lon must fail with 422 Unprocessable Entity.
    """
    response = client.get(
        "/api/v1/heritage-sites/bbox",
        params={
            "min_lat": 25.0,
            "min_lon": 80.0,
            "max_lat": 30.0,
            "max_lon": 75.0,
        },
    )
    assert response.status_code == 422
    assert "min_lon cannot be greater than max_lon" in response.json()["detail"]


def test_bbox_coordinates_out_of_range():
    """
    Latitude > 90 or < -90, Longitude > 180 or < -180 must trigger Pydantic 422 validation.
    """
    response = client.get(
        "/api/v1/heritage-sites/bbox",
        params={
            "min_lat": -95.0,
            "min_lon": 75.0,
            "max_lat": 30.0,
            "max_lon": 80.0,
        },
    )
    assert response.status_code == 422


# =========================================================
# 2. COMPREHENSIVE SITE DETAILS API TESTS
# =========================================================

def test_site_details_non_existent():
    """
    Non-existent site must return 404 Not Found.
    """
    response = client.get("/api/v1/heritage-sites/999999/details")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_site_details_eager_loading():
    """
    Fetching details for an existing site returns all sections and statistics.
    """
    # Fetch first site from list
    list_res = client.get("/api/v1/heritage-sites?limit=1")
    assert list_res.status_code == 200
    sites = list_res.json()
    assert len(sites) > 0
    site_id = sites[0]["id"]

    response = client.get(f"/api/v1/heritage-sites/{site_id}/details")
    assert response.status_code == 200
    data = response.json()

    # Core site verification
    assert data["id"] == site_id
    assert "name" in data
    assert "state" in data
    assert "category" in data

    # Related collections presence
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert "media" in data
    assert isinstance(data["media"], list)
    assert "assets_3d" in data
    assert isinstance(data["assets_3d"], list)
    assert "connections" in data
    assert isinstance(data["connections"], list)

    # Statistics block
    assert "stats" in data
    stats = data["stats"]
    assert stats["total_sources"] == len(data["sources"])
    assert stats["total_media"] == len(data["media"])
    assert stats["total_3d_assets"] == len(data["assets_3d"])
    assert stats["total_connections"] == len(data["connections"])


def test_site_details_file_url_safety():
    """
    Ensure media and 3D assets in site details never expose absolute filesystem paths.
    Only safe file URLs (/api/v1/heritage-media/{id}/file) should be present.
    """
    list_res = client.get("/api/v1/heritage-sites?limit=10")
    assert list_res.status_code == 200
    sites = list_res.json()

    for s in sites:
        res = client.get(f"/api/v1/heritage-sites/{s['id']}/details")
        assert res.status_code == 200
        data = res.json()

        for m in data["media"]:
            assert "file_url" in m
            assert m["file_url"].startswith("/api/v1/heritage-media/")
            # Ensure no raw drive letters or paths
            assert "D:\\" not in m["file_url"]
            assert "C:\\" not in m["file_url"]

        for a in data["assets_3d"]:
            assert "file_url" in a
            assert a["file_url"].startswith("/api/v1/heritage-3d-assets/")
            assert "D:\\" not in a["file_url"]
            assert "C:\\" not in a["file_url"]


# =========================================================
# 3. RELATED HERITAGE DISCOVERY API TESTS
# =========================================================

def test_related_heritage_non_existent():
    """
    Non-existent site must return 404.
    """
    response = client.get("/api/v1/heritage-sites/999999/related")
    assert response.status_code == 404


def test_related_heritage_demarcation():
    """
    Validates clear separation between:
    1. Documented Archival Connections
    2. Structured Relations (shared period/category/architecture/proximity)
    3. AI Semantic Suggestions (with explicit exploratory disclaimer)
    """
    list_res = client.get("/api/v1/heritage-sites?limit=1")
    assert list_res.status_code == 200
    site_id = list_res.json()[0]["id"]

    response = client.get(f"/api/v1/heritage-sites/{site_id}/related")
    assert response.status_code == 200
    data = response.json()

    assert data["site_id"] == site_id
    assert "site_name" in data

    # 1. Documented Connections
    assert "documented_connections" in data
    assert isinstance(data["documented_connections"], list)
    for doc in data["documented_connections"]:
        assert doc["source"] == "DOCUMENTED_ARCHIVAL_RECORD"
        assert "connected_site_id" in doc
        assert "connected_site_name" in doc
        assert "relationship_type" in doc

    # 2. Structured Relations
    assert "structured_relations" in data
    assert isinstance(data["structured_relations"], list)
    for struct in data["structured_relations"]:
        assert "site_id" in struct
        assert "name" in struct
        assert "shared_attributes" in struct
        assert len(struct["shared_attributes"]) > 0

    # 3. Semantic Suggestions
    assert "semantic_suggestions" in data
    assert isinstance(data["semantic_suggestions"], list)
    for sem in data["semantic_suggestions"]:
        assert "site_id" in sem
        assert "recommendation_score" in sem
        assert "disclaimer" in sem
        assert "Not primary archival evidence" in sem["disclaimer"]


# =========================================================
# 4. ADVANCED MULTI-FIELD SEARCH ENHANCEMENTS TESTS
# =========================================================

def test_search_by_architecture():
    """
    Filter sites by architectural style (e.g. Dravidian).
    """
    response = client.get(
        "/api/v1/heritage-sites/search",
        params={"architecture": "Dravidian"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        assert "dravidian" in (item.get("architecture") or "").lower()


def test_search_by_dynasty_or_historical_figures():
    """
    Filter sites by associated dynasty or historical figures.
    """
    response = client.get(
        "/api/v1/heritage-sites/search",
        params={"dynasty": "Chola"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for item in data["items"]:
        # Should match in associated_people, period, or description
        people_str = " ".join(item.get("associated_people") or []).lower()
        period_str = (item.get("period") or "").lower()
        desc_str = (item.get("description") or "").lower()
        assert "chola" in people_str or "chola" in period_str or "chola" in desc_str


def test_search_stable_sorting():
    """
    Test sorting asc and desc by name.
    """
    res_asc = client.get(
        "/api/v1/heritage-sites/search",
        params={"sort_by": "name", "sort_order": "asc", "limit": 10},
    )
    assert res_asc.status_code == 200
    items_asc = res_asc.json()["items"]
    names_asc = [i["name"].lower() for i in items_asc]

    res_desc = client.get(
        "/api/v1/heritage-sites/search",
        params={"sort_by": "name", "sort_order": "desc", "limit": 10},
    )
    assert res_desc.status_code == 200
    items_desc = res_desc.json()["items"]
    names_desc = [i["name"].lower() for i in items_desc]

    assert names_asc == sorted(names_asc)
    assert names_desc == sorted(names_desc, reverse=True)


# =========================================================
# 5. GLOBAL MEDIA & 3D ASSET DISCOVERY ENDPOINTS
# =========================================================

def test_global_media_discovery():
    """
    GET /api/v1/heritage-media returns paginated list with total count and file_url.
    """
    response = client.get("/api/v1/heritage-media?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_next" in data
    for item in data["items"]:
        assert "file_url" in item
        assert item["file_url"].startswith("/api/v1/heritage-media/")


def test_global_3d_asset_discovery():
    """
    GET /api/v1/heritage-3d-assets returns paginated list with total count and file_url.
    """
    response = client.get("/api/v1/heritage-3d-assets?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "has_next" in data
    for item in data["items"]:
        assert "file_url" in item
        assert item["file_url"].startswith("/api/v1/heritage-3d-assets/")
