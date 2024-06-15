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

# TODO #899 Перенести классы в отдельные файлы 51

from typing import TypedDict, final, override

import attrs
import ujson
from databases import Database
from pyeo import elegant

from app_types.update import Update
from integrations.tg.keyboard import KeyboardInterface
from srv.podcasts.podcast import Podcast


class _Row(TypedDict):

    like_count: int
    dislike_count: int


@final
@attrs.define(frozen=True)
@elegant
class PodcastKeyboard(KeyboardInterface):
    """Клавиатура подкаста."""

    _pgsql: Database
    _podcast: Podcast

    @override
    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры."""
        query = '\n'.join([
            'SELECT',
            "    COUNT(CASE WHEN reaction = 'like' THEN 1 END) AS like_count,",
            "    COUNT(CASE WHEN reaction = 'dislike' THEN 1 END) AS dislike_count",
            'FROM podcast_reactions',
            'WHERE podcast_id = :podcast_id',
            'GROUP BY podcast_id',
        ])
        podcast_id = await self._podcast.podcast_id()
        row = await self._pgsql.fetch_one(query, {'podcast_id': podcast_id})
        if row:
            likes_count_map = _Row(
                like_count=row['like_count'],
                dislike_count=row['dislike_count'],
            )
        else:
            likes_count_map = _Row(
                like_count=0,
                dislike_count=0,
            )
        return ujson.dumps({
            'inline_keyboard': [[
                {
                    'text': '👍 {0}'.format(likes_count_map['like_count']),
                    'callback_data': 'like({0})'.format(podcast_id),
                },
                {
                    'text': '👎 {0}'.format(likes_count_map['dislike_count']),
                    'callback_data': 'dislike({0})'.format(podcast_id),
                },
            ]],
        })
