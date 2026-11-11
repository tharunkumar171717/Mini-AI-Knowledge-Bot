from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Response, UploadFile

from app.core.config import get_settings
from app.models.document import Document
from app.services import documents as service
from app.services.extraction import detect_type

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=list[Document])
def list_documents() -> list[Document]:
    return service.list_documents()


@router.get("/{document_id}", response_model=Document)
def get_document(document_id: UUID) -> Document:
    document = service.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/upload", response_model=Document, status_code=202)
def upload_document(background: BackgroundTasks, file: UploadFile = File(...)) -> Document:
    """Store the file and start indexing it. Returns at once with status 'processing'; poll the list for the result."""
    settings = get_settings()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    content = file.file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File is larger than {settings.max_upload_mb} MB.")

    filename = file.filename or "document"
    mime_type = detect_type(filename, content)
    if mime_type is None:
        raise HTTPException(status_code=400, detail="Only PDF, PNG, JPEG and TXT files are allowed.")

    document_id = service.create_document(filename, mime_type, content)
    background.add_task(service.ingest_document, document_id, mime_type)
    return service.get_document(document_id)


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: UUID) -> Response:
    if not service.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return Response(status_code=204)
