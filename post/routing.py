from django.urls import re_path

from . import consumers

http_urlpatterns = [
    re_path(r'^sse/feed/$', consumers.SSEConsumer.as_asgi()),
]
