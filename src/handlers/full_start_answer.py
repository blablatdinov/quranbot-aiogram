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

from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgHtmlParseAnswer, TgMessageAnswer
from services.answers.answer import DefaultKeyboard, ResizedKeyboard
from services.reset_state_answer import ResetStateAnswer
from services.user_state import CachedUserState, RedisUserState
from settings import Settings
from srv.admin_messages.pg_admin_message import PgAdminMessage
from srv.events.sink import SinkInterface
from srv.start.start_answer import NewTgUser, StartAnswer
from srv.start.user_already_active import UserAlreadyActiveSafeAnswer
from srv.start.user_already_exists import UserAlreadyExistsAnswer


@attrs.define(frozen=True)
@final
@elegant
class FullStartAnswer(TgAnswer):
    """Ответ на команду /start."""

    _pgsql: Database
    _empty_answer: TgAnswer
    _event_sink: SinkInterface
    _redis: Redis
    _settings: Settings
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        return await ResetStateAnswer(
            TgAnswerMarkup(
                UserAlreadyActiveSafeAnswer(
                    UserAlreadyExistsAnswer(
                        StartAnswer(
                            TgHtmlParseAnswer(
                                TgMessageAnswer(self._empty_answer),
                            ),
                            PgAdminMessage('start', self._pgsql),
                            NewTgUser(
                                self._pgsql,
                                self._logger,
                                self._event_sink,
                                update,
                            ),
                            self._pgsql,
                            self._settings.admin_chat_ids(),
                        ),
                        answer_to_sender,
                        self._pgsql,
                        self._event_sink,
                    ),
                    answer_to_sender,
                ),
                ResizedKeyboard(
                    DefaultKeyboard(),
                ),
            ),
            CachedUserState(RedisUserState(self._redis, TgChatId(update), self._logger)),
        ).build(update)
