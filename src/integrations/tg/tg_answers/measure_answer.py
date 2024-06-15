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

# TODO #899 Перенести классы в отдельные файлы 26

import time
from typing import SupportsFloat, final, override

import attrs
import httpx
from pyeo import elegant

from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.update_id import UpdateId


@final
@attrs.define(frozen=True)
class Millis(SupportsFloat):
    """Миллисекунды."""

    _millis: float

    @classmethod
    def seconds_ctor(cls, seconds: float) -> SupportsFloat:
        """Конструктор для секунд."""
        return Millis(seconds * 1000)

    @override
    def __float__(self) -> float:
        """Представление в форме числа с плавающей запятой."""
        return self._millis


@final
@attrs.define(frozen=True)
@elegant
class RoundedFloat(SupportsFloat):
    """Округленное дробное число."""

    _origin: SupportsFloat
    _shift_comma: int

    @override
    def __float__(self) -> float:
        """Представление в форме числа с плавающей запятой."""
        return round(float(self._origin), self._shift_comma)


@final
@attrs.define(frozen=True)
@elegant
class TgMeasureAnswer(TgAnswer):
    """Замеренный ответ."""

    _origin: TgAnswer
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        start = time.time()
        self._logger.info('Start process update <{0}>'.format(int(UpdateId(update))))
        requests = await self._origin.build(update)
        self._logger.info('Update <{0}> process time: {1:.2f} ms'.format(
            int(UpdateId(update)),
            float(
                RoundedFloat(
                    Millis.seconds_ctor(
                        time.time() - start,
                    ),
                    2,
                ),
            ),
        ))
        return requests
