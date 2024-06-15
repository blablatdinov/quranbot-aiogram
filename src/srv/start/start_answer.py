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

# TODO #899 Перенести классы в отдельные файлы 40

from collections.abc import Sequence
from typing import Protocol, final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant

from app_types.intable import FkAsyncIntable
from app_types.logger import LogSink
from app_types.update import Update
from exceptions.internal_exceptions import UserNotFoundError
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswer, TgAnswerList, TgAnswerToSender, TgChatIdAnswer, TgTextAnswer
from integrations.tg.tg_datetime import TgDateTime
from srv.admin_messages.admin_message import AdminMessage
from srv.ayats.pg_ayat import PgAyat
from srv.events.sink import SinkInterface
from srv.start.start_message import AsyncIntOrNone, FkAsyncIntOrNone, ReferrerChatId, ReferrerIdOrNone
from srv.users.new_user import PgNewUser, PgNewUserWithEvent


class NewTgUserT(Protocol):
    """Registration of user."""

    async def create(self, referrer_chat_id: AsyncIntOrNone) -> None:
        """Creation."""


@final
@attrs.define(frozen=True)
@elegant
class NewTgUser(NewTgUserT):
    """Registration of user by tg."""

    _pgsql: Database
    _logger: LogSink
    _event_sink: SinkInterface
    _update: Update

    @override
    async def create(self, referrer_chat_id: AsyncIntOrNone) -> None:
        """Creation."""
        try:
            await PgNewUserWithEvent(
                PgNewUser(
                    referrer_chat_id,
                    TgChatId(self._update),
                    self._pgsql,
                    self._logger,
                ),
                self._event_sink,
                TgChatId(self._update),
                TgDateTime(self._update),
            ).create()
        except UserNotFoundError:
            referrer_chat_id = FkAsyncIntOrNone(None)
            await PgNewUserWithEvent(
                PgNewUser(
                    referrer_chat_id,
                    TgChatId(self._update),
                    self._pgsql,
                    self._logger,
                ),
                self._event_sink,
                TgChatId(self._update),
                TgDateTime(self._update),
            ).create()


@final
@attrs.define(frozen=True)
@elegant
class StartAnswer(TgAnswer):
    """Обработчик стартового сообщения."""

    _origin: TgAnswer
    _admin_message: AdminMessage
    _new_tg_user: NewTgUserT
    _pgsql: Database
    _admin_chat_ids: Sequence[int]

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ."""
        referrer_chat_id: AsyncIntOrNone = ReferrerIdOrNone(
            ReferrerChatId(
                str(MessageText(update)),
                self._pgsql,
            ),
        )
        start_message = self._admin_message
        ayat_message = PgAyat(FkAsyncIntable(1), self._pgsql)
        await self._new_tg_user.create(referrer_chat_id)
        referrer_chat_id_calculated = await referrer_chat_id.to_int()
        if referrer_chat_id_calculated:
            return await TgAnswerList(
                TgAnswerToSender(
                    TgTextAnswer(
                        self._origin,
                        start_message,
                    ),
                ),
                TgAnswerToSender(
                    TgTextAnswer(
                        self._origin,
                        ayat_message,
                    ),
                ),
                TgChatIdAnswer(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        'По вашей реферальной ссылке произошла регистрация',
                    ),
                    referrer_chat_id_calculated,
                ),
                TgChatIdAnswer(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        'Зарегистрировался новый пользователь',
                    ),
                    self._admin_chat_ids[0],
                ),
            ).build(update)
        return await TgAnswerList(
            TgAnswerToSender(
                TgTextAnswer(
                    self._origin,
                    start_message,
                ),
            ),
            TgAnswerToSender(
                TgTextAnswer(
                    self._origin,
                    ayat_message,
                ),
            ),
            TgChatIdAnswer(
                TgTextAnswer.str_ctor(
                    self._origin,
                    'Зарегистрировался новый пользователь',
                ),
                self._admin_chat_ids[0],
            ),
        ).build(update)
