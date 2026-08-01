import json
import asyncpg


async def add_message(
    pool: asyncpg.Pool, lead_magnet_id: int, order_index: int, content_type: str,
    text: str | None, file_id: str | None, buttons: list | None,
) -> None:
    await pool.execute(
        """INSERT INTO lead_magnet_messages
           (lead_magnet_id, order_index, content_type, text, file_id, buttons)
           VALUES ($1, $2, $3, $4, $5, $6)""",
        lead_magnet_id, order_index, content_type, text, file_id,
        json.dumps(buttons) if buttons else None,
    )


async def delete_message(pool: asyncpg.Pool, message_id: int) -> None:
    await pool.execute("DELETE FROM lead_magnet_messages WHERE id = $1", message_id)


async def count_messages(pool: asyncpg.Pool, lead_magnet_id: int) -> int:
    row = await pool.fetchrow(
        "SELECT COUNT(*) AS c FROM lead_magnet_messages WHERE lead_magnet_id = $1", lead_magnet_id
    )
    return row["c"]