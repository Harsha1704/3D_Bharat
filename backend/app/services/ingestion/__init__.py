"""
National Indian Heritage Data Ingestion and Batch Scalability Package
"""
from app.services.ingestion.normalizer import (
    normalize_state,
    normalize_name,
    validate_coordinates,
    normalize_category,
)
from app.services.ingestion.adapters import (
    BaseSourceAdapter,
    CsvSourceAdapter,
    JsonSourceAdapter,
    UnescoIndiaAdapter,
    AsiMonumentsAdapter,
)
from app.services.ingestion.duplicate_detector import (
    DuplicateDetector,
    MatchStatus,
)
from app.services.ingestion.state_tracker import StateCoverageTracker
from app.services.ingestion.pipeline import HeritageIngestionPipeline

__all__ = [
    "normalize_state",
    "normalize_name",
    "validate_coordinates",
    "normalize_category",
    "BaseSourceAdapter",
    "CsvSourceAdapter",
    "JsonSourceAdapter",
    "UnescoIndiaAdapter",
    "AsiMonumentsAdapter",
    "DuplicateDetector",
    "MatchStatus",
    "StateCoverageTracker",
    "HeritageIngestionPipeline",
]
