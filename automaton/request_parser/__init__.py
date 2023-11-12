from typing import Tuple, Optional, List

from automaton.enumerations import AUDIOBOOK_RT, MOVIE_RT, TV_RT, CHOICE_RT, UNKNOWN_RT, ADD_USER_COMMAND, REMOVE_USER_COMMAND, \
    ADD_USER, REMOVE_USER, NOTIFY_USERS_COMMAND, NOTIFY_USERS, ADMIN_REQUESTS
from automaton.util.log import api_logger


class RequestParser:

    @staticmethod
    def _check_numerical_num(input_number):
        possible_numbers = [str(num) for num in range(10)]
        number = [num for num in possible_numbers if num in input_number]
        if len(number) == 1:
            return int(number[0])
        return None

    @staticmethod
    def _check_text_number(input_number):
        text_numbers = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
                        'nine': 9, 'ten': 10}
        number = [num for text, num in text_numbers.items() if text in input_number]
        if len(number) == 1:
            return number[0]
        return None

    @classmethod
    def _verify_number(cls, input_number):
        numerical_number = cls._check_numerical_num(input_number)
        if numerical_number is not None:
            return numerical_number
        text_number = cls._check_text_number(input_number)
        if text_number:
            return text_number
        return None

    @staticmethod
    def _is_movie_request(data):
        return 'movie' in data

    @staticmethod
    def _is_tv_request(data):
        return 'tv' in data
    
    @staticmethod
    def _is_audiobook_request(data):
        return 'audiobook' in data

    @classmethod
    def _parse_text_body(cls, data):
        data_l = data.lower()
        if cls._is_movie_request(data_l):
            return MOVIE_RT, cls._truncate_movie_text(data_l)
        elif cls._is_tv_request(data_l):
            return TV_RT, cls._truncate_tv_text(data_l)
        elif cls._is_audiobook_request(data_l):
            return AUDIOBOOK_RT, cls._truncate_audiobook_text(data_l)

        num = cls._verify_number(data_l)
        if num is not None:
            return CHOICE_RT, num

        return UNKNOWN_RT, data

    @staticmethod
    def _truncate_tv_text(text):
        request = text.split('tv', 1)
        if len(request) > 1 and isinstance(request, list):
            return request[1]
        return None

    @staticmethod
    def _truncate_movie_text(text):
        request = text.split('movie', 1)
        if len(request) > 1 and isinstance(request, list):
            return request[1]
        return None
    
    @staticmethod
    def _truncate_audiobook_text(text):
        request = text.split('audiobook', 1)
        if len(request) > 1 and isinstance(request, list):
            return request[1]
        return None

    def parse_request(self, text):
        request_type, body = self._parse_text_body(text)
        return request_type, body

    @staticmethod
    def _check_request(data, command, request_type):
        if command in data:
            return request_type, data.split(command)[1].strip()

    @classmethod
    def parse_admin_request(cls, data: str) -> Tuple[Optional[str], Optional[str]]:
        data_l = data.lower()
        parsed: List = [cls._check_request(data_l, cmd, cmd_type) for cmd_type, cmd in ADMIN_REQUESTS]
        filtered: Optional[List[Tuple[str, str]]] = [(p[0], p[1]) for p in parsed if p is not None]
        request_type, body = (None, None) if not filtered else filtered[0]
        return request_type, body
