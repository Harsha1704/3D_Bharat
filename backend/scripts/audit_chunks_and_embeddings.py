"""
3D BHARAT — Chunk and Embedding Integrity Audit Script
Phase 9.1.1: Rigorous mathematical verification of all 225 chunks and embeddings.
"""

import hashlib
import json
import math
from typing import Dict, Any, List
import numpy as np

from app.core.database import SessionLocal
from app.models.ai_document import AIDocument, AIDocumentChunk, AIChunkEmbedding

def audit_chunks_and_embeddings() -> Dict[str, Any]:
    db = SessionLocal()
    try:
        docs = db.query(AIDocument).all()
        chunks = db.query(AIDocumentChunk).order_by(AIDocumentChunk.id).all()
        embeddings = db.query(AIChunkEmbedding).order_by(AIChunkEmbedding.id).all()

        chunk_ids = {c.id for c in chunks}
        doc_ids = {d.id for d in docs}
        emb_chunk_ids = {e.chunk_id for e in embeddings}

        defects = []

        # 1. Foreign-key & Orphan check
        orphaned_chunks = [c.id for c in chunks if c.document_id not in doc_ids]
        if orphaned_chunks:
            defects.append(f"Orphaned chunks (invalid document_id): {orphaned_chunks}")

        orphaned_embeddings = [e.id for e in embeddings if e.chunk_id not in chunk_ids]
        if orphaned_embeddings:
            defects.append(f"Orphaned embeddings (invalid chunk_id): {orphaned_embeddings}")

        chunks_without_embeddings = [c.id for c in chunks if c.id not in emb_chunk_ids]
        if chunks_without_embeddings:
            defects.append(f"Chunks missing embeddings: {chunks_without_embeddings}")

        # 2. Chunk sequence and uniqueness per document
        chunks_by_doc: Dict[int, List[AIDocumentChunk]] = {}
        for c in chunks:
            chunks_by_doc.setdefault(c.document_id, []).append(c)

        for doc_id, doc_chunks in chunks_by_doc.items():
            doc_chunks.sort(key=lambda x: x.chunk_index)
            expected_seq = list(range(len(doc_chunks)))
            actual_seq = [c.chunk_index for c in doc_chunks]
            if expected_seq != actual_seq:
                defects.append(f"Doc ID {doc_id}: Sequence mismatch. Expected {expected_seq}, got {actual_seq}")

            # Check duplicate texts
            seen_texts = set()
            for c in doc_chunks:
                t = c.chunk_text.strip()
                if not t:
                    defects.append(f"Chunk ID {c.id}: Empty chunk text.")
                if t in seen_texts:
                    defects.append(f"Doc ID {doc_id}, Chunk ID {c.id}: Duplicate chunk text.")
                seen_texts.add(t)

                # Recompute SHA-256
                calc_hash = hashlib.sha256(c.chunk_text.encode("utf-8")).hexdigest()
                if calc_hash != c.chunk_hash:
                    defects.append(f"Chunk ID {c.id}: Checksum mismatch. Calculated {calc_hash}, stored {c.chunk_hash}")

        # 3. Embedding Vector Inspection
        embedding_by_chunk = {e.chunk_id: e for e in embeddings}
        invalid_dim_count = 0
        non_finite_count = 0
        unnormalized_count = 0
        norms = []

        for e in embeddings:
            vec = e.embedding_json
            if not isinstance(vec, list) or len(vec) != 384:
                invalid_dim_count += 1
                defects.append(f"Embedding ID {e.id}: Invalid dimension {len(vec) if isinstance(vec, list) else type(vec)} (expected 384).")
                continue

            arr = np.array(vec, dtype=np.float32)
            if not np.all(np.isfinite(arr)):
                non_finite_count += 1
                defects.append(f"Embedding ID {e.id}: Non-finite vector values (NaN or Inf).")

            norm = float(np.linalg.norm(arr))
            norms.append(norm)
            if abs(norm - 1.0) > 1e-3:
                unnormalized_count += 1
                defects.append(f"Embedding ID {e.id}: Vector not L2 normalized (norm={norm:.6f}).")

        avg_norm = float(np.mean(norms)) if norms else 0.0
        min_norm = float(np.min(norms)) if norms else 0.0
        max_norm = float(np.max(norms)) if norms else 0.0

        summary = {
            "total_documents": len(docs),
            "total_chunks": len(chunks),
            "total_embeddings": len(embeddings),
            "unique_chunks_with_embedding": len(emb_chunk_ids),
            "orphaned_chunks": len(orphaned_chunks),
            "orphaned_embeddings": len(orphaned_embeddings),
            "chunks_missing_embeddings": len(chunks_without_embeddings),
            "invalid_dimensions_count": invalid_dim_count,
            "non_finite_vectors_count": non_finite_count,
            "unnormalized_vectors_count": unnormalized_count,
            "vector_norms_summary": {
                "mean_l2_norm": round(avg_norm, 6),
                "min_l2_norm": round(min_norm, 6),
                "max_l2_norm": round(max_norm, 6),
            },
            "embedding_model_recorded": embeddings[0].embedding_model if embeddings else None,
            "defects_count": len(defects),
            "defects_list": defects,
            "integrity_status": "PASS" if len(defects) == 0 else "FAIL",
        }
        return summary
    finally:
        db.close()

if __name__ == "__main__":
    report = audit_chunks_and_embeddings()
    print("CHUNK_EMBEDDING_AUDIT_REPORT:")
    print(json.dumps(report, indent=2))
