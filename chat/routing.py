from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/room/(?P<room_id>\w+)/$", consumers.RoomChatConsumer.as_asgi()),
    re_path(r"ws/chat/dm/(?P<user_id>\w+)/$", consumers.DirectChatConsumer.as_asgi()),
]

