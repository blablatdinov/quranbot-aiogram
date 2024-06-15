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

from typing import final

import attrs
import httpx
from databases import Database
from pyeo import elegant

from app_types.update import Update
from handlers.skipped_prayers_answer import PrayersStatistic, SkippedPrayersKeyboard
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_id import TgMessageId
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgMessageIdAnswer, TgTextAnswer
from integrations.tg.tg_answers.edit_message_text import TgEditMessageText
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser


@final
@attrs.define(frozen=True)
@elegant
class DecrementSkippedPrayerAnswer(TgAnswer):
    """Уменьшение кол-ва пропущенных намазов."""

    _empty_answer: TgAnswer
    _pgsql: Database

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        query = '\n'.join([
            'UPDATE prayers_at_user AS pau',
            "SET is_read = 't'",
            'WHERE pau.prayer_at_user_id = (',
            '   SELECT pau.prayer_at_user_id',
            '   FROM prayers AS p',
            '   INNER JOIN prayers_at_user AS pau ON pau.prayer_id = p.prayer_id',
            "   WHERE p.name = :prayer_name AND pau.is_read = 'f' AND pau.user_id = :chat_id",
            '   LIMIT 1',
            ')',
            'RETURNING *',
        ])
        await self._pgsql.execute(query, {
            'chat_id': int(TgChatId(update)),
            'prayer_name': str(
                CallbackQueryData(update),
            ).split('(')[1][:-1],
        })
        return await TgAnswerMarkup(
            TgMessageIdAnswer(
                TgTextAnswer(
                    TgEditMessageText(
                        TgAnswerToSender(
                            self._empty_answer,
                        ),
                    ),
                    PrayersStatistic(
                        PgNewPrayersAtUser(TgChatId(update), self._pgsql),
                        TgChatId(update),
                        self._pgsql,
                    ),
                ),
                TgMessageId(update),
            ),
            SkippedPrayersKeyboard(),
        ).build(update)
