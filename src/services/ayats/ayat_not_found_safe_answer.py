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
import httpx

from typing import final
from app_types.stringable import Stringable
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer


class AyatNotFoundSafeAnswer(TgAnswerInterface):
    """Объект обрабатывающий ошибку с не найденным аятом."""

    def __init__(self, answer: TgAnswerInterface, error_answer: TgAnswerInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param error_answer: TgAnswerInterface
        """
        self._origin = answer
        self._error_answer = error_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :returns: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except AyatNotFoundError:
            return await TgTextAnswer(
                self._error_answer,
                'Аят не найден',
            ).build(update)
