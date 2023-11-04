from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    menu = State()
    settings = State()
    chat = State()
