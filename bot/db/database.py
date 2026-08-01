import asyncpg
from pathlib import Path

_pool: asyncpg.Pool | None = None


async def init_pool(dsn: str) -> asyncpg.Pool:
    global _pool
    _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10, ssl=False)
    return _pool


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Pool not initialized")
    return _pool


async def close_pool() -> None:
    if _pool:
        await _pool.close()


async def run_migrations(dsn: str, migrations_dir: str = "bot/db/migrations") -> None:
    conn = await asyncpg.connect(dsn, ssl=False)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                filename VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL DEFAULT now()
            )
        """)
        applied = {r["filename"] for r in await conn.fetch("SELECT filename FROM schema_migrations")}
        files = sorted(Path(migrations_dir).glob("*.sql"))
        for f in files:
            if f.name in applied:
                continue
            sql = f.read_text()
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute("INSERT INTO schema_migrations (filename) VALUES ($1)", f.name)
    finally:
        await conn.close()