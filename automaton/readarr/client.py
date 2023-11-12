import json
from urllib.parse import quote

import requests
from automaton.enumerations import AUDIOBOOK_RT, CHOICE_RT, INVALID_REQUEST_MESSAGE, NO_EXISTING_REQUEST
from automaton.models.request import Request
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from automaton.util.log import api_logger


class ReadarrClient:
    def __init__(self):
        self._api_key = settings.READARR_API_KEY
        self._url = settings.READARR_URL
        self._default_headers = {
            'content-type': 'application/json',
            'ApiKey': self._api_key,
        }

    def _choose_from_existing_request(self, requestor, choice):
        try:
            request = Request.get_existing_request_for_user(requestor)
        except ObjectDoesNotExist:
            return NO_EXISTING_REQUEST
        choices = json.loads(request.provided_options)
        choice_payload = choices[str(choice)]['payload']
        return self.request_audiobook(choice_payload, request=request)

    def resolve_request(self, request_type, requestor, body):
        if request_type == AUDIOBOOK_RT:
            return self.initiate_audiobook_search_request(requestor, body)
        elif request_type == CHOICE_RT:
            return self._choose_from_existing_request(requestor, body)
        else:
            return INVALID_REQUEST_MESSAGE

    def make_readarr_request(self, request_type, from_, body) -> str:
        return self.resolve_request(request_type, from_, body)
    
    def initiate_audiobook_search_request(self, requestor, body):
        response = self.search_for_audiobook_by_term(body)
        created = Request.create_request(requestor, body, json.dumps(response), AUDIOBOOK_RT)
        if len(response) == 0:
            return 'No audiobook results found, you insolent meat sack.'
        if len(response) == 1:
            return self._request_audiobook(response[0]['payload'], created)
        return self.convert_readarr_choice_response_to_text(response) if created else 'Failed to create request in ' \
                                                                                   'database for new audiobook request'
    def search_for_audiobook_by_term(self, term):
        quoted = quote(term.strip())
        api_path = f'/api/v1/search?term={quoted}'
        response = self.request(
            f'{api_path}',
            method='GET'
        )
        api_logger.info(f'Connect to readarr at {api_path}, search_for_audiobook response.')
        return self._get_response_from_readarr_data(response.json())

    def _get_response_from_readarr_data(self, data):
        # book key will be in response if it is book, not author
        books = [item for item in data if 'book' in item]
        return {
            idx: dict(
                title=item['book']['title'],
                payload=item['book'],
            )
            for idx, item in enumerate(books[:6])
        }
    
    def request_audiobook(self, choice_payload, request=None):
        id = choice_payload['editions'][0]['bookId']
        response = None

        # try adding, if it fails, it's already monitored
        # set request params to prevent unwanted monitoring
        choice_payload['author']['addOptions'] = {            
            "monitor": "all",
            "searchForMissingBooks": False
        }
        choice_payload['author']['metadataProfileId'] = 1
        choice_payload['author']['qualityProfileId'] = 2
        choice_payload['author']["rootFolderPath"] = "/media/Storage/audiobooks/"
        choice_payload['addOptions'] = { "searchForNewBook": False }

        # make request
        api_logger.info(f'Book {choice_payload["title"]} is not monitored, attempting to add to readarr')
        api_path = '/api/v1/book'
        response = self.request(
            api_path,
            json_=choice_payload,
            method='POST'
        )
        api_logger.info(
            f'Connect to readarr at {api_path}, received response: {response.json()}')
        if response.status_code < 400:
            id = response.json()['id']
        
        # search for it
        api_path = '/api/v1/command'
        response_search = self.request(
            api_path,
            json_={"name":"BookSearch","bookIds":[id]},
            method='POST'
        )
        api_logger.info(
            f'Connect to readarr at {api_path}, received response: {response_search.json()}')        
        return self.handle_readarr_queue_response(response_search, id, choice_payload['title'], request)

    def request(self, api_path, method='GET',json_=None, headers=None):
        url = f'{self._url}{api_path}'
        api_logger.info(f'Readarr request url: {url}')
        api_logger.info(f'Readarr request json: {json_}')
        api_logger.info(f'Readarr request headers: {headers}')
        headers = {
          'Authorization': f'Bearer {self._api_key}'
        }
        response = requests.request(method, url, headers=headers, json=json_)
        api_logger.info(f'Readarr response code: {response.status_code}')
        api_logger.debug(f'Readarr response json: {response.json()}')
        return response
    
    @staticmethod
    def convert_readarr_choice_response_to_text(response):
        choices = "\n".join(
            [f'[{key}]: {item["title"]}\n\t{item["payload"]["author"]["authorName"]} ({item["payload"]["releaseDate"][0:4]})' for key, item in response.items()])
        return f'Reply with number of choice: \n {choices}'
    
    @classmethod
    def handle_readarr_queue_response(cls, response, media_id, title, request):
        if response.status_code >= 400:
            error = f'Readarr api interface is messed up, no isError flag key ' \
                    f'or message key is not present {response}'
            api_logger.exception(response.text)
            return error
        if request:
            request.complete_request(media_id, title)
        return f'Successfully requested {title}!'