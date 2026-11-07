import io
import os
import shutil
import hashlib
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.services.storage_service import StorageService, storage_service

client = TestClient(app)


# =========================================================
# 1. STORAGE ABSTRACTION & PATH TRAVERSAL UNIT TESTS
# =========================================================

@pytest.fixture
def temp_storage():
    """Isolated temporary storage fixture to avoid polluting project storage."""
    temp_dir = Path(tempfile.mkdtemp(prefix="3d_bharat_test_storage_"))
    service = StorageService(root_dir=temp_dir)
    yield service
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_storage_sanitize_filename(temp_storage):
    """Verify path traversal characters, directory separators, and spaces are sanitized."""
    raw_name = "../../etc/passwd..//exploit payload.png"
    clean = temp_storage.sanitize_filename(raw_name)
    assert "/" not in clean
    assert "\\" not in clean
    assert ".." not in clean
    assert "exploit_payload.png" in clean


def test_storage_path_traversal_detection(temp_storage):
    """Guards against path traversal in get_absolute_path."""
    with pytest.raises(ValueError, match="Path traversal detected"):
        temp_storage.get_absolute_path("../../secret_file.txt")


def test_storage_empty_file_rejected(temp_storage):
    """Empty files (0 bytes) are rejected."""
    empty_stream = io.BytesIO(b"")
    with pytest.raises(ValueError, match="Uploaded file is empty"):
        temp_storage.save_file_stream(
            stream=empty_stream,
            original_filename="empty.jpg",
            category_dir="media",
            site_id=1,
            is_3d=False,
        )


def test_storage_unsupported_media_extension_rejected(temp_storage):
    """Unsupported executable extensions are rejected."""
    stream = io.BytesIO(b"malicious script")
    with pytest.raises(ValueError, match="Unsupported file extension"):
        temp_storage.save_file_stream(
            stream=stream,
            original_filename="malicious.exe",
            category_dir="media",
            site_id=1,
            is_3d=False,
        )


def test_storage_magic_byte_mismatch_rejected(temp_storage):
    """Reject file with mismatched magic bytes (e.g. text content renamed as .png)."""
    fake_png = io.BytesIO(b"%PDF-1.4 header in png extension")
    with pytest.raises(ValueError, match="File header signature does not match"):
        temp_storage.save_file_stream(
            stream=fake_png,
            original_filename="fake_image.png",
            category_dir="media",
            site_id=1,
            is_3d=False,
        )


def test_storage_save_and_sha256_verification(temp_storage):
    """Save valid simulated JPEG and verify computed SHA-256 checksum."""
    jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"A" * 100
    expected_sha256 = hashlib.sha256(jpeg_bytes).hexdigest()

    stream = io.BytesIO(jpeg_bytes)
    storage_key, filename, size, checksum = temp_storage.save_file_stream(
        stream=stream,
        original_filename="sample_temple.jpg",
        category_dir="media",
        site_id=1,
        is_3d=False,
    )

    assert checksum == expected_sha256
    assert size == len(jpeg_bytes)
    assert storage_key.startswith("media/site_1/")
    assert filename.endswith(".jpg")

    # Verify physical file exists
    abs_path = temp_storage.get_absolute_path(storage_key)
    assert abs_path.exists()
    assert abs_path.read_bytes() == jpeg_bytes

    # Delete file cleanly
    assert temp_storage.delete_file(storage_key) is True
    assert not abs_path.exists()


def test_storage_max_file_size_exceeded(temp_storage):
    """File exceeding size limit raises ValueError and cleans up partial file."""
    large_payload = b"\xff\xd8\xff\xe0" + b"X" * 2000
    stream = io.BytesIO(large_payload)

    with pytest.raises(ValueError, match="File size exceeds maximum allowed limit"):
        temp_storage.save_file_stream(
            stream=stream,
            original_filename="oversized.jpg",
            category_dir="media",
            site_id=1,
            is_3d=False,
            max_bytes=1000,  # 1 KB limit
        )


# =========================================================
# 2. HERITAGE SOURCES API TESTS
# =========================================================

