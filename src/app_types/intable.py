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

# TODO #899 Перенести классы в отдельные файлы 13

from typing import Protocol, SupportsInt, final, override

import attrs
from pyeo import elegant


@elegant
class AsyncIntable(Protocol):
    """Интерфейс объектов, которые можно привести к числу."""

    async def to_int(self) -> int:
        """Приведение к числу с возможностью переключения контекста."""


@final
@attrs.define(frozen=True)
@elegant
class FkIntable(SupportsInt):
    """Сквозное число."""

    _source: int

    @override
    def __int__(self) -> int:
        """Приведение к числу."""
        return self._source


@final
@attrs.define(frozen=True)
@elegant
class FkAsyncIntable(AsyncIntable):
    """Сквозное число."""

    _source: SupportsInt

    @override
    async def to_int(self) -> int:
        """Приведение к числу с возможностью переключения контекста."""
        return int(self._source)


@final
@elegant
class CachedAsyncIntable(AsyncIntable):
    """Кэшируемое число."""

    def __init__(self, origin: AsyncIntable) -> None:
        """Конструктор."""
        self._origin = origin
        self._cached = False
        self._cached_value = 0

    @override
    async def to_int(self) -> int:
        """Числовое представление."""
        if self._cached:
            return self._cached_value
        int_val = await self._origin.to_int()
        self._cached = True
        self._cached_value = int_val
        return int_val
