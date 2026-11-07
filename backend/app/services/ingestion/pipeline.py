from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.heritage_site import HeritageSite
from app.models.heritage_source import HeritageSource
from app.models.import_batch import ImportBatch
from app.schemas.import_batch import ImportRecordSummary
from app.services.ingestion.adapters import BaseSourceAdapter
from app.services.ingestion.duplicate_detector import DuplicateDetector, MatchStatus

logger = logging.getLogger("3d_bharat.ingestion")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HeritageIngestionPipeline:
    """
    Robust, idempotent, transaction-safe national heritage data ingestion pipeline.
    Maintains complete provenance, audit trails, and strict data quality gates.
    """

    def __init__(self, db: Session, batch_size: int = 100):
        self.db = db
        self.batch_size = batch_size
        self.detector = DuplicateDetector(db)

    def execute_batch(
        self,
        batch_id: str,
        adapter: BaseSourceAdapter,
        dry_run: bool = False,
    ) -> ImportRecordSummary:
        """
        Executes ingestion for a given source adapter.
        Guarantees idempotency and transaction boundaries.
        """
        # Find or create ImportBatch audit record
        batch_record = self.db.execute(
            select(ImportBatch).where(ImportBatch.batch_id == batch_id)
        ).scalar_one_or_none()

        if not batch_record:
            batch_record = ImportBatch(
                batch_id=batch_id,
                source_organization=adapter.source_organization,
                source_dataset=adapter.source_name,
                source_url=adapter.source_url,
                license=adapter.license,
                status="IN_PROGRESS",
                created_at=utcnow(),
            )
            self.db.add(batch_record)
            self.db.commit()
            self.db.refresh(batch_record)
        else:
            batch_record.status = "IN_PROGRESS"
            self.db.commit()

        total_count = 0
        accepted_count = 0
        rejected_count = 0
        duplicate_count = 0
        updated_count = 0
        inserted_count = 0
        errors: List[str] = []

        try:
            for raw_record in adapter.load_records():
                total_count += 1
                name = raw_record.get("name")
                state = raw_record.get("state")

                # Quality Gate 1: Required Name
                if not name or not name.strip():
                    rejected_count += 1
                    err = f"Record #{total_count} rejected: monument name is empty"
                    errors.append(err)
                    continue

                # Quality Gate 2: Required State
                if not state or not state.strip() or state == "Unknown":
                    rejected_count += 1
                    err = f"Record #{total_count} ('{name}') rejected: missing or invalid state"
                    errors.append(err)
                    continue

                # Check duplicate status
                match_status, matched_site, explanation = self.detector.check_duplicate(
                    external_id=raw_record.get("external_id", ""),
                    name=name,
                    state=state,
                    latitude=raw_record.get("latitude"),
                    longitude=raw_record.get("longitude"),
                )

                if match_status == MatchStatus.EXACT_MATCH and matched_site:
                    duplicate_count += 1
                    # Cautious augmentation: preserve manual/official edits, merge new alternative names if present
                    was_updated = False
                    new_alt = raw_record.get("alternative_names") or []
                    if new_alt:
                        existing_alts = list(matched_site.alternative_names or [])
                        for a in new_alt:
                            if a not in existing_alts:
                                existing_alts.append(a)
                                was_updated = True
                        if was_updated:
                            matched_site.alternative_names = existing_alts

                    # If existing had missing coordinates, and new has valid coords, augment safely
                    if matched_site.latitude is None and raw_record.get("latitude") is not None:
                        matched_site.latitude = raw_record.get("latitude")
                        matched_site.longitude = raw_record.get("longitude")
                        matched_site.location = f"POINT({raw_record.get('longitude')} {raw_record.get('latitude')})"
                        was_updated = True

                    if was_updated:
                        updated_count += 1
                        matched_site.last_verified_at = utcnow()
                        if not dry_run:
                            self.db.commit()

                elif match_status == MatchStatus.AMBIGUOUS_MATCH and matched_site:
                    # Ambiguous match: Flag for manual review rather than merging or creating a duplicate
                    rejected_count += 1
                    err = f"Record #{total_count} ('{name}', {state}) flagged for manual review: {explanation}"
                    errors.append(err)

                else:
                    # Distinct, new monument record
                    accepted_count += 1
                    inserted_count += 1

                    if not dry_run:
                        lat = raw_record.get("latitude")
                        lon = raw_record.get("longitude")
                        location = f"POINT({lon} {lat})" if (lat is not None and lon is not None) else None

                        new_site = HeritageSite(
                            external_id=raw_record["external_id"],
                            name=name,
                            alternative_names=raw_record.get("alternative_names"),
                            state=state,
                            district=raw_record.get("district"),
                            city=raw_record.get("city"),
                            category=raw_record.get("category", "Monument"),
                            period=raw_record.get("period"),
                            dynasty=raw_record.get("dynasty"),
                            construction_year=raw_record.get("construction_year"),
                            architecture=raw_record.get("architecture"),
                            description=raw_record.get("description", f"{name} is an important heritage structure in {state}."),
                            significance=raw_record.get("significance"),
                            latitude=lat,
                            longitude=lon,
                            location=location,
                            tags=raw_record.get("tags"),
                            associated_people=raw_record.get("associated_people"),
                            historical_events=raw_record.get("historical_events"),
                            traditions=raw_record.get("traditions"),
                            verification_status=raw_record.get("verification_status", "OFFICIAL_SOURCE"),
                            batch_id=batch_id,
                            source_reference=raw_record.get("source_reference", adapter.source_name),
                            last_verified_at=utcnow(),
                        )
                        self.db.add(new_site)
                        self.db.flush()

                        # Register official provenance citation in heritage_sources
                        source_entry = HeritageSource(
                            heritage_site_id=new_site.id,
                            title=f"National Inventory Registration: {adapter.source_name}",
                            source_type="ARCHAEOLOGICAL_SURVEY",
                            institution=adapter.source_organization,
                            url=adapter.source_url,
                            license=adapter.license,
                            citation=f"{adapter.source_organization} official documentation. Batch: {batch_id}",
                            verification_status="VERIFIED",
                        )
                        self.db.add(source_entry)
                        self.db.commit()

            # Finalize Batch
            if not dry_run:
                batch_record.total_records = total_count
                batch_record.accepted_records = accepted_count
                batch_record.rejected_records = rejected_count
                batch_record.duplicate_records = duplicate_count
                batch_record.updated_records = updated_count
                batch_record.inserted_records = inserted_count
                batch_record.error_log = json.dumps(errors[:100]) if errors else None
                batch_record.status = "COMPLETED"
                batch_record.completed_at = utcnow()
                self.db.commit()

        except Exception as exc:
            self.db.rollback()
            batch_record.status = "FAILED"
            batch_record.error_log = json.dumps([str(exc)])
            self.db.commit()
            raise RuntimeError(f"Ingestion batch {batch_id} failed: {exc}")

        return ImportRecordSummary(
            batch_id=batch_id,
            organization=adapter.source_organization,
            dataset=adapter.source_name,
            total_records=total_count,
            inserted_records=inserted_count,
            updated_records=updated_count,
            duplicate_records=duplicate_count,
            rejected_records=rejected_count,
            errors=errors,
        )
