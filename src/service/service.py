from abc import ABC

from repo import Repository
from models import User, Context, Message


class Service(ABC):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def is_user_exists(self, username: str) -> bool:
        pass

    def is_user_admin(self, username: str) -> bool:
        pass

    def get_user_by_username(self, username: str) -> User:
        pass

    def get_user_contexts(self, username: str) -> list[Context]:
        pass

    def add_username(self, username: str) -> str:
        pass

    def remove_username(self, username: str) -> str:
        pass

    def add_context(self, context_name: str, username: int) -> str:
        pass

    def remove_context(self, context_id: int) -> str:
        pass

    def send_to_chat(self, prompt: str, context_id: int | None = None) -> str:
        pass

    def save_message(self, message: Message, context_id: int | None = None, user_id: int | None = None) -> None:
        pass