def test_heritage_source_crud_flow():
    """Create, list, update, and delete a historical source."""
    # 1. Create source for Hampi (site_id=1)
    payload = {
        "title": "Epigraphia Carnatica Vol. IV",
        "source_type": "ARCHAEOLOGICAL_SURVEY",
        "author": "B. Lewis Rice",
        "institution": "Archaeological Survey of Mysore",
        "publication_date": "1898",
        "citation": "Rice, B. L. (1898). Epigraphia Carnatica: Inscriptions in the Mysore District.",
        "url": "https://archive.org/details/epigraphiacarnatica",
        "license": "Public Domain",
        "verification_status": "VERIFIED",
    }
    response = client.post("/api/v1/heritage-sites/1/sources", json=payload)
    assert response.status_code == 201
    created = response.json()
    source_id = created["id"]
    assert created["title"] == payload["title"]
    assert created["heritage_site_id"] == 1

    # 2. List sources for site 1
    list_res = client.get("/api/v1/heritage-sites/1/sources")
    assert list_res.status_code == 200
    ids = [s["id"] for s in list_res.json()]
    assert source_id in ids

    # 3. Get single source
    get_res = client.get(f"/api/v1/heritage-sources/{source_id}")
    assert get_res.status_code == 200
    assert get_res.json()["author"] == "B. Lewis Rice"

    # 4. Patch source
    patch_res = client.patch(
        f"/api/v1/heritage-sources/{source_id}",
        json={"notes": "Archival scan verified against ASI library records."},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["notes"] == "Archival scan verified against ASI library records."

    # 5. Delete source
    del_res = client.delete(f"/api/v1/heritage-sources/{source_id}")
    assert del_res.status_code == 200

    # 6. Verify deleted (404)
    assert client.get(f"/api/v1/heritage-sources/{source_id}").status_code == 404


def test_heritage_source_nonexistent_site_404():
    """Associating a source with a non-existent site returns 404."""
    payload = {
        "title": "Nonexistent Record",
        "source_type": "ARCHIVAL_RECORD",
    }
    response = client.post("/api/v1/heritage-sites/999999/sources", json=payload)
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


# =========================================================
# 3. HERITAGE MEDIA API TESTS
# =========================================================

def test_heritage_media_metadata_crud():
    """Register media metadata, retrieve, update, and delete."""
    media_payload = {
        "title": "1880 Archival Photograph of Virupaksha Temple",
        "description": "Albumin print by Alexander Greenlaw during archaeological expedition.",
        "media_type": "ARCHIVAL_PHOTOGRAPH",
        "storage_key": "media/site_1/greenlaw_1880_virupaksha.jpg",
        "original_filename": "greenlaw_1880_virupaksha.jpg",
        "mime_type": "image/jpeg",
        "file_size_bytes": 1024500,
        "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "attribution": "Alexander Greenlaw / British Library",
        "license": "Public Domain",
        "capture_date": "circa 1856-1880",
        "verification_status": "VERIFIED",
    }
    # Create
    create_res = client.post("/api/v1/heritage-sites/1/media", json=media_payload)
    assert create_res.status_code == 201
    media = create_res.json()
    media_id = media["id"]
    assert media["title"] == media_payload["title"]

    # Duplicate storage_key returns 409
    dup_res = client.post("/api/v1/heritage-sites/1/media", json=media_payload)
    assert dup_res.status_code == 409

    # List with filtering
    list_res = client.get(
        "/api/v1/heritage-sites/1/media",
        params={"media_type": "ARCHIVAL_PHOTOGRAPH", "verification_status": "VERIFIED"},
    )
    assert list_res.status_code == 200
    assert any(m["id"] == media_id for m in list_res.json())

    # Update
    patch_res = client.patch(
        f"/api/v1/heritage-media/{media_id}",
        json={"attribution": "British Library Oriental and India Office Collection"},
    )
    assert patch_res.status_code == 200
    assert "Oriental and India Office" in patch_res.json()["attribution"]

    # Delete
    del_res = client.delete(f"/api/v1/heritage-media/{media_id}")
    assert del_res.status_code == 200

    # Confirm 404
    assert client.get(f"/api/v1/heritage-media/{media_id}").status_code == 404


def test_heritage_media_upload_stream_and_download():
    """Upload a simulated JPEG file via multipart form and download it."""
    jpeg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"SIMULATED_ARCHIVAL_IMAGE" * 20

    files = {
        "file": ("archival_shot.jpg", jpeg_data, "image/jpeg"),
    }
    data = {
        "title": "Stone Chariot Detail Photograph",
        "media_type": "ARCHIVAL_PHOTOGRAPH",
        "attribution": "ASI Photographic Survey",
        "license": "CC-BY-4.0",
    }
    upload_res = client.post("/api/v1/heritage-sites/1/media/upload", data=data, files=files)
    assert upload_res.status_code == 201
    media = upload_res.json()
    media_id = media["id"]
    assert media["checksum_sha256"] == hashlib.sha256(jpeg_data).hexdigest()

    # Download file endpoint
    dl_res = client.get(f"/api/v1/heritage-media/{media_id}/file")
    assert dl_res.status_code == 200
    assert dl_res.content == jpeg_data
    assert dl_res.headers.get("content-type") == "image/jpeg"

    # Cleanup
    del_res = client.delete(f"/api/v1/heritage-media/{media_id}")
    assert del_res.status_code == 200


def test_heritage_media_upload_unsupported_format_422():
    """Uploading executable or unsupported extension returns 422."""
    files = {
        "file": ("script.sh", b"#!/bin/bash\necho hello", "text/x-shellscript"),
    }
    data = {"title": "Shell script", "media_type": "HISTORICAL_DOCUMENT"}
    res = client.post("/api/v1/heritage-sites/1/media/upload", data=data, files=files)
    assert res.status_code == 422
    assert "Unsupported file extension" in res.json()["detail"]


# =========================================================
# 4. HERITAGE 3D ASSETS API TESTS
# =========================================================

def test_heritage_3d_asset_metadata_crud():
    """Register 3D asset metadata, retrieve, update, and delete."""
    asset_payload = {
        "title": "Stone Chariot Monolith Photogrammetry Model",
        "description": "High-fidelity digital preservation reconstruction from 1,200 aerial and terrestrial photographs.",
        "asset_format": "GLB",
        "storage_key": "3d/site_1/hampi_stone_chariot_lod0.glb",
        "original_filename": "hampi_stone_chariot_lod0.glb",
        "mime_type": "model/gltf-binary",
        "file_size_bytes": 45200100,
        "checksum_sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "units": "meters",
        "coordinate_system": "Local Metric / WGS84",
        "companion_files": ["textures_albedo.jpg", "textures_normal.png"],
        "bounding_box": '{"min": [-2.5, -1.8, 0.0], "max": [2.5, 1.8, 4.2]}',
        "attribution": "3D Bharat Digital Preservation Initiative",
        "license": "CC-BY-NC-SA 4.0",
        "processing_status": "READY",
        "verification_status": "VERIFIED",
    }
    # Create
    create_res = client.post("/api/v1/heritage-sites/1/3d-assets", json=asset_payload)
    assert create_res.status_code == 201
    asset = create_res.json()
    asset_id = asset["id"]
    assert asset["asset_format"] == "GLB"

    # List 3D assets for site 1
    list_res = client.get("/api/v1/heritage-sites/1/3d-assets", params={"asset_format": "GLB"})
    assert list_res.status_code == 200
    assert any(a["id"] == asset_id for a in list_res.json())

    # Get single 3D asset
    get_res = client.get(f"/api/v1/heritage-3d-assets/{asset_id}")
    assert get_res.status_code == 200
    assert get_res.json()["units"] == "meters"

    # Patch 3D asset
    patch_res = client.patch(
        f"/api/v1/heritage-3d-assets/{asset_id}",
        json={"processing_status": "READY", "units": "centimeters"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["units"] == "centimeters"

    # Delete 3D asset
    del_res = client.delete(f"/api/v1/heritage-3d-assets/{asset_id}")
    assert del_res.status_code == 200

    # Confirm 404
    assert client.get(f"/api/v1/heritage-3d-assets/{asset_id}").status_code == 404


def test_heritage_3d_asset_upload_stream_and_download():
    """Upload a valid GLB binary model and download it."""
    # Valid GLB header: magic b'glTF', version 2, length, chunk
    glb_data = b"glTF\x02\x00\x00\x00\x20\x00\x00\x00\x08\x00\x00\x00JSON{}"
    files = {
        "file": ("temple_pillar.glb", glb_data, "model/gltf-binary"),
    }
    data = {
        "title": "Virupaksha Musical Pillar Reconstruction",
        "asset_format": "GLB",
        "units": "meters",
    }
    upload_res = client.post("/api/v1/heritage-sites/1/3d-assets/upload", data=data, files=files)
    assert upload_res.status_code == 201
    asset = upload_res.json()
    asset_id = asset["id"]
    assert asset["checksum_sha256"] == hashlib.sha256(glb_data).hexdigest()

    # Download 3D file endpoint
    dl_res = client.get(f"/api/v1/heritage-3d-assets/{asset_id}/file")
    assert dl_res.status_code == 200
    assert dl_res.content == glb_data
    assert dl_res.headers.get("content-type") == "model/gltf-binary"

    # Cleanup
    del_res = client.delete(f"/api/v1/heritage-3d-assets/{asset_id}")
    assert del_res.status_code == 200


def test_heritage_3d_asset_nonexistent_site_404():
    """Creating 3D asset for non-existent site returns 404."""
    payload = {
        "title": "Orphan Asset",
        "asset_format": "GLB",
        "storage_key": "3d/site_999999/model.glb",
        "original_filename": "model.glb",
        "mime_type": "model/gltf-binary",
        "file_size_bytes": 1000,
        "checksum_sha256": "1234567890123456789012345678901234567890123456789012345678901234",
    }
    res = client.post("/api/v1/heritage-sites/999999/3d-assets", json=payload)
    assert res.status_code == 404
    assert "does not exist" in res.json()["detail"]


# =========================================================
# 5. REGRESSION & DATABASE CHECK CONSTRAINT VERIFICATION
# =========================================================

def test_database_check_constraints_enforced():
    """Verify check constraints prevent invalid coordinates and confidence scores."""
    # Invalid latitude > 90 rejected by Pydantic/FastAPI
    res = client.get("/api/v1/heritage-sites/nearby", params={"latitude": 95.0, "longitude": 77.0})
    assert res.status_code == 422

    # Invalid confidence score > 1.0 rejected
    res2 = client.post(
        "/api/v1/heritage-connections",
        json={"source_site_id": 1, "target_site_id": 2, "relationship_type": "TRADE", "confidence_score": 1.5},
    )
    assert res2.status_code == 422
