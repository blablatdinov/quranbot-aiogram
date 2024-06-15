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

from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.chat_id import TgChatId
from integrations.tg.coordinates import TgMessageCoordinates
from integrations.tg.exceptions.update_parse_exceptions import MessageTextNotFoundError
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswerFork, TgAnswerToSender, TgMessageAnswer, TgMessageRegexAnswer
from integrations.tg.tg_answers.interface import TgAnswer
from integrations.tg.tg_answers.location_answer import TgLocationAnswer
from integrations.tg.tg_answers.skip_not_processable import TgSkipNotProcessable
from services.reset_state_answer import ResetStateAnswer
from services.user_state import CachedUserState, RedisUserState
from srv.prayers.change_city_answer import ChangeCityAnswer, CityNotSupportedAnswer
from srv.prayers.city import PgCity
from srv.prayers.update_user_city import PgUpdatedUserCity
from srv.prayers.user_not_registered_safe_answer import UserNotRegisteredSafeAnswer
from srv.users.new_user import PgNewUser


@final
@attrs.define(frozen=True)
@elegant
class SearchCityAnswer(TgAnswer):
    """Ответ со списком городов для выбора."""

    _pgsql: Database
    _empty_answer: TgAnswer
    _debug_mode: SupportsBool
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Обработка запроса."""
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        try:
            city = PgCity.name_ctor(str(MessageText(update)), self._pgsql)
        except MessageTextNotFoundError:
            city = PgCity.location_ctor(TgMessageCoordinates(update), self._pgsql)
        return await UserNotRegisteredSafeAnswer(
            PgNewUser.ctor(TgChatId(update), self._pgsql, self._logger),
            TgSkipNotProcessable(
                TgAnswerFork(
                    self._logger,
                    TgMessageRegexAnswer(
                        '.+',
                        CityNotSupportedAnswer(
                            ResetStateAnswer(
                                ChangeCityAnswer(
                                    answer_to_sender,
                                    PgUpdatedUserCity(city, TgChatId(update), self._pgsql),
                                    city,
                                ),
                                CachedUserState(
                                    RedisUserState(self._redis, TgChatId(update), self._logger),
                                ),
                            ),
                            answer_to_sender,
                        ),
                    ),
                    TgLocationAnswer(
                        CityNotSupportedAnswer(
                            ChangeCityAnswer(
                                answer_to_sender,
                                PgUpdatedUserCity(city, TgChatId(update), self._pgsql),
                                city,
                            ),
                            answer_to_sender,
                        ),
                    ),
                ),
            ),
        ).build(update)
