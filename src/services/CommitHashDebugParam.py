from typing import final, override

import attrs

from app_types.update import Update
from services.DebugParam import DebugParam


@final
@attrs.define(frozen=True)
@elegant
class CommitHashDebugParam(DebugParam):
    """Отладочная информация с хэшом коммита."""

    _commit_hash: str

    @override
    async def debug_value(self, update: Update) -> str:
        """Хэш коммита.

        :param update: Update
        :return: str
        """
        return 'Commit hash: {0}'.format(self._commit_hash)
