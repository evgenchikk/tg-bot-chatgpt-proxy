from enum import Enum

from . import handlers
from .routers import router, menu_router, settings_router, chat_router

from .middlewares import CheckUserExistsMiddleware
from .middlewares import ServiceInstanceMiddleware
from .middlewares import ChatMessageHistoryMiddleware


class RouterType(Enum):
    BASE = 'base'
    MENU = 'menu'
    SETTINGS = 'settings'
    CHAT = 'chat'


routers = {
    RouterType.BASE: router,
    RouterType.MENU: menu_router,
    RouterType.SETTINGS: settings_router,
    RouterType.CHAT: chat_router,
}

