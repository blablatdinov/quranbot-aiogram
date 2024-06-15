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

# TODO #899 Перенести классы в отдельные файлы 3

import datetime
import enum
from itertools import batched
from typing import Final, final

import attrs
import httpx
import ujson
from databases import Database
from dateutil import rrule
from pyeo import elegant

from app_types.stringable import AsyncSupportsStr
from app_types.update import Update
from integrations.tg.chat_id import ChatId, TgChatId
from integrations.tg.keyboard import KeyboardInterface
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgMessageAnswer, TgTextAnswer
from srv.prayers.new_prayers_at_user import NewPrayersAtUser
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser

IS_READ_LITERAL: Final = 'is_read'


class _PrayerNames(enum.Enum):

    fajr = ('fajr', 'Иртәнге')
    dhuhr = ('dhuhr', 'Өйлә')
    asr = ('asr', 'Икенде')
    maghrib = ('maghrib', 'Ахшам')
    isha = ("isha'a", 'Ястү')

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(field.name for field in cls)


@final
@attrs.define(frozen=True)
@elegant
class SkippedPrayersKeyboard(KeyboardInterface):
    """Клавиатура для пропущеных намазов."""

    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры."""
        return ujson.dumps({
            'inline_keyboard': [
                [{
                    'text': '{0}: (-1)'.format(field.value[1]),
                    'callback_data': 'decr({0})'.format(field.name),
                }]
                for field in _PrayerNames
            ],
        })


@final
@attrs.define(frozen=True)
@elegant
class PrayersStatistic(AsyncSupportsStr):
    """Статистика непрочитанных намазов."""

    _prayers_at_user: NewPrayersAtUser
    _chat_id: ChatId
    _pgsql: Database

    async def to_str(self) -> str:
        """Приведение к строке."""
        idx = 0
        res = dict.fromkeys(_PrayerNames.names(), 0)
        prayers_per_day = await self._prayers_per_day()
        for date in await self._dates_range():
            if date == prayers_per_day[idx][0]['day']:
                self._exist_prayer_case(prayers_per_day, res, idx)
                idx += 1
            else:
                await self._new_prayer_at_user_case(res, date)
        return '\n'.join([
            'Кол-во непрочитанных намазов:\n',
            'Иртәнге: {0}'.format(res[_PrayerNames.fajr.name]),
            'Өйлә: {0}'.format(res[_PrayerNames.dhuhr.name]),
            'Икенде: {0}'.format(res[_PrayerNames.asr.name]),
            'Ахшам: {0}'.format(res[_PrayerNames.maghrib.name]),
            'Ястү: {0}'.format(res[_PrayerNames.isha.name]),
        ])

    def _exist_prayer_case(self, prayers_per_day: list[tuple], res: dict, idx: int) -> None:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_exist_prayer_case"
        for prayer_idx, prayer_name in enumerate(_PrayerNames.names()):
            res[prayer_name] += int(not prayers_per_day[idx][prayer_idx][IS_READ_LITERAL])

    async def _new_prayer_at_user_case(self, res: dict, date: datetime.date) -> None:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_new_prayer_at_user_case"
        await self._prayers_at_user.create(date)
        for prayer_name in _PrayerNames.names():
            res[prayer_name] += 1

    async def _prayers_per_day(self) -> list[tuple]:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_prayers_per_day"
        query = '\n'.join([
            'SELECT',
            '    pau.is_read,',
            '    p.day,',
            '    p.name',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p ON pau.prayer_id = p.prayer_id',
            'WHERE pau.user_id = :chat_id',
            "ORDER BY p.day, ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        return list(batched(
            await self._pgsql.fetch_all(query, {
                'chat_id': int(self._chat_id),
            }),
            5,
        ))

    async def _dates_range(self) -> list[datetime.date]:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_dates_range"
        query = '\n'.join([
            'SELECT p.day',
            'FROM prayers_at_user AS pau',
            'INNER JOIN prayers AS p ON pau.prayer_id = p.prayer_id',
            'WHERE pau.user_id = :chat_id',
            "ORDER BY p.day, ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
        ])
        rows = await self._pgsql.fetch_all(query, {'chat_id': int(self._chat_id)})
        if not rows:
            return []
        return [
            dt.date()
            for dt in rrule.rrule(
                rrule.DAILY,
                dtstart=rows[0]['day'],
                until=rows[-1]['day'],
            )
        ]


@final
@attrs.define(frozen=True)
@elegant
class SkippedPrayersAnswer(TgAnswer):
    """Пропущенные намазы."""

    _empty_answer: TgAnswer
    _pgsql: Database

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        return await TgAnswerMarkup(
            TgTextAnswer(
                TgAnswerToSender(
                    TgMessageAnswer(self._empty_answer),
                ),
                PrayersStatistic(
                    PgNewPrayersAtUser(TgChatId(update), self._pgsql),
                    TgChatId(update),
                    self._pgsql,
                ),
            ),
            SkippedPrayersKeyboard(),
        ).build(update)
