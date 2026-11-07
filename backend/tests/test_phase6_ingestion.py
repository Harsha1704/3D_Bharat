import io
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.models.import_batch import ImportBatch
from app.services.ingestion.normalizer import (
    normalize_category,
    normalize_name,
    normalize_state,
    validate_coordinates,
)
from app.services.ingestion.adapters import (
    AsiMonumentsAdapter,
    CsvSourceAdapter,
    JsonSourceAdapter,
    UnescoIndiaAdapter,
)
from app.services.ingestion.duplicate_detector import DuplicateDetector, MatchStatus
from app.services.ingestion.pipeline import HeritageIngestionPipeline
from app.services.ingestion.state_tracker import StateCoverageTracker

client = TestClient(app)


# =========================================================
# 1. NORMALIZER UNIT TESTS
# =========================================================

def test_normalize_state_mappings():
    assert normalize_state("Orissa") == "Odisha"
    assert normalize_state("orissa") == "Odisha"
    assert normalize_state("Pondicherry") == "Puducherry"
    assert normalize_state("Uttaranchal") == "Uttarakhand"
    assert normalize_state("NCT of Delhi") == "Delhi"
    assert normalize_state("Jammu & Kashmir") == "Jammu and Kashmir"
    assert normalize_state("") == "Unknown"
    assert normalize_state(None) == "Unknown"


def test_normalize_name_cleaning():
    assert normalize_name("  TAJ MAHAL  ") == "Taj Mahal"
    assert normalize_name("--Qutb Minar,") == "Qutb Minar"
    assert normalize_name("Brihadisvara    Temple") == "Brihadisvara Temple"
    assert normalize_name("") == ""
    assert normalize_name(None) == ""


def test_normalize_category_synonyms():
    assert normalize_category("Hindu Mandir") == "Temple"
    assert normalize_category("Ancient Fort and Citadel") == "Fort"
    assert normalize_category("Rock-cut Caves") == "Cave"
    assert normalize_category("Subterranean Stepwell") == "Stepwell"
    assert normalize_category("Royal Palace") == "Palace"
    assert normalize_category("Historical Mosque") == "Mosque"
    assert normalize_category("Buddhist Stupa") == "Stupa"
    assert normalize_category("") == "Monument"
    assert normalize_category(None) == "Monument"


def test_validate_coordinates():
    # Valid coordinates in India
    lat, lon, warn = validate_coordinates(27.1751, 78.0421)
    assert lat == 27.1751
    assert lon == 78.0421
    assert warn is None

    # Missing coordinates handled cleanly
    lat, lon, warn = validate_coordinates(None, None)
    assert lat is None
    assert lon is None
    assert warn is None

    # Invalid string coordinates
    lat, lon, warn = validate_coordinates("invalid", "coords")
    assert lat is None
    assert "could not be parsed" in warn

    # Out of WGS84 range
    lat, lon, warn = validate_coordinates(120.0, 78.0)
    assert lat is None
    assert "out of WGS84 range" in warn

    # Valid WGS84 but outside India territory
    lat, lon, warn = validate_coordinates(51.5074, -0.1278)  # London
    assert lat == 51.5074
    assert lon == -0.1278
    assert "outside India's geographic territory" in warn


# =========================================================
# 2. ADAPTERS UNIT TESTS
# =========================================================

def test_csv_adapter_parsing():
    csv_content = io.StringIO(
        "name,state,latitude,longitude,category,period\n"
        "Golconda Fort,Telangana,17.3833,78.4011,Fort,16th Century CE\n"
    )
    adapter = CsvSourceAdapter(
        file_path_or_content=csv_content,
        source_name="Test CSV Source",
        source_organization="Test Org",
    )
    records = list(adapter.load_records())
    assert len(records) == 1
    rec = records[0]
    assert rec["name"] == "Golconda Fort"
    assert rec["state"] == "Telangana"
    assert rec["category"] == "Fort"
    assert rec["latitude"] == 17.3833
    assert rec["longitude"] == 78.4011


def test_json_adapter_parsing():
    json_data = [
        {
            "name": "Ajanta Caves",
            "state": "Maharashtra",
            "latitude": 20.5519,
            "longitude": 75.7033,
            "category": "Cave",
        }
    ]
    adapter = JsonSourceAdapter(
        file_path_or_content=json_data,
        source_name="Test JSON Source",
        source_organization="Test Org",
    )
    records = list(adapter.load_records())
    assert len(records) == 1
    assert records[0]["name"] == "Ajanta Caves"
    assert records[0]["state"] == "Maharashtra"


