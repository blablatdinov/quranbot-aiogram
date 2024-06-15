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

import re
from typing import final, override

import attrs
import httpx
from pyeo import elegant

from app_types.stringable import SupportsStr
from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers.interface import TgAnswer


@final
@attrs.define(frozen=True)
@elegant
class TgMessageRegexAnswer(TgAnswer, SupportsStr):
    """Маршрутизация ответов по регулярному выражению."""

    _pattern: str
    _answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ."""
        if 'callback_query' in str(update):
            return []
        try:
            regex_result = re.search(self._pattern, str(MessageText(update)))
        except (AttributeError, MessageTextNotFoundError):
            return []
        if not regex_result:
            return []
        return await self._answer.build(update)

    @override
    def __str__(self) -> str:
        """Строковое представление."""
        return 'TgMessageRegexAnswer. pattern: {0}'.format(self._pattern)
