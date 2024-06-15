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

import pytest
from fakeredis import aioredis

from app_types.intable import FkIntable
from app_types.logger import FkLogSink
from app_types.update import FkUpdate
from integrations.tg.tg_answers import FkAnswer
from integrations.tg.update import TgUpdate
from services.reset_state_answer import ResetStateAnswer
from services.user_state import CachedUserState, RedisUserState, UserStep


@pytest.fixture()
def fake_redis():
    return aioredis.FakeRedis()


async def test_redis_query(fake_redis):
    await ResetStateAnswer(
        FkAnswer(),
        RedisUserState(fake_redis, FkIntable(123), FkLogSink()),
    ).build(TgUpdate({'from': {'id': 123}}))

    assert await fake_redis.get('123:step') == b'nothing'


async def test_origin_answer_not_modificated(fake_redis):
    got = await ResetStateAnswer(
        FkAnswer(),
        RedisUserState(fake_redis, FkIntable(123), FkLogSink()),
    ).build(TgUpdate({'from': {'id': 123}}))
    origin = (await FkAnswer().build(FkUpdate.empty_ctor()))[0].url

    assert got[0].url == origin


async def test_read_cached(fake_redis):
    user_state = CachedUserState(RedisUserState(fake_redis, FkIntable(1), FkLogSink()))
    await fake_redis.set('1:step', b'city_search')

    assert await user_state.step() == UserStep.city_search
    await fake_redis.set('1:step', b'new value')
    assert await user_state.step() == UserStep.city_search


async def test_write_cached(fake_redis):
    await fake_redis.set('1:step', b'city_search')
    user_state = CachedUserState(RedisUserState(fake_redis, FkIntable(1), FkLogSink()))
    await user_state.change_step(UserStep.ayat_search)

    assert await user_state.step() == UserStep.ayat_search
