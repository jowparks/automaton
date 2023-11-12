from typing_extensions import TypedDict

from django.conf import settings
from twilio.rest import Client  # type: ignore


class TwilioMessage(TypedDict):
    message_from: str
    message_to: str
    message: str


class TwilioClient(Client):
    def __init__(self):
        sid = settings.TWILIO_ACCOUNT_SID
        token = settings.TWILIO_AUTH_TOKEN
        super(TwilioClient, self).__init__(sid, token)