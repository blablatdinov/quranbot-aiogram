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

# TODO #899 Перенести классы в отдельные файлы 4

from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.intable import FkAsyncIntable
from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_id import TgMessageId
from integrations.tg.tg_answers import TgAnswerToSender, TgKeyboardEditAnswer, TgMessageIdAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from services.json_path_value import MatchManyJsonPath
from services.reset_state_answer import ResetStateAnswer
from services.user_state import CachedUserState, RedisUserState
from srv.podcasts.podcast import PgPodcast
from srv.podcasts.podcast_answer import MarkuppedPodcastAnswer, PodcastAnswer
from srv.podcasts.podcast_keyboard import PodcastKeyboard
from srv.reactions.pg_reaction import PgReaction
from srv.reactions.podcast_reaction import PodcastReaction


@final
@attrs.define(frozen=True)
@elegant
class PodcastMessageTextNotExistsSafeAnswer(TgAnswer):
    """В случаи нажатия на кнопку с отсутствующем текстом сообщения."""

    _edited_markup_answer: TgAnswer
    _new_podcast_message_answer: TgAnswer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ."""
        try:
            return await self._message_text_exists_case(update)
        except ValueError:
            return await self._new_podcast_message_answer.build(update)

    async def _message_text_exists_case(self, update: Update) -> list[httpx.Request]:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_message_text_exists_case"
        MatchManyJsonPath(
            update.asdict(),
            ('$..message.text', '$..message.audio'),
        ).evaluate()
        return await self._edited_markup_answer.build(update)


@final
@attrs.define(frozen=True)
@elegant
class PodcastReactionChangeAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _origin: TgAnswer
    _redis: Redis
    _pgsql: Database
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ."""
        reaction = PodcastReaction(CallbackQueryData(update))
        podcast = PgPodcast(
            FkAsyncIntable(reaction.podcast_id()),
            self._pgsql,
        )
        await PgReaction(
            self._pgsql,
            TgChatId(update),
            reaction,
        ).apply()
        return await ResetStateAnswer(
            PodcastMessageTextNotExistsSafeAnswer(
                TgMessageIdAnswer(
                    TgAnswerToSender(
                        TgKeyboardEditAnswer(
                            TgAnswerMarkup(
                                self._origin,
                                PodcastKeyboard(self._pgsql, podcast),
                            ),
                        ),
                    ),
                    TgMessageId(update),
                ),
                PodcastAnswer(
                    self._origin,
                    MarkuppedPodcastAnswer(
                        self._debug_mode,
                        self._origin,
                        self._redis,
                        self._pgsql,
                        podcast,
                    ),
                    self._redis,
                    podcast,
                    self._logger,
                    show_podcast_id=True,
                ),
            ),
            CachedUserState(RedisUserState(self._redis, TgChatId(update), self._logger)),
        ).build(update)
