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
from databases import Database
from eljson.json import Json
from pyeo import elegant

from srv.ayats.pg_ayat import PgAyat
from srv.events.recieved_event import ReceivedEvent

JsonPathQuery: TypeAlias = str
AyatChangedEvent: TypeAlias = ReceivedEvent


@final
@attrs.define(frozen=True)
@elegant
class RbmqAyatChangedEvent(AyatChangedEvent):
    """Событие изменения аята из rabbitmq."""

    _pgsql: Database

    @override
    async def process(self, json_doc: Json) -> None:
        """Обработка события."""
        pg_ayat = PgAyat.ayat_changed_event_ctor(json_doc, self._pgsql)
        await pg_ayat.change(json_doc)
