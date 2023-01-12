"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
from typing import final

import httpx

from app_types.stringable import Stringable
from db.connection import database
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerMarkup, TgTextAnswer
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from services.ayats.ayat import Ayat
from services.ayats.ayat_favorite_keyboard_button import AyatFavoriteKeyboardButton
from services.ayats.ayat_neighbor_keyboard import NeighborAyatKeyboard
from services.ayats.enums import AyatCallbackTemplateEnum


@final
class AyatByIdMessageAnswer(TgAnswerInterface):
    """Текстовый ответ на поиск аята."""

    def __init__(self, result_ayat: Ayat, message_answer: TgAnswerInterface):
        """Конструктор класса.

        :param result_ayat: Ayat
        :param message_answer: TgAnswerInterface
        """
        self._result_ayat = result_ayat
        self._message_answer = message_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return await TgAnswerMarkup(
            TgTextAnswer(
                self._message_answer,
                await self._result_ayat.text(),
            ),
            AyatFavoriteKeyboardButton(
                self._result_ayat,
                NeighborAyatKeyboard(
                    NeighborAyats(database, await self._result_ayat.id()),
                    AyatCallbackTemplateEnum.get_ayat,
                ),
                FavoriteAyatsRepository(database),
            ),
        ).build(update)
