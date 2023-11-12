from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import action
from rest_framework.response import Response

from automaton.api import AutomatonViewSet
from automaton.enumerations import MOVIE_RT, SERVER_NUMBER, COMPLETE_RS
from automaton.models import Request
from automaton.twilio import TwilioClient
from automaton.util.log import api_logger


class ReceiveNotificationsViewset(AutomatonViewSet):
    twilio_client = TwilioClient()

    @action(methods=['post'], detail=False)
    def radarr(self, request):
        api_logger.info(f'Radarr webhook received: {request.data}')
        movie_id = request.data['remoteMovie']['tmdbId']
        return self.find_matching_ombi_request(MOVIE_RT, movie_id)

    def find_matching_ombi_request(self, request_type, selected_media_id):
        try:
            fulfilled_request = Request.objects.get(request_type=request_type,
                                                        selected_media_id=selected_media_id)
            fulfilled_request.status = COMPLETE_RS
            fulfilled_request.save()
            item_name = fulfilled_request.display_name
            api_logger.info(f'Fulfilled request for {item_name}')
            return self.create_twilio_responses(fulfilled_request.requestor, SERVER_NUMBER,
                                               f'Your god has granted your request, I have '
                                               f'completed gathering {item_name}')
        except ObjectDoesNotExist:
            api_logger.info(f'No request found matching TheMovieDBID {selected_media_id}')
        finally:
            return Response('Accepted', status=200)
