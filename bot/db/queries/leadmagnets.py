import asyncpg


async def get_active_leadmagnets(pool: asyncpg.Pool) -> list[asyncpg.Record]:
    return await pool.fetch(
        "SELECT * FROM lead_magnets WHERE is_active = true ORDER BY id"
    )


async def get_messages(pool: asyncpg.Pool, lead_magnet_id: int) -> list[asyncpg.Record]:
    return await pool.fetch(
        "SELECT * FROM lead_magnet_messages WHERE lead_magnet_id = $1 ORDER BY order_index",
        lead_magnet_id,
    )


async def list_leadmagnets(pool: asyncpg.Pool) -> list[asyncpg.Record]:
    return await pool.fetch("SELECT * FROM lead_magnets ORDER BY id")


async def get_leadmagnet(pool: asyncpg.Pool, lm_id: int) -> asyncpg.Record | None:
    return await pool.fetchrow("SELECT * FROM lead_magnets WHERE id = $1", lm_id)


async def create_leadmagnet(pool: asyncpg.Pool, name: str) -> int:
    row = await pool.fetchrow(
        "INSERT INTO lead_magnets (name, is_active) VALUES ($1, false) RETURNING id", name
    )
    return row["id"]


async def delete_leadmagnet(pool: asyncpg.Pool, lm_id: int) -> None:
    await pool.execute("DELETE FROM lead_magnets WHERE id = $1", lm_id)


async def set_active(pool: asyncpg.Pool, lm_id: int) -> None:
    await pool.execute("UPDATE lead_magnets SET is_active = true WHERE id = $1", lm_id)


async def set_inactive(pool: asyncpg.Pool, lm_id: int) -> None:
    await pool.execute("UPDATE lead_magnets SET is_active = false WHERE id = $1", lm_id)