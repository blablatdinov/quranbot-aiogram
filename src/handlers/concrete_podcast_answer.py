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
from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.intable import SyncToAsyncIntable
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers.interface import TgAnswer
from services.regular_expression import IntableRegularExpression
from srv.podcasts.podcast import PgPodcast
from srv.podcasts.podcast_answer import MarkuppedPodcastAnswer, PodcastAnswer


@final
@attrs.define(frozen=True)
@elegant
class ConcretePodcastAnswer(TgAnswer):
    """Ответ с подкастом."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: AnswerInterface
        """
        podcast = PgPodcast(
            SyncToAsyncIntable(IntableRegularExpression(str(MessageText(update)))),
            self._pgsql,
        )
        return await PodcastAnswer(
            self._empty_answer,
            MarkuppedPodcastAnswer(
                self._debug_mode,
                self._empty_answer,
                self._redis,
                self._pgsql,
                podcast,
            ),
            self._redis,
            podcast,
            show_podcast_id=False,
        ).build(update)