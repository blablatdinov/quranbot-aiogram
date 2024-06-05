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

import asyncio
import datetime

import pytest

from app_types.update import FkUpdate
from services.user_prayer_keyboard import UserPrayersKeyboard
from srv.prayers.prayer_date import FkPrayerDate
from srv.users.pg_user import PgUser


@pytest.fixture()
async def user(pgsql):
    await pgsql.execute_many(
        'INSERT INTO cities (city_id, name) VALUES (:city_id, :name)',
        [
            {'city_id': city_id, 'name': 'Kazan'}
            for city_id in ('e22d9142-a39b-4e99-92f7-2082766f0987',)
        ],
    )
    await pgsql.execute_many(
        'INSERT INTO users (chat_id, is_active, day, city_id) VALUES (:chat_id, :is_active, :day, :city_id)',
        [
            {'chat_id': 849375, 'is_active': True, 'day': 2, 'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987'},
        ],
    )
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO prayers (prayer_id, name, time, city_id, day)',
            'VALUES (:prayer_id, :prayer_name, :time, :city_id, :day)',
        ]),
        [
            {
                'prayer_id': 1,
                'prayer_name': 'fajr',
                'time': datetime.time(4, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 6, 5),
            },
            {
                'prayer_id': 2,
                'prayer_name': 'sunrise',
                'time': datetime.time(5, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 6, 5),
            },
            {
                'prayer_id': 3,
                'prayer_name': 'dhuhr',
                'time': datetime.time(6, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 6, 5),
            },
            {
                'prayer_id': 4,
                'prayer_name': 'asr',
                'time': datetime.time(7, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 6, 5),
            },
            {
                'prayer_id': 5,
                'prayer_name': 'maghrib',
                'time': datetime.time(8, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 6, 5),
            },
            {
                'prayer_id': 6,
                'prayer_name': "isha'a",
                'time': datetime.time(9, 30),
                'city_id': 'e22d9142-a39b-4e99-92f7-2082766f0987',
                'day': datetime.date(2024, 6, 5),
            },
        ],
    )
    return [
        PgUser.int_ctor(row['chat_id'], pgsql)
        for row in await pgsql.fetch_all('SELECT chat_id FROM users')
    ]


async def test(pgsql, user):
    tasks = [
        UserPrayersKeyboard(
            pgsql,
            FkPrayerDate(datetime.date(2024, 6, 5)),
            849375,
        ).generate(FkUpdate())
        for _ in range(2)
    ]
    with pytest.raises(ValueError, match='Prayers doubled'):
        await asyncio.gather(*tasks)

    assert len(await pgsql.fetch_all('SELECT * FROM prayers_at_user')) == 5
