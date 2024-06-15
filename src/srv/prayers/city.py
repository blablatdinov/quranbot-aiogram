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

# TODO #899 Перенести классы в отдельные файлы 29

import uuid
from typing import Protocol, final, override

import attrs
from databases import Database
from pyeo import elegant

from app_types.stringable import AsyncSupportsStr, FkAsyncStr
from exceptions.content_exceptions import CityNotSupportedError
from integrations.nominatim import NominatimCityName
from integrations.tg.coordinates import Coordinates


class City(Protocol):
    """Интерфейс города."""

    async def city_id(self) -> uuid.UUID:
        """Идентификатор города."""

    async def name(self) -> str:
        """Имя города."""


@final
@attrs.define(frozen=True)
@elegant
class FkCity(City):
    """Стаб города."""

    _city_id: uuid.UUID
    _name: str

    @override
    async def city_id(self) -> uuid.UUID:
        """Идентификатор города."""
        return self._city_id

    @override
    async def name(self) -> str:
        """Имя города."""
        return self._name


@final
@attrs.define(frozen=True)
@elegant
class CityIdByName(AsyncSupportsStr):
    """Идентификатор города по имени."""

    _name: AsyncSupportsStr
    _pgsql: Database

    @override
    async def to_str(self) -> str:
        """Строковое представление."""
        query = 'SELECT city_id FROM cities WHERE name = :name'
        city_id = await self._pgsql.fetch_val(
            query,
            {'name': await self._name.to_str()},
        )
        if not city_id:
            raise CityNotSupportedError
        return city_id


@final
@attrs.define(frozen=True)
@elegant
class PgCity(City):
    """Город в БД postgres."""

    _city_id: AsyncSupportsStr
    _pgsql: Database

    @classmethod
    def name_ctor(cls, city_name: str, pgsql: Database) -> City:
        """Конструктор для имени города."""
        return cls(CityIdByName(FkAsyncStr(city_name), pgsql), pgsql)

    @classmethod
    def location_ctor(cls, location: Coordinates, pgsql: Database) -> City:
        """Конструктор для координат города."""
        return cls(CityIdByName(NominatimCityName(location), pgsql), pgsql)

    @override
    async def city_id(self) -> uuid.UUID:
        """Идентификатор города."""
        return uuid.UUID(await self._city_id.to_str())

    @override
    async def name(self) -> str:
        """Имя города."""
        query = 'SELECT name FROM cities WHERE city_id = :city_id'
        return await self._pgsql.fetch_val(
            query,
            {'city_id': await self._city_id.to_str()},
        )
