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
import httpx
from typing import final
from aioredis import Redis

from app_types.stringable import Stringable
from exceptions.content_exceptions import CityNotSupportedError
from integrations.tg.chat_id import TgChatId
from integrations.tg.coordinates import TgMessageCoordinates
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer
from repository.users.user import UserRepositoryInterface
from services.city.search import CitySearchInterface, SearchCityQuery
from services.user_state import LoggedUserState, UserState, UserStep


class CityNotSupportedAnswer(TgAnswerInterface):
    """Ответ о неподдерживаемом городе."""

    def __init__(self, answer: TgAnswerInterface, error_answer: TgAnswerInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param error_answer: TgAnswerInterface
        """
        self._origin = answer
        self._error_answer = error_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except CityNotSupportedError:
            return await TgTextAnswer(
                self._error_answer,
                'Этот город не поддерживается',
            ).build(update)


class ChangeCityAnswer(TgAnswerInterface):
    """Ответ со сменой города."""

    def __init__(
        self,
        answer: TgAnswerInterface,
        search_city: CitySearchInterface,
        redis: Redis,
        user_repo: UserRepositoryInterface,
    ):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param search_city: CitySearchInterface
        :param redis: Redis
        :param user_repo: UserRepositoryInterface
        """
        self._city = search_city
        self._origin = answer
        self._redis = redis
        self._user_repo = user_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        :raises CityNotSupportedError: если город не поддерживается
        """
        try:
            query = SearchCityQuery.from_string_cs(str(MessageText(update)))
        except AttributeError:
            coordinates = TgMessageCoordinates(update)
            query = SearchCityQuery.from_coordinates_cs(
                coordinates.latitude(),
                coordinates.longitude(),
            )
        cities = await self._city.search(query)
        if not cities:
            raise CityNotSupportedError
        await self._user_repo.update_city(
            int(TgChatId(update)),
            cities[0].id,
        )
        await LoggedUserState(
            UserState(self._redis, int(TgChatId(update))),
        ).change_step(UserStep.nothing)
        return await TgTextAnswer(
            self._origin,
            'Вам будет приходить время намаза для города {0}'.format(cities[0].name),
        ).build(update)
