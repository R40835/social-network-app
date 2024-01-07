from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/notification/calls/$", consumers.CallNotificationConsumer.as_asgi()),
    re_path(r"ws/notification/calls-declined/$", consumers.DeclineCallConsumer.as_asgi()),
]
