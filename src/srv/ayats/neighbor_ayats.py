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

# TODO #899 Перенести классы в отдельные файлы 43

from typing import Final, Protocol, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.listable import AsyncListable
from exceptions.base_exception import BaseAppError
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat import Ayat
from srv.ayats.pg_ayat import PgAyat, TextLenSafeAyat
from srv.ayats.text_search_query import TextSearchQuery

AYAT_ID: Final = 'ayat_id'


@elegant
class NeighborAyats(Protocol):
    """Интерфейс для работы с соседними аятами в хранилище."""

    async def left_neighbor(self) -> Ayat:
        """Левый аят."""

    async def right_neighbor(self) -> Ayat:
        """Правый аят."""

    async def page(self) -> str:
        """Информация о странице."""


@final
@attrs.define(frozen=True)
@elegant
class FavoriteNeighborAyats(NeighborAyats):
    """Класс для работы с соседними аятами в хранилище."""

    _ayat_id: int
    _favorite_ayats: AsyncListable[Ayat]

    @override
    async def left_neighbor(self) -> Ayat:
        """Получить левый аят."""
        fayats = await self._favorite_ayats.to_list()
        for ayat_index, ayat in enumerate(fayats):
            ayat_id = await ayat.identifier().ayat_id()
            if ayat_id == self._ayat_id and ayat_index == 0:
                raise AyatNotFoundError
            elif ayat_id == self._ayat_id:
                return fayats[ayat_index - 1]
        raise AyatNotFoundError

    @override
    async def right_neighbor(self) -> Ayat:
        """Получить правый аят."""
        fayats = await self._favorite_ayats.to_list()
        for ayat_index, ayat in enumerate(fayats):
            ayat_id = await ayat.identifier().ayat_id()
            if ayat_id == self._ayat_id and ayat_index + 1 == len(fayats):
                raise AyatNotFoundError
            elif ayat_id == self._ayat_id:
                return fayats[ayat_index + 1]
        raise AyatNotFoundError

    @override
    async def page(self) -> str:
        """Информация о странице."""
        fayats = await self._favorite_ayats.to_list()
        for ayat_idx, ayat in enumerate(fayats, start=1):
            if self._ayat_id == 1:
                return 'стр. 1/{0}'.format(len(fayats))
            elif await ayat.identifier().ayat_id() == len(fayats):
                return 'стр. {0}/{0}'.format(len(fayats))
            elif self._ayat_id == await ayat.identifier().ayat_id():
                return 'стр. {0}/{1}'.format(ayat_idx, len(fayats))
        msg = 'Page info not generated'
        raise BaseAppError(msg)


@final
@attrs.define(frozen=True)
@elegant
class PgNeighborAyats(NeighborAyats):
    """Класс для работы с соседними аятами в хранилище."""

    _pgsql: Database
    _ayat_id: int

    @override
    async def left_neighbor(self) -> Ayat:
        """Получить левый аят."""
        query = '\n'.join([
            'SELECT ayat_id',
            'FROM ayats',
            'WHERE ayat_id = :ayat_id',
        ])
        row = await self._pgsql.fetch_one(query, {AYAT_ID: self._ayat_id - 1})
        if not row:
            raise AyatNotFoundError
        return TextLenSafeAyat(PgAyat.from_int(row[AYAT_ID], self._pgsql))

    @override
    async def right_neighbor(self) -> Ayat:
        """Получить правый аят."""
        query = '\n'.join([
            'SELECT ayats.ayat_id',
            'FROM ayats',
            'WHERE ayats.ayat_id = :ayat_id',
        ])
        row = await self._pgsql.fetch_one(query, {AYAT_ID: self._ayat_id + 1})
        if not row:
            raise AyatNotFoundError
        return TextLenSafeAyat(PgAyat.from_int(row[AYAT_ID], self._pgsql))

    @override
    async def page(self) -> str:
        """Информация о странице."""
        ayats_count = await self._pgsql.fetch_val('SELECT COUNT(*) FROM ayats')
        actual_page_num = await self._pgsql.fetch_val(
            'SELECT COUNT(*) FROM ayats WHERE ayat_id <= :ayat_id',
            {AYAT_ID: self._ayat_id},
        )
        return 'стр. {0}/{1}'.format(actual_page_num, ayats_count)


@final
@attrs.define(frozen=True)
@elegant
class TextSearchNeighborAyats(NeighborAyats):
    """Класс для работы с сосденими аятами, при текстовом поиске."""

    _pgsql: Database
    _ayat_id: int
    _query: TextSearchQuery
    _search_sql_query = '\n'.join([
        'SELECT ayats.ayat_id',
        'FROM ayats',
        'WHERE ayats.content ILIKE :search_query',
        'ORDER BY ayats.ayat_id',
    ])

    @override
    async def left_neighbor(self) -> Ayat:
        """Получить левый аят."""
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._pgsql.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[1:], start=1):
            if row['ayat_id'] == self._ayat_id:
                return TextLenSafeAyat(
                    PgAyat.from_int(rows[idx - 1][AYAT_ID], self._pgsql),
                )
        raise AyatNotFoundError

    @override
    async def right_neighbor(self) -> Ayat:
        """Получить правый аят."""
        search_query = '%{0}%'.format(await self._query.read())
        rows = await self._pgsql.fetch_all(self._search_sql_query, {'search_query': search_query})
        for idx, row in enumerate(rows[:-1]):
            if row['ayat_id'] == self._ayat_id:
                return TextLenSafeAyat(
                    PgAyat.from_int(rows[idx + 1][AYAT_ID], self._pgsql),
                )
        raise AyatNotFoundError

    @override
    async def page(self) -> str:
        """Информация о странице."""
        actual_page_num = 0
        rows = await self._pgsql.fetch_all(
            self._search_sql_query,
            {'search_query': '%{0}%'.format(await self._query.read())},
        )
        for idx, row in enumerate(rows, start=1):
            if row[AYAT_ID] == self._ayat_id:
                actual_page_num = idx
        return 'стр. {0}/{1}'.format(actual_page_num, len(rows))
