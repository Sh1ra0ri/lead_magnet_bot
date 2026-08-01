import asyncpg
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.db.queries.leadmagnets import get_active_leadmagnets, get_messages
from bot.utils.content_sender import send_message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, pool: asyncpg.Pool) -> None:
    leadmagnets = await get_active_leadmagnets(pool)
    if not leadmagnets:
        await message.answer("Лид-магнит пока не настроен.")
        return

    for leadmagnet in leadmagnets:
        messages = await get_messages(pool, leadmagnet["id"])
        for msg in messages:
            await send_message(bot, message.chat.id, dict(msg))