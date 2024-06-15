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
import ujson
from databases import Database
from pyeo import elegant

from app_types.update import Update
from exceptions.internal_exceptions import PrayerAtUserAlreadyExistsError
from integrations.tg.chat_id import ChatId
from services.answers.answer import KeyboardInterface
from srv.prayers.exist_user_prayers import PgExistUserPrayers
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser
from srv.prayers.prayer_date import PrayerDate


@final
@attrs.define(frozen=True)
@elegant
class UserPrayersKeyboard(KeyboardInterface):
    """Клавиатура времен намаза."""

    _pgsql: Database
    _date: PrayerDate
    _chat_id: ChatId

    @override
    async def generate(self, update: Update) -> str:
        """Генерация."""
        with suppress(PrayerAtUserAlreadyExistsError):
            await PgNewPrayersAtUser(
                self._chat_id,
                self._pgsql,
            ).create(await self._date.parse(update))
        prayers = await PgExistUserPrayers(
            self._pgsql,
            self._chat_id,
            await self._date.parse(update),
        ).fetch()
        return ujson.dumps({
            'inline_keyboard': [[
                {
                    'text': '✅' if user_prayer['is_read'] else '❌',
                    'callback_data': ('mark_not_readed({0})' if user_prayer['is_read'] else 'mark_readed({0})').format(
                        user_prayer['prayer_at_user_id'],
                    ),
                }
                for user_prayer in prayers
            ]],
        })
