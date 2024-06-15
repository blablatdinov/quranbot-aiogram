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

# TODO #899 Перенести классы в отдельные файлы 28

from typing import final, override

import attrs
import ujson
from pyeo import elegant

from app_types.update import Update
from integrations.tg.keyboard import KeyboardInterface


@final
@attrs.define(frozen=True)
@elegant
class ResizedKeyboard(KeyboardInterface):
    """Сжатая в высоту клавиатура."""

    _origin: KeyboardInterface

    @override
    async def generate(self, update: Update) -> str:
        """Генерация."""
        origin_keyboard = await self._origin.generate(update)
        keyboard_as_dict = ujson.loads(origin_keyboard)
        keyboard_as_dict['resize_keyboard'] = True
        return ujson.dumps(keyboard_as_dict)


@final
@elegant
class DefaultKeyboard(KeyboardInterface):
    """Класс клавиатуры по умолчанию."""

    @override
    async def generate(self, update: Update) -> str:
        """Генерация."""
        return '{"keyboard":[["🎧 Подкасты"],["🕋 Время намаза","🏘️ Поменять город"],["🌟 Избранное","🔍 Найти аят"]]}'
