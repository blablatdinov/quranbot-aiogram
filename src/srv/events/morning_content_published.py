"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import uuid
from typing import final, override

import attrs
from databases import Database
from eljson.json import Json
from pyeo import elegant

from app_types.listable import FkAsyncListable
from app_types.logger import LogSink
from app_types.update import FkUpdate
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.sendable import SendableAnswer
from integrations.tg.tg_answers import TgAnswer, TgChatIdAnswer, TgHtmlParseAnswer, TgTextAnswer
from integrations.tg.tg_answers.link_preview_options import TgLinkPreviewOptions
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from services.logged_answer import LoggedAnswer
from settings.settings import Settings
from settings.debug_mode import DebugMode
from srv.events.recieved_event import ReceivedEvent
from srv.events.sink import SinkInterface
from srv.users.active_users import PgUpdatedUsersStatus, UpdatedUsersStatusEvent
from srv.users.pg_user import FkUser, User


@final
@attrs.define(frozen=True)
@elegant
class MorningContentPublishedEvent(ReceivedEvent):
    """Обработка события об утренней рассылки с аятми."""

    _empty_answer: TgAnswer
    _pgsql: Database
    _settings: Settings
    _events_sink: SinkInterface
    _log_sink: LogSink

    @override
    async def process(self, json: Json) -> None:
        """Обработка события.

        :param json: Json
        """
        rows = await self._pgsql.fetch_all('\n'.join([
            'SELECT',
            '    u.chat_id,',
            '    STRING_AGG(',
            "        '<b>'",
            '        || a.sura_id::character varying',
            "        || ':'",
            '        || a.ayat_number',
            "        || ')</b> '",
            '        || a.content,',
            "        '\n'",
            '        ORDER BY a.ayat_id',
            '    ) AS content,',
            "    STRING_AGG(s.link, '||' ORDER BY a.ayat_id) AS sura_link",
            'FROM public.ayats AS a',
            'JOIN public.users AS u ON a.day = u.day',
            'JOIN suras AS s ON a.sura_id = s.sura_id',
            "WHERE u.is_active = 't' {0}".format(' AND chat_id = 358610865' if bool(DebugMode(self._settings)) else ''),
            'GROUP BY u.chat_id',
            'ORDER BY u.chat_id',
        ]))
        unsubscribed_users: list[User] = []
        zipped_ans_chat_ids = zip(
            [
                TgLinkPreviewOptions(
                    TgHtmlParseAnswer(
                        TgTextAnswer.str_ctor(
                            TgChatIdAnswer(
                                TgMessageAnswer(self._empty_answer),
                                row['chat_id'],
                            ),
                            '{0}\n\nhttps://umma.ru{1}'.format(row['content'], row['sura_link'].split('||')[0]),
                        ),
                    ),
                    disabled=True,
                )
                for row in rows
            ],
            [row['chat_id'] for row in rows],
            strict=True,
        )
        for answer, chat_id in zipped_ans_chat_ids:
            await self._iteration(answer, chat_id, unsubscribed_users)
        if not unsubscribed_users:
            return
        await UpdatedUsersStatusEvent(
            PgUpdatedUsersStatus(self._pgsql, FkAsyncListable(unsubscribed_users)),
            FkAsyncListable(unsubscribed_users),
            self._events_sink,
        ).update(to=False)

    async def _iteration(self, answer: TgAnswer, chat_id: int, unsubscribed_users: list[User]) -> None:
        try:
            await LoggedAnswer(
                SendableAnswer(
                    answer,
                    self._log_sink,
                ),
                self._events_sink,
                uuid.uuid4(),
            ).send(FkUpdate())
        except TelegramIntegrationsError as err:
            error_messages = [
                'chat not found',
                'bot was blocked by the user',
                'user is deactivated',
            ]
            for error_message in error_messages:
                if error_message in str(err):
                    unsubscribed_users.append(FkUser(chat_id, 0, is_active=False))  # noqa: PERF401
