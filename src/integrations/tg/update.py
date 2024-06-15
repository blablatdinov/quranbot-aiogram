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

# TODO #899 Перенести классы в отдельные файлы 18

from typing import ClassVar, final, override

import attrs
import ujson
from pyeo import elegant

from app_types.stringable import SupportsStr
from app_types.update import Update


@final
@attrs.define(frozen=True)
@elegant
class TgUpdate(Update):
    """Объект обновления от телеграмма."""

    _update_dict: dict

    @classmethod
    def str_ctor(cls, raw_update: SupportsStr) -> Update:
        """Конструктор для строки."""
        return cls(ujson.loads(str(raw_update)))

    @override
    def __str__(self) -> str:
        """Приведение к строке."""
        return ujson.dumps(self._update_dict)

    @override
    def asdict(self) -> dict:
        """Словарь.

        # TODO #360:30min возможно стоит возвращать валидированный dict: return self.parsed().dict().
        #  Подумать насколько тут необходима валидация

        """
        return self._update_dict


@final
@attrs.define()
@elegant
class CachedTgUpdate(Update):
    """Декоратор, для избежания повторной десериализации.

    _origin: Update - оригинальный объект обновления
    """

    _origin: Update
    _cache: ClassVar = {
        'str': None,
        'parsed': None,
        'asdict': None,
    }

    @override
    def __str__(self) -> str:
        """Приведение к строке."""
        str_cache_key = 'str'
        if not self._cache[str_cache_key]:
            self._cache[str_cache_key] = str(self._origin)
        return self._cache[str_cache_key]

    @override
    def asdict(self) -> dict:
        """Словарь."""
        dict_cache_key = 'asdict'
        if not self._cache[dict_cache_key]:
            self._cache[dict_cache_key] = self._origin.asdict()
        return self._cache[dict_cache_key]
