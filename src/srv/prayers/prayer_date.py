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

# TODO #899 Перенести классы в отдельные файлы 35

import datetime
from contextlib import suppress
from typing import Protocol, final, override

import attrs
import pytz
from databases import Database
from pyeo import elegant

from app_types.update import Update
from integrations.tg.message_text import MessageText
from srv.prayers.prayer_status import PrayerStatus


@elegant
class PrayerDate(Protocol):
    """Дата времен намаза."""

    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения."""


@final
@attrs.define(frozen=True)
@elegant
class FkPrayerDate(PrayerDate):
    """Фейковая дата времен намаза."""

    _origin: datetime.date

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения."""
        return self._origin


@final
@attrs.define(frozen=True)
@elegant
class PrayersRequestDate(PrayerDate):
    """Дата намаза."""

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения."""
        date = str(MessageText(update)).split(' ')[-1]
        if date == 'намаза':
            return datetime.datetime.now(pytz.timezone('Europe/Moscow')).date()
        formats = ('%d.%m.%Y', '%d-%m-%Y')  # noqa: WPS323 not string formatting
        for fmt in formats:
            with suppress(ValueError):
                return datetime.datetime.strptime(date, fmt).astimezone(
                    pytz.timezone('Europe/Moscow'),
                ).date()
        msg = "time data '{0}' does not match formats {1}".format(date, formats)
        raise ValueError(msg)


@final
@attrs.define(frozen=True)
@elegant
class PrayersMarkAsDate(PrayerDate):
    """Дата намаза при редактировании."""

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из текста сообщения."""
        msg_first_line = str(MessageText(update)).split('\n')[0]
        date = msg_first_line.split(' ')[-1][1:-1]
        return (
            datetime.datetime
            .strptime(date, '%d.%m.%Y')  # noqa: WPS323 not string formatting
            .astimezone(pytz.timezone('Europe/Moscow'))
            .date()
        )


@final
@attrs.define(frozen=True)
@elegant
class DateFromUserPrayerId(PrayerDate):
    """Дата намаза по идентификатору времени намаза."""

    _pgsql: Database

    @override
    async def parse(self, update: Update) -> datetime.date:
        """Парсинг из идентификатора времени намаза."""
        query = '\n'.join([
            'SELECT prayers.day',
            'FROM prayers_at_user',
            'INNER JOIN prayers ON prayers_at_user.prayer_id = prayers.prayer_id',
            'WHERE prayer_at_user_id = :prayer_at_user_id',
        ])
        return await self._pgsql.fetch_val(query, {
            'prayer_at_user_id': PrayerStatus.update_ctor(update).user_prayer_id(),
        })
