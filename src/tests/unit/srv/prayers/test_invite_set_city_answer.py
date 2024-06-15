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

from typing import override

import httpx
import ujson

from app_types.logger import FkLogSink
from app_types.update import FkUpdate, Update
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.tg_answers import FkAnswer, TgAnswer
from srv.prayers.invite_set_city_answer import InviteSetCityAnswer, UserWithoutCitySafeAnswer


class FkOrigin(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise UserHasNotCityIdError


async def test_exception():
    got = await UserWithoutCitySafeAnswer(FkOrigin(), FkAnswer()).build(FkUpdate.empty_ctor())

    assert got[0].url == 'https://some.domain'


async def test_invite_set_city_answer(fake_redis):
    got = await InviteSetCityAnswer(
        FkAnswer(), fake_redis, FkLogSink(),
    ).build(FkUpdate('{"chat":{"id":1}}'))

    assert got[0].url.params['reply_markup'] == ujson.dumps({
        'inline_keyboard': [[
            {'text': 'Поиск города', 'switch_inline_query_current_chat': ''},
        ]],
    })
