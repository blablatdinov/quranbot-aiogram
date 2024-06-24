from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from srv.users.valid_chat_id import ValidChatId


import attrs
from pyeo import elegant


from typing import SupportsInt, final, override


@final
@attrs.define(frozen=True)
@elegant
class FkValidChatId(ValidChatId):
    """Фейковый объект с валидным идентификатором чата.

    Использовать для случаев создания пользователя если мы уверены в наличии идентификатора в хранилище.
    Например: srv.users.active_users.ActiveUsers
    """

    _origin: AsyncInt

    @classmethod
    def int_ctor(cls, int_value: SupportsInt) -> ValidChatId:
        """Числовой конструктор.

        :param int_value: SupportsInt
        :return: FkValidChatId
        """
        return cls(FkAsyncInt(int_value))

    @override
    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        return await self._origin.to_int()