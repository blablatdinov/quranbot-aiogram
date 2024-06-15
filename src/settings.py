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

from pathlib import Path
from typing import final

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent  # Path to src dir


@final
class Settings(BaseSettings):
    """Настройки приложения."""

    REDIS_DSN: RedisDsn
    DEBUG: bool
    DATABASE_URL: PostgresDsn
    API_TOKEN: str
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_VHOST: str
    SENTRY_DSN: str
    ADMIN_CHAT_IDS: str
    TELEGRAM_CLIENT_ID: str = ''
    TELEGRAM_CLIENT_HASH: str = ''
    BASE_DIR: Path = BASE_DIR
    DAILY_AYATS: bool = False
    DAILY_PRAYERS: bool = False
    RAMADAN_MODE: bool = False

    def admin_chat_ids(self) -> list[int]:
        """Список идентификаторов админов."""
        return [
            int(chat_id.strip())
            for chat_id in self.ADMIN_CHAT_IDS.strip().split(',')
        ]
