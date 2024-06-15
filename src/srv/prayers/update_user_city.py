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

# TODO #899 Перенести классы в отдельные файлы 31

from typing import Protocol, final, override

import attrs
from databases import Database
from pyeo import elegant

from exceptions.internal_exceptions import UserNotFoundError
from integrations.tg.chat_id import ChatId
from srv.prayers.city import City


@elegant
class UpdatedUserCity(Protocol):
    """Обновленный город у пользователя."""

    async def update(self) -> None:
        """Обновление."""


@final
@attrs.define(frozen=True)
@elegant
class FkUpdateUserCity(UpdatedUserCity):
    """Стаб для обновления города."""

    @override
    async def update(self) -> None:
        """Обновление."""


@final
@attrs.define(frozen=True)
@elegant
class PgUpdatedUserCity(UpdatedUserCity):
    """Обновленный город у пользователя в БД postgres."""

    _city: City
    _chat_id: ChatId
    _pgsql: Database

    @override
    async def update(self) -> None:
        """Обновление."""
        query = '\n'.join([
            'UPDATE users',
            'SET city_id = :city_id',
            'WHERE chat_id = :chat_id',
            'RETURNING *',
        ])
        updated_rows = await self._pgsql.fetch_all(query, {
            'city_id': str(await self._city.city_id()),
            'chat_id': int(self._chat_id),
        })
        if not updated_rows:
            raise UserNotFoundError
