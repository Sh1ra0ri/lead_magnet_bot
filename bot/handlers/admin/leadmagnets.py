from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import asyncpg

from bot.states.admin_states import LeadMagnetCreate
from bot.filters.is_admin import IsAdmin
from bot.keyboards.inline import (
    leadmagnets_list_kb, leadmagnet_view_kb, leadmagnet_edit_kb,
    content_type_kb, cancel_kb, button_choice_kb, yes_no_kb, admin_menu_kb,
    content_type_with_back_kb, back_kb, button_choice_with_back_kb,
)
from bot.db.queries.leadmagnets import (
    list_leadmagnets, get_leadmagnet, create_leadmagnet, delete_leadmagnet,
    set_active, set_inactive, get_messages,
)
from bot.db.queries.messages import add_message, delete_message, count_messages

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

async def _show_list(message, pool: asyncpg.Pool):
    items = await list_leadmagnets(pool)
    if not items:
        await message.edit_text("Лид-магнитов пока нет.", reply_markup=admin_menu_kb())
    else:
        await message.edit_text("Лид-магниты:", reply_markup=leadmagnets_list_kb(items))


async def _show_view(message, pool: asyncpg.Pool, lm_id: int):
    lm = await get_leadmagnet(pool, lm_id)
    await message.edit_text(
        f"Лид-магнит: {lm['name']}\nАктивен: {'да' if lm['is_active'] else 'нет'}",
        reply_markup=leadmagnet_view_kb(lm_id, lm["is_active"]),
    )


@router.callback_query(F.data == "lm_list")
async def lm_list(callback: CallbackQuery, pool: asyncpg.Pool):
    await _show_list(callback.message, pool)
    await callback.answer()


@router.callback_query(F.data.startswith("lm_view:"))
async def lm_view(callback: CallbackQuery, pool: asyncpg.Pool):
    lm_id = int(callback.data.split(":")[1])
    await _show_view(callback.message, pool, lm_id)
    await callback.answer()


@router.callback_query(F.data.startswith("lm_set_active:"))
async def lm_set_active(callback: CallbackQuery, pool: asyncpg.Pool):
    lm_id = int(callback.data.split(":")[1])
    await set_active(pool, lm_id)
    await callback.answer("Активирован")
    await _show_view(callback.message, pool, lm_id)


@router.callback_query(F.data.startswith("lm_set_inactive:"))
async def lm_set_inactive(callback: CallbackQuery, pool: asyncpg.Pool):
    lm_id = int(callback.data.split(":")[1])
    await set_inactive(pool, lm_id)
    await callback.answer("Деактивирован")
    await _show_view(callback.message, pool, lm_id)


