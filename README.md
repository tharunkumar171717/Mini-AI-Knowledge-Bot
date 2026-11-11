# Mini AI Knowledge Bot

Upload documents and ask questions about them. Answers come from Gemini, using only the passages
retrieved from your documents, and cite the file name and page.

```
upload → text layer (PyMuPDF) or Gemini OCR for scanned pages / images → chunks
       → Sentence Transformers embeddings → Supabase Postgres + pgvector
question → embedding → cosine similarity search (top-K) → Gemini → answer + sources
```

Supported files: PDF (text or scanned), PNG, JPEG, TXT. A PDF page with almost no text layer
(fewer than `OCR_MIN_CHARS` characters) is rendered to an image and OCR'd by Gemini.

## Layout

```
Mini-AI-Knowledge-Bot/
  backend/
    app/
      main.py              FastAPI app, CORS, /health
      core/config.py       settings loaded from backend/.env
      database/            Postgres connection pool, table creation
      models/              request/response schemas
      routes/              document_routes.py (/api/documents), chat_routes.py (/api/chat)
      services/            extraction (OCR), chunking, embeddings, search, llm, gemini client
    documents/             uploaded files (git-ignored)
    samples/               sample payoff statement and knowledge.txt
    requirements.txt
    .env.example
  frontend/                React + Vite + Tailwind UI
  venv/                    Python virtualenv
```

## Configuration

`backend/.env` (copy from `backend/.env.example`; never commit it):

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Supabase Postgres, session pooler (port 5432). Same project as PaperTrail. |
| `GEMINI_API_KEY` | Key from Google AI Studio. |
| `GEMINI_MODEL` / `GEMINI_FALLBACK_MODEL` | Model that answers questions, and the one tried when it is busy or unavailable. |
| `OCR_MODEL` | Model that reads scanned pages and images. |
| `EMBEDDING_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K`, `MAX_UPLOAD_MB` | Retrieval tuning and upload limit. |
| `CORS_ORIGINS` | JSON list of frontend URLs allowed to call the API. |

The database is shared with PaperTrail, so this app's tables are named `kb_documents` and
`kb_chunks`. They are created on startup.

`frontend/.env` has `VITE_API_BASE_URL` (default `http://localhost:8001`).

## Run locally

Ports 8001 / 5174 are used so this runs alongside PaperTrail (8000 / 5173).

```bash
# backend
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload --port 8001
curl http://localhost:8001/health

# frontend (another terminal)
cd frontend
npm install
npm run dev          # http://localhost:5174
```

API docs: http://localhost:8001/docs

## API

| Method | Path | Body | Returns |
| --- | --- | --- | --- |
| GET | `/health` | | database and pgvector status |
| GET | `/api/documents` | | list of documents |
| GET | `/api/documents/{id}` | | one document |
| POST | `/api/documents/upload` | multipart `file` | the document, status `processing` (indexed in the background) |
| DELETE | `/api/documents/{id}` | | 204 |
| POST | `/api/chat` | `{"question": "...", "top_k": 5}` | `{"answer": "...", "sources": [...]}` |

Document: `{"id", "filename", "mime_type", "status", "page_count", "ocr_pages", "error", "created_at"}`.
Source: `{"filename", "page", "content", "score"}`.
