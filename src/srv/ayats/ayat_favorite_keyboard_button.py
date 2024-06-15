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

from typing import final, override

import attrs
import ujson
from pyeo import elegant

from app_types.supports_bool import AsyncSupportsBool
from app_types.update import Update
from integrations.tg.keyboard import KeyboardInterface
from srv.ayats.ayat import Ayat


@final
@attrs.define(frozen=True)
@elegant
class AyatFavoriteKeyboardButton(KeyboardInterface):
    """Кнопка с добавлением аята в избранные."""

    _origin: KeyboardInterface
    _is_favor: AsyncSupportsBool
    _ayat: Ayat

    @override
    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры."""
        keyboard = ujson.loads(await self._origin.generate(update))
        is_favor = await self._is_favor.to_bool()
        keyboard['inline_keyboard'].append([{
            'text': 'Удалить из избранного' if is_favor else 'Добавить в избранное',
            'callback_data': ('removeFromFavor({0})' if is_favor else 'addToFavor({0})').format(
                await self._ayat.identifier().ayat_id(),
            ),
        }])
        return ujson.dumps(keyboard)
