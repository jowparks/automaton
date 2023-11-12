import json
from django.db import models

from automaton.enumerations import ABANDONED_RS, REQUEST_SOURCES, REQUEST_TYPES, REQUEST_STATUSES, AWAITING_RS, REQUESTED_RS
from automaton.models.requestor import Requestor


class Request(models.Model):
    request_source = models.CharField(max_length=50,
                                    choices=REQUEST_SOURCES)
    request_type = models.CharField(max_length=50,
                                    choices=REQUEST_TYPES)
    display_name = models.TextField(null=True, default=None)
    request_body = models.TextField(null=True, default=None)
    provided_options = models.TextField(null=True, default=None)
    requestor = models.ForeignKey(Requestor, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,
                              choices=REQUEST_STATUSES,
                              default=AWAITING_RS)
    objects = models.Manager()
    selected_media_id = models.IntegerField(db_index=True, null=True, default=None)


    def complete_request(self, media_id, title):
        self.display_name = title
        self.selected_media_id = media_id
        self.status = REQUESTED_RS
        self.save()

    @staticmethod
    def get_existing_request_for_user(requestor):
        return Request.objects.get(
            requestor=requestor,
            status=AWAITING_RS,
        )

    @staticmethod
    def create_request(requestor, body, provided_options, request_type):
        Request.objects.filter(
            requestor=requestor, status=AWAITING_RS).update(status=ABANDONED_RS)
        return Request.objects.create(
            display_name=None,
            request_type=request_type,
            request_body=body,
            requestor=requestor,
            provided_options=provided_options,
            status=AWAITING_RS,
        )
