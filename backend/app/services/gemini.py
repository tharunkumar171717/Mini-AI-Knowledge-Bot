import logging
import time
from functools import lru_cache

from google import genai
from google.genai import errors

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Overloaded (503), rate-limited (429) or transient server errors: worth retrying.
RETRYABLE_CODES = {429, 500, 503, 504}
# Model unknown or retired for this key: skip straight to the next model.
SKIP_MODEL_CODES = {404}
RETRIES_PER_MODEL = 3


class GeminiError(Exception):
    pass


@lru_cache
def client() -> genai.Client:
    key = get_settings().gemini_api_key
    if not key:
        raise GeminiError("GEMINI_API_KEY is not set in backend/.env.")
    return genai.Client(api_key=key)


def generate(models: list[str], contents, config=None) -> str:
    """Call Gemini, retrying overloads and moving to the next model in `models` if one stays busy."""
    last_error: Exception | None = None
    for model in dict.fromkeys(m for m in models if m):  # drop empties and duplicates, keep order
        for attempt in range(RETRIES_PER_MODEL):
            try:
                response = client().models.generate_content(model=model, contents=contents, config=config)
            except errors.APIError as exc:
                last_error = exc
                if exc.code in SKIP_MODEL_CODES:
                    logger.warning("Gemini model %s unavailable (%s), trying next model", model, exc.code)
                    break
                if exc.code not in RETRYABLE_CODES:
                    raise GeminiError(f"Gemini request failed: {exc}") from exc
                logger.warning("Gemini %s returned %s (attempt %d)", model, exc.code, attempt + 1)
                if attempt + 1 < RETRIES_PER_MODEL:
                    time.sleep(2**attempt)  # 1s, 2s
                continue
            except GeminiError:
                raise
            except Exception as exc:
                raise GeminiError(f"Gemini request failed: {exc}") from exc
            return (response.text or "").strip()

    raise GeminiError(f"Gemini is unavailable right now, please try again in a minute. ({last_error})") from last_error
