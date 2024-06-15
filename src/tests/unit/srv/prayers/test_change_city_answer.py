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
from typing import override

import httpx

from app_types.update import FkUpdate, Update
from exceptions.content_exceptions import CityNotSupportedError
from integrations.tg.tg_answers import FkAnswer, TgAnswer
from srv.prayers.change_city_answer import ChangeCityAnswer, CityNotSupportedAnswer
from srv.prayers.city import FkCity
from srv.prayers.update_user_city import FkUpdateUserCity


class _Answer(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise CityNotSupportedError


async def test():
    got = await ChangeCityAnswer(
        FkAnswer(),
        FkUpdateUserCity(),
        FkCity(uuid.uuid4(), 'Казань'),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url.params['text'] == 'Вам будет приходить время намаза для города Казань'


async def test_city_not_supported():
    got = await CityNotSupportedAnswer(_Answer(), FkAnswer()).build(FkUpdate.empty_ctor())

    assert got[0].url.params['text'] == 'Этот город не поддерживается'
