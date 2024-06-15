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

# TODO #899 Перенести классы в отдельные файлы 58

from typing import final, override

import attrs
import httpx
from pyeo import elegant

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from exceptions.content_exceptions import TelegramFileIdNotFilledError
from integrations.tg.tg_answers import TgAnswer


@final
@attrs.define(frozen=True)
@elegant
class TgFileIdNotFilledSafeAnswer(TgAnswer):
    """Декоратор для обработки файлов с незаполненным идентификатором файла."""

    _file_id_answer: TgAnswer
    _text_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        try:
            return await self._file_id_answer.build(update)
        except TelegramFileIdNotFilledError:
            return await self._text_answer.build(update)


@final
@attrs.define(frozen=True)
@elegant
class FileAnswer(TgAnswer):
    """Класс ответа с файлом."""

    _debug_mode: SupportsBool
    _telegram_file_id_answer: TgAnswer
    _file_link_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Отправка."""
        if self._debug_mode:
            return await self._file_link_answer.build(update)
        return await TgFileIdNotFilledSafeAnswer(
            self._telegram_file_id_answer,
            self._file_link_answer,
        ).build(update)
