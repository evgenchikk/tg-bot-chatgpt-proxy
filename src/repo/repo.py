from abc import ABC

from models import Message, Context, User


class Repository(ABC):
    def is_user_exists(self, username: str) -> bool:
        pass

    def get_user_by_username(self, username: str) -> User:
        pass

    def is_user_admin(self, username: str) -> bool:
        pass

    def get_user_contexts(self, username: str) -> list[Context]:
        pass

    def add_username(self, username: str) -> User:
        pass

    def remove_username(self, username: str) -> User:
        pass

    def add_context(self, context_name: str, user_id: int) -> Context:
        pass

    def remove_context(self, context_id: int) -> Context:
        pass

    def get_messages_by_context_id(self, context_id: int) -> list[Message]:
        pass

    def save_message(self, message: Message, context_id: int | None = None, user_id: int | None = None) -> Message:
        pass
