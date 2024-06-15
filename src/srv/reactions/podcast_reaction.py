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

# TODO #899 Перенести классы в отдельные файлы 37

from typing import Literal, Protocol, final, override

import attrs
from pyeo import elegant

from app_types.stringable import SupportsStr
from services.regular_expression import IntableRegularExpression


@elegant
class PodcastReactionsT(Protocol):
    """Реакция на подкаст."""

    def podcast_id(self) -> int:
        """Идентификатор подкаста."""

    def status(self) -> Literal['like', 'dislike']:
        """Реакция."""


@final
@attrs.define(frozen=True)
@elegant
class PodcastReaction(PodcastReactionsT):
    """Реакция на подкаст.

    >>> prayer_reaction = PodcastReaction('like(17)')
    >>> prayer_reaction.podcast_id()
    17
    >>> prayer_reaction.status()
    'like'
    """

    _callback_query: SupportsStr

    @override
    def podcast_id(self) -> int:
        """Идентификатор подкаста."""
        return int(IntableRegularExpression(str(self._callback_query)))

    @override
    def status(self) -> Literal['like', 'dislike']:
        """Реакция."""
        if 'dislike' in str(self._callback_query):
            return 'dislike'
        return 'like'
