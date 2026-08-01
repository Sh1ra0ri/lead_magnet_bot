from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.filters.is_admin import IsAdmin
from bot.keyboards.inline import admin_menu_kb

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer("Панель администратора:", reply_markup=admin_menu_kb())


@router.callback_query(F.data == "admin_panel")
async def admin_panel_cb(callback: CallbackQuery):
    await callback.message.edit_text("Панель администратора:", reply_markup=admin_menu_kb())
    await callback.answer()