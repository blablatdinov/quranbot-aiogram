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

# TODO #899 Перенести классы в отдельные файлы 23

import asyncio
from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant

from app_types.logger import LogSink
from app_types.runable import Runable
from exceptions.base_exception import InternalBotError
from integrations.tg.polling_updates import PollingUpdatesIterator
from integrations.tg.sendable import SendableInterface


@final
@attrs.define(frozen=True)
@elegant
class PollingApp(Runable):
    """Приложение на long polling."""

    _updates: PollingUpdatesIterator
    _sendable: SendableInterface
    _logger: LogSink

    @override
    async def run(self) -> None:
        """Запуск."""
        self._logger.info('Start app on polling')
        background_tasks = set()
        async for update_list in self._updates:
            for update in update_list:
                self._logger.debug('Update: {update}', update=update)
                task = asyncio.create_task(self._sendable.send(update))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
                await asyncio.sleep(0.1)


@final
@attrs.define(frozen=True)
@elegant
class AppWithGetMe(Runable):
    """Объект для запуска с предварительным запросом getMe."""

    _origin: Runable
    _token: str
    _logger: LogSink

    @override
    async def run(self) -> None:
        """Запуск."""
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api.telegram.org/bot{0}/getMe'.format(self._token))
            if response.status_code != httpx.codes.OK:
                raise InternalBotError(response.text)
            self._logger.info(response.content)
        await self._origin.run()


@final
@attrs.define(frozen=True)
@elegant
class DatabaseConnectedApp(Runable):
    """Декоратор для подключения к БД."""

    _pgsql: Database
    _app: Runable

    @override
    async def run(self) -> None:
        """Запуск."""
        await self._pgsql.connect()
        await self._app.run()
