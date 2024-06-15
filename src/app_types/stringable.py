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

# TODO #899 Перенести классы в отдельные файлы 15

from typing import Protocol, final, override

import attrs
from pyeo import elegant


@elegant
class SupportsStr(Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    @override
    def __str__(self) -> str:
        """Приведение к строке."""


@elegant
class AsyncSupportsStr(Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    async def to_str(self) -> str:
        """Приведение к строке."""


@final
@attrs.define(frozen=True)
@elegant
class FkAsyncStr(AsyncSupportsStr):
    """Обертка для строки."""

    _source: str

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        return self._source


@final
@attrs.define(frozen=True)
@elegant
class ThroughString(SupportsStr):
    """Обертка для строки."""

    _source: str

    @override
    def __str__(self) -> str:
        """Строковое представление."""
        return self._source


@final
@attrs.define(frozen=True)
@elegant
class UnwrappedString(SupportsStr):
    """Строки без переноса."""

    _origin: SupportsStr

    @override
    def __str__(self) -> str:
        """Строковое представление."""
        return str(self._origin).replace('\n', '')
