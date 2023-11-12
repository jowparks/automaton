import json
from os import stat
from urllib.parse import quote_plus
from automaton.enumerations import TV_RT
from automaton.models.request import Request
from automaton.ombi import OmbiBase
from automaton.util.log import api_logger


class TVRequestMixin(OmbiBase):
    def initiate_tv_search_request(self, requestor, body):
        response = self._search_for_tv_by_term(body)
        if len(response) == 0:
            return 'No TV results found, sorry'
        if len(response) == 1:
            return self._request_tv_by_id(response[0]['id'], response[0]['title'])
        created = Request._request(requestor, body, json.dumps(response), TV_RT)
        return self.convert_ombi_choice_response_to_text(response) if created else 'Failed to create request in ' \
                                                                                   'database for new movie request'

    def _search_for_tv_by_term(self, term):
        """
        Search ombi for tv by search term
        :param term:
        :return: search data
        """
        api_path = f'/api/v2/Search/multi/{quote_plus(term.strip())}'
        ombi_response = self.request(
            f'{api_path}',
            json_={
                "movies": False,
                "tvShows": True,
                "music": False,
                "people": False
            },
            method='POST'
        )
        api_logger.info(
            f'Connect to Ombi at {api_path}, received response: {ombi_response}')
        return self._get_response_from_ombi_tv_data(ombi_response)

    def _request_tv_by_id(self, tv_id, title, request=None):
        """
        Request movie in OMBI by
        :param id:
        :return:
        """
        api_path = '/api/v2/Requests/tv'
        ombi_response = self.request(
            api_path,
            json_={
                "requestAll": True,
                # dogshit ombi code has theMovieDbId as id field in v2 api
                "theMovieDbId": tv_id,
            },
            method='POST'
        )
        api_logger.info(
            f'Connect to Ombi at {api_path}, received response: {ombi_response}')
        return self.handle_ombi_queue_response(ombi_response, tv_id, title, request)

    def _get_response_from_ombi_tv_data(self, data):
        all_options = {
            idx: dict(
                title=item['title'],
                id=item['id'],
                release=self._get_tv_data(item['id']).get('firstAired')
            )
            for idx, item in enumerate(data[:6])
        }
        if len(all_options) > 5:
            return {key: val for key, val in all_options.items() if key < 6}
        api_logger.info(f'Returning {all_options} to client')
        return all_options

    def _get_tv_data(self, tvDbId: int) -> dict:
        """
        Request tv data for given db id
        :param id:
        :return:
        """
        api_path = f'/api/v2/Search/tv/{tvDbId}'
        ombi_response = self.request(
            api_path,
        )
        api_logger.info(
            f'Connect to Ombi at {api_path}, received response: {ombi_response}')
        return ombi_response
