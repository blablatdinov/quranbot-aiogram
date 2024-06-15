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
from typing import final

import attrs
from asyncpg.exceptions import UniqueViolationError
from databases import Database
from pyeo import elegant

from exceptions.internal_exceptions import PrayerAtUserAlreadyExistsError, PrayerAtUserNotCreatedError
from integrations.tg.chat_id import ChatId
from srv.prayers.new_prayers_at_user import NewPrayersAtUser


@final
@attrs.define(frozen=True)
@elegant
class PgNewPrayersAtUser(NewPrayersAtUser):
    """Новые записи о статусе намаза."""

    _chat_id: ChatId
    _pgsql: Database

    async def create(self, date: datetime.date) -> None:
        """Создать."""
        prayer_group_id = str(uuid.uuid4())
        await self._pgsql.fetch_val(
            'INSERT INTO prayers_at_user_groups VALUES (:prayer_group_id)', {'prayer_group_id': prayer_group_id},
        )
        query = '\n'.join([
            'INSERT INTO prayers_at_user',
            '(user_id, prayer_id, is_read, prayer_group_id)',
            'SELECT',
            '    :chat_id,',
            '    p.prayer_id,',
            '    false,',
            '    :prayer_group_id',
            'FROM prayers AS p',
            'INNER JOIN cities AS c ON p.city_id = c.city_id',
            'INNER JOIN users AS u ON u.city_id = c.city_id',
            "WHERE p.day = :date AND u.chat_id = :chat_id AND p.name <> 'sunrise'",
            'ORDER BY',
            "    ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
            'RETURNING *',
        ])
        try:
            created_prayers = await self._pgsql.fetch_all(query, {
                'chat_id': int(self._chat_id),
                'prayer_group_id': prayer_group_id,
                'date': date,
            })
        except UniqueViolationError as err:
            raise PrayerAtUserAlreadyExistsError from err
        if not created_prayers:
            raise PrayerAtUserNotCreatedError
