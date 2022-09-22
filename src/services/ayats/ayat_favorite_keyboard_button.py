import json

from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.schemas import Ayat
from services.answers.answer import KeyboardInterface


class AyatFavoriteKeyboardButton(KeyboardInterface):
    """Кнопка с добавлением аята в избранные."""

    def __init__(self, ayat: Ayat, keyboard: KeyboardInterface, favorite_ayat_repo: FavoriteAyatRepositoryInterface):
        self._ayat = ayat
        self._origin = keyboard
        self._favorite_ayat_repo = favorite_ayat_repo

    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        keyboard = json.loads(await self._origin.generate(update))
        is_favor = await self._favorite_ayat_repo.check_ayat_is_favorite_for_user(self._ayat.id, update.chat_id())
        keyboard['inline_keyboard'].append([{
            'text': 'Удалить из избранного' if is_favor else 'Добавить в избранное',
            'callback_data': ('removeFromFavor({0})' if is_favor else 'addToFavor({0})').format(self._ayat.id),
        }])
        return json.dumps(keyboard)