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
from pathlib import Path
from typing import final, override

import attrs
from pyeo import elegant

from settings.settings import BASE_DIR, Settings


@final
@elegant
@attrs.define(frozen=True)
class EnvFileSettings(Settings):
    """Настройки из .env файла."""

    _path: Path

    @classmethod
    def from_filename(cls, file_path: str) -> Settings:
        """Конструктор для имени файла.

        :param file_path: str
        :return: Settings
        """
        return cls(Path(BASE_DIR / file_path))

    @override
    def __getattr__(self, attr_name: str) -> str:
        """Получить атрибут.

        :param attr_name: str
        :return: str
        """
        if attr_name == 'BASE_DIR':
            return str(BASE_DIR)
        return self._search_in_file(attr_name)

    def _search_in_file(self, attr_name: str) -> str:
        for line in self._path.read_text().strip().split('\n'):
            if '=' not in line:
                continue
            var_name, var_value = line.split('=')
            if var_name == attr_name:
                return var_value
        msg = '{0} not defined'.format(attr_name)
        raise ValueError(msg)
