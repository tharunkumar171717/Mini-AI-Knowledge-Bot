from psycopg_pool import ConnectionPool

from app.core.config import get_settings

_pool: ConnectionPool | None = None


def open_pool() -> None:
    global _pool
    # Supabase's pooler rejects server-side prepared statements, hence prepare_threshold=None.
    _pool = ConnectionPool(
        get_settings().database_url,
        min_size=1,
        max_size=5,
        kwargs={"prepare_threshold": None},
        open=True,
    )
    _pool.wait(timeout=15)


def close_pool() -> None:
    if _pool is not None:
        _pool.close()


def get_pool() -> ConnectionPool:
    # Opened on first use as well as at startup, for hosts that skip the ASGI lifespan (serverless).
    if _pool is None:
        open_pool()
    return _pool


def check_database() -> dict:
    with get_pool().connection() as conn:
        version = conn.execute("select version()").fetchone()[0]
        row = conn.execute(
            "select default_version, installed_version from pg_available_extensions where name = 'vector'"
        ).fetchone()
    return {
        "postgres": version.split(",")[0],
        "pgvector_available": row is not None,
        "pgvector_installed": bool(row and row[1]),
    }
