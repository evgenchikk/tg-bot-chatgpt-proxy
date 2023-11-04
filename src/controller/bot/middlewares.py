import logging
from typing import Callable

from aiogram import BaseMiddleware
from aiogram.types import Message as TgMessage

from service import Service
from models import Message, Role


log = logging.getLogger('service')

class CheckUserExistsMiddleware(BaseMiddleware):
    def __init__(self, service: Service) -> None:
        self.service = service

    async def __call__(self, handler, event, data):
        if not self.service.is_user_exists(event.from_user.username):
            await event.answer('Contact @evgenchikkkkkk to get access')
            return None

        return await handler(event, data)


class ServiceInstanceMiddleware(BaseMiddleware):
    def __init__(self, service: Service) -> None:
        self.service = service

    async def __call__(self, handler, event, data):
        return await handler(event, data | {'service': self.service})


class ChatMessageHistoryMiddleware(BaseMiddleware):
    def __init__(self, service: Service) -> None:
        self.service = service

    async def __call__(self, handler: Callable, event: TgMessage, data: dict):
        response_txt: str = await handler(event, data)

        try:
            state_data: dict = await data['state'].get_data()
            user_id: int = state_data.get('user_id')
            context_id: int | None = state_data.get('selected_context_id')

            user_message = Message(role=Role('user'), content=event.text)
            assist_message = Message(role=Role('assistant'), content=response_txt)

            self.service.save_message(user_message, context_id, user_id)
            self.service.save_message(assist_message, context_id, user_id)
        except Exception as e:
            log.error('Got an error in ChatMessageHistoryMiddleware', exc_info=e)
