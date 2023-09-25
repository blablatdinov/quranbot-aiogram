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
import re
from typing import Final, Literal, final

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.intable import SyncToAsyncIntable
from app_types.stringable import SupportsStr
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_id import MessageId
from integrations.tg.tg_answers import TgAnswerToSender, TgKeyboardEditAnswer, TgMessageIdAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from services.reset_state_answer import ResetStateAnswer
from srv.podcasts.podcast import RandomPodcast
from srv.podcasts.podcast_keyboard import PodcastKeyboard

PODCAST_ID_LITERAL: Final = 'podcast_id'
USER_ID_LITERAL: Final = 'user_id'


@final
@attrs.define(frozen=True)
@elegant
class PrayerReaction(object):
    """Реакция на подкаст."""

    _callback_query: SupportsStr

    def podcast_id(self) -> int:
        """Идентификатор подкаста.

        :return: int
        """
        return int(re.findall(r'\((.+)\)', str(self._callback_query))[0])

    def status(self) -> Literal['like'] | Literal['dislike']:
        """Реакция.

        :return: Literal['like'] | Literal['dislike']
        """
        if 'dislike' in str(self._callback_query):
            return 'dislike'
        return 'like'


@final
@attrs.define(frozen=True)
@elegant
class PrayerReactionChangeAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _origin: TgAnswer
    _redis: Redis
    _pgsql: Database

    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: AnswerInterface
        """
        reaction = PrayerReaction(CallbackQueryData(update))
        query = """
            SELECT reaction
            FROM podcast_reactions
            WHERE user_id = :user_id AND podcast_id = :podcast_id
        """
        prayer_existed_reaction = await self._pgsql.fetch_val(query, {
            USER_ID_LITERAL: int(TgChatId(update)),
            PODCAST_ID_LITERAL: reaction.podcast_id(),
        })
        if prayer_existed_reaction:
            if prayer_existed_reaction == reaction.status():
                query = """
                    DELETE FROM podcast_reactions
                    WHERE user_id = :user_id AND podcast_id = :podcast_id
                """
                await self._pgsql.execute(query, {
                    USER_ID_LITERAL: int(TgChatId(update)),
                    PODCAST_ID_LITERAL: reaction.podcast_id(),
                })
            else:
                query = """
                    UPDATE podcast_reactions
                    SET reaction = :reaction
                    WHERE user_id = :user_id AND podcast_id = :podcast_id
                """
                await self._pgsql.execute(query, {
                    'reaction': reaction.status(),
                    USER_ID_LITERAL: int(TgChatId(update)),
                    PODCAST_ID_LITERAL: reaction.podcast_id(),
                })
        else:
            query = """
                INSERT INTO podcast_reactions (podcast_id, user_id, reaction)
                VALUES (:podcast_id, :user_id, :reaction)
            """
            await self._pgsql.execute(query, {
                PODCAST_ID_LITERAL: reaction.podcast_id(),
                USER_ID_LITERAL: int(TgChatId(update)),
                'reaction': reaction.status(),
            })
        podcast = RandomPodcast(
            SyncToAsyncIntable(reaction.podcast_id()),
            self._pgsql,
        )
        return await ResetStateAnswer(
            TgAnswerToSender(
                TgMessageIdAnswer(
                    TgKeyboardEditAnswer(
                        TgAnswerMarkup(
                            self._origin,
                            PodcastKeyboard(self._pgsql, podcast),
                        ),
                    ),
                    int(MessageId(update)),
                ),
            ),
            self._redis,
        ).build(update)