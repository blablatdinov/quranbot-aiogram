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

# TODO #899 Перенести классы в отдельные файлы 11

from typing import Protocol, final

from pyeo import elegant


@elegant
class LogSink(Protocol):
    """Интерфейс объектов для логгирования."""

    def info(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, WPS110
        """Информационный уровень."""

    def debug(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для отладки."""

    def error(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для ошибок."""

    def exception(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для исключений."""


@final
@elegant
class FkLogSink(LogSink):
    """Фейковый логгер."""

    stack: list[str]

    def __init__(self) -> None:
        """Ctor."""
        self.stack = []

    def info(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, WPS110
        """Информационный уровень."""
        self.stack.append('INFO {0}'.format(args[0]))

    def debug(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для отладки."""
        self.stack.append('DEBUG {0}'.format(args[0]))

    def error(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для ошибок."""
        self.stack.append('ERROR {0}'.format(args[0]))

    def exception(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Уровень для исключений."""
        self.stack.append('ERROR {0}'.format(args[0]))
