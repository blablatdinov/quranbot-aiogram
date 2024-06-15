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

# TODO #899 Перенести классы в отдельные файлы 36

from typing import final, override

import attrs
import httpx
from pyeo import elegant
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.update import Update
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup
from services.switch_inline_query_answer import SwitchInlineQueryKeyboard
from services.user_state import RedisUserState, UserStep


@final
@attrs.define(frozen=True)
@elegant
class UserWithoutCitySafeAnswer(TgAnswer):
    """Объект для обработки случаев когда пользователь запрашивает время намаза без установленного города."""

    _origin: TgAnswer
    _invite_set_city_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        try:
            return await self._origin.build(update)
        except UserHasNotCityIdError:
            return await self._invite_set_city_answer.build(update)


@final
@attrs.define(frozen=True)
@elegant
class InviteSetCityAnswer(TgAnswer):
    """Ответ с приглашением ввести город."""

    _message_answer: TgAnswer
    _redis: Redis
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        await RedisUserState(
            self._redis, TgChatId(update), self._logger,
        ).change_step(UserStep.city_search)
        return await TgAnswerMarkup(
            self._message_answer,
            SwitchInlineQueryKeyboard(),
        ).build(update)
