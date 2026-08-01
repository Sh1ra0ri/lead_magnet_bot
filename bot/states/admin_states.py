from aiogram.fsm.state import StatesGroup, State


class LeadMagnetCreate(StatesGroup):
    name = State()
    content_type = State()
    content = State()
    button_choice = State()
    button_text = State()
    button_url = State()


class AdminAdd(StatesGroup):
    waiting_id = State()