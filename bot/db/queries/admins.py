import asyncpg


async def is_admin(pool: asyncpg.Pool, telegram_id: int) -> bool:
    row = await pool.fetchrow("SELECT 1 FROM admins WHERE telegram_id = $1", telegram_id)
    return row is not None


async def add_admin(pool: asyncpg.Pool, telegram_id: int, added_by: int) -> None:
    await pool.execute(
        "INSERT INTO admins (telegram_id, added_by) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        telegram_id, added_by,
    )


async def remove_admin(pool: asyncpg.Pool, telegram_id: int) -> None:
    await pool.execute("DELETE FROM admins WHERE telegram_id = $1", telegram_id)


async def list_admins(pool: asyncpg.Pool) -> list[asyncpg.Record]:
    return await pool.fetch("SELECT * FROM admins ORDER BY id")