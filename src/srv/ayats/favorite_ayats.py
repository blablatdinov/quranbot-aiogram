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
from databases import Database
from pyeo import elegant

from app_types.intable import FkAsyncIntable
from app_types.listable import AsyncListable
from integrations.tg.chat_id import ChatId
from srv.ayats.ayat import Ayat
from srv.ayats.pg_ayat import PgAyat, TextLenSafeAyat


@final
@attrs.define(frozen=True)
@elegant
class FavoriteAyats(AsyncListable):
    """Избранные аяты."""

    _chat_id: ChatId
    _pgsql: Database

    @override
    async def to_list(self) -> list[Ayat]:
        """Получить избранные аяты."""
        query = '\n'.join([
            'SELECT fa.ayat_id',
            'FROM favorite_ayats AS fa',
            'INNER JOIN users AS u ON fa.user_id = u.chat_id',
            'WHERE u.chat_id = :chat_id',
            'ORDER BY fa.ayat_id',
        ])
        rows = await self._pgsql.fetch_all(query, {'chat_id': int(self._chat_id)})
        return [
            TextLenSafeAyat(PgAyat(FkAsyncIntable(row['ayat_id']), self._pgsql))
            for row in rows
        ]
