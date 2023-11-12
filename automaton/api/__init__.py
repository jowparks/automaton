from typing import List

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.views import exception_handler
from automaton.twilio import TwilioClient, TwilioMessage
from automaton.util.log import api_logger


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    originating_from = context['request'].data['From']
    originating_to = context['request'].data['To']
    if not response:
        print('Uh oh')
        api_logger.error(exc)
        msg = TwilioClient().messages.create(to=originating_from,
                                             from_=originating_to,
                                             body='Major system malfunction')
        return HttpResponse(msg, content_type='text/xml')
    if response.status_code in [401, 403]:

        msg = TwilioClient().messages.create(to=originating_from,
                                             from_=originating_to,
                                             body='Go away')
        return HttpResponse(msg, content_type='text/xml')

    return response


class AutomatonViewSet(viewsets.ViewSet):

    twilio_client = TwilioClient()

    def create_twilio_responses(self, messages: List[TwilioMessage]) -> HttpResponse:
        return_val: str = ''
        for msg in messages:
            return_val += str(
                self.twilio_client.messages.create(
                    to=msg['message_to'],
                    from_=msg['message_from'],
                    body=msg['message']
                )
            )

        return HttpResponse(return_val, content_type='text/xml')