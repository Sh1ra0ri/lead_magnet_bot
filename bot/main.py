import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.db.database import init_pool, run_migrations, close_pool
from bot.db.queries.admins import add_admin
from bot.handlers.user import router as user_router
from bot.handlers.admin.panel import router as admin_panel_router
from bot.handlers.admin.leadmagnets import router as admin_lm_router
from bot.handlers.admin.admins import router as admin_admins_router

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await run_migrations(settings.DB_DSN)
    pool = await init_pool(settings.DB_DSN)
    await add_admin(pool, settings.SUPER_ADMIN_ID, settings.SUPER_ADMIN_ID)

    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp["pool"] = pool

    dp.include_router(admin_panel_router)
    dp.include_router(admin_lm_router)
    dp.include_router(admin_admins_router)
    dp.include_router(user_router)

    try:
        await dp.start_polling(bot)
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())