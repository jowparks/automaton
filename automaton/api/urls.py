from rest_framework.routers import DefaultRouter, SimpleRouter

from automaton.api.intiate_request import InitiateRequestViewset
from automaton.api.notify import ReceiveNotificationsViewset

router = DefaultRouter()
router.register('request', InitiateRequestViewset, base_name='request')
router.register('notify', ReceiveNotificationsViewset, base_name='notify')

app_name = 'api'
urlpatterns = router.urls
