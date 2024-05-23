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

import uuid

import httpx
import pytest

from app_types.logger import FkLogSink
from integrations.tg.tg_answers import TgEmptyAnswer
from srv.events.mailing_created import MailingCreatedEvent
from srv.events.sink import FkSink
from srv.json_glom.json_doc import GlomJson


@pytest.fixture()
def _mock_http(respx_mock):
    respx_mock.get('https://api.telegram.org/bottoken/sendMessage?chat_id=483457&text=Hello&parse_mode=html').mock(
        return_value=httpx.Response(
            json={
                'ok': True,
                'result': {
                    'message_id': 52551,
                    'from': {
                        'id': 452230948,
                        'is_bot': True,
                        'first_name': 'WokeUpSmiled',
                        'username': 'WokeUpSmiled_bot',
                    },
                    'chat': {
                        'id': 358610865,
                        'first_name': 'Алмаз',
                        'last_name': 'Илалетдинов',
                        'username': 'ilaletdinov',
                        'type': 'private',
                    },
                    'date': 1710448509,
                    'text': 'Hello',
                },
            },
            status_code=200,
        ),
    )


@pytest.fixture()
async def _users(pgsql):
    await pgsql.execute_many(
        '\n'.join([
            'INSERT INTO users (chat_id)',
            'VALUES',
            '(:chat_id)',
        ]),
        [{'chat_id': 483457}],
    )


@pytest.mark.usefixtures('_mock_http', '_users')
async def test(pgsql, settings_ctor):
    await MailingCreatedEvent(
        TgEmptyAnswer('token'),
        pgsql,
        FkSink(),
        FkLogSink(),
        settings_ctor(admin_chat_ids='93754').ADMIN_CHAT_IDS,
    ).process(
        GlomJson.dict_ctor({'data': {
            'mailing_id': str(uuid.uuid4()),
            'text': 'Hello',
            'group': 'all',
        }}),
    )
