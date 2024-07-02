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
from itertools import chain

import httpx
import pytest
import pytz
from telethon import functions, types


@pytest.fixture()
def _user_city(tg_client, db_conn, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    wait_until(tg_client, 3)
    db_cursor = db_conn.cursor()
    db_cursor.execute(
        'UPDATE users SET city_id = %s WHERE chat_id = %s',
        ('bc932b25-707e-4af1-8b6e-facb5e6dfa9b', 5354079702),
    )
    db_conn.commit()


@pytest.fixture()
def expected_message():
    date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    dumrt_response = httpx.get(
        'http://dumrt.ru/netcat_files/482/640/Kazan.csv?t={0}'.format(date.strftime('%d%m%y')),
    ).text
    for line in dumrt_response.strip().split('\n'):
        elems = line.strip().split(';')
        if date.strftime('%d.%m.%Y') == elems[0]:
            return '\n'.join([
                'Время намаза для г. Казань ({0})'.format(date.strftime('%d.%m.%Y')),
                '',
                'Иртәнге: {0}',
                'Восход: {1}',
                'Өйлә: {2}',
                'Икенде: {3}',
                'Ахшам: {4}',
                'Ястү: {5}',
            ]).format(
                *[
                    (
                        datetime.datetime
                        .strptime(elems[idx], '%H:%M')
                        .replace(tzinfo=pytz.timezone('Europe/Moscow'))
                        .strftime('%H:%M')
                    )
                    for idx in (1, 3, 5, 6, 7, 8)
                ],
            )
    msg = 'Prayers on dumrt not found'
    raise ValueError(msg)


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user_city')
def test_prayer_times(tg_client, bot_name, expected_message, wait_until):
    tg_client.send_message(bot_name, 'Время намаза')
    messages = wait_until(tg_client, 5)

    assert messages[0].message == expected_message


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user_city')
@pytest.mark.flaky(retries=3)
def test_mark_as_readed(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Время намаза')
    messages = wait_until(tg_client, 5)
    list(chain.from_iterable(
        button_row for button_row in messages[0].get_buttons()
    ))[1].click()
    messages = wait_until(tg_client, 5)

    assert [
        (button.text, button.data)
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == [
        ('❌', b'mark_readed(1)'),
        ('✅', b'mark_not_readed(2)'),
        ('❌', b'mark_readed(3)'),
        ('❌', b'mark_readed(4)'),
        ('❌', b'mark_readed(5)'),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user_city')
@pytest.mark.flaky(retries=3)
def test_mark_not_readed(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Время намаза')
    messages = wait_until(tg_client, 5)
    list(chain.from_iterable(
        button_row for button_row in messages[0].get_buttons()
    ))[1].click()
    messages = wait_until(tg_client, 5)
    list(chain.from_iterable(
        button_row for button_row in messages[0].get_buttons()
    ))[1].click()
    messages = wait_until(tg_client, 5)

    assert [
        (button.text, button.data)
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == [
        ('❌', b'mark_readed(1)'),
        ('❌', b'mark_readed(2)'),
        ('❌', b'mark_readed(3)'),
        ('❌', b'mark_readed(4)'),
        ('❌', b'mark_readed(5)'),
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_with_set_city_by_name(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Время намаза')
    wait_until(tg_client, 2)
    tg_client.send_message(bot_name, 'Казань')
    messages = wait_until(tg_client, 4)

    assert messages[0].message == 'Вам будет приходить время намаза для города Казань'


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_with_set_city_by_location(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Время намаза')
    wait_until(tg_client, 2)
    tg_client(
        functions.messages.SendMediaRequest(
            bot_name,
            types.InputMediaGeoPoint(
                types.InputGeoPoint(55.7887, 49.1221),
            ),
            '',
        ),
    )
    messages = wait_until(tg_client, 3)

    assert messages[0].message == 'Вам будет приходить время намаза для города Казань'


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user_city')
# @pytest.mark.flaky(retries=3)
def test_with_change_city(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, 'Время намаза')
    wait_until(tg_client, 5)
    tg_client.send_message(bot_name, 'Поменять город')
    wait_until(tg_client, 7)
    tg_client.send_message(bot_name, 'Набережные Челны')
    wait_until(tg_client, 9)
    tg_client.send_message(bot_name, 'Время намаза')
    messages = wait_until(tg_client, 11)

    assert [
        (button.text, button.data)
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == [
        ('❌', b'mark_readed(1)'),
        ('❌', b'mark_readed(2)'),
        ('❌', b'mark_readed(3)'),
        ('❌', b'mark_readed(4)'),
        ('❌', b'mark_readed(5)'),
    ]
