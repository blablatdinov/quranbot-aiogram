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

from app_types.intable import ThroughAsyncIntable
from app_types.stringable import Stringable
from db.connection import database
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgTextAnswer
from services.answers.answer import FileAnswer, TelegramFileIdAnswer
from services.ayats.ayat import QAyat
from services.ayats.ayat_by_id_message_answer import AyatByIdMessageAnswer
from services.ayats.search_by_sura_ayat_num import AyatSearchInterface
from services.regular_expression import IntableRegularExpression


@final
class AyatByIdAnswer(TgAnswerInterface):
    """Ответ на аят по идентификатору."""

    def __init__(
        self,
        debug_mode: bool,
        ayat_search: AyatSearchInterface,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
    ):
        """Конструктор класса.

        :param debug_mode: bool
        :param ayat_search: AyatSearchInterface
        :param message_answer: TgAnswerInterface
        :param file_answer: TgAnswerInterface
        """
        self._debug_mode = debug_mode
        self._ayat_search = ayat_search
        self._message_answer = message_answer
        self._file_answer = file_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        result_ayat = QAyat(
            ThroughAsyncIntable(
                int(IntableRegularExpression(
                    str(CallbackQueryData(update)),
                )),
            ),
            database,
        )
        return await TgAnswerList(
            AyatByIdMessageAnswer(
                result_ayat, self._message_answer,
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._file_answer,
                    await result_ayat.tg_file_id(),
                ),
                TgTextAnswer(
                    self._message_answer,
                    await result_ayat.file_link(),
                ),
            ),
        ).build(update)
