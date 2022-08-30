from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import sentry_sdk
from pydantic import BaseSettings, HttpUrl

BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    """Класс с настройками."""

    BASE_DIR: Path = BASE_DIR
    API_TOKEN: str
    DATABASE_URL: str
    TEST_DATABASE_URL: str = ''
    SENTRY_DSN: Optional[HttpUrl] = None
    DEBUG: bool
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 5
    ADMIN_CHAT_IDS: list[int] = [358610865]
    WEBHOOK_HOST: str = 'https://quranbot.ilaletdinov.ru'
    WEBHOOK_PATH: str = '/bot'
    WEBAPP_HOST: str = 'localhost'
    WEBAPP_PORT: int = 8010

    @property
    def webhook_url(self) -> str:
        """Путь для приема пакетов от телеграма.

        :return: str
        """
        return urljoin(self.WEBHOOK_HOST, self.WEBHOOK_PATH)

    @property
    def alembic_db_url(self) -> str:
        """Формирование адреса подключения к БД для алембика.

        :return: str
        """
        uri = self.DATABASE_URL
        if self.DATABASE_URL and self.DATABASE_URL.startswith('postgres://'):
            uri = self.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        return uri.replace('postgresql', 'postgresql+asyncpg')

    class Config(object):
        """Конфигурация настроек."""

        env_file = '.env'


settings = Settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )
