from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

DocumentStatus = Literal["processing", "completed", "failed"]


class Document(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    status: DocumentStatus
    page_count: int | None = None
    ocr_pages: int = 0
    error: str | None = None
    created_at: datetime
