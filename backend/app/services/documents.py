import logging
from uuid import UUID

from psycopg.rows import class_row

from app.core.config import get_settings
from app.database.connection import get_pool
from app.models.document import Document
from app.services.chunking import chunk_text
from app.services.embeddings import embed, to_pgvector
from app.services.extraction import extract

logger = logging.getLogger(__name__)

_COLUMNS = "id, filename, mime_type, status, page_count, ocr_pages, error, created_at"



def get_document(document_id: UUID) -> Document | None:
    with get_pool().connection() as conn:
        cur = conn.cursor(row_factory=class_row(Document))
        return cur.execute(f"select {_COLUMNS} from kb_documents where id = %s", (document_id,)).fetchone()


def list_documents() -> list[Document]:
    with get_pool().connection() as conn:
        cur = conn.cursor(row_factory=class_row(Document))
        return cur.execute(f"select {_COLUMNS} from kb_documents order by created_at desc").fetchall()


def delete_document(document_id: UUID) -> bool:
    """Delete the document, its file and its chunks (via cascade). Returns False if it didn't exist."""
    with get_pool().connection() as conn:
        row = conn.execute("delete from kb_documents where id = %s returning id", (document_id,)).fetchone()
    return row is not None


def get_file(document_id: UUID) -> tuple[str, str, bytes] | None:
    """(filename, mime_type, content) of the original upload, or None if missing."""
    with get_pool().connection() as conn:
        row = conn.execute(
            "select filename, mime_type, content from kb_documents where id = %s", (document_id,)
        ).fetchone()
    if row is None or row[2] is None:
        return None
    return row[0], row[1], bytes(row[2])


def create_document(filename: str, mime_type: str, content: bytes) -> UUID:
    """Insert a 'processing' row holding the original file.

    The file lives in Postgres rather than on disk because serverless hosts (Vercel) have no
    persistent disk; uploads are capped at MAX_UPLOAD_MB, so rows stay small.
    """
    with get_pool().connection() as conn:
        return conn.execute(
            "insert into kb_documents (filename, mime_type, content) values (%s, %s, %s) returning id",
            (filename, mime_type, content),
        ).fetchone()[0]


def ingest_document(document_id: UUID, mime_type: str) -> None:
    """Extract (OCR if needed), chunk, embed and store the text, then mark the document completed or failed.

    Runs as a background task after the upload request has returned, so errors are
    recorded on the document row instead of raised.
    """
    settings = get_settings()
    try:
        stored = get_file(document_id)
        if stored is None:
            raise ValueError("The uploaded file is missing.")
        extracted = extract(stored[2], mime_type)

        rows = []  # (page, chunk_index, content)
        for page, text in extracted.pages:
            for i, chunk in enumerate(chunk_text(text, settings.chunk_size, settings.chunk_overlap)):
                rows.append((page, i, chunk))
        if not rows:
            raise ValueError("No readable text was found in this file.")

        vectors = embed([content for _, _, content in rows])

        with get_pool().connection() as conn:  # one transaction: all chunks or none
            conn.cursor().executemany(
                "insert into kb_chunks (document_id, page, chunk_index, content, embedding)"
                " values (%s, %s, %s, %s, %s::vector)",
                [
                    (document_id, page, i, content, to_pgvector(vec))
                    for (page, i, content), vec in zip(rows, vectors)
                ],
            )
            conn.execute(
                "update kb_documents set status = 'completed', page_count = %s, ocr_pages = %s, error = null"
                " where id = %s",
                (len(extracted.pages), extracted.ocr_pages, document_id),
            )
        logger.info("Indexed %s: %d pages, %d OCR'd, %d chunks",
                    document_id, len(extracted.pages), extracted.ocr_pages, len(rows))
    except Exception as exc:
        logger.exception("Indexing %s failed", document_id)
        with get_pool().connection() as conn:
            conn.execute(
                "update kb_documents set status = 'failed', error = %s where id = %s",
                (str(exc) or type(exc).__name__, document_id),
            )
