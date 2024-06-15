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

from typing import final, override

import attrs
import httpx
from pyeo import elegant

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from srv.ayats.text_search_query import TextSearchQuery


@final
@attrs.define(frozen=True)
@elegant
class HighlightedSearchAnswer(TgAnswer):
    """Ответ с подсвеченным поисковым текстом."""

    _origin: TgAnswer
    _search_query: TextSearchQuery

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ."""
        new_requests = []
        requests = await self._origin.build(update)
        search_query = await self._search_query.read()
        for request in requests:
            try:
                text = request.url.params['text']
            except KeyError:
                new_requests.append(request)
                continue
            if search_query in text:
                new_requests.append(httpx.Request(
                    method=request.method,
                    url=request.url.copy_set_param(
                        'text',
                        text.replace('+', ' ') .replace(search_query, '<b>{0}</b>'.format(search_query)),
                    ),
                    headers=request.headers,
                ))
            else:
                new_requests.append(request)
        return new_requests
