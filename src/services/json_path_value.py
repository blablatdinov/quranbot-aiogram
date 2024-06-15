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

# TODO #899 Перенести классы в отдельные файлы 9

from collections.abc import Iterable
from contextlib import suppress
from typing import Generic, Protocol, TypeVar, final, override

import attrs
import jsonpath_ng
from pyeo import elegant

from app_types.stringable import SupportsStr

_ET_co = TypeVar('_ET_co', covariant=True)


@elegant
class JsonPath(Protocol[_ET_co]):
    """Интерфейс объектов, получающих значение по jsonpath."""

    def evaluate(self) -> _ET_co:
        """Получить значение."""


@final
@attrs.define(frozen=True)
@elegant
class JsonPathValue(JsonPath, Generic[_ET_co]):
    """Объект, получающий значение по jsonpath.

    Пример поиска идентификатора чата:

    .. code-block:: python3

        int(
            SafeJsonPathValue(
                MatchManyJsonPath(
                    self._update.asdict(),
                    ('$..chat.id', '$..from.id'),
                ),
                InternalBotError(),
            ).evaluate(),
        )
    """

    _json: dict
    _json_path: SupportsStr

    @override
    def evaluate(self) -> _ET_co:
        """Получить значение."""
        match = jsonpath_ng.parse(self._json_path).find(self._json)
        if not match:
            raise ValueError
        return match[0].value


@final
@attrs.define(frozen=True)
@elegant
class MatchManyJsonPath(JsonPath, Generic[_ET_co]):
    """Поиск по нескольким jsonpath."""

    _json: dict
    _json_paths: Iterable[SupportsStr]

    @override
    def evaluate(self) -> _ET_co:
        """Получить значение."""
        for path in self._json_paths:
            with suppress(ValueError):
                return JsonPathValue(
                    self._json,
                    path,
                ).evaluate()
        raise ValueError


@final
@attrs.define(frozen=True)
@elegant
class ErrRedirectJsonPath(JsonPath, Generic[_ET_co]):
    """JsonPath с преобразованием исключений."""

    _origin: JsonPath
    _to_error: Exception

    @override
    def evaluate(self) -> _ET_co:
        """Получить значение."""
        with suppress(ValueError):
            return self._origin.evaluate()
        raise self._to_error
