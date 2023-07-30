"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import Protocol, final

import attrs
from aioredis import Redis
from loguru import logger
from pyeo import elegant


@elegant
class AyatTextSearchQueryInterface(Protocol):
    """Интерфейс запроса для поиска аятов."""

    async def write(self) -> None:
        """Запись."""

    async def read(self) -> str:
        """Чтение."""


@final
@attrs.define(frozen=True)
@elegant
class AyatTextSearchQuery(AyatTextSearchQueryInterface):
    """Запрос поиска аята."""

    _redis: Redis
    _chat_id: int
    _query: tuple[str, ...] = ()

    _key_template = '{0}:ayat_search_query'

    @classmethod
    def for_write_cs(cls, redis: Redis, query: str, chat_id: int):
        """Конструктор для записи.

        :param redis: Redis
        :param query: str
        :param chat_id: int
        :return: AyatTextSearchQuery
        """
        return AyatTextSearchQuery(redis, query=(query,), chat_id=chat_id)

    @classmethod
    def for_reading_cs(cls, redis: Redis, chat_id: int):
        """Конструктор для чтения.

        :param redis: Redis
        :param chat_id: int
        :return: AyatTextSearchQuery
        """
        return AyatTextSearchQuery(redis, chat_id=chat_id)

    async def write(self) -> None:
        """Запись.

        :raises ValueError: if query not give
        """
        key = self._key_template.format(self._chat_id)
        logger.info('Try writing key: {0}, value: {1}'.format(key, self._query[0]))
        try:
            await self._redis.set(key, self._query[0])
        except IndexError as err:
            logger.error('Writing {0} fail query not give'.format(key))
            raise ValueError('Query not give') from err
        logger.info('Key: {0} wrote'.format(self._key_template.format(self._chat_id)))

    async def read(self) -> str:
        """Чтение.

        :return: str
        :raises ValueError: user has not search query
        """
        key = self._key_template.format(self._chat_id)
        logger.info('Try read {0}'.format(key))
        redis_value = await self._redis.get(key)
        if not redis_value:
            logger.error("User hasn't search query")
            raise ValueError("User hasn't search query")
        seqrch_query = redis_value.decode('utf-8')
        logger.info('Read value: {0}'.format(seqrch_query))
        return seqrch_query
