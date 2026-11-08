import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_list_3d_assets_public():
    response = client.get("/api/v1/heritage-3d/assets")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert any(item["is_pilot"] is True for item in data["items"])


def test_get_pilot_monument_asset():
    response = client.get("/api/v1/heritage-3d/pilot")
    assert response.status_code == 200
    data = response.json()
    assert data["is_pilot"] is True
    assert data["heritage_site_id"] == 3
    assert data["asset_format"] == "GLB"
    assert data["asset_origin"] == "ARCHITECTURAL_VISUALIZATION"
    assert "file_url" in data
    assert data["file_size_bytes"] > 0
    assert len(data["checksum_sha256"]) == 64
    assert data["rights_status"] == "RIGHTS_REVIEW_REQUIRED"
    assert data["licence_name"] == "RIGHTS_REVIEW_PENDING"
    assert data["redistribution_allowed"] is False
    assert "UNESCO" in (data["source_identifier"] or "")


def test_get_asset_by_id():
    # First get pilot to know its ID
    pilot_resp = client.get("/api/v1/heritage-3d/pilot")
    asset_id = pilot_resp.json()["id"]

    response = client.get(f"/api/v1/heritage-3d/assets/{asset_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == asset_id
    assert data["title"] is not None
    assert data["validation_status"] == "READY"


def test_get_asset_file_download():
    pilot_resp = client.get("/api/v1/heritage-3d/pilot")
    asset_id = pilot_resp.json()["id"]

    response = client.get(f"/api/v1/heritage-3d/assets/{asset_id}/file")
    assert response.status_code == 200
    assert response.headers["content-type"] == "model/gltf-binary"
    assert response.content.startswith(b"glTF")
    assert len(response.content) >= 1000


def test_get_site_3d_assets():
    response = client.get("/api/v1/heritage-3d/sites/3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["heritage_site_id"] == 3


def test_security_write_access_enforcement(monkeypatch):
    test_key = "secure_preservation_key_phase10"
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", test_key)

    pilot_resp = client.get("/api/v1/heritage-3d/pilot")
    asset_id = pilot_resp.json()["id"]

    # 1. Missing header -> 401
    unauth_resp = client.post(f"/api/v1/heritage-3d/assets/{asset_id}/validate")
    assert unauth_resp.status_code == 401

    # 2. Wrong key -> 401
    wrong_resp = client.post(
        f"/api/v1/heritage-3d/assets/{asset_id}/validate",
        headers={"X-API-Key": "invalid_key"},
    )
    assert wrong_resp.status_code == 401

    # 3. Correct key -> 200
    auth_resp = client.post(
        f"/api/v1/heritage-3d/assets/{asset_id}/validate",
        headers={"X-API-Key": test_key},
    )
    assert auth_resp.status_code == 200
    assert auth_resp.json()["is_valid"] is True


def test_validate_and_publish_with_auth(monkeypatch):
    test_key = "secure_preservation_key_phase10"
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", test_key)

    pilot_resp = client.get("/api/v1/heritage-3d/pilot")
    asset_id = pilot_resp.json()["id"]

    # Validate
    val_resp = client.post(
        f"/api/v1/heritage-3d/assets/{asset_id}/validate",
        headers={"X-API-Key": test_key},
    )
    assert val_resp.status_code == 200
    val_data = val_resp.json()
    assert val_data["is_valid"] is True
    assert val_data["magic_bytes_valid"] is True
    assert val_data["format_recognized"] is True

    # Publish
    pub_resp = client.post(
        f"/api/v1/heritage-3d/assets/{asset_id}/publish",
        headers={"X-API-Key": test_key},
        json={"visibility_status": "PUBLIC"},
    )
    assert pub_resp.status_code == 200
    pub_data = pub_resp.json()
    assert pub_data["visibility_status"] == "PUBLIC"


def test_ingest_new_3d_asset_workflow(monkeypatch):
    test_key = "secure_preservation_key_phase10"
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", test_key)

    from app.scripts.generate_pilot_model import GLBBuilder, generate_box
    builder = GLBBuilder()
    mat = builder.add_material("TestMat", (0.5, 0.5, 0.5, 1.0))
    v, n, idx = generate_box(2.0, 2.0, 2.0)
    mesh = builder.add_mesh_primitive(v, n, idx, mat, "TestBox")
    builder.add_node("TestBoxNode", mesh)
    builder.scenes[0]["nodes"] = [0]
    glb_bytes = builder.build_glb()

    files = {
        "file": ("test_shrine.glb", io.BytesIO(glb_bytes), "model/gltf-binary")
    }
    form_data = {
        "site_id": 1,
        "title": "Hampi Test Shrine Model",
        "asset_format": "GLB",
        "asset_origin": "ARCHITECTURAL_VISUALIZATION",
        "licence_name": "CC-BY-4.0",
        "rights_status": "CREATIVE_COMMONS",
        "is_pilot": False,
    }

    resp = client.post(
        "/api/v1/heritage-3d/assets",
        headers={"X-API-Key": test_key},
        data=form_data,
        files=files,
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == "Hampi Test Shrine Model"
    assert created["validation_status"] == "READY"
    assert "file_url" in created

    # Test file retrieval for newly uploaded asset
    file_resp = client.get(created["file_url"])
    assert file_resp.status_code == 200
    assert file_resp.content.startswith(b"glTF")

    # Cleanup test fixture
    client.delete(f"/api/v1/heritage-3d-assets/{created['id']}", headers={"X-API-Key": test_key})
