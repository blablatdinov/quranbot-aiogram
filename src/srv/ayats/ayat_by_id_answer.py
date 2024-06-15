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
import httpx
from databases import Database
from pyeo import elegant

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.tg_answers import TgAnswer, TgAnswerList, TgAnswerToSender, TgAudioAnswer, TgTextAnswer
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from srv.ayats.ayat_by_id_message_answer import AyatByIdMessageAnswer
from srv.ayats.pg_ayat import PgAyat, TextLenSafeAyat
from srv.files.file_answer import FileAnswer
from srv.files.file_id_answer import TelegramFileIdAnswer


@final
@attrs.define(frozen=True)
@elegant
class AyatByIdAnswer(TgAnswer):
    """Ответ на аят по идентификатору."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        result_ayat = TextLenSafeAyat(PgAyat.from_callback_query(CallbackQueryData(update), self._pgsql))
        return await TgAnswerList(
            AyatByIdMessageAnswer(
                result_ayat, TgHtmlMessageAnswerToSender(self._empty_answer), self._pgsql,
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    TgAnswerToSender(TgAudioAnswer(self._empty_answer)),
                    await result_ayat.audio(),
                ),
                TgTextAnswer.str_ctor(
                    TgHtmlMessageAnswerToSender(self._empty_answer),
                    await (await result_ayat.audio()).file_link(),
                ),
            ),
        ).build(update)
