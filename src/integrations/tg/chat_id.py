import re

from app_types.intable import Intable
from app_types.stringable import Stringable, UnwrappedString
from exceptions.base_exception import InternalBotError


class TgChatId(Intable):
    """Идентификатор чата."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InternalBotError: В случае отсутсвия идентификатора чата в json
        """
        unwrapped_string = str(UnwrappedString(self._update))
        chat_json_object = re.search('chat"(:|: )({.+?})', unwrapped_string)
        if chat_json_object:
            return self._parse_id(chat_json_object)
        chat_json_object = re.search('from"(:|: )({.+?})', unwrapped_string)
        if chat_json_object:
            return self._parse_id(chat_json_object)
        raise InternalBotError

    def _parse_id(self, chat_json_object: re.Match) -> int:
        chat_id_regex_result = re.search(r'id"(:|: )(\d+)', chat_json_object.group(2))
        if not chat_id_regex_result:
            raise InternalBotError
        return int(chat_id_regex_result.group(2))
