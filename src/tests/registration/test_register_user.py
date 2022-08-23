from services.answers.answer import Answer


async def test(register_service, ayat_repository_mock, user_repository_mock):
    got = await register_service(user_repository_mock, 231, '/start')

    assert got == [
        Answer(chat_id=231, message='start message_handlers'),
        Answer(chat_id=231, message=str(ayat_repository_mock.storage[0])),
    ]
    assert await user_repository_mock.get_by_chat_id(231)
    # TODO: check, that event about user action sended in queue


async def test_already_registered_user(
    register_service,
    ayat_repository_mock,
    user_repository_with_registered_active_user,
):
    got = await register_service(user_repository_with_registered_active_user, 444, '/start')

    assert got == Answer(chat_id=444, message='Вы уже зарегистрированы')
    # TODO: check, that event about user action sended in queue


async def test_inactive_user(register_service, user_repository_with_registered_inactive_user):
    got = await register_service(user_repository_with_registered_inactive_user, 444, '/start')

    assert got == Answer(chat_id=444, message='Рады видеть вас снова, вы продолжите с дня 15')
    # TODO: check, that event about user action sended in queue


async def test_with_referrer(
    register_service,
    user_repository_with_registered_inactive_user,
    ayat_repository_mock,
):
    got = await register_service(user_repository_with_registered_inactive_user, 222, '/start 1')

    created_user = await user_repository_with_registered_inactive_user.get_by_chat_id(222)

    assert len(user_repository_with_registered_inactive_user.storage) == 2
    assert created_user.referrer == 1
    assert got == [
        Answer(chat_id=222, message='start message_handlers'),
        Answer(chat_id=222, message=str(ayat_repository_mock.storage[0])),
        Answer(chat_id=444, message='По вашей реферральной ссылке произошла регистрация'),
    ]
    # TODO: check, that event about user action sended in queue
