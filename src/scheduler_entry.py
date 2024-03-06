"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
import logging

import httpx
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from settings.cached_settings import CachedSettings
from settings.env_file_settings import EnvFileSettings
from settings.settings import BASE_DIR
from srv.events.sink import RabbitmqSink

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


async def _morning_ayats_task() -> None:
    settings = CachedSettings(EnvFileSettings(BASE_DIR.parent / '.env'))
    await RabbitmqSink(settings, logger).send(
        'quranbot.mailings',
        {},
        'Mailing.DailyAyats',
        1,
    )


async def _daily_prayers_task() -> None:
    settings = CachedSettings(EnvFileSettings(BASE_DIR.parent / '.env'))
    await RabbitmqSink(settings, logger).send(
        'quranbot.mailings',
        {},
        'Mailing.DailyPrayers',
        1,
    )


async def main() -> None:
    """Entrypoint."""
    settings = CachedSettings(EnvFileSettings(BASE_DIR.parent / '.env'))
    redis_settings = httpx.URL(settings.REDIS_DSN)
    jobstores = {
        'default': RedisJobStore(
            host=redis_settings.host,
            port=redis_settings.port,
            db=0,
            username=redis_settings.username,
            password=redis_settings.password,
        ),
    }
    scheduler = AsyncIOScheduler(jobstores=jobstores)
    job = scheduler.add_job(_morning_ayats_task, 'cron', hour='7')
    job = scheduler.add_job(_daily_prayers_task, 'cron', hour='20')
    scheduler.start()
    logger.info('Starting the scheduler...')
    try:
        while True:  # noqa: WPS457
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping the scheduler...')
        job.remove()
        scheduler.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
