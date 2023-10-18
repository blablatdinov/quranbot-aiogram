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

from typing import TypeAlias, final, override

import attrs
from pyeo import elegant

from services.regular_expression import IntableRegularExpression
from srv.ayats.ayat_identifier import AyatId
from srv.ayats.favorite_ayat_status import FavoriteAyatStatus

# Строка имеющая формат addToFavor(<id аята>) или removeFromFavor(<id аята>)
type _ChangeAyatStatusCommand = str


@final
@attrs.define(frozen=True)
@elegant
class AyatFavoriteStatus(FavoriteAyatStatus):
    """Пользовательский ввод статуса аята в избранном.

    >>> ayat_favor_status = AyatFavoriteStatus('addToFavor(14)')
    >>> ayat_favor_status.ayat_id()
    14
    >>> ayat_favor_status.change_to()
    True

    >>> ayat_favor_status = AyatFavoriteStatus('removeFromFavor(14)')
    >>> ayat_favor_status.ayat_id()
    14
    >>> ayat_favor_status.change_to()
    False
    """

    _source: _ChangeAyatStatusCommand

    @override
    def ayat_id(self) -> AyatId:
        """Идентификатор аята.

        :return: int
        """
        return int(IntableRegularExpression(self._source))

    @override
    def change_to(self) -> bool:
        """Целевое значение.

        :return: bool
        """
        return 'addToFavor' in self._source
