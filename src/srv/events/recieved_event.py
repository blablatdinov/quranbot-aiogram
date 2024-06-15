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

# TODO #899 Перенести классы в отдельные файлы 62

from typing import Protocol, TypeAlias, TypeVar, final, override

import attrs
from eljson.json import Json
from pyeo import elegant

JsonPathQuery: TypeAlias = str
JsonPathReturnType_co = TypeVar('JsonPathReturnType_co', covariant=True)


@elegant
class ReceivedEvent(Protocol[JsonPathReturnType_co]):
    """Событие."""

    async def process(self, json_doc: Json) -> None:
        """Обработать событие."""


@elegant
@attrs.define(frozen=True)
@final
class EventFork(ReceivedEvent):
    """Событие."""

    _name: str
    _version: int
    _origin: ReceivedEvent

    @override
    async def process(self, json_doc: Json) -> None:
        """Обработать событие."""
        name_match = json_doc.path('$.event_name')[0] == self._name
        version_match = json_doc.path('$.event_version')[0] == self._version
        if name_match and version_match:
            await self._origin.process(json_doc)
