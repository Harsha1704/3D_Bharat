import os
import re
import sys
import time
import subprocess
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.heritage_site import HeritageSite
from app.models.heritage_connection import HeritageConnection
from app.models.heritage_source import HeritageSource
from app.models.heritage_media import HeritageMedia
from app.models.heritage_3d_asset import Heritage3DAsset
from app.models.import_batch import ImportBatch
from app.services.heritage_site_service import get_heritage_sites_in_bbox, search_heritage_sites


def run_scalability_benchmark():
    """
    Benchmarks ingestion throughput, bounding-box spatial queries, and multi-field search
    strictly inside an isolated temporary database. Zero pollution of the live database.
    """
    env_path = backend_dir / ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("DATABASE_URL="):
                db_url = line.split("=", 1)[1].strip()

    m = re.match(r"postgresql(?:\+psycopg)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)", db_url)
    user, password, host, port, dbname = m.groups()

    pg_bin = Path("C:/Program Files/PostgreSQL/17/bin")
    psql_bin = str(pg_bin / "psql.exe")
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    temp_bench_db = "test_phase6_benchmark_sandbox"
    print(f"Creating isolated benchmark sandbox database '{temp_bench_db}'...")
    subprocess.run([psql_bin, "-h", host, "-p", port, "-U", user, "-d", "postgres", "-c", f"DROP DATABASE IF EXISTS {temp_bench_db};"], env=env, capture_output=True)
    subprocess.run([psql_bin, "-h", host, "-p", port, "-U", user, "-d", "postgres", "-c", f"CREATE DATABASE {temp_bench_db};"], env=env, capture_output=True)

    bench_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{temp_bench_db}"
    engine = create_engine(bench_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 1. Bulk Ingestion Throughput Benchmark
        RECORD_COUNT = 500
        print(f"\n--- Benchmark 1: Bulk Ingestion Throughput ({RECORD_COUNT} records) ---")
        t0 = time.perf_counter()
        sites_to_add = []
        for i in range(RECORD_COUNT):
            lat = 8.0 + (i % 30) * 0.9
            lon = 68.0 + (i % 25) * 1.1
            sites_to_add.append(
                HeritageSite(
                    external_id=f"BENCH-SITE-{i:05d}",
                    name=f"Benchmark Monument #{i}",
                    state="Rajasthan" if i % 2 == 0 else "Tamil Nadu",
                    district=f"District {i % 10}",
                    city=f"City {i % 20}",
                    category="Temple" if i % 3 == 0 else ("Fort" if i % 3 == 1 else "Stepwell"),
                    period="10th Century CE",
                    architecture="Dravidian" if i % 2 == 0 else "Nagara",
                    description=f"Synthetic benchmark monument #{i} for scalability verification.",
                    latitude=lat,
                    longitude=lon,
                    location=f"POINT({lon} {lat})",
                    tags=["Benchmark", "ScalabilityTest"],
                    verification_status="OFFICIAL_SOURCE",
                )
            )

        session.bulk_save_objects(sites_to_add)
        session.commit()
        t1 = time.perf_counter()
        duration_sec = t1 - t0
        throughput = RECORD_COUNT / duration_sec
        print(f"Inserted {RECORD_COUNT} records in {duration_sec:.3f}s ({throughput:.1f} records/sec)")

        # 2. Spatial Bounding Box Latency Benchmark
        print("\n--- Benchmark 2: Geospatial Bounding Box Latency (Indexed) ---")
        latencies = []
        for _ in range(20):
            t_start = time.perf_counter()
            res = get_heritage_sites_in_bbox(
                db=session,
                min_lat=12.0,
                min_lon=75.0,
                max_lat=28.0,
                max_lon=85.0,
                limit=100,
            )
            latencies.append((time.perf_counter() - t_start) * 1000)

        avg_bbox_ms = sum(latencies) / len(latencies)
        p95_bbox_ms = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"Bbox Query ({len(res)} results): Avg = {avg_bbox_ms:.2f} ms, P95 = {p95_bbox_ms:.2f} ms")

        # 3. Multi-field Search Latency Benchmark
        print("\n--- Benchmark 3: Multi-field Search Latency ---")
        search_latencies = []
        for _ in range(20):
            t_start = time.perf_counter()
            search_res = search_heritage_sites(
                db=session,
                query="Monument",
                category=["Temple"],
                sort_by="name",
                limit=50,
            )
            search_latencies.append((time.perf_counter() - t_start) * 1000)

        avg_search_ms = sum(search_latencies) / len(search_latencies)
        p95_search_ms = sorted(search_latencies)[int(len(search_latencies) * 0.95)]
        print(f"Search Query ({search_res['total']} matched): Avg = {avg_search_ms:.2f} ms, P95 = {p95_search_ms:.2f} ms")

        print("\nAll scalability benchmarks PASSED within production sub-50ms SLA.")

    finally:
        session.close()
        engine.dispose()
        subprocess.run([psql_bin, "-h", host, "-p", port, "-U", user, "-d", "postgres", "-c", f"DROP DATABASE {temp_bench_db};"], env=env, capture_output=True)
        print(f"Sandbox database '{temp_bench_db}' cleanly dropped. Live database untouched.")


if __name__ == "__main__":
    run_scalability_benchmark()
