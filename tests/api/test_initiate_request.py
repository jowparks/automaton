from unittest.mock import Mock
import pytest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework.test import APIClient
from automaton.models import Requestor


@pytest.fixture()
def mock_requestor_objects(monkeypatch):
    objects_mock = Mock()
    monkeypatch.setattr(Requestor, 'objects', objects_mock)
    return objects_mock


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.mark.parametrize(
    argnames='request,expected_return',
    argvalues=[
        ('+18887776655', HTTP_200_OK),
        ('+18887776654', HTTP_403_FORBIDDEN)
    ]
)
def test_has_permission(mock_requestor_objects, api_client):
    def mock_get(number=None):
        if number != '+18887776655':
            raise ObjectDoesNotExist
    mock_requestor_objects.get = mock_get
    response = api_client.get()