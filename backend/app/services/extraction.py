"""Turn an uploaded file into (page_number, text) pairs.

PDF pages with a real text layer are read directly. Scanned pages and images
are sent to Gemini for OCR, which is slower but handles documents like faxed
payoff statements.
"""

import logging
from dataclasses import dataclass

import pymupdf
from google.genai import types

from app.core.config import get_settings
from app.services import gemini

logger = logging.getLogger(__name__)

PDF = "application/pdf"
IMAGE_TYPES = {"image/png", "image/jpeg"}
TEXT = "text/plain"
SUPPORTED_TYPES = {PDF, TEXT, *IMAGE_TYPES}

OCR_PROMPT = """Perform OCR on this document image.
- Extract all readable text.
- Preserve headings and paragraphs.
- Write tables as rows with columns separated by " | ".
- Do not skip important information such as amounts, dates, names and account numbers.
- Do not invent missing information.
- Return only the extracted content."""


@dataclass
class Extracted:
    pages: list[tuple[int, str]]
    ocr_pages: int = 0


def ocr_image(image_bytes: bytes, mime_type: str) -> str:
    settings = get_settings()
    return gemini.generate(
        [settings.ocr_model, settings.gemini_fallback_model],
        [types.Part.from_bytes(data=image_bytes, mime_type=mime_type), OCR_PROMPT],
        types.GenerateContentConfig(temperature=0),
    )


def _extract_pdf(content: bytes) -> Extracted:
    min_chars = get_settings().ocr_min_chars
    result = Extracted(pages=[])
    with pymupdf.open(stream=content, filetype="pdf") as doc:
        for number, page in enumerate(doc, start=1):
            text = page.get_text()
            if len(text.strip()) < min_chars:
                png = page.get_pixmap(matrix=pymupdf.Matrix(2, 2)).tobytes("png")
                text = ocr_image(png, "image/png")
                result.ocr_pages += 1
                logger.info("p.%d: OCR'd (%d chars)", number, len(text))
            result.pages.append((number, text))
    return result


def extract(content: bytes, mime_type: str) -> Extracted:
    if mime_type == PDF:
        return _extract_pdf(content)
    if mime_type in IMAGE_TYPES:
        return Extracted(pages=[(1, ocr_image(content, mime_type))], ocr_pages=1)
    if mime_type == TEXT:
        return Extracted(pages=[(1, content.decode("utf-8", errors="replace"))])
    raise ValueError(f"Unsupported file type: {mime_type}")


def detect_type(filename: str, content: bytes) -> str | None:
    """Work out the file type from its bytes, not the browser's Content-Type, which can't be trusted."""
    if content.startswith(b"%PDF"):
        return PDF
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if content.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if filename.lower().endswith((".txt", ".md")):
        try:
            content.decode("utf-8")
            return TEXT
        except UnicodeDecodeError:
            return None
    return None
