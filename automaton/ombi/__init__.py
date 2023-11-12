import json

import requests
from django.conf import settings

from automaton.enumerations import AWAITING_RS, ABANDONED_RS, REQUESTED_RS
from automaton.models.request import Request
from automaton.util.log import api_logger


class OmbiBase:
    def __init__(self):
        self._api_key = settings.OMBI_API_KEY
        self._url = settings.OMBI_URL
        self._default_headers = {
            'content-type': 'application/json',
            'ApiKey': self._api_key,
        }

    def request(self, api_path, method='GET', json_=None, headers=None):
        params = self._create_request_params(json_, headers)
        response = requests.request(method, f'{self._url}{api_path}', **params)
        api_logger.info(f'Ombi response code: {response.status_code}')
        api_logger.debug(f'Ombi response json: {response.json()}')
        return response.json()

    def _create_request_params(self, json_, headers):
        params = {}
        if headers is None:
            params['headers'] = self._default_headers
        else:
            params['headers'] = headers
        if json_:
            params['json'] = json_
        return params

    @classmethod
    def handle_ombi_queue_response(cls, ombi_response, media_id, title, request):
        if 'isError' not in ombi_response or 'message' not in ombi_response:
            error = f'Ombi api interface is messed up, no isError flag key ' \
                    f'or message key is not present {ombi_response}'
            api_logger.exception(error)
            return error
        if ombi_response['isError'] is True:
            error = f'Error requesting, {ombi_response}'
            api_logger.exception(error)
            return error
        if request:
            request.complete_request(media_id, title)
        return f'Successfully requested {title}!'

    @staticmethod
    def convert_ombi_choice_response_to_text(response):
        choices = "\n".join(
            [f'[{key}]: {item["title"]}' for key, item in response.items()])
        return f'Reply with number of choice: \n {choices}'
