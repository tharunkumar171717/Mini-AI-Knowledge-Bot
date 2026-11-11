"""Re-embed every stored chunk with the current EMBEDDING_MODEL.

Run after changing the embedding model:  python -m scripts.reembed   (from backend/)
"""
from app.database.connection import close_pool, get_pool
from app.services.embeddings import BATCH_SIZE, embed, to_pgvector


def main() -> None:
    with get_pool().connection() as conn:
        rows = conn.execute("select id, content from kb_chunks order by id").fetchall()
    print(f"Re-embedding {len(rows)} chunks")
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start:start + BATCH_SIZE]
        vectors = embed([content for _, content in batch])
        with get_pool().connection() as conn:
            conn.cursor().executemany(
                "update kb_chunks set embedding = %s::vector where id = %s",
                [(to_pgvector(v), chunk_id) for (chunk_id, _), v in zip(batch, vectors)],
            )
        print(f"  {start + len(batch)}/{len(rows)}")


if __name__ == "__main__":
    main()
    close_pool()
