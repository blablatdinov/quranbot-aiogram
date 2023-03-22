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
from typing import Protocol, final

from databases import Database

from app_types.intable import AsyncIntable
from app_types.stringable import Stringable
from exceptions.content_exceptions import AyatNotFoundError
from repository.ayats.sura import Sura
from services.ayats.ayat_id_by_sura_ayat_num import AyatIdBySuraAyatNum
from services.ayats.search.ayat_search_query import SearchQuery, ValidatedSearchQuery


class Ayat(Protocol):
    """Интерфейс аята."""

    async def id(self) -> int:
        """Идентификатор аята."""

    async def text(self) -> str:
        """Строковое представление."""

    async def tg_file_id(self) -> str:
        """Идентификатор файла в телеграм."""

    async def file_link(self) -> str:
        """Ссылка на файл."""


@final
class QAyat(Ayat):
    """Аят."""

    def __init__(self, ayat_id: AsyncIntable, database: Database):
        """Конструктор класса.

        :param ayat_id: AsyncIntable
        :param database: Database
        """
        self._ayat_id = ayat_id
        self._database = database

    @classmethod
    async def by_sura_ayat_num(cls, sura_ayat_num: Stringable, database: Database) -> Ayat:
        """Конструктор для поиска по номеру суры, аята.

        :param sura_ayat_num: Stringable
        :param database: Database
        :return: Ayat
        """
        return QAyat(
            AyatIdBySuraAyatNum(
                Sura(database),
                ValidatedSearchQuery(
                    SearchQuery(sura_ayat_num),
                ),
                database,
            ),
            database,
        )

    async def id(self) -> int:
        """Идентификатор аята.

        :return: int
        """
        return await self._ayat_id.to_int()

    async def text(self) -> str:
        """Текст аята.

        :return: str
        :raises AyatNotFoundError: если аят не найден
        """
        query = """
            SELECT
                a.ayat_id as id,
                a.sura_id as sura_num,
                s.link as sura_link,
                a.ayat_number as ayat_num,
                a.arab_text,
                a.content,
                a.transliteration
            FROM ayats a
            INNER JOIN suras s on a.sura_id = s.sura_id
            WHERE a.ayat_id = :ayat_id
        """
        ayat_id = await self._ayat_id.to_int()
        row = await self._database.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError('Аят с id={0} не найден'.format(ayat_id))
        link = 'https://umma.ru{sura_link}'.format(sura_link=row['sura_link'])
        template = '<a href="{link}">{sura}:{ayat})</a>\n{arab_text}\n\n{content}\n\n<i>{transliteration}</i>'
        return template.format(
            link=link,
            sura=row['sura_num'],
            ayat=row['ayat_num'],
            arab_text=row['arab_text'],
            content=row['content'],
            transliteration=row['transliteration'],
        )

    async def tg_file_id(self) -> str:
        """Идентификатор файла в телеграм.

        :return: str
        :raises AyatNotFoundError: если аят не найден
        """
        query = """
            SELECT
                cf.telegram_file_id
            FROM ayats a
            INNER JOIN files cf on a.audio_id = cf.file_id
            WHERE a.ayat_id = :ayat_id
        """
        ayat_id = await self._ayat_id.to_int()
        row = await self._database.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError('Аят с id={0} не найден'.format(ayat_id))
        return row['telegram_file_id']

    async def file_link(self) -> str:
        """Ссылка на файл.

        :return: str
        :raises AyatNotFoundError: если аят не найден
        """
        query = """
            SELECT
                cf.link
            FROM ayats a
            INNER JOIN files cf on a.audio_id = cf.file_id
            WHERE a.ayat_id = :ayat_id
        """
        ayat_id = await self._ayat_id.to_int()
        row = await self._database.fetch_one(query, {'ayat_id': ayat_id})
        if not row:
            raise AyatNotFoundError('Аят с id={0} не найден'.format(ayat_id))
        return row['link']