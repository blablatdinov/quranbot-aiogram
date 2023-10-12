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
import multiprocessing
import time
from pprint import pformat
from typing import override

import psycopg2
import pytest
from loguru import logger
from telethon.sync import TelegramClient

from main import main
from settings.env_file_settings import EnvFileSettings
from tests.creating_test_db import create_db, drop_db, fill_test_db


@pytest.fixture(scope='session')
def bot_name():
    return '@WokeUpSmiled_bot'


@pytest.fixture()
def _clear_db():
    qbot_connection = psycopg2.connect(EnvFileSettings.from_filename('../.env').DATABASE_URL)
    qbot_connection.autocommit = True
    cursor = qbot_connection.cursor()
    tables = (
        'prayers_at_user',
        'favorite_ayats',
        'podcast_reactions',
        'users',
    )
    for table in tables:
        cursor.execute('DELETE FROM {0}'.format(table))  # noqa: S608
    cursor.execute("SELECT setval('prayers_at_user_prayer_at_user_id_seq', 1, false)")


@pytest.fixture()
def db_conn():
    connection = psycopg2.connect(EnvFileSettings.from_filename('../.env').DATABASE_URL)
    connection.autocommit = True
    yield connection
    connection.close()


@pytest.fixture()
def db_query_vals(db_conn):
    @override
    def _db_query_vals(query):  # noqa: WPS430
        cursor = db_conn.cursor()
        cursor.execute(query)
        returned_values = cursor.fetchall()
        cursor.close()
        db_conn.close()
        return returned_values
    return _db_query_vals


@pytest.fixture(scope='session')
def _bot_process():
    create_db()
    fill_test_db()
    bot = multiprocessing.Process(target=main, args=(['src/main.py', 'run_polling'],))
    event_handler = multiprocessing.Process(target=main, args=(['src/main.py', 'receive_events'],))
    bot.start()
    event_handler.start()
    yield
    event_handler.terminate()
    bot.terminate()
    bot.join()
    drop_db()


@pytest.fixture()
def wait_until(bot_name):
    @override
    def _wait_until(tg_client, messages_count, retry=50, delay=0.1):  # noqa: WPS430
        for _ in range(retry):
            time.sleep(delay)
            last_messages = [mess for mess in tg_client.iter_messages(bot_name) if mess.message]
            if len(last_messages) > messages_count:
                break
            if len(last_messages) == messages_count:
                return last_messages
        logger.debug('Taked messages: {0}, count: {1}'.format(
            pformat([mess.message for mess in last_messages], width=99999),
            len(last_messages),
        ))
        raise TimeoutError
    return _wait_until


@pytest.fixture()
def tg_client(bot_name):
    asyncio.set_event_loop(asyncio.new_event_loop())
    settings = EnvFileSettings.from_filename('../.env')
    with TelegramClient('me', settings.TELEGRAM_CLIENT_ID, settings.TELEGRAM_CLIENT_HASH) as client:
        all_messages = [message.id for message in client.iter_messages('@WokeUpSmiled_bot')]
        client.delete_messages(entity=bot_name, message_ids=all_messages)
        yield client
