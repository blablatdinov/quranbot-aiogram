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

# TODO #899 Перенести классы в отдельные файлы 10

from typing import Protocol, final, override

import attrs
import ujson
from pyeo import elegant

from app_types.stringable import SupportsStr


@elegant
class Update(SupportsStr, Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    def __str__(self) -> str:
        """Приведение к строке."""

    def asdict(self) -> dict:
        """Словарь."""


@final
@attrs.define(frozen=True)
@elegant
class FkUpdate(Update):
    """Подделка обновления."""

    _raw: SupportsStr

    @classmethod
    def empty_ctor(cls):
        return cls('{}')  # noqa: P103. Empty json

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        return str(self._raw)

    @override
    def asdict(self) -> dict:
        """Словарь.

        :return: dict
        """
        return ujson.loads(str(self._raw))
