import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database.connection import check_database, close_pool, open_pool
from app.database.schema import init_schema
from app.routes import chat_routes, document_routes
from app.services.embeddings import warm_up

logging.basicConfig(level=logging.INFO, format="%(levelname)s:     %(name)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    init_schema()
    # Load the embedding model in the background so the server starts at once.
    threading.Thread(target=warm_up, daemon=True).start()
    yield
    close_pool()


app = FastAPI(
    title="Mini AI Knowledge Bot",
    description="Upload documents (OCR for scanned PDFs and images) and ask questions about them.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(document_routes.router)
app.include_router(chat_routes.router)


@app.get("/")
def home():
    return {"message": "Mini AI Knowledge Bot API is running"}


@app.get("/health")
def health() -> dict:
    try:
        return {"status": "ok", "database": check_database()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {exc}") from exc
