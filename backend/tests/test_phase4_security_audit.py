import io
import os
import shutil
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.services.storage_service import StorageService

client = TestClient(app)


@pytest.fixture
def temp_storage():
    temp_dir = Path(tempfile.mkdtemp(prefix="3d_bharat_sec_storage_"))
    service = StorageService(root_dir=temp_dir)
    yield service
    shutil.rmtree(temp_dir, ignore_errors=True)


# =========================================================
# 1. COMPREHENSIVE FORMAT VALIDATION AUDIT (18 FORMATS)
# =========================================================

@pytest.mark.parametrize(
    "filename,sample_bytes,is_3d",
    [
        # Images & Documents
        ("photo.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00", False),
        ("photo.jpeg", b"\xff\xd8\xff\xdb\x00\x43", False),
        ("graphic.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR", False),
        ("picture.webp", b"RIFF\x20\x00\x00\x00WEBPVP8 ", False),
        ("scan_le.tif", b"II*\x00\x08\x00\x00\x00", False),
        ("scan_be.tiff", b"MM\x00*\x00\x00\x00\x08", False),
        ("record.pdf", b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n", False),
        # Audio & Video
        ("guide.mp3", b"ID3\x04\x00\x00\x00\x00\x00\x23TIT2", False),
        ("guide_sync.mp3", b"\xff\xfb\x90\x44\x00\x00", False),
        ("audio.wav", b"RIFF\x24\x08\x00\x00WAVEfmt ", False),
        ("audio.ogg", b"OggS\x00\x02\x00\x00\x00\x00", False),
        ("track.m4a", b"\x00\x00\x00\x20ftypM4A \x00\x00\x02\x00", False),
        ("video.mp4", b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00", False),
        ("video.webm", b"\x1a\x45\xdf\xa3\x9f\x42\x86\x81\x01", False),
        # 3D Digital Assets
        ("model.glb", b"glTF\x02\x00\x00\x00\x28\x00\x00\x00", True),
        ("model.gltf", b'{\n  "asset": {"version": "2.0"},\n  "scenes": []\n}', True),
        ("statue.obj", b"# Wavefront OBJ\nv 0.0 1.0 0.0\nv 1.0 0.0 0.0\nf 1 2 3\n", True),
        ("material.mtl", b"# Wavefront Material\nnewmtl Bronze\nKa 1.0 1.0 1.0\nKd 0.8 0.5 0.2\n", True),
        ("cloud.ply", b"ply\nformat ascii 1.0\nelement vertex 10\nend_header\n", True),
        ("splat.splat", b"\x00" * 64, True),
    ],
)
def test_valid_file_validation_for_all_formats(temp_storage, filename, sample_bytes, is_3d):
    """Verify that every supported format evaluates and accepts valid header data."""
    ext, mime = temp_storage.validate_file_content(filename, sample_bytes, is_3d=is_3d)
    assert filename.lower().endswith(ext)
    assert mime is not None


@pytest.mark.parametrize(
    "filename,corrupted_bytes,is_3d",
    [
        ("fake.jpg", b"NOT_A_JPEG_FILE", False),
        ("fake.png", b"GIF89a corrupted", False),
        ("fake.webp", b"RIFF1234NOTWEBP", False),
        ("fake.tif", b"NOT_TIFF_MAGIC", False),
        ("fake.pdf", b"DOCUMENT_NO_HEADER", False),
        ("fake.mp3", b"CORRUPT_AUDIO_STREAM", False),
        ("fake.wav", b"RIFF1234NOTWAV", False),
        ("fake.ogg", b"NOT_OGG_MAGIC", False),
        ("fake.mp4", b"NO_FTYP_BOX_HEADER", False),
        ("fake.webm", b"NO_EBML_HEADER", False),
        ("fake.glb", b"NOT_GLB_BINARY", True),
        ("fake.gltf", b"NOT_JSON_AT_ALL", True),
        ("fake.obj", b"just random binary non obj lines", True),
        ("fake.mtl", b"just random invalid mtl text", True),
        ("fake.ply", b"NOT_PLY_HEADER", True),
    ],
)
def test_corrupted_content_rejected(temp_storage, filename, corrupted_bytes, is_3d):
    """Verify that corrupted, spoofed, or non-conforming content is strictly rejected."""
    with pytest.raises(ValueError):
        temp_storage.validate_file_content(filename, corrupted_bytes, is_3d=is_3d)


# =========================================================
# 2. OBJ / glTF COMPANION FILE SECURITY & ISOLATION
# =========================================================

def test_companion_file_isolation_and_path_traversal(temp_storage):
    """Verify companion files cannot escape the asset directory or overwrite others."""
    # 1. Create primary 3D OBJ asset
    obj_content = b"# OBJ\nmtllib temple_mat.mtl\nv 0.0 0.0 0.0\nf 1 1 1\n"
    key, _, _, _ = temp_storage.save_file_stream(
        stream=io.BytesIO(obj_content),
        original_filename="temple.obj",
        category_dir="3d",
        site_id=1,
        is_3d=True,
    )

    # 2. Upload companion MTL file
    mtl_content = b"# MTL\nnewmtl Granite\nKa 0.2 0.2 0.2\n"
    comp_key, comp_name, size, _ = temp_storage.save_companion_file(
        parent_storage_key=key,
        companion_filename="../../evil_path.mtl",  # Traversal attempt
        stream=io.BytesIO(mtl_content),
    )

    # Path traversal should be stripped
    assert ".." not in comp_name
    assert comp_name == "evil_path.mtl"
    assert "/companions/" in comp_key

    # Absolute path must remain strictly inside companions subfolder
    abs_comp_path = temp_storage.get_absolute_path(comp_key)
    assert abs_comp_path.exists()
    assert abs_comp_path.parent.name == "companions"


def test_companion_verification_endpoint_workflow():
    """Verify OBJ companion detection via API verify endpoint."""
    # 1. Upload OBJ referencing a companion MTL
    obj_content = b"# Monument\nmtllib hampi_chariot.mtl\nv 1.0 1.0 1.0\nf 1 1 1\n"
    upload_res = client.post(
        "/api/v1/heritage-sites/1/3d-assets/upload",
        data={"title": "Hampi Chariot OBJ", "asset_format": "OBJ"},
        files={"file": ("hampi_chariot.obj", obj_content, "model/obj")},
    )
    assert upload_res.status_code == 201
    asset_id = upload_res.json()["id"]

    # 2. Check verify endpoint: should report INCOMPLETE with missing 'hampi_chariot.mtl'
    verify_res = client.get(f"/api/v1/heritage-3d-assets/{asset_id}/verify")
    assert verify_res.status_code == 200
    report = verify_res.json()
    assert report["status"] == "INCOMPLETE"
    assert "hampi_chariot.mtl" in report["missing_companions"]

    # 3. Upload the companion file
    mtl_content = b"newmtl GranitePillar\nKa 0.5 0.5 0.5\n"
    attach_res = client.post(
        f"/api/v1/heritage-3d-assets/{asset_id}/companions",
        files={"file": ("hampi_chariot.mtl", mtl_content, "text/plain")},
    )
    assert attach_res.status_code == 201

    # 4. Check verify endpoint again: now COMPLETE
    verify_res2 = client.get(f"/api/v1/heritage-3d-assets/{asset_id}/verify")
    assert verify_res2.status_code == 200
    report2 = verify_res2.json()
    assert report2["status"] == "COMPLETE"
    assert "hampi_chariot.mtl" in report2["found_companions"]
    assert len(report2["missing_companions"]) == 0

    # 5. Cleanup
    client.delete(f"/api/v1/heritage-3d-assets/{asset_id}")


# =========================================================
# 3. ACCESS CONTROL & PRODUCTION AUTHENTICATION GATE
# =========================================================

def test_production_write_protection_gate(monkeypatch):
    """In production mode, write endpoints require PRESERVATION_WRITE_API_KEY."""
    # Simulate production environment without API key configured
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", None)

    # Attempt write: should be locked with 503
    res = client.post(
        "/api/v1/heritage-sites/1/sources",
        json={"title": "Unauthenticated Source", "source_type": "ARCHIVAL_RECORD"},
    )
    assert res.status_code == 503
    assert "disabled in production" in res.json()["detail"]


def test_production_api_key_authentication(monkeypatch):
    """In production mode with API key configured, verifies X-API-Key and Bearer tokens."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "PRESERVATION_WRITE_API_KEY", "secret_preservation_key_789")

    payload = {"title": "Secure Source", "source_type": "ARCHIVAL_RECORD"}

    # 1. Missing header -> 401
    res1 = client.post("/api/v1/heritage-sites/1/sources", json=payload)
    assert res1.status_code == 401

    # 2. Wrong key -> 401
    res2 = client.post(
        "/api/v1/heritage-sites/1/sources",
        json=payload,
        headers={"X-API-Key": "wrong_key"},
    )
    assert res2.status_code == 401

    # 3. Correct X-API-Key -> 201
    res3 = client.post(
        "/api/v1/heritage-sites/1/sources",
        json=payload,
        headers={"X-API-Key": "secret_preservation_key_789"},
    )
    assert res3.status_code == 201
    source_id = res3.json()["id"]

    # 4. Correct Bearer token -> 200 (Delete)
    res4 = client.delete(
        f"/api/v1/heritage-sources/{source_id}",
        headers={"Authorization": "Bearer secret_preservation_key_789"},
    )
    assert res4.status_code == 200


# =========================================================
# 4. DATABASE & STORAGE TRANSACTION FAILURE SAFETY
# =========================================================

def test_storage_cleanup_on_database_commit_failure(temp_storage, monkeypatch):
    """Verify physical file is deleted if database insert fails."""
    from app.api.v1 import heritage_media

    # Monkeypatch create_heritage_media in router to raise an unexpected database error
    def faulty_create(*args, **kwargs):
        raise RuntimeError("Simulated Database Commit Crash")

    monkeypatch.setattr(heritage_media, "create_heritage_media", faulty_create)

    jpeg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"X" * 100
    files = {"file": ("crash_test.jpg", jpeg_data, "image/jpeg")}
    data = {"title": "Crash Test Image", "media_type": "ARCHIVAL_PHOTOGRAPH"}

    res = client.post("/api/v1/heritage-sites/1/media/upload", data=data, files=files)
    assert res.status_code == 400
    assert "Simulated Database Commit Crash" in res.json()["detail"]


def test_duplicate_storage_key_prevention():
    """Verify unique storage_key constraint prevents duplicate asset registration."""
    payload = {
        "title": "Unique Key Test 1",
        "media_type": "ARCHIVAL_PHOTOGRAPH",
        "storage_key": "media/site_1/fixed_unique_key.jpg",
        "original_filename": "fixed.jpg",
        "mime_type": "image/jpeg",
        "file_size_bytes": 1024,
        "checksum_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    }
    # First insert -> 201
    res1 = client.post("/api/v1/heritage-sites/1/media", json=payload)
    assert res1.status_code == 201
    media_id = res1.json()["id"]

    # Second insert with identical storage_key -> 409 Conflict
    res2 = client.post("/api/v1/heritage-sites/1/media", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]

    # Clean up
    client.delete(f"/api/v1/heritage-media/{media_id}")
