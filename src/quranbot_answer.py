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
from databases import Database
from redis.asyncio import Redis

from app_types.update import Update
from handlers.favorites_answer import FavoriteAyatsAnswer
from handlers.full_start_answer import FullStartAnswer
from handlers.paginate_by_search_ayat import PaginateBySearchAyat
from handlers.podcast_answer import PodcastAnswer
from handlers.prayer_reaction_change_answer import PrayerReactionChangeAnswer
from handlers.prayer_time_answer import PrayerTimeAnswer
from handlers.search_ayat_by_keyword_answer import SearchAyatByKeywordAnswer
from handlers.search_ayat_by_numbers_answer import SearchAyatByNumbersAnswer
from handlers.search_city_answer import SearchCityAnswer
from handlers.status_answer import StatusAnswer
from handlers.user_prayer_status_change_answer import UserPrayerStatusChangeAnswer
from integrations.tg.tg_answers import (
    TgAnswer,
    TgAnswerFork,
    TgAnswerToSender,
    TgCallbackQueryRegexAnswer,
    TgEmptyAnswer,
    TgMessageAnswer,
    TgMessageRegexAnswer,
    TgTextAnswer,
)
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from services.answers.change_state_answer import ChangeStateAnswer
from services.answers.safe_fork import SafeFork
from services.help_answer import HelpAnswer
from services.state_answer import StepAnswer
from services.user_state import UserStep
from settings.admin_chat_ids import AdminChatIds
from settings.debug_mode import DebugMode
from settings.settings import Settings
from srv.admin_messages.pg_admin_message import PgAdminMessage
from srv.ayats.ayat_by_id_answer import AyatByIdAnswer
from srv.ayats.change_favorite_ayat_answer import ChangeFavoriteAyatAnswer
from srv.ayats.favorite_ayat_page import FavoriteAyatPage
from srv.events.sink import SinkInterface
from srv.prayers.inline_query_answer import InlineQueryAnswer
from srv.prayers.invite_set_city_answer import InviteSetCityAnswer


@final
class QuranbotAnswer(TgAnswer):
    """Ответ бота quranbot."""

    def __init__(
        self,
        database: Database,
        redis: Redis,
        event_sink: SinkInterface,
        settings: Settings,
    ) -> None:
        """Конструктор класса.

        :param database: Database
        :param redis: Redis
        :param event_sink: SinkInterface
        :param settings: Settings
        """
        self._pgsql = database
        self._redis = redis
        self._event_sink = event_sink
        self._settings = settings
        self._pre_build()

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await self._answer.build(update)

    def _pre_build(self) -> None:
        empty_answer = TgEmptyAnswer(self._settings.API_TOKEN)
        self._answer = SafeFork(
            TgAnswerFork(
                TgMessageRegexAnswer(
                    'Подкасты',
                    PodcastAnswer.random_podcast_ctor(
                        DebugMode(self._settings),
                        empty_answer,
                        self._redis,
                        self._pgsql,
                    ),
                ),
                TgMessageRegexAnswer(
                    r'/podcast\d+',
                    PodcastAnswer.concrete_podcast_ctor(
                        DebugMode(self._settings),
                        empty_answer,
                        self._redis,
                        self._pgsql,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Время намаза',
                    PrayerTimeAnswer.new_prayers_ctor(
                        self._pgsql, empty_answer, AdminChatIds(self._settings), self._redis,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Избранное',
                    FavoriteAyatsAnswer(DebugMode(self._settings), self._pgsql, self._redis, empty_answer),
                ),
                TgMessageRegexAnswer(
                    r'\d+:\d+',
                    SearchAyatByNumbersAnswer(DebugMode(self._settings), empty_answer, self._redis, self._pgsql),
                ),
                TgMessageRegexAnswer(
                    'Найти аят',
                    ChangeStateAnswer(
                        TgTextAnswer.str_ctor(TgHtmlMessageAnswerToSender(empty_answer), 'Введите слово для поиска:'),
                        self._redis,
                        UserStep.ayat_search,
                    ),
                ),
                TgMessageRegexAnswer(
                    'Поменять город',
                    InviteSetCityAnswer(
                        TgTextAnswer.str_ctor(
                            TgHtmlMessageAnswerToSender(empty_answer),
                            'Отправьте местоположение или воспользуйтесь поиском',
                        ),
                        self._redis,
                    ),
                ),
                TgMessageRegexAnswer(
                    '/start',
                    FullStartAnswer(self._pgsql, empty_answer, self._event_sink, self._redis, self._settings),
                ),
                TgMessageRegexAnswer(
                    '/status',
                    StatusAnswer(empty_answer, self._pgsql, self._redis),
                ),
                TgMessageRegexAnswer(
                    '/help',
                    HelpAnswer(empty_answer, PgAdminMessage('start', self._pgsql), self._redis),
                ),
                StepAnswer(
                    UserStep.ayat_search.value,
                    SearchAyatByKeywordAnswer(DebugMode(self._settings), empty_answer, self._redis, self._pgsql),
                    self._redis,
                ),
                TgCallbackQueryRegexAnswer(
                    '(mark_readed|mark_not_readed)',
                    UserPrayerStatusChangeAnswer(empty_answer, self._pgsql, self._redis),
                ),
                TgCallbackQueryRegexAnswer(
                    '(like|dislike)',
                    PrayerReactionChangeAnswer(DebugMode(self._settings), empty_answer, self._redis, self._pgsql),
                ),
                TgCallbackQueryRegexAnswer(
                    'getAyat',
                    AyatByIdAnswer(DebugMode(self._settings), empty_answer, self._pgsql),
                ),
                StepAnswer(
                    UserStep.ayat_search.value,
                    TgCallbackQueryRegexAnswer(
                        'getSAyat',
                        PaginateBySearchAyat(empty_answer, self._redis, self._pgsql, self._settings),
                    ),
                    self._redis,
                ),
                StepAnswer(
                    UserStep.city_search.value,
                    SearchCityAnswer(self._pgsql, empty_answer, DebugMode(self._settings), self._redis),
                    self._redis,
                ),
                TgCallbackQueryRegexAnswer(
                    'getFAyat',
                    FavoriteAyatPage(DebugMode(self._settings), empty_answer, self._pgsql),
                ),
                TgCallbackQueryRegexAnswer(
                    '(addToFavor|removeFromFavor)',
                    ChangeFavoriteAyatAnswer(self._pgsql, empty_answer, self._redis),
                ),
                InlineQueryAnswer(empty_answer, self._pgsql),
            ),
            TgAnswerToSender(
                TgMessageAnswer(empty_answer),
            ),
        )
