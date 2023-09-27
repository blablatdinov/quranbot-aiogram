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
from typing import Protocol, TypeAlias, final

import attrs
from databases import Database

from app_types.intable import AsyncIntable
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.search_query import AyatNum, SuraId

AyatId: TypeAlias = int


class AyatIdentifier(Protocol):
    """Информация для идентификации аята."""

    async def ayat_id(self) -> AyatId:
        """Идентификатор в хранилище."""

    async def sura_num(self) -> SuraId:
        """Номер суры."""

    async def ayat_num(self) -> AyatNum:
        """Номер аята."""


@final
@attrs.define(frozen=True)
class PgAyatIdentifier(AyatIdentifier):
    """Информация для идентификации аята."""

    _ayat_id: AsyncIntable
    _pgsql: Database

    async def ayat_id(self) -> AyatId:
        """Идентификатор в хранилище.

        :return: AyatId
        """
        return await self._ayat_id.to_int()

    async def sura_num(self) -> SuraId:
        """Номер суры.

        :return: SuraId
        :raises AyatNotFoundError: в случае если аят не найден
        """
        query = """
            SELECT a.sura_id
            FROM ayats AS a
            WHERE a.ayat_id = :ayat_id
        """
        ayat_id = await self.ayat_id()
        row = await self._pgsql.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError
        return row['sura_id']

    async def ayat_num(self) -> AyatNum:
        """Номер аята.

        :return: AyatNum
        :raises AyatNotFoundError: в случае если аят не найден
        """
        query = """
            SELECT ayat_number
            FROM ayats
            WHERE ayat_id = :ayat_id
        """
        ayat_id = await self.ayat_id()
        row = await self._pgsql.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError
        return row['ayat_number']


@attrs.define(frozen=True)
class FkIdentifier(AyatIdentifier):
    """Identifier stub."""

    _id: int
    _sura_num: int
    _ayat_num: str

    async def ayat_id(self) -> int:
        """Идентификатор.

        :return: int
        """
        return self._id

    async def sura_num(self) -> int:
        """Номер суры.

        :return: int
        """
        return self._sura_num

    async def ayat_num(self) -> str:
        """Номер аята.

        :return: str
        """
        return self._ayat_num
