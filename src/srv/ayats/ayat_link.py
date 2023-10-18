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

from app_types.stringable import SupportsStr

type _AyatNum = str


@final
@elegant
@attrs.define(frozen=True)
class AyatLink(SupportsStr):
    """Ссылка на аят.

    >>> str(AyatLink('/sura-2-al-bakara-korova/', 2, '1-5'))
    'https://umma.ru/sura-2-al-bakara-korova/#2-1'
    >>> str(AyatLink('/sura-2-al-bakara-korova/', 2, '6, 7'))
    'https://umma.ru/sura-2-al-bakara-korova/#2-6'
    >>> str(AyatLink('/sura-2-al-bakara-korova/', 2, '15-18'))
    'https://umma.ru/sura-2-al-bakara-korova/#2-15'
    """

    _sura_link: str
    _sura_num: int
    _ayat_num: _AyatNum

    @override
    def __str__(self) -> str:
        """Формирование ссылки с якорем на аят.

        Пример: https://umma.ru/sura-56-al-vaky-a-sobytie/#56-18

        :return: str
        """
        return 'https://umma.ru{0}#{1}-{2}'.format(
            self._sura_link,
            self._sura_num,
            self._ayat_first_digit(self._ayat_num),
        )

    def _ayat_first_digit(self, ayat_num: _AyatNum) -> str:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_ayat_first_digit"
        num = ''
        for char in ayat_num:
            if not char.isdigit():
                break
            num += char
        return num
