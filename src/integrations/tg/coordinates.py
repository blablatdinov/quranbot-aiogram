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

# TODO #899 Перенести классы в отдельные файлы 24

from typing import Protocol, final, override

import attrs
from pyeo import elegant

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import CoordinatesNotFoundError
from services.json_path_value import ErrRedirectJsonPath, JsonPathValue


@elegant
class Coordinates(Protocol):
    """Интерфейс координат."""

    def latitude(self) -> float:
        """Ширина."""

    def longitude(self) -> float:
        """Долгота."""


@final
@attrs.define(frozen=True)
@elegant
class FkCoordinates(Coordinates):
    """Стаб для координат."""

    _latitude: float
    _longitude: float

    @override
    def latitude(self) -> float:
        """Широта."""
        return self._latitude

    @override
    def longitude(self) -> float:
        """Долгота."""
        return self._longitude


@final
@attrs.define(frozen=True)
@elegant
class TgMessageCoordinates(Coordinates):
    """Координаты, принятые из чата."""

    _update: Update

    @override
    def latitude(self) -> float:
        """Ширина."""
        return float(
            ErrRedirectJsonPath(
                JsonPathValue(
                    self._update.asdict(),
                    '$..[latitude]',
                ),
                CoordinatesNotFoundError(),
            ).evaluate(),
        )

    @override
    def longitude(self) -> float:
        """Долгота."""
        return float(
            ErrRedirectJsonPath(
                JsonPathValue(
                    self._update.asdict(),
                    '$..[longitude]',
                ),
                CoordinatesNotFoundError(),
            ).evaluate(),
        )
