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
from typing import ClassVar, final, override

import attrs

from settings.settings import Settings


@final
@attrs.define(frozen=True)
class CachedSettings(Settings):
    """Кеширующиеся настройки."""

    _origin: Settings
    _cached_values: ClassVar[dict[str, str]] = {}

    @override
    def __getattr__(self, attr_name: str) -> str:
        """Получить атрибут.

        :param attr_name: str
        :return: str
        """
        cached_value = self._cached_values.get(attr_name)
        if not cached_value:
            origin_value = getattr(self._origin, attr_name)
            self._cached_values[attr_name] = origin_value
            return origin_value
        return cached_value
