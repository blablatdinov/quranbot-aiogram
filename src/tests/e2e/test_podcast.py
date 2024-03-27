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
import pytest


@pytest.fixture()
def _user(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/start')
    wait_until(tg_client, 3)


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user')
def test(tg_client, bot_name, wait_until):
    """Тест просмотра подкаста.

    [
        ('👍 0', b'like(be07e25e-6f12-4a87-9713-b86d6b814e24)'),
        ('👎 0', b'dislike(be07e25e-6f12-4a87-9713-b86d6b814e24)')
    ]

    """
    tg_client.send_message(bot_name, '🎧 Подкасты')
    messages = wait_until(tg_client, 6)
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


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user')
def test_random(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '🎧 Подкасты')
    wait_until(tg_client, 6)
    tg_client.send_message(bot_name, '🎧 Подкасты')
    messages = wait_until(tg_client, 9)

    assert messages[0].message != messages[2].message


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user')
@pytest.mark.parametrize(('target_button', 'expected'), [
    ('👍', ['👍 1', '👎 0']),
    ('👎', ['👍 0', '👎 1']),
])
@pytest.mark.tg_button()
def test_reaction(tg_client, bot_name, wait_until, target_button, expected):
    tg_client.send_message(bot_name, '🎧 Подкасты')
    messages = wait_until(tg_client, 6)
    next(
        button
        for button_row in messages[-1].get_buttons()
        for button in button_row
        if target_button in button.text
    ).click()
    messages = wait_until(tg_client, 6)

    assert expected == [
        button.text
        for button_row in messages[-1].get_buttons()
        for button in button_row
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user')
@pytest.mark.parametrize(('first_reaction', 'second_reaction', 'expected'), [
    ('👎', '👍', ['👍 1', '👎 0']),
    ('👍', '👎', ['👍 0', '👎 1']),
])
@pytest.mark.tg_button()
def test_reverse_reaction(tg_client, bot_name, wait_until, first_reaction, second_reaction, expected):
    tg_client.send_message(bot_name, '🎧 Подкасты')
    messages = wait_until(tg_client, 6)
    next(
        button
        for button_row in messages[-1].get_buttons()
        for button in button_row
        if first_reaction in button.text
    ).click()
    messages = wait_until(tg_client, 6)
    next(
        button
        for button_row in messages[-1].get_buttons()
        for button in button_row
        if second_reaction in button.text
    ).click()
    messages = wait_until(tg_client, 6)

    assert expected == [
        button.text
        for button_row in messages[-1].get_buttons()
        for button in button_row
    ]


@pytest.mark.usefixtures('_bot_process', '_clear_db', '_user')
@pytest.mark.parametrize('reaction', ['👎', '👍'])
@pytest.mark.tg_button()
def test_undo_reaction(tg_client, bot_name, wait_until, reaction, db_query_vals):
    tg_client.send_message(bot_name, '/podcast1')
    messages = wait_until(tg_client, 5)
    next(
        button
        for button_row in messages[-1].get_buttons()
        for button in button_row
        if reaction in button.text
    ).click()
    messages = wait_until(tg_client, 5)
    next(
        button
        for button_row in messages[-1].get_buttons()
        for button in button_row
        if reaction in button.text
    ).click()
    messages = wait_until(tg_client, 5)

    assert [
        button.text
        for button_row in messages[0].get_buttons()
        for button in button_row
    ] == ['👍 0', '👎 0']
    assert db_query_vals(
        'SELECT reaction FROM podcast_reactions WHERE podcast_id = 1',
    ) == [('showed',)]


@pytest.mark.usefixtures('_bot_process', '_clear_db')
def test_concrete(tg_client, bot_name, wait_until):
    tg_client.send_message(bot_name, '/podcast17')
    messages = wait_until(tg_client, 2)

    assert messages[0].message == 'https://umma.ru/audio/2015/shamil/2015_07_17/2015_07_17_5.mp3'
