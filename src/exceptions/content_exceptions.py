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
# flake8: noqa: WPS202
from typing import final

from exceptions.base_exception import BaseAppError


@final
class SuraNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутствии нужной суры."""

    user_message = 'Сура не найдена'


@final
class AyatNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутствии нужного аята."""

    user_message = 'Аят не найден'


@final
class BotFileNotFoundError(BaseAppError):
    """Файл не найден."""


@final
class CityNotSupportedError(BaseAppError):
    """Исключение, вызываемое если при поиске города, он не нашелся в БД."""

    user_message = 'Такой город не обслуживается'


@final
class UserHasNotCityIdError(BaseAppError):
    """Исключение, вызываемое если пользователь без установленного города запросил времена намазов."""

    user_message = 'Вы не указали город, отправьте местоположение или воспользуйтесь поиском'


@final
class AyatHaveNotNeighborsError(BaseAppError):
    """Исключение, вызываемое при попытке сгенерировать клавиатуру для аята без соседей."""

    admin_message = 'У аята нет соседей'


@final
class UserHasNotFavoriteAyatsError(BaseAppError):
    """Исключение, вызываемое при попытке получить избранные аяты, пользователем, у которого их нет."""

    user_message = 'Вы еще не добавляли аятов в избранное'


@final
class TelegramFileIdNotFilledError(BaseAppError):
    """Идентификатор файла не заполнен."""
