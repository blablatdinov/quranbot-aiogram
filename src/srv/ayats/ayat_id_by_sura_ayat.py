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

# TODO #899 Перенести классы в отдельные файлы 41

import uuid
from typing import final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.intable import AsyncIntable
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_identifier import AyatId
from srv.ayats.search_query import SearchQuery


@final
@attrs.define(frozen=True)
@elegant
class AyatIdBySuraAyatNum(AsyncIntable):
    """Поиск аятов по номеру суры, аята."""

    _query: SearchQuery
    _pgsql: Database

    @override
    async def to_int(self) -> AyatId:
        """Числовое представление."""
        query = '\n'.join([
            'SELECT ayat_id FROM ayats',
            'WHERE',
            '    sura_id = :sura_id',
            '    AND (',
            '        ayat_number LIKE :ayat_num_str',
            '        OR ayat_number LIKE :ayat_comma_prefix',
            '        OR ayat_number LIKE :ayat_comma_postfix',
            '        OR (',
            "            CAST(SUBSTRING(ayat_number FROM '^[0-9]+') AS INTEGER) <= :ayat_num",
            "            AND CAST(SUBSTRING(ayat_number FROM '[0-9]+$') AS INTEGER) >= :ayat_num",
            '        )',
            '    )',
        ])
        row = await self._pgsql.fetch_one(query, {
            'sura_id': self._query.sura(),
            'ayat_comma_prefix': '%,{0}'.format(self._query.ayat()),
            'ayat_comma_postfix': '%{0},'.format(self._query.ayat()),
            'ayat_num': int(self._query.ayat()),
            'ayat_num_str': self._query.ayat(),
        })
        if not row:
            raise AyatNotFoundError
        return row['ayat_id']


@final
@attrs.define(frozen=True)
@elegant
class AyatIdByPublicId(AsyncIntable):
    """Поиск аятов по номеру суры, аята."""

    _public_id: uuid.UUID
    _pgsql: Database

    @override
    async def to_int(self) -> AyatId:
        """Числовое представление."""
        query = '\n'.join([
            'SELECT ayat_id FROM ayats',
            'WHERE public_id = :public_id',
        ])
        row = await self._pgsql.fetch_one(query, {
            'public_id': str(self._public_id),
        })
        if not row:
            raise AyatNotFoundError
        return row['ayat_id']
