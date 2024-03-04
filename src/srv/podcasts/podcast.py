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
from typing import Protocol, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.intable import AsyncIntable
from exceptions.base_exception import InternalBotError
from exceptions.content_exceptions import TelegramFileIdNotFilledError
from srv.files.file import FileLink, TgFile, TgFileId


@elegant
class Podcast(TgFile, Protocol):
    """Интерфейс подкаста."""

    async def podcast_id(self) -> int:
        """Идентификатор аята."""


@final
@attrs.define(frozen=True)
@elegant
class PgPodcast(Podcast):
    """Объект подкаста."""

    _podcast_id: AsyncIntable
    _pgsql: Database

    @override
    async def podcast_id(self) -> int:
        """Идентификатор подкаста.

        :return: int
        """
        return await self._podcast_id.to_int()

    @override
    async def tg_file_id(self) -> TgFileId:
        """Получить идентификатор файла.

        :returns: str
        :raises InternalBotError: если таблица с подкастами не заполнена
        :raises TelegramFileIdNotFilledError: идентификатор файла не заполнен
        """
        query = '\n'.join([
            'SELECT f.telegram_file_id',
            'FROM podcasts AS p',
            'INNER JOIN files AS f ON p.file_id = f.file_id',
            'WHERE p.podcast_id = :podcast_id',
        ])
        row = await self._pgsql.fetch_one(
            query,
            {'podcast_id': await self._podcast_id.to_int()},
        )
        if not row:
            msg = 'Подкасты не найдены'
            raise InternalBotError(msg)
        if not row['telegram_file_id']:
            raise TelegramFileIdNotFilledError
        return row['telegram_file_id']

    @override
    async def file_link(self) -> FileLink:
        """Получить ссылку на файл.

        :returns: str
        :raises InternalBotError: если таблица с подкастами не заполнена
        """
        query = '\n'.join([
            'SELECT f.link',
            'FROM podcasts AS p',
            'INNER JOIN files AS f ON p.file_id = f.file_id',
            'WHERE p.podcast_id = :podcast_id',
        ])
        row = await self._pgsql.fetch_one(
            query,
            {'podcast_id': await self._podcast_id.to_int()},
        )
        if not row:
            msg = 'Подкасты не найдены'
            raise InternalBotError(msg)
        return row['link']
