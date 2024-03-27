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
import time
from pathlib import Path

import pika
import psycopg2
import pytest
import ujson

from settings.env_file_settings import EnvFileSettings


@pytest.fixture()
def _revert_changes():
    yield
    qbot_connection = psycopg2.connect(EnvFileSettings.from_filename('../.env').DATABASE_URL)
    qbot_connection.autocommit = True
    cursor = qbot_connection.cursor()
    cursor.execute('DELETE FROM ayats WHERE ayat_id = 1')
    for line in Path('src/tests/e2e/db-fixtures/bot/ayats.sql').read_text().strip().split('\n'):
        if '0acec6b6-4b3c-4ce9-8d11-3985f52a1c03' in line:
            cursor.execute(line)
            break
    cursor.close()
    qbot_connection.close()


@pytest.mark.usefixtures('_bot_process', '_revert_changes', '_clear_db')
def test_change_ayat(db_query_vals):
    settings = EnvFileSettings.from_filename('../.env')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost',
        port=5672,
        credentials=pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS),
    ))
    channel = connection.channel()
    channel.basic_publish(
        exchange='',
        routing_key='quranbot.ayats',
        body=ujson.dumps({
            'event_id': 'some_id',
            'event_version': 1,
            'event_name': 'Ayat.Changed',
            'event_time': '392409283',
            'producer': 'some producer',
            'data': {
                'public_id': '0acec6b6-4b3c-4ce9-8d11-3985f52a1c03',
                'day': 2,
                'audio_id': 'a2ed8d0e-ce4b-4994-9a12-e36482263cb7',
                'ayat_number': '1-3',
                'content': 'Updated content',
                'arab_text': 'Updated arab text',
                'transliteration': 'Updated arab transliteration',
            },
        }).encode('utf-8'),
    )

    time.sleep(5)

    assert db_query_vals('SELECT * FROM ayats WHERE ayat_id = 1') == [
        (
            1,
            '0acec6b6-4b3c-4ce9-8d11-3985f52a1c03',
            2,
            1,
            'a2ed8d0e-ce4b-4994-9a12-e36482263cb7',
            '1-3',
            'Updated content',
            'Updated arab text',
            'Updated arab transliteration',
        ),
    ]
