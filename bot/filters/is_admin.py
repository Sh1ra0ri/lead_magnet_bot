from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
import asyncpg

from bot.db.queries.admins import is_admin as db_is_admin


class IsAdmin(BaseFilter):
    async def __call__(self, event: TelegramObject, pool: asyncpg.Pool) -> bool:
        return await db_is_admin(pool, event.from_user.id)