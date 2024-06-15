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

# flake8: noqa: WPS202

from typing import final, override

import attrs

from exceptions.base_exception import BaseAppError


@final
class NotFoundReferrerIdError(BaseAppError):
    """Исключение возбуждается в случае если невозможно зарегистрировать пользователя с рефералом."""

    user_message = 'Невозможно зарегистрировать пользователя с рефералом'


@final
class UserNotFoundError(BaseAppError):
    """Исключение возбуждается в случае если пользователь не найден."""

    user_message = 'Пользователь не найден'


@final
class UserHasNotGeneratedPrayersError(BaseAppError):
    """У пользователя нет сгенерированных времен намаза на текущий день."""

    admin_message = ''


@final
class NotProcessableUpdateError(BaseAppError):
    """Исключение, вызываемое если бот не знает как обработать запрос."""

    admin_message = ''


@final
@attrs.define(frozen=True)
class TelegramIntegrationsError(BaseAppError):
    """Исключение, возбуждаемое при некорректном ответе от API телеграмма."""

    _message: str
    admin_message = 'Ошибка интеграции telegram'

    @override
    def __str__(self) -> str:
        """Строковое представление."""
        return self._message


@final
@attrs.define(frozen=True)
class UnreacheableError(BaseAppError):
    """Ошибка непредвиденного состояния."""


@final
@attrs.define(frozen=True)
class PrayerAtUserAlreadyExistsError(BaseAppError):
    """У пользователя уже сгенерированы времена намазов."""


@final
@attrs.define(frozen=True)
class PrayerAtUserNotCreatedError(BaseAppError):
    """Времена намазов не созданы."""
