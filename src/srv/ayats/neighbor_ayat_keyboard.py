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

# TODO #899 Перенести классы в отдельные файлы 48

from contextlib import suppress
from typing import Protocol, final, override

import attrs
import ujson
from pyeo import elegant

from app_types.update import Update
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.keyboard import KeyboardInterface
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.neighbor_ayats import NeighborAyats


@elegant
class NeighborAyatsButtons(Protocol):
    """Кнопки для клавиатуры с соседними аятами."""

    async def left(self) -> dict[str, str] | None:
        """Левая кнопка."""

    async def right(self) -> dict[str, str] | None:
        """Правая кнопка."""


@final
@attrs.define(frozen=True)
@elegant
class NeighborAyatsBtns(NeighborAyatsButtons):
    """Кнопки для клавиатуры с соседними аятами."""

    _ayats_neighbors: NeighborAyats
    _callback_template: AyatCallbackTemplateEnum

    async def left(self) -> dict[str, str] | None:
        """Левая кнопка."""
        with suppress(AyatNotFoundError):
            left = await self._ayats_neighbors.left_neighbor()
            return {
                'text': '<- {0}:{1}'.format(
                    await left.identifier().sura_num(),
                    await left.identifier().ayat_num(),
                ),
                'callback_data': self._callback_template.format(await left.identifier().ayat_id()),
            }
        return None

    async def right(self) -> dict[str, str] | None:
        """Правая кнопка."""
        with suppress(AyatNotFoundError):
            right = await self._ayats_neighbors.right_neighbor()
            return {
                'text': '{0}:{1} ->'.format(
                    await right.identifier().sura_num(),
                    await right.identifier().ayat_num(),
                ),
                'callback_data': self._callback_template.format(await right.identifier().ayat_id()),
            }
        return None


@final
@attrs.define(frozen=True)
@elegant
class NeighborAyatKeyboard(KeyboardInterface):
    """Клавиатура с соседними аятами."""

    _ayats_neighbors: NeighborAyats
    _callback_template: AyatCallbackTemplateEnum

    @override
    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры."""
        buttons = []
        btns = NeighborAyatsBtns(self._ayats_neighbors, self._callback_template)
        left_button = await btns.left()
        if left_button:
            buttons.append(left_button)
        buttons.append({
            'text': await self._ayats_neighbors.page(),
            'callback_data': 'fake',
        })
        right_button = await btns.right()
        if right_button:
            buttons.append(right_button)
        return ujson.dumps({
            'inline_keyboard': [buttons],
        })
