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

from app_types.update import FkUpdate, Update
from integrations.tg.tg_answers import FkAnswer, TgAnswer
from srv.ayats.favorite_ayat_empty_safe import FavoriteAyatEmptySafeAnswer


class IndexErrorAnswer(TgAnswer):

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        raise IndexError


async def test():
    got = await FavoriteAyatEmptySafeAnswer(
        FkAnswer('http://right-way.com'),
        FkAnswer('http://error-way.com'),
    ).build(FkUpdate.empty_ctor())

    assert str(got[0].url) == 'http://right-way.com'


async def test_error():
    got = await FavoriteAyatEmptySafeAnswer(
        IndexErrorAnswer(),
        FkAnswer(),
    ).build(FkUpdate.empty_ctor())

    assert str(got[0].url) == 'https://some.domain'
