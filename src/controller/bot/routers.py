from aiogram import Router

from .states import UserState


router = Router()

menu_router = Router()
menu_router.message.filter(UserState.menu)
menu_router.callback_query.filter(UserState.menu)

settings_router = Router()
settings_router.message.filter(UserState.settings)
settings_router.callback_query.filter(UserState.settings)

chat_router = Router()
chat_router.message.filter(UserState.chat)
chat_router.callback_query.filter(UserState.chat)
