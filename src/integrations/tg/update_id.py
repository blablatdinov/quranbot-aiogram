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
import re

from typing import final
from app_types.intable import Intable
from app_types.stringable import Stringable
from exceptions.base_exception import InternalBotError


class UpdateId(Intable):
    """Идентификатор обновления."""

    def __init__(self, raw_json: Stringable):
        """Конструктор класса.

        :param raw_json: Stringable
        """
        self._raw = raw_json

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InternalBotError: если не удалось получить идентификатор обновления
        """
        regex_result = re.search(r'update_id"(:|: )(\d+)', str(self._raw))
        if not regex_result:
            raise InternalBotError
        return int(regex_result.group(2))
