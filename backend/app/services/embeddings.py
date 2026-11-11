import logging
import math

from google.genai import types

from app.core.config import get_settings
from app.database.schema import EMBEDDING_DIM
from app.services import gemini

logger = logging.getLogger(__name__)

# Gemini accepts up to 100 texts per embed request.
BATCH_SIZE = 100


def _normalize(vector: list[float]) -> list[float]:
    # Gemini only returns unit-length vectors at full size; truncated ones must be rescaled.
    norm = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / norm for x in vector]


def embed(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Unit-length embeddings from Gemini, so cosine similarity is a plain dot product.

    Use task_type="RETRIEVAL_QUERY" for questions and the default for document chunks.
    """
    config = types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM, task_type=task_type)
    model = get_settings().embedding_model
    vectors: list[list[float]] = []
    for start in range(0, len(texts), BATCH_SIZE):
        try:
            response = gemini.client().models.embed_content(
                model=model, contents=texts[start:start + BATCH_SIZE], config=config
            )
        except gemini.GeminiError:
            raise
        except Exception as exc:
            raise gemini.GeminiError(f"Embedding request failed: {exc}") from exc
        vectors.extend(_normalize(e.values) for e in response.embeddings)
    return vectors


def to_pgvector(vector: list[float]) -> str:
    """pgvector's text format, used with a ::vector cast in SQL."""
    return "[" + ",".join(f"{x:.7g}" for x in vector) + "]"
