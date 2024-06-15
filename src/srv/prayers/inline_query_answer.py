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
import ujson
from databases import Database
from pyeo import elegant

from app_types.update import Update
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.exceptions.update_parse_exceptions import InlineQueryNotFoundError
from integrations.tg.inline_query import InlineQuery, InlineQueryId
from integrations.tg.tg_answers import TgAnswer
from services.debug_answer import DebugAnswer
from srv.prayers.city_names import CityNames


@final
@attrs.define(frozen=True)
@elegant
class InlineQueryAnswer(TgAnswer):
    """Ответ на инлайн поиск."""

    _origin: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ."""
        try:
            inline_query_data = str(InlineQuery(update))
        except InlineQueryNotFoundError as err:
            raise NotProcessableUpdateError from err
        origin_requests = await DebugAnswer(self._origin).build(update)
        city_names = await CityNames(self._pgsql, inline_query_data).to_list()
        return [
            httpx.Request(
                origin_requests[0].method,
                (
                    origin_requests[0]
                    .url
                    .join('answerInlineQuery')
                    .copy_add_param('inline_query_id', int(InlineQueryId(update)))
                    .copy_add_param(
                        'results',
                        ujson.dumps([
                            {
                                'id': str(idx),
                                'type': 'article',
                                'title': city_name,
                                'input_message_content': {'message_text': city_name},
                            }
                            for idx, city_name in enumerate(city_names)
                        ]),
                    )
                ),
            ),
        ]
