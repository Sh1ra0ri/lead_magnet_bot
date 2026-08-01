from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список лид-магнитов", callback_data="lm_list")],
        [InlineKeyboardButton(text="➕ Добавить лид-магнит", callback_data="lm_add")],
        [InlineKeyboardButton(text="👥 Администраторы", callback_data="admin_list")],
    ])


def leadmagnets_list_kb(items):
    rows = [
        [InlineKeyboardButton(
            text=f"{'✅ ' if i['is_active'] else ''}{i['name']}",
            callback_data=f"lm_view:{i['id']}",
        )] for i in items
    ]
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def leadmagnet_view_kb(lm_id, is_active):
    rows = [[InlineKeyboardButton(text="✏️ Редактировать сообщения", callback_data=f"lm_edit:{lm_id}")]]
    if is_active:
        rows.append([InlineKeyboardButton(text="❌ Сделать неактивным", callback_data=f"lm_set_inactive:{lm_id}")])
    else:
        rows.append([InlineKeyboardButton(text="✅ Сделать активным", callback_data=f"lm_set_active:{lm_id}")])
    rows.append([InlineKeyboardButton(text="🗑 Удалить", callback_data=f"lm_delete:{lm_id}")])
    rows.append([InlineKeyboardButton(text="◀️ К списку", callback_data="lm_list")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def leadmagnet_edit_kb(lm_id, messages):
    rows = [
        [InlineKeyboardButton(text=f"❌ #{m['order_index']} {m['content_type']}",
                               callback_data=f"lm_msg_del:{lm_id}:{m['id']}")]
        for m in messages
    ]
    rows.append([InlineKeyboardButton(text="➕ Добавить сообщение", callback_data=f"lm_msg_add:{lm_id}")])
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"lm_view:{lm_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def content_type_kb():
    types = ["text", "photo", "video", "document", "audio", "voice"]
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=f"ct:{t}")] for t in types])


def yes_no_kb(yes_cb, no_cb):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Да", callback_data=yes_cb),
        InlineKeyboardButton(text="Нет", callback_data=no_cb),
    ]])


def admins_list_kb(admins):
    rows = [
        [InlineKeyboardButton(text=f"🗑 {a['telegram_id']}", callback_data=f"admin_remove:{a['telegram_id']}")]
        for a in admins
    ]
    rows.append([InlineKeyboardButton(text="➕ Добавить админа", callback_data="admin_add")])
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)