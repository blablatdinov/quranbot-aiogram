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

from pathlib import Path

import pytest
import ujson

from srv.json_glom.json_doc import GlomJson


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_start(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    last_messages = wait_until(tg_client, 3)

    assert last_messages[1].message == Path('src/tests/e2e/fixtures/start.txt').read_text(encoding='utf-8')
    assert last_messages[0].message == Path('src/tests/e2e/fixtures/1_1_ayat.txt').read_text(encoding='utf-8')


@pytest.mark.usefixtures('_bot_process', '_clear_db')
@pytest.mark.flaky(retries=3)
def test_generated_events(tg_client, bot_name, wait_event):
    tg_client.send_message(bot_name, '/start')
    events = wait_event(2, delay=5)

    assert not GlomJson(events[0]).path('$.data.messages[0].is_unknown')[0]
    assert not GlomJson(events[1]).path('$.data.messages[0].is_unknown')[0]
    assert ujson.loads(
        GlomJson(events[0]).path('$.data.messages[0].message_json')[0],
    )['text'] == '/start'
    assert (
        GlomJson(events[1]).path('$.data.messages[0].trigger_message_id')[0]
        == ujson.loads(
            GlomJson(events[0]).path('$.data.messages[0].message_json')[0],
        )['message_id']
    )
    assert (
        GlomJson(events[1]).path('$.data.messages[1].trigger_message_id')[0]
        == ujson.loads(
            GlomJson(events[0]).path('$.data.messages[0].message_json')[0],
        )['message_id']
    )
