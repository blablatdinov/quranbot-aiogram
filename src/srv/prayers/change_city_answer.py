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

# TODO #899 Перенести классы в отдельные файлы 32

from typing import final, override

import attrs
import httpx
from pyeo import elegant

from app_types.update import Update
from exceptions.content_exceptions import CityNotSupportedError
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer
from srv.prayers.city import City
from srv.prayers.update_user_city import UpdatedUserCity


@final
@attrs.define(frozen=True)
@elegant
class CityNotSupportedAnswer(TgAnswer):
    """Ответ о неподдерживаемом городе."""

    _origin: TgAnswer
    _error_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ."""
        try:
            return await self._origin.build(update)
        except CityNotSupportedError:
            return await TgTextAnswer.str_ctor(
                self._error_answer,
                'Этот город не поддерживается',
            ).build(update)


@final
@attrs.define(frozen=True)
@elegant
class ChangeCityAnswer(TgAnswer):
    """Ответ со сменой города."""

    _origin: TgAnswer
    _user_city: UpdatedUserCity
    _city: City

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа."""
        await self._user_city.update()
        return await TgTextAnswer.str_ctor(
            self._origin,
            'Вам будет приходить время намаза для города {0}'.format(await self._city.name()),
        ).build(update)
