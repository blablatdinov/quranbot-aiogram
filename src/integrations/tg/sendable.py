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
import asyncio
import json
from typing import Protocol, final
from urllib import parse as url_parse

import attrs
import httpx
from loguru import logger
from more_itertools import chunked
from pyeo import elegant

from app_types.update import Update
from exceptions.internal_exceptions import TelegramIntegrationsError
from integrations.tg.tg_answers.interface import TgAnswer


@elegant
class SendableInterface(Protocol):
    """Интерфейс объекта, отправляющего ответы в API."""

    async def send(self, update) -> list[dict]:
        """Отправка.

        :param update: Update
        """


@final
@attrs.define(frozen=True)
@elegant
class SendableAnswer(SendableInterface):
    """Объект, отправляющий ответы в API."""

    _answer: TgAnswer

    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: Update
        :return: list[str]
        :raises TelegramIntegrationsError: при невалидном ответе от API телеграмма
        """
        responses = []
        success_status = 200
        async with httpx.AsyncClient() as client:
            for request in await self._answer.build(update):
                logger.debug('Try send request to: {0}'.format(url_parse.unquote(str(request.url))))
                resp = await client.send(request)
                responses.append(resp.text)
                if resp.status_code != success_status:
                    raise TelegramIntegrationsError(resp.text)
            return [json.loads(response) for response in responses]


@final
@attrs.define(frozen=True)
@elegant
class UserNotSubscribedSafeSendable(SendableInterface):
    """Декоратор для обработки отписанных пользователей."""

    _origin: SendableInterface

    async def send(self, update) -> list[dict]:
        """Отправка.

        :param update: Update
        :return: list[dict]
        :raises TelegramIntegrationsError: если ошибка не связана с блокировкой бота
        """
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
                dict_response = json.loads(str(err))
                return [dict_response]
            raise err
        return responses


@final
@attrs.define(frozen=True)
@elegant
class BulkSendableAnswer(SendableInterface):
    """Массовая отправка."""

    _answers: list[TgAnswer]

    async def send(self, update: Update) -> list[dict]:
        """Отправка.

        :param update: Update
        :return: list[dict]
        """
        tasks = [
            UserNotSubscribedSafeSendable(
                SendableAnswer(answer),
            ).send(update)
            for answer in self._answers
        ]
        responses = []
        for sendable_slice in chunked(tasks, 10):
            res_list = await asyncio.gather(*sendable_slice)
            for res in res_list:
                responses.append(res)
        return responses
