from app.database.connection import get_pool

# 384 = output size of sentence-transformers/all-MiniLM-L6-v2.
# Changing EMBEDDING_MODEL to one with another size means changing this and re-embedding.
EMBEDDING_DIM = 384

# Tables are prefixed kb_ because this Supabase database is shared with PaperTrail,
# which owns the unprefixed `documents` and `chunks` tables.
SCHEMA_SQL = f"""
create extension if not exists vector;

create table if not exists kb_documents (
    id          uuid primary key default gen_random_uuid(),
    filename    text not null,
    mime_type   text not null,
    status      text not null default 'processing'
                check (status in ('processing', 'completed', 'failed')),
    page_count  integer,
    ocr_pages   integer not null default 0,
    error       text,
    created_at  timestamptz not null default now()
);

create table if not exists kb_chunks (
    id           bigserial primary key,
    document_id  uuid not null references kb_documents(id) on delete cascade,
    page         integer not null,
    chunk_index  integer not null,
    content      text not null,
    embedding    vector({EMBEDDING_DIM}) not null
);

create index if not exists kb_chunks_document_id_idx on kb_chunks (document_id);
"""


def init_schema() -> None:
    """Create the extension, tables and indexes if they don't exist yet."""
    with get_pool().connection() as conn:
        conn.execute(SCHEMA_SQL)