@router.callback_query(F.data.startswith("lm_delete:"))
async def lm_delete_confirm(callback: CallbackQuery):
    lm_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(
        "Удалить лид-магнит вместе со всеми сообщениями?",
        reply_markup=yes_no_kb(f"lm_delete_yes:{lm_id}", f"lm_view:{lm_id}"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lm_delete_yes:"))
async def lm_delete_yes(callback: CallbackQuery, pool: asyncpg.Pool):
    lm_id = int(callback.data.split(":")[1])
    await delete_leadmagnet(pool, lm_id)
    await callback.answer("Удалено")
    await _show_list(callback.message, pool)


@router.callback_query(F.data.startswith("lm_edit:"))
async def lm_edit(callback: CallbackQuery, pool: asyncpg.Pool):
    lm_id = int(callback.data.split(":")[1])
    messages = await get_messages(pool, lm_id)
    await callback.message.edit_text("Сообщения лид-магнита:", reply_markup=leadmagnet_edit_kb(lm_id, messages))
    await callback.answer()


@router.callback_query(F.data.startswith("lm_msg_del:"))
async def lm_msg_del(callback: CallbackQuery, pool: asyncpg.Pool):
    _, lm_id, msg_id = callback.data.split(":")
    await delete_message(pool, int(msg_id))
    messages = await get_messages(pool, int(lm_id))
    await callback.message.edit_text("Сообщения лид-магнита:", reply_markup=leadmagnet_edit_kb(int(lm_id), messages))
    await callback.answer("Удалено")


@router.callback_query(F.data == "lm_add")
async def lm_add_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LeadMagnetCreate.name)
    await callback.message.edit_text("Введите название лид-магнита:", reply_markup=cancel_kb())
    await callback.answer()


@router.message(LeadMagnetCreate.name)
async def lm_add_name(message: Message, state: FSMContext, pool: asyncpg.Pool):
    lm_id = await create_leadmagnet(pool, message.text)
    await state.update_data(lm_id=lm_id, is_new=True)
    await state.set_state(LeadMagnetCreate.content_type)
    await message.answer("Выберите тип первого сообщения:", reply_markup=content_type_with_back_kb())


@router.callback_query(F.data.startswith("lm_msg_add:"))
async def lm_msg_add_start(callback: CallbackQuery, state: FSMContext):
    lm_id = int(callback.data.split(":")[1])
    await state.update_data(lm_id=lm_id, is_new=False)
    await state.set_state(LeadMagnetCreate.content_type)
    await callback.message.edit_text("Выберите тип сообщения:", reply_markup=content_type_with_back_kb())
    await callback.answer()


@router.callback_query(LeadMagnetCreate.content_type, F.data.startswith("ct:"))
async def lm_add_content_type(callback: CallbackQuery, state: FSMContext):
    content_type = callback.data.split(":")[1]
    await state.update_data(content_type=content_type)
    await state.set_state(LeadMagnetCreate.content)
    prompt = "Отправьте текст сообщения:" if content_type == "text" else f"Отправьте файл ({content_type}):"
    await callback.message.edit_text(prompt, reply_markup=back_kb("lm_content_back"))
    await callback.answer()


@router.callback_query(F.data == "lm_content_back")
async def lm_content_back(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору типа контента"""
    await state.set_state(LeadMagnetCreate.content_type)
    await callback.message.edit_text("Выберите тип сообщения:", reply_markup=content_type_with_back_kb())
    await callback.answer()


@router.message(LeadMagnetCreate.content)
async def lm_add_content(message: Message, state: FSMContext):
    data = await state.get_data()
    content_type = data["content_type"]
    file_id, text = None, None

    if content_type == "text":
        text = message.text
    elif content_type == "photo" and message.photo:
        file_id, text = message.photo[-1].file_id, message.caption
    elif content_type == "video" and message.video:
        file_id, text = message.video.file_id, message.caption
    elif content_type == "document" and message.document:
        file_id, text = message.document.file_id, message.caption
    elif content_type == "audio" and message.audio:
        file_id, text = message.audio.file_id, message.caption
    elif content_type == "voice" and message.voice:
        file_id = message.voice.file_id
    else:
        await message.answer("Не тот тип, отправьте ещё раз.", reply_markup=back_kb("lm_content_back"))
        return

    await state.update_data(text=text, file_id=file_id)
    await state.set_state(LeadMagnetCreate.button_choice)
    await message.answer("Добавить кнопку-ссылку?", reply_markup=button_choice_with_back_kb())


@router.callback_query(F.data == "lm_button_back")
async def lm_button_back(callback: CallbackQuery, state: FSMContext):
    """Возврат к вводу контента"""
    data = await state.get_data()
    content_type = data["content_type"]
    await state.set_state(LeadMagnetCreate.content)
    prompt = "Отправьте текст сообщения:" if content_type == "text" else f"Отправьте файл ({content_type}):"
    await callback.message.edit_text(prompt, reply_markup=back_kb("lm_content_back"))
    await callback.answer()


@router.callback_query(LeadMagnetCreate.button_choice, F.data == "btn_yes")
async def lm_button_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LeadMagnetCreate.button_text)
    await callback.message.edit_text("Текст кнопки:", reply_markup=back_kb("lm_button_text_back"))
    await callback.answer()


@router.callback_query(F.data == "lm_button_text_back")
async def lm_button_text_back(callback: CallbackQuery, state: FSMContext):
    """Возврат к выбору кнопки"""
    await state.set_state(LeadMagnetCreate.button_choice)
    await callback.message.edit_text("Добавить кнопку-ссылку?", reply_markup=button_choice_with_back_kb())
    await callback.answer()


@router.message(LeadMagnetCreate.button_text)
async def lm_button_text(message: Message, state: FSMContext):
    await state.update_data(button_text=message.text)
    await state.set_state(LeadMagnetCreate.button_url)
    await message.answer("Ссылка (URL):", reply_markup=back_kb("lm_button_url_back"))


@router.callback_query(F.data == "lm_button_url_back")
async def lm_button_url_back(callback: CallbackQuery, state: FSMContext):
    """Возврат к вводу текста кнопки"""
    await state.set_state(LeadMagnetCreate.button_text)
    await callback.message.edit_text("Текст кнопки:", reply_markup=back_kb("lm_button_text_back"))
    await callback.answer()


@router.message(LeadMagnetCreate.button_url)
async def lm_button_url(message: Message, state: FSMContext, pool: asyncpg.Pool):
    data = await state.get_data()
    buttons = [{"text": data["button_text"], "url": message.text}]
    await _save_and_ask_next(message, state, pool, buttons)


@router.callback_query(LeadMagnetCreate.button_choice, F.data == "btn_no")
async def lm_button_no(callback: CallbackQuery, state: FSMContext, pool: asyncpg.Pool):
    await _save_and_ask_next(callback.message, state, pool, None, edit=True)
    await callback.answer()


async def _save_and_ask_next(message: Message, state: FSMContext, pool: asyncpg.Pool, buttons, edit=False):
    data = await state.get_data()
    lm_id = data["lm_id"]
    order = await count_messages(pool, lm_id) + 1
    await add_message(pool, lm_id, order, data["content_type"], data.get("text"), data.get("file_id"), buttons)
    await state.set_state(LeadMagnetCreate.content_type)

    text, kb = "Сообщение сохранено. Добавить ещё одно?", yes_no_kb("lm_more_yes", f"lm_done:{lm_id}")
    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "lm_more_yes")
async def lm_more_yes(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LeadMagnetCreate.content_type)
    await callback.message.edit_text("Тип следующего сообщения:", reply_markup=content_type_with_back_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("lm_done:"))
async def lm_done(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Лид-магнит сохранён ✅", reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "lm_cancel")
async def lm_cancel(callback: CallbackQuery, state: FSMContext, pool: asyncpg.Pool):
    data = await state.get_data()
    lm_id = data.get("lm_id")
    if lm_id and data.get("is_new"):
        count = await count_messages(pool, lm_id)
        if count == 0:
            await delete_leadmagnet(pool, lm_id)
    await state.clear()
    await callback.message.edit_text("Создание отменено.", reply_markup=admin_menu_kb())
    await callback.answer()