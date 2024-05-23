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

import httpx
import pytest
import pytz
import ujson
from furl import furl
from loguru import logger

from integrations.tg.tg_answers import TgEmptyAnswer
from srv.events.morning_content_published import MorningContentPublishedEvent
from srv.events.sink import RabbitmqSink
from srv.json_glom.json_doc import GlomJson
from srv.users.pg_user import PgUser


@pytest.fixture()
def _mock_http(respx_mock):
    rv = {
        'return_value': httpx.Response(
            200, text=ujson.dumps({'ok': True, 'result': True}),
        ),
    }
    url = furl('https://api.telegram.org/botfakeToken/sendMessage').add({
        'text': '<b>1:1)</b> First ayat content\n<b>1:2)</b> Second ayat content\n\nhttps://umma.ru/sura-1',
        'chat_id': '358610865',
        'parse_mode': 'html',
        'link_preview_options': '{"is_disabled":true}',
    })
    respx_mock.get(str(url)).mock(
        return_value=httpx.Response(
            text='{"ok":false,"error_code":403,"description":"Forbidden: bot was blocked by the user"}',
            status_code=400,
        ),
    )
    chat_content = {
        '24391797': '<b>1:1)</b> First ayat content\n<b>1:2)</b> Second ayat content\n\nhttps://umma.ru/sura-1',
        '206497847': '<b>2:1-4)</b> Third ayat content\n\nhttps://umma.ru/sura-2',
    }
    for chat_id, text in chat_content.items():
        respx_mock.get(str(furl('https://api.telegram.org/botfakeToken/sendMessage').add({
            'text': text,
            'chat_id': chat_id,
            'parse_mode': 'html',
            'link_preview_options': '{"is_disabled":true}',
        }))).mock(**rv)


@pytest.fixture()
async def _ayats(pgsql):
    await pgsql.execute(
        'INSERT INTO files (file_id, created_at) VALUES (:file_id, :created_at)',
        {
            'file_id': '7fc47c04-2271-4ef0-9e47-ba08f499932b',
            'created_at': datetime.datetime(2020, 1, 1, tzinfo=pytz.timezone('Europe/Moscow')),
        },
    )
    await pgsql.execute_many(
        'INSERT INTO suras (sura_id, link) VALUES (:sura_id, :link)',
        [
            {'sura_id': 1, 'link': '/sura-1'},
            {'sura_id': 2, 'link': '/sura-2'},
            {'sura_id': 3, 'link': '/sura-3'},
        ],
    )
    common = {
        'public_id': '',
        'audio_id': '7fc47c04-2271-4ef0-9e47-ba08f499932b',
        'arab_text': '',
        'transliteration': '',
    }
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO ayats',
            '(ayat_id, public_id, sura_id, audio_id, ayat_number, content, arab_text, transliteration, day)',
            'VALUES',
            '(:ayat_id, :public_id, :sura_id, :audio_id, :ayat_number, :content, :arab_text, :transliteration, :day)',
        ]),
        [
            {
                'ayat_id': 1,
                'sura_id': 1,
                'ayat_number': '1',
                'content': 'First ayat content',
                'day': 2,
            } | common,
            {
                'ayat_id': 2,
                'sura_id': 1,
                'ayat_number': '2',
                'content': 'Second ayat content',
                'day': 2,
            } | common,
            {
                'ayat_id': 3,
                'sura_id': 2,
                'ayat_number': '1-4',
                'content': 'Third ayat content',
                'day': 3,
            } | common,
        ],
    )


@pytest.fixture()
async def users(pgsql):
    await pgsql.execute_many(
        'INSERT INTO users (chat_id, is_active, day) VALUES (:chat_id, :is_active, :day)',
        [
            {'chat_id': 358610865, 'is_active': True, 'day': 2},
            {'chat_id': 206497847, 'is_active': True, 'day': 3},
            {'chat_id': 827078672, 'is_active': False, 'day': 5},
            {'chat_id': 24391797, 'is_active': True, 'day': 2},
        ],
    )
    return [
        PgUser.int_ctor(row['chat_id'], pgsql)
        for row in await pgsql.fetch_all('SELECT chat_id FROM users')
    ]


@pytest.mark.usefixtures('_ayats', '_mock_http')
async def test(pgsql, users, settings_ctor):
    settings = settings_ctor(  # noqa: S106. Not secure issue
        rabbitmq_host='localhost',
        rabbitmq_user='guest',
        rabbitmq_pass='guest',  # noqa: S106. Not secure issue
        rabbitmq_vhost='',
        daily_ayats='on',
    )
    await MorningContentPublishedEvent(
        TgEmptyAnswer('fakeToken'),
        pgsql,
        settings,
        RabbitmqSink(settings, logger),
        logger,
    ).process(GlomJson({}))

    assert [
        (await user.chat_id(), await user.is_active(), await user.day())
        for user in users
    ] == [
        (358610865, False, 2),
        (206497847, True, 4),
        (827078672, False, 5),
        (24391797, True, 3),
    ]
