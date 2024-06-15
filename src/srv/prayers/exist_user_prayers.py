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

# TODO #899 Перенести классы в отдельные файлы 33

import datetime
from typing import Protocol, TypedDict, final, override

import attrs
from databases import Database
from pyeo import elegant

from integrations.tg.chat_id import ChatId


class _ExistUserPrayersDict(TypedDict):

    prayer_at_user_id: int
    is_read: bool


class ExistUserPrayers(Protocol):
    """Существующие времена намаза у пользователя."""

    async def fetch(self) -> list[_ExistUserPrayersDict]:
        """Получить."""


@final
@attrs.define(frozen=True)
@elegant
class PgExistUserPrayers(ExistUserPrayers):
    """Существующие времена намаза у пользователя."""

    _pgsql: Database
    _chat_id: ChatId
    _date: datetime.date

    @override
    async def fetch(self) -> list[_ExistUserPrayersDict]:
        """Получить."""
        select_query = '\n'.join([
            'SELECT',
            '    pau.prayer_at_user_id,',
            '    pau.is_read',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p on pau.prayer_id = p.prayer_id',
            "WHERE p.day = :date AND pau.user_id = :chat_id AND p.name <> 'sunrise'",
            'ORDER BY pau.prayer_at_user_id',
        ])
        return [
            {
                'prayer_at_user_id': record['prayer_at_user_id'],
                'is_read': record['is_read'],
            }
            for record in await self._pgsql.fetch_all(select_query, {
                'date': self._date,
                'chat_id': int(self._chat_id),
            })
        ]
