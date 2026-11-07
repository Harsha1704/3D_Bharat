import hashlib
import logging
from typing import List, Optional
import numpy as np

from app.core.config import settings

logger = logging.getLogger("3d_bharat.ai_embedding")

_embedding_model = None
_model_failed = False


def get_embedding_model():
    """
    Lazy load SentenceTransformer model to optimize startup time and memory.
    """
    global _embedding_model, _model_failed
    if _embedding_model is not None:
        return _embedding_model
    if _model_failed:
        return None

    try:
        from sentence_transformers import SentenceTransformer
        model_name = settings.AI_EMBEDDING_MODEL or "all-MiniLM-L6-v2"
        _embedding_model = SentenceTransformer(model_name)
        logger.info("SentenceTransformer model '%s' loaded successfully.", model_name)
        return _embedding_model
    except Exception as exc:
        _model_failed = True
        logger.warning("Could not initialize SentenceTransformer (%s): %s", settings.AI_EMBEDDING_MODEL, exc)
        return None


def is_embedding_ready() -> bool:
    return get_embedding_model() is not None


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate normalized 384-d vector embedding for a single text chunk.
    """
    model = get_embedding_model()
    if model is None:
        return None

    cleaned_text = text.strip()
    if not cleaned_text:
        return None

    try:
        embedding = model.encode(cleaned_text, normalize_embeddings=True)
        return [float(x) for x in embedding]
    except Exception as exc:
        logger.error("Error generating text embedding: %s", exc)
        return None


def generate_batch_embeddings(texts: List[str]) -> List[Optional[List[float]]]:
    """
    Batch generation for efficiency.
    """
    model = get_embedding_model()
    if model is None or not texts:
        return [None] * len(texts)

    try:
        embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
        return [[float(x) for x in emb] for emb in embeddings]
    except Exception as exc:
        logger.error("Error in batch embedding: %s", exc)
        return [None] * len(texts)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two normalized vectors.
    """
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    a = np.array(vec1, dtype=np.float32)
    b = np.array(vec2, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))
