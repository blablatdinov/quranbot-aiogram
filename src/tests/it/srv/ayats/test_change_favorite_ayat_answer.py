"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import datetime

import pytest
import pytz
import ujson

from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from integrations.tg.tg_answers import FkAnswer
from srv.ayats.change_favorite_ayat_answer import ChangeFavoriteAyatAnswer


@pytest.fixture()
async def _db_ayat(pgsql):
    created_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO files (file_id, telegram_file_id, link, created_at)',
            "VALUES (:file_id, 'aoiejf298jr9p23u8qr3', 'https://link-to-file.domain', :created_at)",
        ]),
        {'file_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90', 'created_at': created_at},
    )
    await pgsql.execute('\n'.join([
        'INSERT INTO suras (sura_id, link) VALUES',
        "(1, 'https://link-to-sura.domain')",
    ]))
    await pgsql.execute(
        '\n'.join([
            'INSERT INTO ayats',
            '(ayat_id, sura_id, public_id, day, audio_id, ayat_number, content, arab_text, transliteration)',
            'VALUES',
            '(:ayat_id, :sura_id, :public_id, :day, :audio_id, :ayat_number, :content, :arab_text, :transliteration)',
        ]),
        {
            'ayat_id': 1,
            'sura_id': 1,
            'public_id': '3067bdc4-8dc0-456b-aa68-e38122b5f2f8',
            'day': 1,
            'audio_id': '82db206b-34ed-4ae0-ac83-1f0c56dfde90',
            'ayat_number': '1-7',
            'content': 'Content',
            'arab_text': 'Arab text',
            'transliteration': 'Transliteration',
        },
    )
    await pgsql.execute('INSERT INTO users (chat_id) VALUES (1)')


@pytest.mark.usefixtures('_db_ayat')
async def test_add(pgsql, fake_redis):
    got = await ChangeFavoriteAyatAnswer(
        pgsql, FkAnswer(), fake_redis, FkLogSink(),
    ).build(FkUpdate(
        ujson.dumps({
            'callback_query': {'data': 'addToFavor(1)'},
            'chat': {'id': 1},
            'message': {'message_id': 1},
        }),
    ))

    assert ujson.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [
            [{'callback_data': 'fake', 'text': 'стр. 1/1'}],
            [{'callback_data': 'removeFromFavor(1)', 'text': 'Удалить из избранного'}],
        ],
    }


@pytest.mark.usefixtures('_db_ayat')
async def test_remove(pgsql, fake_redis):
    got = await ChangeFavoriteAyatAnswer(
        pgsql, FkAnswer(), fake_redis, FkLogSink(),
    ).build(FkUpdate(
        ujson.dumps({
            'callback_query': {'data': 'removeFromFavor(1)'},
            'chat': {'id': 1},
            'message': {'message_id': 1},
        }),
    ))

    assert ujson.loads(got[0].url.params['reply_markup']) == {
        'inline_keyboard': [
            [{'callback_data': 'fake', 'text': 'стр. 1/1'}],
            [{'callback_data': 'addToFavor(1)', 'text': 'Добавить в избранное'}],
        ],
    }
