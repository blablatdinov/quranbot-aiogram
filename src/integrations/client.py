import abc
from typing import TypeVar

import aiohttp
from pydantic import BaseModel

ParseModel = TypeVar('ParseModel', bound=BaseModel)


class IntegrationClientInterface(object):
    """Интерфейс HTTP клиента."""

    @abc.abstractmethod
    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        :raises NotImplementedError: if not implement
        """
        raise NotImplementedError


class IntegrationClient(IntegrationClientInterface):
    """Aiohttp клиент."""

    async def act(self, url: str, model_for_parse: type[ParseModel]) -> ParseModel:
        """Выполнить запрос.

        :param url: str
        :param model_for_parse: type(BaseModel)
        :returns: type(BaseModel)
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()

        return model_for_parse.parse_raw(text)
