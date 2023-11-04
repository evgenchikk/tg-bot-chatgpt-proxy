from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

from models import Context

from .utils import UserAction


def get_root_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='/menu')]],
        resize_keyboard=True,
    )


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='settings', callback_data='settings'))
    builder.row(InlineKeyboardButton(text='chat mode', callback_data='chat'))

    return builder.as_markup()


def get_settings_keyboard(settings: dict, is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not settings.get('context_enabled'):
        builder.add(InlineKeyboardButton(text='enable context', callback_data=UserAction.SWITCH_CONTEXT.value))
    else:
        builder.add(InlineKeyboardButton(text='disable context', callback_data=UserAction.SWITCH_CONTEXT.value))
        builder.row(
            InlineKeyboardButton(text='list contexts', callback_data=UserAction.LIST_CONTEXTS.value),
            InlineKeyboardButton(text='new context', callback_data=UserAction.NEW_CONTEXT.value),
        )

    if is_admin:
        builder.row(
            InlineKeyboardButton(text='add user', callback_data=UserAction.ADD_USER.value),
            InlineKeyboardButton(text='remove user', callback_data=UserAction.REMOVE_USER.value)
        )

    builder.row(InlineKeyboardButton(text='menu', callback_data='menu'))

    return builder.as_markup()


def get_contexts_keyboard(contexts: list[Context]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for c in contexts:
        builder.row(
            InlineKeyboardButton(text=c.name, callback_data=UserAction.SET_CONTEXT.value),
            InlineKeyboardButton(text='🗑', callback_data=f'{UserAction.REMOVE_CONTEXT.value}|{c.id}'),
            InlineKeyboardButton(text='✅', callback_data=f'{UserAction.SELECT_CONTEXT.value}|{c.id}|{c.name}'),
        )

    builder.row(InlineKeyboardButton(text='🔙', callback_data='settings'))

    return builder.as_markup()


def get_go_to_settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='🔙', callback_data='settings')]]
    )


def get_chat_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='menu', callback_data='menu'))

    return builder.as_markup()
