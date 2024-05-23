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

import httpx
import pytest
import ujson

from app_types.logger import FkLogSink
from integrations.tg.tg_answers import FkAnswer
from srv.events.check_user_status import CheckUsersStatus
from srv.events.sink import FkSink
from srv.json_glom.json_doc import GlomJson


@pytest.fixture()
def _mock_actives(respx_mock):
    rv = {
        'return_value': httpx.Response(
            200, text=ujson.dumps({'ok': True, 'result': True}),
        ),
    }
    respx_mock.get('https://some.domain/sendChatAction?chat_id=1&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=2&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=3&action=typing').mock(**rv)


@pytest.fixture()
def _mock_unsubscribed(respx_mock):
    rv = {
        'return_value': httpx.Response(
            400, text='{"ok":false,"error_code":400,"description":"Bad Request: chat not found"}',
        ),
    }
    respx_mock.get('https://some.domain/sendChatAction?chat_id=1&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=2&action=typing').mock(**rv)
    respx_mock.get('https://some.domain/sendChatAction?chat_id=3&action=typing').mock(
        return_value=httpx.Response(200, text=ujson.dumps({'ok': True, 'result': True})),
    )


@pytest.fixture()
async def _users(pgsql):
    await pgsql.execute_many('INSERT INTO users (chat_id) VALUES (:chat_id)', [
        {'chat_id': 1},
        {'chat_id': 2},
        {'chat_id': 3},
    ])


@pytest.mark.usefixtures('_users', '_mock_actives')
async def test_user_status(pgsql):
    await CheckUsersStatus(
        FkAnswer(), pgsql, FkSink(), FkLogSink(),
    ).process(GlomJson({}))

    assert [
        row['is_active']
        for row in await pgsql.fetch_all('SELECT is_active FROM users')
    ] == [True, True, True]


@pytest.mark.usefixtures('_users', '_mock_unsubscribed')
async def test_unsubscribed(pgsql):
    await CheckUsersStatus(
        FkAnswer(), pgsql, FkSink(), FkLogSink(),
    ).process(GlomJson({}))

    assert [
        (row['chat_id'], row['is_active'])
        for row in await pgsql.fetch_all('SELECT chat_id, is_active FROM users ORDER BY chat_id')
    ] == [(1, False), (2, False), (3, True)]
