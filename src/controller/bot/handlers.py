from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from service import Service
from service.exceptions import InvalidUsername, InvalidContextName, UnexpectedResponse, TooLongPrompt

from .routers import router, menu_router, settings_router, chat_router
from .states import UserState
from .utils import UserAction
from . import keyboards


# Root

@router.message(Command(commands=('menu', 'start')))
async def menu(message: Message, state: FSMContext, service: Service):
    await state.set_state(UserState.menu)
    await message.answer('✨ *Menu*', reply_markup=keyboards.get_menu_keyboard())

# ----------- Root


# Menu

@menu_router.callback_query(F.data == 'settings')
async def settings_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    state_data = await state.get_data()
    settings = state_data.get('settings', {})

    context = 'disabled'
    if settings.get('context_enabled', False):
        context = 'enabled'

    reply = '⚙️ *Current settings*\n\n'
    reply += f'📜 `Context: {context}`'

    if context_name := state_data.get('selected_context_name'):
        reply += f' `({context_name})`'

    await state.set_state(UserState.settings)
    await callback.message.edit_text(
        reply,
        reply_markup=keyboards.get_settings_keyboard(
            settings,
            service.is_user_admin(callback.from_user.username)
        ),
    )

@menu_router.callback_query(F.data == 'chat')
async def chat_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    state_data = await state.get_data()

    user = service.get_user_by_username(callback.from_user.username)

    reply = 'Chat mode\n'
    if context_name := state_data.get('selected_context_name'):
        reply += f'Context: `{context_name}`'

    await state.set_state(UserState.chat)
    await state.set_data(state_data | {'user_id': user.id})
    await callback.message.edit_text(
        reply,
        reply_markup=keyboards.get_chat_keyboard(),
    )


# ----------- Menu


# Settings

async def settings(message: Message, state: FSMContext, service: Service):
    state_data = await state.get_data()
    settings = state_data.get('settings', {})

    context = 'disabled'
    if settings.get('context_enabled', False):
        context = 'enabled'

    reply = '⚙️ *Current settings*\n\n'
    reply += f'📜 `Context: {context}`'

    if context_name := state_data.get('selected_context_name'):
        reply += f' `({context_name})`'

    await state.set_state(UserState.settings)
    await message.answer(
        reply,
        reply_markup=keyboards.get_settings_keyboard(
            settings,
            service.is_user_admin(message.from_user.username)
        ),
    )

@settings_router.callback_query(F.data == 'settings')
async def settings_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    state_data = await state.get_data()
    settings = state_data.get('settings', {})

    context = 'disabled'
    if settings.get('context_enabled', False):
        context = 'enabled'

    reply = '⚙️ *Current settings*\n\n'
    reply += f'📜 `Context: {context}`\n'

    if context_name := state_data.get('selected_context_name'):
        reply += f' `({context_name})`'

    await state.set_state(UserState.settings)
    await callback.message.edit_text(
        reply,
        reply_markup=keyboards.get_settings_keyboard(
            settings,
            service.is_user_admin(callback.from_user.username)
        ),
    )

@settings_router.callback_query(F.data == 'menu')
async def menu_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    await state.set_state(UserState.menu)
    await callback.message.edit_text('✨ *Menu*', reply_markup=keyboards.get_menu_keyboard())


@settings_router.callback_query(F.data == UserAction.SWITCH_CONTEXT.value)
async def switch_context_enabled_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    state_data = await state.get_data()
    settings = state_data.get('settings', {})

    settings['context_enabled'] = not settings.get('context_enabled')

    await state.set_data(state_data | {'settings': settings})
    await settings_cb(callback, state, service)


@settings_router.callback_query(F.data == UserAction.LIST_CONTEXTS.value or F.data == UserAction.SELECT_CONTEXT.value)
async def list_contexts_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    contexts = service.get_user_contexts(callback.from_user.username)

    reply = '📜 *Contexts*\n\n'
    if not contexts:
        reply += '`No existing contexts`'

    await callback.message.edit_text(
        reply,
        reply_markup=keyboards.get_contexts_keyboard(contexts),
    )


