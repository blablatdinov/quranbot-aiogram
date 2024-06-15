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
from typing import final, override

import attrs
import pytz
from databases import Database
from eljson.json import Json
from loguru import logger
from pyeo import elegant

from srv.events.recieved_event import ReceivedEvent


@final
@attrs.define(frozen=True)
@elegant
class PrayerCreatedEvent(ReceivedEvent):
    """Событие создания аята из rabbitmq."""

    _pgsql: Database

    @override
    async def process(self, json: Json) -> None:
        """Обработка события."""
        query = '\n'.join([
            'INSERT INTO prayers (name, time, city_id, day) VALUES',
            '(:name, :time, :city_id, :day)',
        ])
        await self._pgsql.execute(
            query,
            {
                'name': json.path('$.data.name')[0],
                'time': datetime.datetime.strptime(json.path('$.data.time')[0], '%H:%M').replace(
                    tzinfo=pytz.timezone('Europe/Moscow'),
                ),
                'city_id': json.path('$.data.city_id')[0],
                'day': datetime.datetime.strptime(json.path('$.data.day')[0], '%Y-%m-%d').astimezone(
                    pytz.timezone('Europe/Moscow'),
                ),
            },
        )
        logger.info('Prayer created')
