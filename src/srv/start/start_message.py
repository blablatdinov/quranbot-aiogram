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

# TODO #899 Перенести классы в отдельные файлы 39

from contextlib import suppress
from typing import Protocol, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.intable import AsyncIntable, FkAsyncIntable
from exceptions.base_exception import BaseAppError
from exceptions.internal_exceptions import UserNotFoundError
from exceptions.user import StartMessageNotContainReferrerError
from services.regular_expression import IntableRegularExpression
from srv.users.pg_user import PgUser
from srv.users.valid_chat_id import PgValidChatId


@elegant
class AsyncIntOrNone(Protocol):
    """AsyncIntOrNone."""

    async def to_int(self) -> int | None:
        """Числовое представление."""


@final
@attrs.define(frozen=True)
@elegant
class FkAsyncIntOrNone(AsyncIntOrNone):
    """FkAsyncIntOrNone."""

    _origin_value: int | None

    @override
    async def to_int(self) -> int | None:
        """Числовое представление."""
        return self._origin_value


@final
@attrs.define(frozen=True)
@elegant
class ReferrerChatId(AsyncIntable):
    """Идентификатор чата пригласившего."""

    _message: str
    _pgsql: Database

    @override
    async def to_int(self) -> int:
        """Получить идентификатор пригласившего."""
        try:
            message_meta = int(IntableRegularExpression(self._message))
        except BaseAppError as err:
            raise StartMessageNotContainReferrerError from err
        max_legacy_id = 3000
        if message_meta < max_legacy_id:
            return await PgUser.legacy_id_ctor(
                FkAsyncIntable(
                    IntableRegularExpression(self._message),
                ),
                self._pgsql,
            ).chat_id()
        return await PgUser(
            PgValidChatId.int_ctor(
                self._pgsql,
                IntableRegularExpression(self._message),
            ),
            self._pgsql,
        ).chat_id()


@final
@attrs.define(frozen=True)
@elegant
class ReferrerIdOrNone(AsyncIntOrNone):
    """Идентификатор чата пригласившего."""

    _origin: AsyncIntable

    @override
    async def to_int(self) -> int | None:
        """Получить идентификатор пригласившего."""
        with suppress(StartMessageNotContainReferrerError, UserNotFoundError):
            return await self._origin.to_int()
        return None
