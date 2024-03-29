"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
from typing import Protocol, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.intable import AsyncIntable, FkAsyncIntable


@elegant
class User(Protocol):
    """Интерфейс пользователя."""

    async def chat_id(self) -> int:
        """Идентификатор чата."""

    async def day(self) -> int:
        """День для рассылки утреннего контента."""

    async def is_active(self) -> bool:
        """Статус активности пользователя."""


@final
@attrs.define(frozen=True)
@elegant
class FkUser(User):
    """Фейковый пользователь."""

    _chat_id: int
    _day: int
    _is_active: bool

    async def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        return self._chat_id

    async def day(self) -> int:
        """День для рассылки утреннего контента.

        :return: int
        """
        return self._day

    async def is_active(self) -> bool:
        """Статус пользователя.

        :return: bool
        """
        return self._is_active


@final
@attrs.define(frozen=True)
@elegant
class ChatIdByLegacyId(AsyncIntable):
    """Идентификатор чата по старому идентификатору в БД.

    Остались реферальные ссылки, сгенерированные на предыдущей версии бота
    """

    _pgsql: Database
    _legacy_id: AsyncIntable

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        query = '\n'.join([
            'SELECT chat_id',
            'FROM users',
            'WHERE legacy_id = :legacy_id',
        ])
        return await self._pgsql.fetch_val(query, {'legacy_id': await self._legacy_id.to_int()})


@final
@attrs.define(frozen=True)
@elegant
class PgUser(User):
    """Пользователь в БД postgres."""

    _chat_id: AsyncIntable
    _pgsql: Database

    @classmethod
    def legacy_id_ctor(cls, legacy_id: AsyncIntable, pgsql: Database) -> User:
        """Конструктор по старому идентификатору в БД.

        :param legacy_id: int
        :param pgsql: Database
        :return: User
        """
        return cls(ChatIdByLegacyId(pgsql, legacy_id), pgsql)

    @classmethod
    def int_ctor(cls, chat_id: int, pgsql: Database) -> User:
        """Конструктор по идентификатору чата.

        :param chat_id: int
        :param pgsql: Database
        :return: User
        """
        return cls(FkAsyncIntable(chat_id), pgsql)

    @override
    async def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        return await self._chat_id.to_int()

    @override
    async def day(self) -> int:
        """День для рассылки утреннего контента.

        :return: int
        """
        query = '\n'.join([
            'SELECT day',
            'FROM users',
            'WHERE chat_id = :chat_id',
        ])
        return await self._pgsql.fetch_val(query, {'chat_id': await self._chat_id.to_int()})

    @override
    async def is_active(self) -> bool:
        """Статус пользователя.

        :return: bool
        """
        query = '\n'.join([
            'SELECT is_active',
            'FROM users',
            'WHERE chat_id = :chat_id',
        ])
        return await self._pgsql.fetch_val(query, {'chat_id': await self._chat_id.to_int()})
