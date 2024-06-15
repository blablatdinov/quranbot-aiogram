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
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer, TgMessageRegexAnswer
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.cached_ayat_search_query import CachedAyatSearchQueryAnswer
from srv.ayats.highlighted_search_answer import HighlightedSearchAnswer
from srv.ayats.search_ayat_by_text import SearchAyatByTextAnswer


@final
@attrs.define(frozen=True)
@elegant
class SearchAyatByKeywordAnswer(TgAnswer):
    """Ответ с временами намаза."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        return await TgMessageRegexAnswer(
            '.+',
            HighlightedSearchAnswer(
                CachedAyatSearchQueryAnswer(
                    SearchAyatByTextAnswer(
                        self._debug_mode,
                        self._empty_answer,
                        self._redis,
                        self._pgsql,
                        self._logger,
                    ),
                    self._redis,
                    self._logger,
                ),
                AyatTextSearchQuery(
                    self._redis,
                    TgChatId(update),
                    self._logger,
                ),
            ),
        ).build(update)
