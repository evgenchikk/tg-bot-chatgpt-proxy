import os
import logging

import openai

from repo import Repository
from models import User, ChatCompletionResponse, Message, Role, Context

from .service import Service
from .exceptions import MissingAPIKey, EmptyPrompt, UnexpectedResponse
from .exceptions import InvalidUsername, InvalidContextName, TooLongPrompt


log = logging.getLogger('service')

class ServiceImpl(Service):
    def __init__(self, repository: Repository, config: dict) -> None:
        super().__init__(repository)

        self.model = config.get('model', 'gpt-3.5-turbo')
        self.temperature = config.get('temperature', 1)
        self.max_tokens = config.get('max_tokens', 256)
        self.timeout = config.get('timeout', 60)

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            log.error('Environment variable OPENAI_API_KEY not set')
            raise MissingAPIKey

        openai.api_key = api_key

    def is_user_exists(self, username: str) -> bool:
        return self.repository.is_user_exists(username)

    def is_user_admin(self, username: str) -> bool:
        return self.repository.is_user_admin(username)

    def get_user_by_username(self, username: str) -> User:
        return self.repository.get_user_by_username(username)

    def get_user_contexts(self, username: str) -> list[Context]:
        return self.repository.get_user_contexts(username)

    def add_username(self, username: str) -> str:
        username = username.replace('@', '')
        if not username or len(username.split()) > 1:
            log.warning(f'Got invalid username: {username}')
            raise InvalidUsername

        user = self.repository.add_username(username)
        return user.username

    def remove_username(self, username: str) -> str:
        username = username.replace('@', '')
        if not username or len(username.split()) > 1:
            log.warning(f'Got invalid username: {username}')
            raise InvalidUsername

        user = self.repository.remove_username(username)
        return user.username

    def add_context(self, context_name: str, username: str) -> str:
        if len(context_name.split()) > 1:
            raise InvalidContextName
        if not (user := self.get_user_by_username(username)):
            raise Exception

        context = self.repository.add_context(context_name, user.id)
        return context.name

    def remove_context(self, context_id: int) -> str:
        context = self.repository.remove_context(context_id)
        return context.name

    def send_to_chat(self, prompt: str, context_id: int | None = None) -> str:
        if prompt == '':
            log.warning('Empty prompt provided')
            raise EmptyPrompt

        if (length := len(prompt)) > 4096:
            log.warning(f'Got too long prompt (length {length})')
            raise TooLongPrompt

        messages: list[Message] = []
        message = Message(role=Role('user'), content=prompt)

        if context_id:
            messages = self.repository.get_messages_by_context_id(context_id)

        messages.append(message)

        response: ChatCompletionResponse = None

        try:
            response: dict = openai.ChatCompletion.create(
                model=self.model,
                messages=[message.to_dict() for message in messages],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            response: ChatCompletionResponse = ChatCompletionResponse.from_dict(response)
        except openai.error.Timeout:
            log.error(f'Timeout ({self.timeout})')
            raise TimeoutError
        except Exception as e:
            log.error(f'Got unexpected response: {response}', exc_info=e)
            raise UnexpectedResponse

        return response.choices[0].message.content

    def save_message(self, message: Message, context_id: int | None = None, user_id: int | None = None) -> None:
        self.repository.save_message(message, context_id, user_id)
