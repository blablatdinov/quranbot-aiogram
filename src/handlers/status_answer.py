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

import time
from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgAnswerToSender, TgMessageAnswer, TgTextAnswer
from integrations.tg.tg_answers.measure_answer import Millis, RoundedFloat


@final
@attrs.define(frozen=True)
@elegant
class StatusAnswer(TgAnswer):
    """Ответ со статусом системы."""

    _empty_answer: TgAnswer
    _pgsql: Database
    _redis: Redis

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        return await TgTextAnswer.str_ctor(
            TgAnswerToSender(
                TgMessageAnswer(self._empty_answer),
            ),
            '{0}\n{1}'.format(
                await self._measure_pgsql(),
                await self._measure_redis(),
            ),
        ).build(update)

    async def _measure_pgsql(self) -> str:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_measure_pgsql"
        db_start = time.time()
        await self._pgsql.execute('SELECT 1')
        return 'DB: {0} ms'.format(float(
            RoundedFloat(
                Millis.seconds_ctor(time.time() - db_start),
                2,
            ),
        ))

    async def _measure_redis(self) -> str:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_measure_redis"
        redis_start = time.time()
        await self._redis.ping()
        return 'Redis: {0} ms'.format(float(
            RoundedFloat(
                Millis.seconds_ctor(time.time() - redis_start),
                2,
            ),
        ))
