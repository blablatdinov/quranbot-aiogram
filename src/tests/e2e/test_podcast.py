"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
import pytest


@pytest.fixture()
def user(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    wait_until(tg_client, 3)


@pytest.mark.usefixtures('bot_process', 'clear_db')
def test(tg_client, bot_name, wait_until):
    """Тест просмотра подкаста.

    [
        ('👍 0', b'like(be07e25e-6f12-4a87-9713-b86d6b814e24)'),
        ('👎 0', b'dislike(be07e25e-6f12-4a87-9713-b86d6b814e24)')
    ]

    """
    tg_client.send_message(bot_name, '🎧 Подкасты')
    messages = wait_until(tg_client, 2)
    buttons = [
        (button.text, button.data)
        for button_row in messages[0].get_buttons()
        for button in button_row
    ]

    assert messages[0].message.startswith('http')
    assert messages[0].message.endswith('.mp3')
    assert [
        button.text
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == ['👍 0', '👎 0']
    assert buttons[0][1].decode('utf-8').startswith('like(')
    assert buttons[1][1].decode('utf-8').startswith('dislike(')


@pytest.mark.usefixtures('bot_process', 'clear_db')
def test_random(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '🎧 Подкасты')
    wait_until(tg_client, 2)
    tg_client.send_message(bot_name, '🎧 Подкасты')
    messages = wait_until(tg_client, 4)

    assert messages[0].message != messages[2].message


@pytest.mark.usefixtures('bot_process', 'clear_db', 'user')
def test_like(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '🎧 Подкасты')
    messages = wait_until(tg_client, 5)
    next(
        button
        for button_row in messages[0].get_buttons()
        for button in button_row
        if '👍' in button.text
    ).click()
    messages = wait_until(tg_client, 5)

    assert [
        button.text
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == ['👍 1', '👎 0']


# def test_like_for_disliked_podcast(): pass
# def test_undo_like(): pass
# def test_dislike(): pass
# def test_dislike_for_liked_podcast(): pass
# def test_undo_dislike(): pass
