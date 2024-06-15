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
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer
from services.regular_expression import IntableRegularExpression
from srv.ayats.ayat_answer import AyatAnswer
from srv.ayats.ayat_answer_keyboard import AyatAnswerKeyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.favorite_ayats import FavoriteAyats
from srv.ayats.favorites.user_favorite_ayats import UserFavoriteAyats
from srv.ayats.neighbor_ayats import FavoriteNeighborAyats


@final
@attrs.define(frozen=True)
@elegant
class FavoriteAyatPage(TgAnswer):
    """Страница с избранным аятом."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        favorite_ayats = await FavoriteAyats(TgChatId(update), self._pgsql).to_list()
        for ayat in favorite_ayats:
            expect_ayat_id = IntableRegularExpression(CallbackQueryData(update))
            if await ayat.identifier().ayat_id() == int(expect_ayat_id):
                result_ayat = ayat
                break
        return await AyatAnswer(
            self._debug_mode,
            self._empty_answer,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                FavoriteNeighborAyats(
                    await result_ayat.identifier().ayat_id(),
                    UserFavoriteAyats(self._pgsql, TgChatId(update)),
                ),
                AyatCallbackTemplateEnum.get_favorite_ayat,
                self._pgsql,
            ),
        ).build(update)
