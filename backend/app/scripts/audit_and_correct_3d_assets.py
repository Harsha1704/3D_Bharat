"""
3D BHARAT - Phase 10.1 Database Correction Script
Corrects provenance, origin classification, and licensing metadata for the pilot asset,
and isolates test fixture records to PRIVATE visibility.
"""
from sqlalchemy import select, update
from app.core.database import SessionLocal
from app.models.heritage_3d_asset import Heritage3DAsset


def run_corrections():
    db = SessionLocal()
    try:
        # 1. Update Pilot Asset (Konark Sun Temple - Site ID 3)
        pilot = db.execute(
            select(Heritage3DAsset).where(Heritage3DAsset.is_pilot == True)
        ).scalar_one_or_none()

        if not pilot:
            pilot = db.execute(
                select(Heritage3DAsset).where(Heritage3DAsset.heritage_site_id == 3)
            ).scalars().first()

        if pilot:
            print(f"Updating Pilot Asset (ID: {pilot.id})...")
            pilot.asset_origin = "ARCHITECTURAL_VISUALIZATION"
            pilot.rights_status = "RIGHTS_REVIEW_REQUIRED"
            pilot.licence_name = "RIGHTS_REVIEW_PENDING"
            pilot.licence_url = None
            pilot.commercial_use_allowed = False
            pilot.modification_allowed = False
            pilot.redistribution_allowed = False
            pilot.creator = "3D BHARAT Computational Heritage Studio (Procedural Generator)"
            pilot.publisher = "3D BHARAT National Heritage Intelligence Platform"
            pilot.attribution_text = (
                "Konark Sun Temple procedural architectural visualization synthesized via "
                "3D BHARAT geometry engine. Geometry based on canonical Kalinga deula treatise "
                "proportions. Institutional rights and public redistribution under review. "
                "Permitted for in-browser visual inspection only."
            )
            pilot.description = (
                "Procedural 3D architectural visualization of the Konark Sun Temple (Surya Deula), "
                "programmatically synthesized from Kalinga architectural canons (stepped pyramidal "
                "Jagamohana with 4 pidha tiers, 24 cosmic chariot wheels, crowning fluted amalaka stone, "
                "and golden kalasha finial). Internal synthetic research visualization."
            )
            pilot.visibility_status = "PUBLIC"
            pilot.validation_status = "READY"
            pilot.is_pilot = True
            print("Pilot asset updated with verified provenance and rights-review classification.")

        # 2. Isolate all test fixtures (Hampi Test Shrine Model)
        test_fixtures = db.execute(
            select(Heritage3DAsset).where(Heritage3DAsset.title.ilike("%Test%"))
        ).scalars().all()

        for tf in test_fixtures:
            print(f"Isolating Test Fixture (ID: {tf.id}, Title: {tf.title})...")
            tf.visibility_status = "PRIVATE"
            tf.validation_status = "TEST_FIXTURE"
            tf.is_pilot = False
            tf.redistribution_allowed = False

        db.commit()
        print("All database corrections committed successfully.")

        # 3. Print verification summary
        all_assets = db.execute(
            select(Heritage3DAsset).order_by(Heritage3DAsset.id)
        ).scalars().all()
        print("\n--- Verified 3D Asset Records Post-Correction ---")
        for a in all_assets:
            print(
                f"ID={a.id} site={a.heritage_site_id} title={a.title[:30]!r} "
                f"origin={a.asset_origin} lic={a.licence_name} rights={a.rights_status} "
                f"vis={a.visibility_status} redis={a.redistribution_allowed} pilot={a.is_pilot}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    run_corrections()