def test_unesco_adapter_enrichment():
    data = [
        {
            "whc_id": "242",
            "name": "Taj Mahal",
            "state": "Uttar Pradesh",
            "latitude": 27.1751,
            "longitude": 78.0421,
        }
    ]
    adapter = UnescoIndiaAdapter(data)
    records = list(adapter.load_records())
    assert len(records) == 1
    assert records[0]["external_id"] == "UNESCO-WHC-242"
    assert records[0]["source_reference"] == "UNESCO World Heritage Property #242"
    assert records[0]["verification_status"] == "OFFICIAL_SOURCE"


def test_asi_adapter_enrichment():
    csv_content = io.StringIO(
        "asi_id,monument_name,state,latitude,longitude,circle\n"
        "ASI-CHITTOR-01,Chittorgarh Fort,Rajasthan,24.8887,74.6269,Jaipur Circle\n"
    )
    adapter = AsiMonumentsAdapter(csv_content)
    records = list(adapter.load_records())
    assert len(records) == 1
    assert records[0]["external_id"] == "ASI-ASI-CHITTOR-01"
    assert "ASI Circle: Jaipur Circle" in records[0]["tags"]
    assert records[0]["verification_status"] == "OFFICIAL_SOURCE"


# =========================================================
# 3. DUPLICATE DETECTOR UNIT TESTS
# =========================================================

def test_duplicate_detector_exact_external_id():
    db: Session = SessionLocal()
    try:
        detector = DuplicateDetector(db)
        # ASI_TAJ_009 is an existing site
        status, site, expl = detector.check_duplicate(
            external_id="ASI_TAJ_009",
            name="Different Name",
            state="Different State",
        )
        assert status == MatchStatus.EXACT_MATCH
        assert site is not None
        assert site.external_id == "ASI_TAJ_009"
    finally:
        db.close()


def test_duplicate_detector_exact_name_and_state():
    db: Session = SessionLocal()
    try:
        detector = DuplicateDetector(db)
        status, site, expl = detector.check_duplicate(
            external_id="NEW_ID_9999",
            name="Taj Mahal",
            state="Uttar Pradesh",
        )
        assert status == MatchStatus.EXACT_MATCH
        assert site is not None
        assert site.name == "Taj Mahal"
    finally:
        db.close()


def test_duplicate_detector_no_match():
    db: Session = SessionLocal()
    try:
        detector = DuplicateDetector(db)
        status, site, expl = detector.check_duplicate(
            external_id="UNIQUE_EXT_ID_12345",
            name="Completely Unique Monument XYZ",
            state="Kerala",
        )
        assert status == MatchStatus.NO_MATCH
        assert site is None
    finally:
        db.close()


# =========================================================
# 4. PIPELINE EXECUTION & IDEMPOTENCY TESTS
# =========================================================

def test_pipeline_dry_run_does_not_mutate_db():
    db: Session = SessionLocal()
    try:
        sites_before = db.execute(text("SELECT count(*) FROM heritage_sites")).scalar()

        json_data = [
            {
                "name": "Dry Run Test Monument",
                "state": "Gujarat",
                "latitude": 23.0,
                "longitude": 72.0,
                "category": "Temple",
            }
        ]
        adapter = JsonSourceAdapter(
            file_path_or_content=json_data,
            source_name="Dry Run Test",
            source_organization="Test Org",
        )
        pipeline = HeritageIngestionPipeline(db)
        summary = pipeline.execute_batch(
            batch_id="TEST-BATCH-DRY-RUN",
            adapter=adapter,
            dry_run=True,
        )

        sites_after = db.execute(text("SELECT count(*) FROM heritage_sites")).scalar()
        assert sites_before == sites_after
        assert summary.inserted_records == 1
    finally:
        db.close()


def test_pipeline_rejects_empty_monument_name():
    db: Session = SessionLocal()
    try:
        json_data = [
            {
                "name": "",  # Empty name
                "state": "Karnataka",
            }
        ]
        adapter = JsonSourceAdapter(
            file_path_or_content=json_data,
            source_name="Empty Name Test",
            source_organization="Test Org",
        )
        pipeline = HeritageIngestionPipeline(db)
        summary = pipeline.execute_batch(
            batch_id="TEST-BATCH-EMPTY-NAME",
            adapter=adapter,
            dry_run=True,
        )
        assert summary.rejected_records == 1
        assert "monument name is empty" in summary.errors[0]
    finally:
        db.close()


