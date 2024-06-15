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

# TODO #899 Перенести классы в отдельные файлы 34

from typing import Final, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.stringable import AsyncSupportsStr
from app_types.update import Update
from exceptions.content_exceptions import UserHasNotCityIdError
from exceptions.prayer_exceptions import PrayersNotFoundError
from integrations.nominatim import CityNameById
from integrations.tg.chat_id import ChatId
from srv.prayers.prayer_date import PrayerDate

TIME_LITERAL: Final = 'time'


@final
@attrs.define(frozen=True)
@elegant
class UserCityId(AsyncSupportsStr):
    """Идентификатор города."""

    _pgsql: Database
    _chat_id: ChatId

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        query = '\n'.join([
            'SELECT c.city_id',
            'FROM cities AS c',
            'INNER JOIN users AS u ON u.city_id = c.city_id',
            'WHERE u.chat_id = :chat_id',
        ])
        city_name = await self._pgsql.fetch_val(query, {'chat_id': int(self._chat_id)})
        if not city_name:
            raise UserHasNotCityIdError
        return city_name


@final
@attrs.define(frozen=True)
@elegant
class PrayersText(AsyncSupportsStr):
    """Текст сообщения с намазами."""

    _pgsql: Database
    _date: PrayerDate
    _city_id: AsyncSupportsStr
    _update: Update

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        query = '\n'.join([
            'SELECT',
            '    c.name AS city_name,',
            '    p.day,',
            '    p.time,',
            '    p.name',
            'FROM prayers AS p',
            'INNER JOIN cities AS c ON p.city_id = c.city_id',
            'WHERE p.day = :date AND c.city_id = :city_id',
            'ORDER BY',
            "    ARRAY_POSITION(ARRAY['fajr', 'sunrise', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        rows = await self._pgsql.fetch_all(query, {
            'date': await self._date.parse(self._update),
            'city_id': await self._city_id.to_str(),
        })
        if not rows:
            raise PrayersNotFoundError(
                await CityNameById(self._pgsql, self._city_id).to_str(),
                await self._date.parse(self._update),
            )
        template = '\n'.join([
            'Время намаза для г. {city_name} ({date})\n',
            'Иртәнге: {fajr_prayer_time}',
            'Восход: {sunrise_prayer_time}',
            'Өйлә: {dhuhr_prayer_time}',
            'Икенде: {asr_prayer_time}',
            'Ахшам: {magrib_prayer_time}',
            'Ястү: {ishaa_prayer_time}',
        ])
        time_format = '%H:%M'
        return template.format(
            city_name=rows[0]['city_name'],
            date=rows[0]['day'].strftime('%d.%m.%Y'),
            fajr_prayer_time=rows[0][TIME_LITERAL].strftime(time_format),
            sunrise_prayer_time=rows[1][TIME_LITERAL].strftime(time_format),
            dhuhr_prayer_time=rows[2][TIME_LITERAL].strftime(time_format),
            asr_prayer_time=rows[3][TIME_LITERAL].strftime(time_format),
            magrib_prayer_time=rows[4][TIME_LITERAL].strftime(time_format),
            ishaa_prayer_time=rows[5][TIME_LITERAL].strftime(time_format),
        )
