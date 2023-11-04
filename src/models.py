from enum import Enum

from attrs import define


class Role(Enum):
    user = 'user'
    assistant = 'assistant'


@define
class User:
    id: int
    tg_internal_id: int | None
    username: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            tg_internal_id=data.get('tg_internal_id'),
            username=data['username'],
        )


@define
class Context:
    id: int
    user_id: int
    name: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            name=data.get('name', ''),
        )


@define
class Message:
    role: Role
    content: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            role=Role(data['role']),
            content=data['content'],
        )

    def to_dict(self) -> dict:
        return {
            'role': self.role.value,
            'content': self.content,
        }


@define
class ChatCompletionResponseUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            prompt_tokens=data['prompt_tokens'],
            completion_tokens=data['completion_tokens'],
            total_tokens=data['total_tokens'],
        )


@define
class ChatCompletionResponseChoice:
    index: int
    message: Message
    finish_reason: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            index=data['index'],
            message=Message.from_dict(data['message']),
            finish_reason=data['finish_reason'],
        )


@define
class ChatCompletionResponse:
    id: str
    object: str
    created: int
    model: str
    choices: list[ChatCompletionResponseChoice]
    usage: ChatCompletionResponseUsage

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            object=data['object'],
            created=data['created'],
            model=data['model'],
            choices=[ChatCompletionResponseChoice.from_dict(choice) for choice in data['choices']],
            usage=ChatCompletionResponseUsage.from_dict(data['usage']),
        )
