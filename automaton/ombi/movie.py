import json
from urllib.parse import quote_plus

import requests
from automaton.enumerations import MOVIE_RT
from automaton.models.request import Request
from automaton.ombi import OmbiBase
from automaton.util.log import api_logger


class MovieRequestMixin(OmbiBase):
    def initiate_movie_search_request(self, requestor, body):
        response = self._search_for_movie_by_term(body)
        created = Request.create_request(requestor, body, json.dumps(response), MOVIE_RT)
        if len(response) == 0:
            return 'No movie results found, you insolent meat sack.'
        if len(response) == 1:
            return self._request_movie_by_id(response[0]['id'], response[0]['title'], created)
        return self.convert_ombi_choice_response_to_text(response) if created else 'Failed to create request in ' \
                                                                                   'database for new movie request'

    def _search_for_movie_by_term(self, term):
        """
        Search ombi for movie by search term
        :param term:
        :return: search data
        """
        api_path = f'/api/v2/Search/multi/{quote_plus(term.strip())}'
        ombi_response = self.request(
            f'{api_path}',
            json_={
                "movies": True,
                "tvShows": False,
                "music": False,
                "people": False
            },
            method='POST'
        )
        api_logger.info(f'Connect to Ombi at {api_path}, received response.')
        return self._get_response_from_ombi_movie_data(ombi_response)

    def _request_movie_by_id(self, movie_id, title, request=None):
        """
        Request movie in OMBI by
        :param id:
        :return:
        """
        api_path = '/api/v1/Request/movie'
        ombi_response = self.request(
            api_path,
            json_={
                'theMovieDbId': movie_id,
                'languageCode': 'en'
            },
            method='POST'
        )
        api_logger.info(
            f'Connect to Ombi at {api_path}, received response: {ombi_response}')
        return self.handle_ombi_queue_response(ombi_response, movie_id, title, request)

    def _get_response_from_ombi_movie_data(self, data):
        all_options = {
            idx: dict(
                title=item['title'],
                id=item['id'],
            )
            for idx, item in enumerate(data[:6])
        }
        if len(all_options) > 5:
            return {key: val for key, val in all_options.items() if key < 6}
        return all_options
