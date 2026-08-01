from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import asyncpg

from bot.states.admin_states import AdminAdd
from bot.filters.is_admin import IsAdmin
from bot.keyboards.inline import admins_list_kb, admin_menu_kb
from bot.db.queries.admins import list_admins, add_admin, remove_admin

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


@router.callback_query(F.data == "admin_list")
async def admins_list(callback: CallbackQuery, pool: asyncpg.Pool):
    admins = await list_admins(pool)
    await callback.message.edit_text("Администраторы:", reply_markup=admins_list_kb(admins))
    await callback.answer()


@router.callback_query(F.data == "admin_add")
async def admin_add_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminAdd.waiting_id)
    await callback.message.edit_text("Перешлите сообщение от нового админа или отправьте его Telegram ID:")
    await callback.answer()


@router.message(AdminAdd.waiting_id)
async def admin_add_finish(message: Message, state: FSMContext, pool: asyncpg.Pool):
    if message.forward_from:
        new_id = message.forward_from.id
    elif message.text and message.text.isdigit():
        new_id = int(message.text)
    else:
        await message.answer("Не удалось распознать ID. Перешлите сообщение или отправьте число.")
        return

    await add_admin(pool, new_id, message.from_user.id)
    await state.clear()
    await message.answer(f"Админ {new_id} добавлен ✅", reply_markup=admin_menu_kb())


@router.callback_query(F.data.startswith("admin_remove:"))
async def admin_remove(callback: CallbackQuery, pool: asyncpg.Pool):
    telegram_id = int(callback.data.split(":")[1])
    await remove_admin(pool, telegram_id)
    admins = await list_admins(pool)
    await callback.message.edit_text("Администраторы:", reply_markup=admins_list_kb(admins))
    await callback.answer("Удалён")