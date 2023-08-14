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
from databases import Database
from pydantic import parse_obj_as
from pyeo import elegant

from exceptions.base_exception import BaseAppError
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.chat_id import ChatId
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.schemas import AyatShort
from srv.ayats.text_search_query import TextSearchQuery


@elegant
class NeighborAyatsRepositoryInterface(Protocol):
    """Интерфейс для работы с соседними аятами в хранилище."""

    async def left_neighbor(self) -> AyatShort:
        """Левый аят."""

    async def right_neighbor(self) -> AyatShort:
        """Правый аят."""

    async def page(self) -> str:
        """Информация о странице."""


@final
@attrs.define(frozen=True)
@elegant
class FavoriteNeighborAyats(NeighborAyatsRepositoryInterface):
    """Класс для работы с соседними аятами в хранилище."""

    _ayat_id: int
    _chat_id: ChatId
    _favorite_ayats_repo: FavoriteAyatRepositoryInterface

    async def left_neighbor(self) -> AyatShort:
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        fayats = await self._favorite_ayats_repo.get_favorites(self._chat_id)
        for ayat_index, ayat in enumerate(fayats):
            if ayat.id == self._ayat_id and ayat_index == 0:
                raise AyatNotFoundError
            elif ayat.id == self._ayat_id:
                return fayats[ayat_index - 1].get_short()
        raise AyatNotFoundError

    async def right_neighbor(self) -> AyatShort:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        fayats = await self._favorite_ayats_repo.get_favorites(self._chat_id)
        for ayat_index, ayat in enumerate(fayats):
            if ayat.id == self._ayat_id and ayat_index + 1 == len(fayats):
                raise AyatNotFoundError
            elif ayat.id == self._ayat_id:
                return fayats[ayat_index + 1].get_short()
        raise AyatNotFoundError

    async def page(self) -> str:
        """Информация о странице.

        :return: str
        :raises BaseAppError: if page not generated
        """
        fayats = await self._favorite_ayats_repo.get_favorites(self._chat_id)
        for ayat_idx, ayat in enumerate(fayats, start=1):
            if self._ayat_id == 1:
                return 'стр. 1/{0}'.format(len(fayats))
            elif ayat.id == len(fayats):
                return 'стр. {0}/{0}'.format(len(fayats))
            elif self._ayat_id == ayat.id:
                return 'стр. {0}/{1}'.format(ayat_idx, len(fayats))
        raise BaseAppError('Page info not generated')


@final
@attrs.define(frozen=True)
@elegant
class NeighborAyats(NeighborAyatsRepositoryInterface):
    """Класс для работы с соседними аятами в хранилище."""

    _connection: Database
    _ayat_id: int

    async def left_neighbor(self) -> AyatShort:
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        query = """
            SELECT
                ayats.ayat_id as id,
                ayats.ayat_number as ayat_num,
                ayats.sura_id as sura_num
            FROM ayats
            WHERE ayats.ayat_id = :ayat_id
        """
        row = await self._connection.fetch_one(query, {'ayat_id': self._ayat_id - 1})
        if not row:
            raise AyatNotFoundError
        return parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437

    async def right_neighbor(self) -> AyatShort:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        query = """
            SELECT
                ayats.ayat_id as id,
                ayats.ayat_number as ayat_num,
                ayats.sura_id as sura_num
            FROM ayats
            WHERE ayats.ayat_id = :ayat_id
        """
        row = await self._connection.fetch_one(query, {'ayat_id': self._ayat_id + 1})
        if not row:
            raise AyatNotFoundError
        return parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437

    async def page(self) -> str:
        """Информация о странице.

        :return: str
        """
        ayats_count = await self._connection.fetch_val('SELECT COUNT(*) FROM ayats')
        actual_page_num = await self._connection.fetch_val(
            'SELECT COUNT(*) FROM ayats WHERE ayat_id <= :ayat_id',
            {'ayat_id': self._ayat_id},
        )
        return 'стр. {0}/{1}'.format(actual_page_num, ayats_count)


@final
@attrs.define(frozen=True)
@elegant
class TextSearchNeighborAyatsRepository(NeighborAyatsRepositoryInterface):
    """Класс для работы с сосденими аятами, при текстовом поиске."""

    _connection: Database
    _ayat_id: int
    _query: TextSearchQuery
    _search_sql_query = """
        SELECT
            ayats.ayat_id as id,
            ayats.ayat_number as ayat_num,
            ayats.sura_id as sura_num
        FROM ayats
        WHERE content ILIKE :search_query
        ORDER BY ayat_id
    """

    async def left_neighbor(self) -> AyatShort:
        """Получить левый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._connection.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[1:], start=1):
            ayat = parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437
            if ayat.id == self._ayat_id:
                try:
                    return parse_obj_as(AyatShort, rows[idx - 1]._mapping)  # noqa: WPS437
                except IndexError as err:
                    raise AyatNotFoundError from err
        raise AyatNotFoundError

    async def right_neighbor(self) -> AyatShort:
        """Получить правый аят.

        :return: AyatShort
        :raises AyatNotFoundError: if ayat not found
        """
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._connection.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[:-1]):
            ayat = parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437
            if ayat.id == self._ayat_id:
                try:
                    return parse_obj_as(AyatShort, rows[idx + 1]._mapping)  # noqa: WPS437
                except IndexError as err:
                    raise AyatNotFoundError from err
        raise AyatNotFoundError

    async def page(self) -> str:
        """Информация о странице.

        :return: str
        """
        actual_page_num = 0
        rows = await self._connection.fetch_all(
            self._search_sql_query,
            {'search_query': '%{0}%'.format(await self._query.read())},
        )
        for idx, row in enumerate(rows, start=1):
            ayat = parse_obj_as(AyatShort, row._mapping)  # noqa: WPS437
            if ayat.id == self._ayat_id:
                actual_page_num = idx
        return 'стр. {0}/{1}'.format(actual_page_num, len(rows))
