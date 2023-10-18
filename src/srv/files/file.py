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
from pyeo import elegant

type TgFileId = str
type FileLink = str


class TgFile(Protocol):
    """Тип файла."""

    async def tg_file_id(self) -> TgFileId:
        """Идентификатор файла в телеграм."""

    async def file_link(self) -> FileLink:
        """Ссылка на файл."""


@final
@attrs.define(frozen=True)
@elegant
class FkFile(TgFile):
    """Фейковый файл."""

    _file_id: str
    _link: str

    @override
    async def tg_file_id(self) -> TgFileId:
        """Идентификатор файла в телеграм.

        :return: TgFileId
        """
        return self._file_id

    @override
    async def file_link(self) -> FileLink:
        """Идентификатор файла в телеграм.

        :return: FileLink
        """
        return self._link
