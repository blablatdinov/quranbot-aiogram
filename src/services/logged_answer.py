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

import datetime
import uuid
from typing import Final, final, override

import attrs
import pytz
import ujson
from pyeo import elegant

from app_types.update import Update
from integrations.tg.sendable import SendableInterface
from srv.events.sink import SinkInterface

MESSAGE_LITERAL: Final = 'message'
UPDATES_LOG: Final = 'qbot_admin.updates_log'
CALLBACK_QUERY: Final = 'callback_query'
MESSAGES: Final = 'messages'
MESSAGE_JSON: Final = 'message_json'
IS_UNKNOWN: Final = 'is_unknown'
TRIGGER_MESSAGE_ID: Final = 'trigger_message_id'
TRIGGER_CALLBACK_ID: Final = 'trigger_callback_id'
MAILING_ID: Final = 'mailing_id'
MESSAGES_CREATED: Final = 'Messages.Created'


@final
@attrs.define(frozen=True)
@elegant
class LoggedAnswer(SendableInterface):
    """Декоратор логирующий сообщения."""

    _origin: SendableInterface
    _event_sink: SinkInterface
    _mailing_id: uuid.UUID | None = None

    @override
    async def send(self, update: Update) -> list[dict]:  # noqa: WPS217, WPS231
        """Отправка."""
        if update.asdict().get(MESSAGE_LITERAL):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [{
                        MESSAGE_JSON: ujson.dumps(update.asdict()[MESSAGE_LITERAL]),
                        IS_UNKNOWN: False,
                        TRIGGER_MESSAGE_ID: None,
                        TRIGGER_CALLBACK_ID: None,
                        MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                    }],
                },
                MESSAGES_CREATED,
                1,
            )
        elif update.asdict().get(CALLBACK_QUERY):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    'json': str(update),
                    'timestamp': datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')).isoformat(),
                },
                'Button.Pushed',
                1,
            )
        sent_answers = await self._origin.send(update)
        if update.asdict().get(MESSAGE_LITERAL):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [
                        {
                            MESSAGE_JSON: ujson.dumps(answer['result']),
                            IS_UNKNOWN: False,
                            TRIGGER_MESSAGE_ID: update.asdict()[MESSAGE_LITERAL]['message_id'],
                            TRIGGER_CALLBACK_ID: None,
                            MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                        }
                        for answer in sent_answers
                    ],
                },
                MESSAGES_CREATED,
                1,
            )
            return sent_answers
        elif update.asdict().get(CALLBACK_QUERY):
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [
                        {
                            MESSAGE_JSON: ujson.dumps(answer['result']),
                            IS_UNKNOWN: False,
                            TRIGGER_MESSAGE_ID: None,
                            TRIGGER_CALLBACK_ID: update.asdict()[CALLBACK_QUERY]['id'],
                            MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                        }
                        for answer in sent_answers
                    ],
                },
                MESSAGES_CREATED,
                1,
            )
        else:
            await self._event_sink.send(
                UPDATES_LOG,
                {
                    MESSAGES: [
                        {
                            MESSAGE_JSON: ujson.dumps(answer['result']),
                            IS_UNKNOWN: False,
                            TRIGGER_MESSAGE_ID: None,
                            TRIGGER_CALLBACK_ID: None,
                            MAILING_ID: str(self._mailing_id) if self._mailing_id else None,
                        }
                        for answer in sent_answers
                    ],
                },
                MESSAGES_CREATED,
                1,
            )
        return sent_answers
