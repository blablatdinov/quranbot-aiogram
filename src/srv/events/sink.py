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

# TODO #899 Перенести классы в отдельные файлы 59

import time
import uuid
from typing import Protocol, final, override

import aio_pika
import attrs
import ujson
from loguru import logger
from pyeo import elegant
from quranbot_schema_registry import validate_schema

from app_types.logger import LogSink
from settings import Settings


@elegant
class SinkInterface(Protocol):
    """Интерфейс отправщика событий."""

    async def send(self, queue_name: str, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие."""


@final
@attrs.define(frozen=True)
@elegant
class FkSink(SinkInterface):
    """Фейковый слив для событий."""

    @override
    async def send(self, queue_name: str, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие."""


@final
@attrs.define(frozen=True)
@elegant
class RabbitmqSink(SinkInterface):
    """События в rabbitmq."""

    _settings: Settings
    _logger: LogSink

    @override
    async def send(self, queue_name: str, event_data: dict, event_name: str, version: int) -> None:
        """Отправить событие."""
        event = {
            'event_id': str(uuid.uuid4()),
            'event_version': 1,
            'event_name': event_name,
            'event_time': str(int(time.time())),
            'producer': 'quranbot',
            'data': event_data,
        }
        body_json = ujson.dumps(event)
        try:
            validate_schema(
                body_json,
                event_name,
                version,
            )
        except TypeError as err:
            logger.error('Schema of event: {0} invalid. {1}'.format(
                body_json, str(err),
            ))
            return
        connection = await aio_pika.connect_robust(
            'amqp://{0}:{1}@{2}:5672/{3}'.format(
                self._settings.RABBITMQ_USER,
                self._settings.RABBITMQ_PASS,
                self._settings.RABBITMQ_HOST,
                self._settings.RABBITMQ_VHOST,
            ),
        )
        self._logger.info('Try to publish event: {0}'.format(body_json))
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=body_json.encode('utf-8')),
                routing_key=queue_name,
            )
        self._logger.info('Event: {0} published'.format(body_json))
