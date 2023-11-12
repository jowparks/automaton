import re
from typing import NewType, Tuple, Union, List, Optional, Callable

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models.query import QuerySet
from automaton.models.request import Request
from automaton.readarr.client import ReadarrClient
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission

from automaton.api import AutomatonViewSet
from automaton.enumerations import ADD_USER, AUDIOBOOK_RT, CHOICE_RT, MOVIE_RT, REMOVE_USER, ADMIN_REQUESTS, INVALID_REQUEST_MESSAGE, \
    GENERAL_ERROR_MESSAGE, TV_RT, WELCOME_MESSAGE, HELP_MESSAGE, NOTIFY_USERS
from automaton.models import Requestor
from automaton.ombi.client import OmbiClient
from automaton.request_parser import RequestParser
from automaton.twilio import TwilioMessage
from automaton.util.log import api_logger


class RegisteredRequestor(BasePermission):
    def has_permission(self, request, view):
        from_ = request.data['From']
        try:
            Requestor.objects.get(number=from_)
        except ObjectDoesNotExist:
            return False
        return True


class InitiateRequestViewset(AutomatonViewSet):
    ombi_client = OmbiClient()
    readarr_client = ReadarrClient()
    request_parser = RequestParser()
    permission_classes = (RegisteredRequestor,)
    help_request = 'helpme'
    admin_help_msg = 'Possible admin commands: {}'.format([r[1] for r in ADMIN_REQUESTS])

    def __init__(self, *args, **kwargs):
        super(InitiateRequestViewset, self). __init__(*args, **kwargs)
        self.admin_request_map = {
            ADD_USER: self._add_requestor,
            REMOVE_USER: self._remove_requestor,
            NOTIFY_USERS: self._notify_users,
        }

    @action(methods=['get', 'post'], detail=False)
    def basic(self, request):
        api_logger.info(f'Starting request generation')
        requestor: Requestor = Requestor.objects.get(number=request.data['From'])
        originating_to: str = request.data['To']
        originating_body: str = request.data['Body']
        try:
            return self.create_twilio_responses(
                self.resolve_all_possible_requests(originating_body, originating_to, requestor)
            )
        except Exception as e:
            api_logger.exception(f'Fatal error occurred: {e}')
            return self.create_twilio_responses(
                [
                    TwilioMessage(
                        message=GENERAL_ERROR_MESSAGE,
                        message_from=originating_to,
                        message_to=requestor.number
                    )
                ]
            )

    def resolve_all_possible_requests(self, originating_body, originating_to, requestor: Requestor) -> List[TwilioMessage]:
        messages: List[TwilioMessage] = \
            self.resolve_help_request(requestor, originating_to, originating_body) or \
            self.resolve_admin_requests(requestor, originating_to, originating_body) or \
            self.resolve_user_request(requestor, originating_to, originating_body)
        return messages

    def resolve_user_request(self, requestor: Requestor, originating_to: str, originating_body: str) -> List[TwilioMessage]:
        request_type, body = self.request_parser.parse_request(originating_body)
        if request_type is None or body is None:
            return [
                TwilioMessage(
                    message=INVALID_REQUEST_MESSAGE,
                    message_to=requestor.number,
                    message_from=originating_to,
                )
            ]

        api_logger.info(f'Request from "{requestor.number}" with originating body "{originating_body}"'
                        f' was processed to type "{request_type}" and body "{body}" is being processed"')
        request_choice = None
        if request_type == CHOICE_RT:
            request_choice = Request.get_existing_request_for_user(requestor).request_type

        if request_type == AUDIOBOOK_RT or request_choice == AUDIOBOOK_RT:
            response = self.readarr_client.make_readarr_request(request_type, requestor, body)
        else:
            response = self.ombi_client.make_ombi_request(request_type, requestor, body)
        return [
            TwilioMessage(
                message=response,
                message_to=requestor.number,
                message_from=originating_to,
            )
        ]

    def resolve_help_request(self, requestor: Requestor, originating_to: str, originating_body: str) -> Optional[List[TwilioMessage]]:
        if self.help_request == originating_body.lower().strip():
            if requestor.is_admin:
                msg = f'{HELP_MESSAGE}   {self.admin_help_msg}'
            else:
                msg = HELP_MESSAGE

            return [
                TwilioMessage(
                    message_from=originating_to,
                    message_to=requestor.number,
                    message=msg
                )
            ]
        return None

    def resolve_admin_requests(self, requestor: Requestor, originating_to: str, data: str) -> Optional[List[TwilioMessage]]:
        if requestor.is_admin:
            api_logger.info(f'Admin request received: {data}')
            admin_requst_type: Optional[str]
            parsed_body: Optional[str]
            admin_request_type, parsed_body = self.request_parser.parse_admin_request(data)
            if admin_request_type and parsed_body:
                func: Callable[[str, str, Requestor], List[TwilioMessage]] = self.admin_request_map[admin_request_type]
                return func(parsed_body, originating_to, requestor)
        return None

    def _add_requestor(self, number: str, originating_to: str, requestor: Requestor) -> List[TwilioMessage]:
        msg: str
        if not re.search('\+[0-9]{11}', number):
            msg = 'Failed, number of created user must match 11 digit code (eg "+18883459876"'
        else:
            try:
                with transaction.atomic():
                    user = User.objects.create(username=number)
                    Requestor.objects.create(number=number, user=user)
                    welcome_msg: TwilioMessage = TwilioMessage(
                        message_from=originating_to,
                        message_to=number,
                        message=WELCOME_MESSAGE
                    )
                creation_msg = TwilioMessage(
                    message=f'Successfully created {number}',
                    message_to=requestor.number,
                    message_from=originating_to,
                )
                api_logger.info(creation_msg)
                return [
                    welcome_msg,
                    creation_msg
                ]
            except IntegrityError:
                msg = f'Failed, requestor already exists for {number}'
            except Exception as e:
                api_logger.exception(f'{e}')
                msg = 'Unknown failure occurred while creating user, maybe twilio could not send message to new user?'
        return [
                TwilioMessage(
                    message=msg,
                    message_from=originating_to,
                    message_to=requestor.number
                )
            ]

    @staticmethod
    def _remove_requestor(deleted_num: str, originating_to: str, requestor: Requestor) -> List[TwilioMessage]:
        msg: str
        try:
            # deletion will cascade
            User.objects.get(username=deleted_num).delete()
            removal_msg = f'Successfully removed {deleted_num}'
            api_logger.info(removal_msg)
            msg = removal_msg
        except ObjectDoesNotExist:
            msg = f'Failed, cannot find requestor with {deleted_num} number to delete'
        return [
            TwilioMessage(
                message=msg,
                message_from=originating_to,
                message_to=requestor.number
            )
        ]

    @staticmethod
    def _notify_users(msg: str, originating_to: str, requestor: Requestor) -> List[TwilioMessage]:
        requestors: QuerySet = Requestor.objects.all()
        r: Requestor
        msgs: List = [
            TwilioMessage(
                message_from=originating_to,
                message_to=r.number,
                message=msg
            ) for r in requestors
        ]
        return msgs
