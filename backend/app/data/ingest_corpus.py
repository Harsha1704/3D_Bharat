"""
3D BHARAT — Archival Knowledge Corpus Ingestion Script
Phase 9.1: Verified Heritage Knowledge Corpus

Idempotently ingests authentic archival documents into PostgreSQL,
computes SHA-256 hashes, splits into semantic chunks with section headings,
and generates 384-dimensional vector embeddings via all-MiniLM-L6-v2.
"""

import sys
import logging
from typing import Dict, Any

from app.core.database import SessionLocal
from app.schemas.ai import AIDocumentIngestRequest
from app.services.ai_document_service import ingest_document, count_documents_and_chunks
from app.services.ai_embedding_service import is_embedding_ready
from app.data.archival_corpus import ARCHIVAL_CORPUS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("3d_bharat.ingest_corpus")


def run_ingestion() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        logger.info("Starting Archival Knowledge Corpus Ingestion...")
        logger.info("Embedding service ready: %s", is_embedding_ready())
        
        ingested_count = 0
        skipped_count = 0
        total_chunks_created = 0

        for doc_data in ARCHIVAL_CORPUS:
            req = AIDocumentIngestRequest(
                document_id=doc_data["document_id"],
                title=doc_data["title"],
                document_type=doc_data.get("document_type", "RESEARCH_REPORT"),
                source_url=doc_data.get("source_url"),
                publisher_institution=doc_data.get("publisher_institution"),
                author=doc_data.get("author"),
                publication_date=doc_data.get("publication_date"),
                text_content=doc_data["text_content"],
                permission_classification=doc_data.get("permission_classification", "OPEN_ACCESS_RESEARCH"),
                heritage_site_id=doc_data.get("heritage_site_id"),
            )

            try:
                doc = ingest_document(db, req)
                ingested_count += 1
                total_chunks_created += doc.total_chunks
                logger.info(
                    "Ingested document '%s' (ID: %s, chunks: %d, site: %s)",
                    doc.title,
                    doc.document_id,
                    doc.total_chunks,
                    doc.heritage_site_id,
                )
            except Exception as exc:
                logger.warning("Document '%s' could not be ingested: %s", doc_data["document_id"], exc)
                skipped_count += 1

        total_docs, total_chunks = count_documents_and_chunks(db)
        logger.info(
            "Ingestion completed: %d documents processed. Database now contains %d documents and %d chunks.",
            ingested_count,
            total_docs,
            total_chunks,
        )

        return {
            "ingested_count": ingested_count,
            "skipped_count": skipped_count,
            "total_documents_in_db": total_docs,
            "total_chunks_in_db": total_chunks,
        }
    finally:
        db.close()


if __name__ == "__main__":
    result = run_ingestion()
    print("INGESTION_SUMMARY:", result)
