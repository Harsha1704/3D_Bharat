from typing import List, Optional
from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_write_access
from app.models.import_batch import ImportBatch
from app.schemas.import_batch import (
    ImportBatchResponse,
    ImportRecordSummary,
)
from app.services.ingestion.adapters import AsiMonumentsAdapter, UnescoIndiaAdapter
from app.services.ingestion.pipeline import HeritageIngestionPipeline
from app.services.ingestion.state_tracker import StateCoverageTracker

router = APIRouter(
    prefix="/heritage-ingestion",
    tags=["National Heritage Ingestion & Scalability"],
)

_tracker = StateCoverageTracker()


@router.get(
    "/batches",
    response_model=List[ImportBatchResponse],
    summary="List all national data ingestion batch logs",
)
def list_import_batches(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(ImportBatch).offset(skip).limit(limit).order_by(ImportBatch.id.desc())
    return list(db.execute(stmt).scalars().all())


@router.get(
    "/batches/{batch_id}",
    response_model=ImportBatchResponse,
    summary="Get details and error logs for an import batch",
)
def get_import_batch(
    batch_id: str,
    db: Session = Depends(get_db),
):
    batch = db.execute(
        select(ImportBatch).where(ImportBatch.batch_id == batch_id)
    ).scalar_one_or_none()

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Import batch '{batch_id}' not found.",
        )
    return batch


@router.get(
    "/state-tracker",
    summary="National State and Union Territory coverage tracker for all 36 Indian regions",
)
def get_state_coverage_tracker():
    return {
        "summary": _tracker.get_national_summary(),
        "states": _tracker.list_all_states(),
    }


@router.post(
    "/run-baseline/{source_type}",
    response_model=ImportRecordSummary,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(verify_write_access)],
    summary="Run national baseline ingestion for authentic verified sample (UNESCO or ASI)",
)
def run_baseline_ingestion(
    source_type: str,  # 'unesco' or 'asi'
    dry_run: bool = Query(default=False, description="Preview execution without writing to database"),
    db: Session = Depends(get_db),
):
    backend_data_dir = Path(__file__).resolve().parent.parent.parent / "data"

    if source_type.lower() == "unesco":
        file_path = backend_data_dir / "sample_unesco_india.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="UNESCO baseline data file missing.")
        adapter = UnescoIndiaAdapter(file_path)
        batch_id = "BATCH-UNESCO-INDIA-BASELINE-001"

    elif source_type.lower() == "asi":
        file_path = backend_data_dir / "sample_asi_monuments.csv"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="ASI baseline data file missing.")
        adapter = AsiMonumentsAdapter(file_path)
        batch_id = "BATCH-ASI-CENTRAL-BASELINE-001"

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported source_type. Valid options: 'unesco', 'asi'.",
        )

    pipeline = HeritageIngestionPipeline(db=db)
    return pipeline.execute_batch(
        batch_id=batch_id,
        adapter=adapter,
        dry_run=dry_run,
    )
