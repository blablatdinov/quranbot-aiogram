import httpx

from db.connection import database
from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from services.ayats.ayat_answer import AyatAnswer
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.keyboards import AyatAnswerKeyboard


class AyatBySuraAyatNumAnswer(TgAnswerInterface):
    """Ответ на поиск аята по номеру суры, аята."""

    def __init__(
        self,
        debug_mode: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        ayat_search: AyatSearchInterface,
    ):
        self._debug_mode = debug_mode
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._ayat_search = ayat_search

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        result_ayat = await self._ayat_search.search(update.message().text())
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(result_ayat, FavoriteAyatsRepository(database)),
        ).build(update)