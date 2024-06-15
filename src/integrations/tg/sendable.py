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

# TODO #899 Перенести классы в отдельные файлы 21

import asyncio
from itertools import chain
from typing import Protocol, final, override
from urllib import parse as url_parse

import attrs
import httpx
import ujson
from more_itertools import distribute
from pyeo import elegant

from app_types.logger import LogSink
from app_types.update import Update
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.tg_answers.interface import TgAnswer


@elegant
class SendableInterface(Protocol):
    """Интерфейс объекта, отправляющего ответы в API."""

    async def send(self, update: Update) -> list[dict]:
        """Отправка."""


@final
@attrs.define(frozen=True)
@elegant
class FkSendable(SendableInterface):
    """Фейковый объект для отправки ответов."""

    _origin: list[dict]

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка."""
        return self._origin


@final
@attrs.define(frozen=True)
@elegant
class SendableAnswer(SendableInterface):
    """Объект, отправляющий ответы в API."""

    _answer: TgAnswer
    _logger: LogSink

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка."""
        responses = []
        success_status = 200
        async with httpx.AsyncClient() as client:
            for request in await self._answer.build(update):
                self._logger.debug('Try send request to: {0}'.format(
                    url_parse.unquote(str(request.url)),
                ))
                resp = await client.send(request)
                responses.append(resp.text)
                if resp.status_code != success_status:
                    raise TelegramIntegrationsError(resp.text)
            return [ujson.loads(response) for response in responses]


@final
@attrs.define(frozen=True)
@elegant
class UserNotSubscribedSafeSendable(SendableInterface):
    """Декоратор для обработки отписанных пользователей."""

    _origin: SendableInterface

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка."""
        try:
            responses = await self._origin.send(update)
        except TelegramIntegrationsError as err:
            error_messages = [
                'chat not found',
                'bot was blocked by the user',
                'user is deactivated',
            ]
            for error_message in error_messages:
                if error_message not in str(err):
                    continue
                dict_response = ujson.loads(str(err))
                return [dict_response]
            raise TelegramIntegrationsError(str(err)) from err
        return responses


@final
@attrs.define(frozen=True)
@elegant
class BulkSendableAnswer(SendableInterface):
    """Массовая отправка."""

    _answers: list[TgAnswer]
    _logger: LogSink

    @override
    async def send(self, update: Update) -> list[dict]:
        """Отправка."""
        tasks = [
            UserNotSubscribedSafeSendable(
                SendableAnswer(answer, self._logger),
            ).send(update)
            for answer in self._answers
        ]
        responses: list[dict] = []
        for sendable_slice in distribute(10, tasks):
            res_list = await asyncio.gather(*sendable_slice)
            for res in chain.from_iterable(res_list):
                responses.append(res)  # noqa: PERF402
        return responses
