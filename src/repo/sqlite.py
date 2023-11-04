import sqlite3
import logging
from contextlib import closing

from models import Message, Context, User

from .repo import Repository


log = logging.getLogger('repository')
DB_PATH = '../db.sqlite'

class SQLite(Repository):
    def __init__(self) -> None:
        self.connection = sqlite3.connect(DB_PATH)
        self.connection.row_factory = sqlite3.Row
        self.init_db_structure()

    def init_db_structure(self) -> None:
        with closing(self.connection.cursor()) as cursor:
            with open('../sql/db_init.sql') as db_init:
                cursor.executescript(db_init.read())

        self.connection.commit()

    def is_user_exists(self, username: str) -> bool:
        if not isinstance(username, str):
            log.warning(f'Got non str username: {username}')
            return False

        username = username.split()[0]
        username = username.replace(';', '')

        sql = 'select exists(select 1 from Users u where u.username = ?);'

        exists = False

        with closing(self.connection.cursor()) as cursor:
            exists = cursor.execute(sql, (username,)).fetchone()[0]

        return bool(exists)

    def get_user_by_username(self, username: str) -> User:
        if not isinstance(username, str):
            log.warning(f'Got non str username: {username}')
            return None

        username = username.split()[0]
        username = username.replace(';', '')

        sql = 'select * from Users where username = ?;'

        user: User = None

        with closing(self.connection.cursor()) as cursor:
            raw_result = cursor.execute(sql, (username,))

            user = User.from_dict(dict(raw_result.fetchone()))

        return user

    def is_user_admin(self, username: str) -> bool:
        if not isinstance(username, str):
            log.warning(f'Got non str username: {username}')
            return False

        username = username.split()[0]
        username = username.replace(';', '')

        sql = 'select exists(select 1 \
                    from Admins a \
                    join Users u on a.user_id = u.id \
                    where u.username = ? \
                );'

        is_admin = False

        with closing(self.connection.cursor()) as cursor:
            is_admin = cursor.execute(sql, (username,)).fetchone()[0]

        return bool(is_admin)

    def get_user_contexts(self, username: str) -> list[Context]:
        if not isinstance(username, str):
            log.warning(f'Got non str username: {username}')
            return False

        username = username.split()[0]
        username = username.replace(';', '')

        contexts: list[Context] = []

        sql = 'select c.id, c.user_id, c.name \
            from Contexts c \
            join Users u on c.user_id = u.id \
            where u.username = ?;'

        with closing(self.connection.cursor()) as cursor:
            raw_result = cursor.execute(sql, (username,))

            for row in raw_result.fetchall():
                contexts.append(
                    Context.from_dict(dict(row))
                )

        return contexts

    def add_username(self, username: str) -> User:
        if not isinstance(username, str):
            log.warning(f'Got non string username: {username}')
            return ''

        sql = 'insert into Users (username) values (?) returning *;'

        user: User = None

        try:
            with closing(self.connection.cursor()) as cursor:
                raw_result = cursor.execute(sql, (username,))
                user = User.from_dict(dict(raw_result.fetchone()))

            self.connection.commit()
        except Exception as e:
            log.error('Got an error on add_username', exc_info=e)
            return None

        return user

    def remove_username(self, username: str) -> User:
        if not isinstance(username, str):
            log.warning(f'Got non string username: {username}')
            return ''

        sql = 'delete from Users where username = ? returning *;'

        user: User = None

        try:
            with closing(self.connection.cursor()) as cursor:
                raw_result = cursor.execute(sql, (username,))
                user = User.from_dict(dict(raw_result.fetchone()))

            self.connection.commit()
        except Exception as e:
            log.error('Got an error on remove_username', exc_info=e)
            return None

        return user

    def add_context(self, context_name: str, user_id: int) -> Context:
        context: Context = None

        sql = 'insert into Contexts (user_id, name) values (?, ?) returning *;'

        try:
            with closing(self.connection.cursor()) as cursor:
                raw_result = cursor.execute(sql, (user_id, context_name))
                context = Context.from_dict(dict(raw_result.fetchone()))

            self.connection.commit()
        except Exception as e:
            log.error('Got an error on add_context', exc_info=e)
            return None

        return context

    def remove_context(self, context_id: int) -> Context:
        context: Context = None

        sql = 'delete from Contexts where id = ? returning *;'

        try:
            with closing(self.connection.cursor()) as cursor:
                raw_result = cursor.execute(sql, (context_id,))
                context = Context.from_dict(dict(raw_result.fetchone()))

            self.connection.commit()
        except Exception as e:
            log.error('Got an error on remove_context', exc_info=e)
            return None

        return context

    def get_messages_by_context_id(self, context_id: int) -> list[Message]:
        if not isinstance(context_id, int):
            log.warning(f'Got non integer context_id: {context_id}')
            return []

        messages: list[Message] = []

        sql = 'select id, role, content \
            from ContextMessages cm \
            where cm.context_id = ?;'

        with closing(self.connection.cursor()) as cursor:
            raw_result = cursor.execute(sql, (context_id,))

            for row in raw_result.fetchall():
                messages.append(
                    Message.from_dict(dict(row))
                )

        return messages

    def save_message(self, message: Message, context_id: int | None = None, user_id: int | None = None) -> Message:
        try:
            sql = ''
            if context_id:
                sql = 'insert into ContextMessages (context_id, role, content) values (?, ?, ?)'

                with closing(self.connection.cursor()) as cursor:
                    cursor.execute(sql, (context_id, message.role.value, message.content))
            else:
                sql = 'insert into StandaloneMessages (user_id, content) values (?, ?)'

                with closing(self.connection.cursor()) as cursor:
                    cursor.execute(sql, (user_id, message.content))

            self.connection.commit()
        except Exception as e:
            log.error('Got an error on save_message', exc_info=e)

        return message
