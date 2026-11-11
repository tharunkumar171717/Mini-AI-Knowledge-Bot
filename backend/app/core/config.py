from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]  # backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # Supabase Postgres (session pooler, port 5432). Needs the pgvector extension.
    database_url: str

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    # Tried when gemini_model stays overloaded after retries. Empty string disables it.
    gemini_fallback_model: str = "gemini-3.5-flash"
    # Used to read scanned pages and images.
    ocr_model: str = "gemini-3.5-flash-lite"
    # A PDF page with fewer characters than this in its text layer is treated as scanned and OCR'd.
    ocr_min_chars: int = 50

    embedding_model: str = "gemini-embedding-001"
    max_upload_mb: int = 20
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 5

    cors_origins: list[str] = ["http://localhost:5174"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
