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

from typing import Protocol, TypeAlias

from eljson.json import Json
from pyeo import elegant

from app_types.stringable import AsyncSupportsStr
from srv.ayats.ayat_identifier import AyatIdentifier
from srv.files.file import TgFile

AyatText: TypeAlias = str


@elegant
class Ayat(AsyncSupportsStr, Protocol):
    """Интерфейс аята."""

    def identifier(self) -> AyatIdentifier:
        """Идентификатор аята."""

    async def to_str(self) -> AyatText:
        """Строковое представление."""

    async def audio(self) -> TgFile:
        """Аудио файл."""

    async def change(self, event_body: Json) -> None:
        """Изменить содержимое аята."""
