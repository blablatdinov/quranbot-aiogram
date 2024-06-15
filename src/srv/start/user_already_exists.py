# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from contextlib import suppress
from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant

from app_types.update import Update
from exceptions.user import UserAlreadyActiveError, UserAlreadyExistsError
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer
from integrations.tg.tg_datetime import TgDateTime
from srv.events.sink import SinkInterface
from srv.users.active_users import PgUpdatedUsersStatus, PgUsers
from srv.users.pg_user import PgUser
from srv.users.valid_chat_id import PgValidChatId


@final
@attrs.define(frozen=True)
@elegant
class UserAlreadyExistsAnswer(TgAnswer):
    """Декоратор обработчика стартового сообщение с предохранением от UserAlreadyExists."""

    _origin: TgAnswer
    _sender_answer: TgAnswer
    _pgsql: Database
    _event_sink: SinkInterface

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ."""
        with suppress(UserAlreadyExistsError):
            return await self._origin.build(update)
        user = PgUser(PgValidChatId.int_ctor(self._pgsql, TgChatId(update)), self._pgsql)
        await self._update_and_push_event(update)
        if await user.is_active():
            raise UserAlreadyActiveError
        return await TgTextAnswer.str_ctor(
            self._sender_answer,
            'Рады видеть вас снова, вы продолжите с дня {0}'.format(await user.day()),
        ).build(update)

    async def _update_and_push_event(self, update: Update) -> None:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_update_and_push_event"
        await PgUpdatedUsersStatus(
            self._pgsql,
            PgUsers(self._pgsql, [int(TgChatId(update))]),
        ).update(to=True)
        await self._event_sink.send(
            'qbot_admin.users',
            {
                'user_id': int(TgChatId(update)),
                'date_time': str(TgDateTime(update).datetime()),
            },
            'User.Reactivated',
            1,
        )
