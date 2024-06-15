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

# TODO #899 Перенести классы в отдельные файлы 45

from typing import final, override

import attrs
from redis.asyncio import Redis

from app_types.logger import LogSink
from exceptions.content_exceptions import UserHasNotSearchQueryError
from integrations.tg.chat_id import ChatId
from srv.ayats.text_search_query import TextSearchQuery


@final
class CachedTextSearchQuery(TextSearchQuery):
    """Закэшированный запрос."""

    @override
    def __init__(self, origin: TextSearchQuery) -> None:
        """Ctor."""
        self._origin = origin
        self._cached = ''

    @override
    async def write(self, query: str) -> None:
        """Запись."""
        await self._origin.write(query)
        self._cached = query

    @override
    async def read(self) -> str:
        """Чтение."""
        if self._cached:
            return self._cached
        self._cached = await self._origin.read()
        return self._cached


@final
@attrs.define(frozen=True)
class AyatTextSearchQuery(TextSearchQuery):
    """Запрос поиска аята."""

    _redis: Redis
    _chat_id: ChatId
    _logger: LogSink

    _key_template = '{0}:ayat_search_query'

    @override
    async def write(self, query: str) -> None:
        """Запись."""
        key = self._key_template.format(int(self._chat_id))
        self._logger.info('Try writing key: {0}, value: {1}'.format(key, query))
        await self._redis.set(key, query)
        self._logger.info('Key: {0} wrote'.format(
            self._key_template.format(int(self._chat_id)),
        ))

    @override
    async def read(self) -> str:
        """Чтение."""
        key = self._key_template.format(int(self._chat_id))
        self._logger.info('Try read {0}'.format(key))
        redis_value = await self._redis.get(key)
        if not redis_value:
            msg = "User hasn't search query"
            self._logger.error(msg)
            raise UserHasNotSearchQueryError(msg)
        seqrch_query = redis_value.decode('utf-8')
        self._logger.info('Read value: {0}'.format(seqrch_query))
        return seqrch_query
