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
from typing import Union

from repository.ayats.ayat import AyatRepositoryInterface
from repository.ayats.schemas import Ayat
from services.ayats.search_by_sura_ayat_num import AyatSearchInterface


class AyatById(AyatSearchInterface):
    """Поиск аята по идентификатору аята."""

    def __init__(self, ayat_repo: AyatRepositoryInterface):
        """Конструктор класса.

        :param ayat_repo: AyatRepositoryInterface
        """
        self._ayat_repo = ayat_repo

    async def search(self, search_query: Union[str, int]) -> Ayat:
        """Поиск аята.

        :param search_query: str
        :return: list[httpx.Request]
        :raises TypeError: if search has str type
        """
        if isinstance(search_query, str):
            raise TypeError
        return await self._ayat_repo.get(search_query)
