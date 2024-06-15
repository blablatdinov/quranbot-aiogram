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

# TODO #899 Перенести классы в отдельные файлы 20

from typing import Protocol, SupportsInt, final, override

import attrs
import httpx
import ujson
from pyeo import elegant

from app_types.stringable import SupportsStr
from app_types.update import Update
from integrations.tg.update import TgUpdate


@final
@elegant
class UpdatesTimeout(SupportsInt):
    """Таймаут для обновлений."""

    @override
    def __int__(self) -> int:
        """Числовое представление."""
        return 5


@elegant
class UpdatesURLInterface(Protocol):
    """Интерфейс URL запроса для получения уведомлений."""

    def generate(self, update_id: int) -> str:
        """Генерация."""


@final
@attrs.define(frozen=True)
@elegant
class UpdatesURL(SupportsStr):
    """Базовый URL обновлений из телеграма."""

    _token: str

    @override
    def __str__(self) -> str:
        """Строчное представление."""
        return 'https://api.telegram.org/bot{0}/getUpdates'.format(self._token)


@final
@attrs.define(frozen=True)
@elegant
class UpdatesWithOffsetURL(UpdatesURLInterface):
    """URL для получения только новых обновлений."""

    _updates_url: SupportsStr

    @override
    def generate(self, update_id: int) -> str:
        """Генерация."""
        return '{0}?offset={1}'.format(self._updates_url, update_id)


@final
@attrs.define(frozen=True)
@elegant
class UpdatesLongPollingURL(UpdatesURLInterface):
    """URL обновлений с таймаутом."""

    _origin: UpdatesURLInterface
    _long_polling_timeout: SupportsInt

    @override
    def generate(self, update_id: int) -> str:
        """Генерация."""
        return str(httpx.URL(self._origin.generate(update_id)).copy_add_param(
            'timeout',
            int(self._long_polling_timeout),
        ))


@elegant
class UpdatesIteratorInterface(Protocol):
    """Интерфейс итератора по обновлениям."""

    def __aiter__(self) -> 'UpdatesIteratorInterface':
        """Точка входа в итератор."""

    async def __anext__(self) -> list[Update]:
        """Вернуть следующий элемент."""


@final
@attrs.define(slots=True)
@elegant
class PollingUpdatesIterator(UpdatesIteratorInterface):
    """Итератор по обновлениям."""

    _updates_url: UpdatesURLInterface
    _updates_timeout: SupportsInt

    _offset: int = 0

    @override
    def __aiter__(self) -> 'UpdatesIteratorInterface':
        """Точка входа в итератор."""
        return self

    @override
    async def __anext__(self) -> list[Update]:
        """Вернуть следующий элемент."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    self._updates_url.generate(self._offset),
                    timeout=int(self._updates_timeout),
                )
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                return []
            resp_content = resp.text
            try:
                parsed_result = ujson.loads(resp_content)['result']
            except KeyError:
                return []
            if not parsed_result:
                return []
            self._offset = parsed_result[-1]['update_id'] + 1  # noqa: WPS601
            return [TgUpdate(elem) for elem in parsed_result]
