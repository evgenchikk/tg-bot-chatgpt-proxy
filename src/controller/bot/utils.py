from enum import Enum


class UserAction(Enum):
    ADD_USER = 'add_user'
    REMOVE_USER = 'remove_user'
    SWITCH_CONTEXT = 'switch_context'
    SELECT_CONTEXT = 'select_context'
    LIST_CONTEXTS = 'list_contexts'
    NEW_CONTEXT = 'new_context'
    SET_CONTEXT = 'set_context'
    REMOVE_CONTEXT = 'remove_context'
