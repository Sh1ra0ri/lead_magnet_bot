import json

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def build_keyboard(buttons) -> InlineKeyboardMarkup | None:
    if not buttons:
        return None
    data = json.loads(buttons) if isinstance(buttons, str) else buttons
    rows = [[InlineKeyboardButton(text=b["text"], url=b["url"])] for b in data]
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_message(bot: Bot, chat_id: int, message: dict) -> None:
    kb = build_keyboard(message["buttons"])
    content_type = message["content_type"]
    text = message["text"]
    file_id = message["file_id"]

    if content_type == "text":
        await bot.send_message(chat_id, text, reply_markup=kb)
    elif content_type == "photo":
        await bot.send_photo(chat_id, file_id, caption=text, reply_markup=kb)
    elif content_type == "video":
        await bot.send_video(chat_id, file_id, caption=text, reply_markup=kb)
    elif content_type == "document":
        await bot.send_document(chat_id, file_id, caption=text, reply_markup=kb)
    elif content_type == "audio":
        await bot.send_audio(chat_id, file_id, caption=text, reply_markup=kb)
    elif content_type == "voice":
        await bot.send_voice(chat_id, file_id, caption=text, reply_markup=kb)