def test_pipeline_idempotency_rerun_safe():
    """
    Running a batch twice must not insert duplicate monuments on the second pass.
    """
    db: Session = SessionLocal()
    test_ext_id = "TEST-IDEMPOTENT-001"
    try:
        # Cleanup if leftover from earlier run
        db.execute(text(f"DELETE FROM heritage_sites WHERE external_id = '{test_ext_id}'"))
        db.execute(text("DELETE FROM import_batches WHERE batch_id = 'BATCH-TEST-IDEMPOTENCY'"))
        db.commit()

        json_data = [
            {
                "external_id": test_ext_id,
                "name": "Idempotent Test Stupa",
                "state": "Madhya Pradesh",
                "latitude": 23.5500,
                "longitude": 77.8000,
                "category": "Stupa",
                "alternative_names": ["Test Stupa Alt 1"],
            }
        ]
        adapter = JsonSourceAdapter(
            file_path_or_content=json_data,
            source_name="Idempotency Test Source",
            source_organization="Idempotency Test Org",
        )
        pipeline = HeritageIngestionPipeline(db)

        # First run: inserts record
        summary1 = pipeline.execute_batch("BATCH-TEST-IDEMPOTENCY", adapter, dry_run=False)
        assert summary1.inserted_records == 1
        assert summary1.duplicate_records == 0

        # Second run: detects duplicate, 0 new rows inserted
        summary2 = pipeline.execute_batch("BATCH-TEST-IDEMPOTENCY", adapter, dry_run=False)
        assert summary2.inserted_records == 0
        assert summary2.duplicate_records == 1

    finally:
        # Clean up test artifact
        db.execute(text(f"DELETE FROM heritage_sites WHERE external_id = '{test_ext_id}'"))
        db.execute(text("DELETE FROM import_batches WHERE batch_id = 'BATCH-TEST-IDEMPOTENCY'"))
        db.commit()
        db.close()


def test_pipeline_preserves_manually_verified_records():
    """
    If a record already exists with OFFICIAL_SOURCE status, an incoming batch
    cannot overwrite its core attributes with weaker data.
    """
    db: Session = SessionLocal()
    test_ext_id = "TEST-PRESERVE-001"
    try:
        # Seed an official site
        site = HeritageSite(
            external_id=test_ext_id,
            name="Official Royal Palace",
            state="Rajasthan",
            category="Palace",
            description="Verified official archival description.",
            verification_status="OFFICIAL_SOURCE",
        )
        db.add(site)
        db.commit()

        # Attempt to ingest duplicate with lower quality description
        json_data = [
            {
                "external_id": test_ext_id,
                "name": "Official Royal Palace",
                "state": "Rajasthan",
                "description": "Short unverified description.",
                "alternative_names": ["New Local Palace Name"],
            }
        ]
        adapter = JsonSourceAdapter(
            file_path_or_content=json_data,
            source_name="Weaker Test Source",
            source_organization="Test Org",
        )
        pipeline = HeritageIngestionPipeline(db)
        summary = pipeline.execute_batch("BATCH-TEST-PRESERVE", adapter, dry_run=False)

        assert summary.duplicate_records == 1
        assert summary.inserted_records == 0

        # Check that original description is strictly preserved!
        refreshed = db.execute(
            select(HeritageSite).where(HeritageSite.external_id == test_ext_id)
        ).scalar_one()
        assert refreshed.description == "Verified official archival description."
        # Check that alternative names were safely augmented
        assert "New Local Palace Name" in refreshed.alternative_names

    finally:
        db.execute(text(f"DELETE FROM heritage_sites WHERE external_id = '{test_ext_id}'"))
        db.execute(text("DELETE FROM import_batches WHERE batch_id = 'BATCH-TEST-PRESERVE'"))
        db.commit()
        db.close()


# =========================================================
# 5. STATE TRACKER UNIT TESTS
# =========================================================

def test_state_coverage_tracker():
    tracker = StateCoverageTracker()
    all_states = tracker.list_all_states()
    assert len(all_states) == 36  # 28 States + 8 Union Territories

    delhi = tracker.get_state("Delhi")
    assert delhi is not None
    assert delhi.region == "Northern"

    summary = tracker.get_national_summary()
    assert summary["total_states_and_uts"] == 36
    assert summary["total_estimated_national_monuments"] > 3000
    assert summary["national_state_coverage_pct"] > 0


# =========================================================
# 6. INGESTION API ENDPOINTS TESTS
# =========================================================

def test_api_state_tracker_endpoint():
    response = client.get("/api/v1/heritage-ingestion/state-tracker")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "states" in data
    assert len(data["states"]) == 36


def test_api_batches_endpoint():
    response = client.get("/api/v1/heritage-ingestion/batches")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_api_run_baseline_dry_run():
    response = client.post("/api/v1/heritage-ingestion/run-baseline/unesco?dry_run=true")
    assert response.status_code == 200
    data = response.json()
    assert data["batch_id"] == "BATCH-UNESCO-INDIA-BASELINE-001"
    assert data["total_records"] > 0


def test_api_run_baseline_invalid_source():
    response = client.post("/api/v1/heritage-ingestion/run-baseline/unknown_archive")
    assert response.status_code == 400
    assert "Unsupported source_type" in response.json()["detail"]
