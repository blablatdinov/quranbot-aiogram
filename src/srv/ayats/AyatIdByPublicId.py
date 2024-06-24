from app_types.intable import AsyncInt
from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_identifier import AyatId


import attrs
from databases import Database
from pyeo import elegant


import uuid
from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class AyatIdByPublicId(AsyncInt):
    """Поиск аятов по номеру суры, аята."""

    _public_id: uuid.UUID
    _pgsql: Database

    @override
    async def to_int(self) -> AyatId:
        """Числовое представление.

        :return: int
        :raises AyatNotFoundError: если аят не найден
        """
        query = '\n'.join([
            'SELECT ayat_id FROM ayats',
            'WHERE public_id = :public_id',
        ])
        row = await self._pgsql.fetch_one(query, {
            'public_id': str(self._public_id),
        })
        if not row:
            raise AyatNotFoundError
        return row['ayat_id']