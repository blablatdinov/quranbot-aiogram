from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters

from constants import PODCAST_BUTTON
from db import DBConnection
from repository.podcast import PodcastRepository
from services.podcast import PodcastAnswer, PodcastService


async def podcasts_handler(message: types.Message, state: FSMContext):
    """Получить случайный подкаст.

    :param message: types.Message
    :param state: FSMContext
    """
    async with DBConnection() as connection:
        answer = PodcastAnswer(
            await PodcastService(
                PodcastRepository(connection),
            ).get_random(),
        ).transform()

    await state.finish()
    await answer.send(message.chat.id)


def register_podcasts_message_handlers(dp: Dispatcher):
    """Регистрация обработчиков.

    :param dp: Dispatcher
    """
    dp.register_message_handler(podcasts_handler, filters.Regexp(PODCAST_BUTTON), state='*')
