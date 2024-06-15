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

import urllib

from app_types.update import FkUpdate
from integrations.tg.tg_answers import FkAnswer
from srv.ayats.highlighted_search_answer import HighlightedSearchAnswer
from srv.ayats.text_search_query import FkTextSearchQuery


async def test():
    got = await HighlightedSearchAnswer(
        FkAnswer('https://some.domain?text=How to write tests in python?'),
        FkTextSearchQuery('How to write tests'),
    ).build(FkUpdate.empty_ctor())

    assert len(got) == 1
    assert urllib.parse.unquote(
        str(got[0].url),
    ) == 'https://some.domain?text=<b>How to write tests</b> in python?'


async def test_key_error():
    got = await HighlightedSearchAnswer(FkAnswer(), FkTextSearchQuery('How to write tests')).build(FkUpdate.empty_ctor())

    assert len(got) == 1
    assert urllib.parse.unquote(
        str(got[0].url),
    ) == 'https://some.domain'


async def test_other_text():
    got = await HighlightedSearchAnswer(
        FkAnswer('https://some.domain?text=How to write documentation'), FkTextSearchQuery('How to write tests'),
    ).build(FkUpdate.empty_ctor())

    assert len(got) == 1
    assert urllib.parse.unquote(
        str(got[0].url),
    ) == 'https://some.domain?text=How to write documentation'
