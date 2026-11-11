import logging
import threading
import time
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger(__name__)
_load_lock = threading.Lock()


@lru_cache
def _cached_model() -> SentenceTransformer:
    name = get_settings().embedding_model
    try:
        # Use the Hugging Face cache without a network check when the model is already downloaded.
        return SentenceTransformer(name, local_files_only=True)
    except Exception:
        return SentenceTransformer(name)


def _model() -> SentenceTransformer:
    # The lock makes a request that arrives during warm-up wait for it instead of loading a second copy.
    with _load_lock:
        return _cached_model()


def warm_up() -> None:
    start = time.perf_counter()
    try:
        embed(["warm up"])
        logger.info("Embedding model ready in %.1fs", time.perf_counter() - start)
    except Exception:
        logger.exception("Embedding model failed to load; it will be retried on first use")


def embed(texts: list[str]) -> list[list[float]]:
    """Unit-length embeddings, so cosine similarity is a plain dot product."""
    vectors = _model().encode(texts, normalize_embeddings=True, batch_size=32)
    return vectors.tolist()


def to_pgvector(vector: list[float]) -> str:
    """pgvector's text format, used with a ::vector cast in SQL."""
    return "[" + ",".join(f"{x:.7g}" for x in vector) + "]"
