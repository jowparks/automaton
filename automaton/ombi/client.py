import json

from django.core.exceptions import ObjectDoesNotExist

from automaton.enumerations import MOVIE_RT, TV_RT, CHOICE_RT, INVALID_REQUEST_MESSAGE, NO_EXISTING_REQUEST
from automaton.models.request import Request
from automaton.ombi.movie import MovieRequestMixin
from automaton.ombi.tv import TVRequestMixin


class OmbiClient(MovieRequestMixin, TVRequestMixin):

    def _choose_from_existing_request(self, requestor, choice):
        try:
            request = Request.get_existing_request_for_user(requestor)
        except ObjectDoesNotExist:
            return NO_EXISTING_REQUEST
        choices = json.loads(request.provided_options)
        choice_id = choices[str(choice)]['id']
        choice_title = choices[str(choice)]['title']
        if request.request_type == MOVIE_RT:
            return self._request_movie_by_id(choice_id, choice_title, request=request)
        elif request.request_type == TV_RT:
            return self._request_tv_by_id(choice_id, choice_title, request=request)
        return INVALID_REQUEST_MESSAGE

    def resolve_request(self, request_type, requestor, body):
        if request_type == MOVIE_RT:
            return self.initiate_movie_search_request(requestor, body)
        elif request_type == TV_RT:
            return self.initiate_tv_search_request(requestor, body)
        elif request_type == CHOICE_RT:
            return self._choose_from_existing_request(requestor, body)
        else:
            return INVALID_REQUEST_MESSAGE
        
    def _request_audiobook_by_id(self, audiobook_id, title, request=None):
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

    def make_ombi_request(self, request_type, from_, body) -> str:
        return self.resolve_request(request_type, from_, body)