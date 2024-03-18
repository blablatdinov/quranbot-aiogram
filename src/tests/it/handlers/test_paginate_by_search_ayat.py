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
import json

from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from handlers.paginate_by_search_ayat import PaginateBySearchAyat
from integrations.tg.tg_answers import FkAnswer
from settings.settings import FkSettings


async def test(fake_redis, pgsql):
    got = await PaginateBySearchAyat(
        FkAnswer(),
        fake_redis,
        pgsql,
        FkSettings({}),
        FkLogSink(),
    ).build(FkUpdate(json.dumps({
        'chat': {'id': 843759},
        'callback_query': {
            'data': '1',
        },
    })))

    assert got[0].url.params['text'] == 'Пожалуйста, введите запрос для поиска:'
