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
from redis.asyncio import Redis

from app_types.intable import FkAsyncIntable
from app_types.logger import LogSink
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_id import TgMessageId
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerFork,
    TgAnswerMarkup,
    TgAnswerToSender,
    TgChatIdAnswer,
    TgKeyboardEditAnswer,
    TgMessageIdAnswer,
)
from services.regular_expression import IntableRegularExpression
from services.state_answer import StepAnswer
from services.user_state import UserStep
from srv.ayats.ayat_answer_keyboard import AyatAnswerKeyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.ayat_favorite_status import AyatFavoriteStatus
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.favorite_ayats_after_remove import FavoriteAyatsAfterRemove
from srv.ayats.neighbor_ayats import FavoriteNeighborAyats, PgNeighborAyats, TextSearchNeighborAyats
from srv.ayats.pg_ayat import PgAyat, TextLenSafeAyat


@final
@attrs.define(frozen=True)
@elegant
class ChangeFavoriteAyatAnswer(TgAnswer):
    """Ответ на запрос о смене аята в избранном."""

    _pgsql: Database
    _origin: TgAnswer
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        status = AyatFavoriteStatus(str(CallbackQueryData(update)))
        result_ayat = TextLenSafeAyat(
            PgAyat(
                FkAsyncIntable(
                    IntableRegularExpression(
                        str(CallbackQueryData(update)),
                    ),
                ),
                self._pgsql,
            ),
        )
        if status.change_to():
            query = '\n'.join([
                'INSERT INTO favorite_ayats',
                '(ayat_id, user_id)',
                'VALUES',
                '(:ayat_id, :user_id)',
            ])
        else:
            query = '\n'.join([
                'DELETE FROM favorite_ayats',
                'WHERE ayat_id = :ayat_id AND user_id = :user_id',
            ])
        await self._pgsql.execute(
            query, {'ayat_id': status.ayat_id(), 'user_id': int(TgChatId(update))},
        )
        chat_id = TgChatId(update)
        return await TgAnswerFork(
            self._logger,
            StepAnswer(
                UserStep.ayat_favor.value,
                TgChatIdAnswer(
                    TgMessageIdAnswer(
                        TgAnswerMarkup(
                            TgKeyboardEditAnswer(TgAnswerToSender(self._origin)),
                            AyatAnswerKeyboard(
                                result_ayat,
                                FavoriteNeighborAyats(
                                    status.ayat_id(),
                                    FavoriteAyatsAfterRemove(chat_id, status.ayat_id(), self._pgsql),
                                ),
                                AyatCallbackTemplateEnum.get_favorite_ayat,
                                self._pgsql,
                            ),
                        ),
                        TgMessageId(update),
                    ),
                    chat_id,
                ),
                self._redis,
                self._logger,
            ),
            StepAnswer(
                UserStep.ayat_search.value,
                TgChatIdAnswer(
                    TgMessageIdAnswer(
                        TgAnswerMarkup(
                            TgKeyboardEditAnswer(TgAnswerToSender(self._origin)),
                            AyatAnswerKeyboard(
                                result_ayat,
                                TextSearchNeighborAyats(
                                    self._pgsql,
                                    status.ayat_id(),
                                    AyatTextSearchQuery(self._redis, chat_id, self._logger),
                                ),
                                AyatCallbackTemplateEnum.get_search_ayat,
                                self._pgsql,
                            ),
                        ),
                        TgMessageId(update),
                    ),
                    chat_id,
                ),
                self._redis,
                self._logger,
            ),
            TgChatIdAnswer(
                TgMessageIdAnswer(
                    TgAnswerMarkup(
                        TgKeyboardEditAnswer(TgAnswerToSender(self._origin)),
                        AyatAnswerKeyboard(
                            result_ayat,
                            PgNeighborAyats(
                                self._pgsql, await result_ayat.identifier().ayat_id(),
                            ),
                            AyatCallbackTemplateEnum.get_ayat,
                            self._pgsql,
                        ),
                    ),
                    TgMessageId(update),
                ),
                chat_id,
            ),
        ).build(update)
