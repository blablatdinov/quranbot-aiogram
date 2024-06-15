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

from app_types.supports_bool import AsyncSupportsBool
from integrations.tg.chat_id import ChatId
from srv.ayats.ayat import Ayat


@final
@attrs.define(frozen=True)
@elegant
class AyatIsFavor(AsyncSupportsBool):
    """Является ли аят избранным."""

    _ayat: Ayat
    _chat_id: ChatId
    _pgsql: Database

    @override
    async def to_bool(self) -> bool:
        """Приведение к булевому значению."""
        query = '\n'.join([
            'SELECT COUNT(*)',
            'FROM favorite_ayats AS fa',
            'INNER JOIN users AS u ON fa.user_id = u.chat_id',
            'WHERE fa.ayat_id = :ayat_id AND u.chat_id = :chat_id',
        ])
        count = await self._pgsql.fetch_val(
            query, {'ayat_id': await self._ayat.identifier().ayat_id(), 'chat_id': self._chat_id},
        )
        return bool(count)
