import json
import struct
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)

TEST_API_KEY = "audit_write_key_phase10_1"


def test_pilot_provenance_and_origin_classification():
    """Verify pilot asset is classified honestly as ARCHITECTURAL_VISUALIZATION."""
    res = client.get("/api/v1/heritage-3d/pilot")
    assert res.status_code == 200
    data = res.json()
    assert data["heritage_site_id"] == 3
    assert data["is_pilot"] is True
    assert data["asset_origin"] == "ARCHITECTURAL_VISUALIZATION"
    assert data["asset_origin"] != "PHOTOGRAMMETRY_SCAN"
    assert data["asset_origin"] != "LASER_SCAN"


def test_licensing_and_rights_review_status():
    """Verify rights review status and resolution of CC-BY contradiction."""
    res = client.get("/api/v1/heritage-3d/pilot")
    assert res.status_code == 200
    data = res.json()
    assert data["rights_status"] == "RIGHTS_REVIEW_REQUIRED"
    assert data["licence_name"] == "RIGHTS_REVIEW_PENDING"
    assert data["commercial_use_allowed"] is False
    assert data["redistribution_allowed"] is False
    assert "visual inspection only" in (data["attribution_text"] or "").lower()


def test_binary_download_restriction_enforcement():
    """Verify binary redistribution download is blocked with 403 while viewer streaming is allowed with 200."""
    res = client.get("/api/v1/heritage-3d/pilot")
    asset_id = res.json()["id"]

    # 1. Download request (attachment) must be rejected with 403 Forbidden
    download_res = client.get(f"/api/v1/heritage-3d/assets/{asset_id}/file?download=true")
    assert download_res.status_code == 403
    assert "restricted" in download_res.json()["detail"].lower()

    # 2. Viewer streaming request (inline) must be permitted with 200 OK
    view_res = client.get(f"/api/v1/heritage-3d/assets/{asset_id}/file?download=false")
    assert view_res.status_code == 200
    assert view_res.headers["content-type"] == "model/gltf-binary"
    assert "inline" in view_res.headers.get("content-disposition", "")
    assert view_res.content.startswith(b"glTF")


def test_test_asset_isolation_from_public_endpoints():
    """Verify that private test fixtures are excluded from public discovery."""
    res = client.get("/api/v1/heritage-3d/assets")
    assert res.status_code == 200
    data = res.json()
    items = data["items"]

    # No test fixtures should appear in public list
    for item in items:
        assert "Test" not in item["title"]
        assert item["visibility_status"] == "PUBLIC"
        assert item.get("validation_status") != "TEST_FIXTURE"

    # Attempting to fetch a private test asset directly should return 404
    # IDs 80, 81, 82, 86 were test assets
    for test_id in (80, 81, 82, 86):
        test_res = client.get(f"/api/v1/heritage-3d/assets/{test_id}")
        assert test_res.status_code == 404

        test_file_res = client.get(f"/api/v1/heritage-3d/assets/{test_id}/file")
        assert test_file_res.status_code == 404


def test_sha256_file_integrity_and_magic_bytes():
    """Verify physical GLB file SHA-256 and glTF 2.0 binary chunk layout."""
    res = client.get("/api/v1/heritage-3d/pilot")
    data = res.json()
    expected_hash = "adeaa0451653da6e03aa413cdccb6dd248de0fbe0d6eaaafc2a3e7070360d2c4"
    assert data["checksum_sha256"] == expected_hash

    # Stream model bytes and check binary layout
    view_res = client.get(f"/api/v1/heritage-3d/assets/{data['id']}/file")
    assert view_res.status_code == 200
    raw = view_res.content
    assert len(raw) == 170484

    magic, version, length = struct.unpack("<4sII", raw[:12])
    assert magic == b"glTF"
    assert version == 2
    assert length == 170484

    json_len, json_type = struct.unpack("<II", raw[12:20])
    assert json_type == 0x4E4F534A  # 'JSON'
    gltf_json = json.loads(raw[20:20+json_len].decode("utf-8"))
    assert gltf_json["asset"]["version"] == "2.0"
    assert len(gltf_json["nodes"]) == 59
    assert len(gltf_json["meshes"]) == 59
    assert len(gltf_json["materials"]) == 4


def test_geometry_architectural_hierarchy_inspection():
    """Verify presence of canonical Kalinga architectural nodes in the pilot model."""
    res = client.get("/api/v1/heritage-3d/pilot")
    data = res.json()
    view_res = client.get(f"/api/v1/heritage-3d/assets/{data['id']}/file")
    raw = view_res.content

    json_len, _ = struct.unpack("<II", raw[12:20])
    gltf_json = json.loads(raw[20:20+json_len].decode("utf-8"))
    node_names = [n.get("name", "") for n in gltf_json["nodes"]]

    # Check key architectural elements
    assert "Lower_Plinth_Jagati" in node_names
    assert "Upper_Carved_Plinth" in node_names
    assert "Jagamohana_Bada_Sanctum" in node_names
    assert "Jagamohana_Pidha_Tier_1" in node_names
    assert "Amalaka_Fluted_Stone" in node_names
    assert "Kalasha_Golden_Finial" in node_names

    # Check 24 wheels
    wheel_nodes = [n for n in node_names if "Wheel_" in n]
    assert len(wheel_nodes) >= 24


def test_security_authorization_on_write_endpoints(monkeypatch):
    """Verify that protected write and validation endpoints strictly enforce API key."""
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", TEST_API_KEY)
    pilot_resp = client.get("/api/v1/heritage-3d/pilot")
    asset_id = pilot_resp.json()["id"]

    # Validate unauth
    unauth_val = client.post(f"/api/v1/heritage-3d/assets/{asset_id}/validate")
    assert unauth_val.status_code == 401

    # Validate with key
    auth_val = client.post(
        f"/api/v1/heritage-3d/assets/{asset_id}/validate",
        headers={"X-API-Key": TEST_API_KEY},
    )
    assert auth_val.status_code == 200
    assert auth_val.json()["is_valid"] is True
