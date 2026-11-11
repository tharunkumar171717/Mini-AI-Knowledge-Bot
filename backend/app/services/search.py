from psycopg.rows import class_row

from app.database.connection import get_pool
from app.models.chat import Source
from app.services.embeddings import embed, to_pgvector


def search_chunks(question: str, top_k: int) -> list[Source]:
    """The top_k chunks closest to the question by cosine similarity, from completed documents only."""
    vector = to_pgvector(embed([question])[0])
    with get_pool().connection() as conn:
        cur = conn.cursor(row_factory=class_row(Source))
        return cur.execute(
            """
            select d.filename, c.page, c.content,
                   1 - (c.embedding <=> %(v)s::vector) as score
            from kb_chunks c
            join kb_documents d on d.id = c.document_id
            where d.status = 'completed'
            order by c.embedding <=> %(v)s::vector
            limit %(k)s
            """,
            {"v": vector, "k": top_k},
        ).fetchall()