@settings_router.callback_query(F.data == UserAction.NEW_CONTEXT.value)
async def new_context_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    state_data = await state.get_data()
    await state.set_data(state_data | {'action': UserAction(callback.data)})

    reply = '📜 *Enter the context name*\n\nName should be only one word'

    await callback.message.edit_text(reply, reply_markup=keyboards.get_go_to_settings_keyboard())


@settings_router.callback_query(F.data.startswith(UserAction.REMOVE_CONTEXT.value))
async def remove_context_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    context_id = callback.data.split('|')[1]

    try:
        service.remove_context(context_id)
    except Exception:
        await settings(callback.message, state, service)
        return

    await list_contexts_cb(callback, state, service)


@settings_router.callback_query(F.data.startswith(UserAction.SELECT_CONTEXT.value))
async def select_context_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    context_id = int(callback.data.split('|')[1])
    context_name = callback.data.split('|')[2]

    state_data = await state.get_data()
    await state.set_data(state_data | {
        'selected_context_id': context_id,
        'selected_context_name': context_name,
    })

    await settings_cb(callback, state, service)


@settings_router.callback_query(F.data.in_((UserAction.ADD_USER.value, UserAction.REMOVE_USER.value)))
async def add_or_remove_user_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    state_data = await state.get_data()
    await state.set_data(state_data | {'action': UserAction(callback.data)})

    reply = '⚙️ *Send username*'

    await callback.message.edit_text(reply, reply_markup=keyboards.get_go_to_settings_keyboard())


@settings_router.message()
async def message_handler(message: Message, state: FSMContext, service: Service):
    state_data = await state.get_data()

    action: UserAction = state_data.get('action')

    username = ''
    reply = ''
    context_name = ''

    action_replies = {
        UserAction.ADD_USER: 'Username `{}` added to whitelist',
        UserAction.REMOVE_USER: 'Username `{}` removed from whitelist',
        UserAction.NEW_CONTEXT: 'New context `{}` created',
    }

    try:
        if action == UserAction.ADD_USER:
            try:
                username = service.add_username(message.text)
                reply = action_replies[action].format(username)
            except InvalidUsername:
                await message.reply('Username must be valid')
                raise Exception
        elif action == UserAction.REMOVE_USER:
            try:
                username = service.remove_username(message.text)
                reply = action_replies[action].format(username)
            except InvalidUsername:
                await message.reply('Username must be valid')
                raise Exception
        elif action == UserAction.NEW_CONTEXT:
            try:
                context_name = service.add_context(message.text, message.from_user.username)
                reply = action_replies[action].format(context_name)
            except InvalidContextName:
                await message.reply('Context name must be valid')
                raise Exception
        else:
            raise Exception
    except Exception:
        await settings(message, state, service)
        return

    await message.reply(reply)

    try:
        del state_data['action']
        await state.set_data(state_data)
    except KeyError:
        pass

    await settings(message, state, service)

# ----------- Settings


# Chat

@chat_router.callback_query(F.data == 'menu')
async def menu_cb(callback: CallbackQuery, state: FSMContext, service: Service):
    await state.set_state(UserState.menu)
    await callback.message.edit_text('✨ *Menu*', reply_markup=keyboards.get_menu_keyboard())


@chat_router.message()
async def handle_chat_message(message: Message, state: FSMContext, service: Service) -> str:
    state_data = await state.get_data()

    context_enabled: bool | None = bool(state_data.get('settings', {}).get('context_enabled'))
    context_id: int | None = state_data.get('selected_context_id')
    context_name: str | None = state_data.get('selected_context_name')

    reply_entries = []
    chat_response = ''

    try:
        chat_response = service.send_to_chat(message.text, context_id)
        reply_entries.append(chat_response)
    except TooLongPrompt:
        reply_entries.append('*Your message is too long*')
    except TimeoutError:
        reply_entries.append('*Timeout...* Try again')
    except UnexpectedResponse:
        reply_entries.append('*Internal error.* Try again later')

    if context_enabled:
        reply_entries.append(f'------\nContext: {context_name}')

    await message.reply(
        '\n\n'.join(reply_entries),
        reply_markup=keyboards.get_chat_keyboard(),
        parse_mode=None,
    )

    return chat_response

# ----------- Chat
