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

from typing import final, override

from pyeo import elegant

from app_types.update import Update


@final
@elegant
class CachedTgUpdate(Update):
    """Декоратор, для избежания повторной десериализации."""

    def __init__(self, origin: Update) -> None:
        """Ctor.

        :param _origin: Update - оригинальный объект обновления
        """
        self._origin = origin
        self._cache = {
            'str': '',
            'parsed': None,
            'asdict': {},
        }

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        str_cache_key = 'str'
        if not self._cache[str_cache_key]:
            self._cache[str_cache_key] = str(self._origin)
        return self._cache[str_cache_key]

    @override
    def asdict(self) -> dict:
        """Словарь.

        :return: dict
        """
        dict_cache_key = 'asdict'
        if not self._cache[dict_cache_key]:
            self._cache[dict_cache_key] = self._origin.asdict()
        return self._cache[dict_cache_key]
