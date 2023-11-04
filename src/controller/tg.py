import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.token import TokenValidationError

from service import Service

from .controller import Controller
from .bot import routers, RouterType
from .bot import CheckUserExistsMiddleware, ServiceInstanceMiddleware, ChatMessageHistoryMiddleware


log = logging.getLogger('controller')

class TGController(Controller):
    def __init__(self, service: Service) -> None:
        super().__init__(service)

        api_token = os.getenv('TG_API_TOKEN')
        if not api_token:
            log.error('Environment variable OPENAI_API_KEY is not set')
            raise

        try:
            bot = Bot(token=api_token, parse_mode=ParseMode.MARKDOWN_V2)
        except TokenValidationError:
            log.error('Got token validation error')
            return

        dispatcher = Dispatcher()
        dispatcher.message.outer_middleware(CheckUserExistsMiddleware(service))

        dispatcher.message.middleware(ChatActionMiddleware())
        dispatcher.message.middleware(ServiceInstanceMiddleware(service))
        dispatcher.callback_query.middleware(ChatActionMiddleware())
        dispatcher.callback_query.middleware(ServiceInstanceMiddleware(service))

        routers[RouterType.CHAT].message.middleware(ChatMessageHistoryMiddleware(service))

        dispatcher.include_routers(*routers.values())

        self.bot = bot
        self.dispatcher = dispatcher

    async def run(self) -> None:
        await self.bot.delete_webhook(drop_pending_updates=True)
        await self.dispatcher.start_polling(self.bot)
