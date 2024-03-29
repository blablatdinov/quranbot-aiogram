"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import os
import shutil
from pathlib import Path

import pytest

from settings.cached_settings import CachedSettings
from settings.env_file_settings import EnvFileSettings
from settings.os_env_settings import OsEnvSettings
from settings.os_or_file_settings import OsOrFileSettings
from settings.settings import FkSettings


@pytest.fixture()
def env_file(tmp_path):
    env_file_path = Path(tmp_path / '.env')
    env_file_path.write_text('FOO=bar\n\nFIZ=foo')
    return env_file_path


def test(env_file):
    assert EnvFileSettings(env_file).FOO == 'bar'
    assert EnvFileSettings(env_file).FIZ == 'foo'


def test_os_env():
    os.environ['FOO'] = 'bar'

    assert OsEnvSettings().FOO == 'bar'


def test_cached(env_file):
    cached_settings = CachedSettings(EnvFileSettings(env_file))
    value_from_file = cached_settings.FOO
    shutil.rmtree(env_file.parent)
    assert cached_settings.FOO == 'bar' == value_from_file


def test_not_found(env_file):
    with pytest.raises(ValueError, match='unknown not defined'):
        assert EnvFileSettings(env_file).unknown == 'bar'


def test_or_settings():
    settings = OsOrFileSettings(
        FkSettings({'FOO': 'foo_value'}),
        FkSettings({'BAR': 'bar_value'}),
    )

    assert settings.FOO == 'foo_value'
    assert settings.BAR == 'bar_value'
