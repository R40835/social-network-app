from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/notification/posts/$", consumers.PostNotificationConsumer.as_asgi()),
    re_path(r"ws/notification/direct-messages/$", consumers.DmNotificationConsumer.as_asgi()),
    re_path(r"ws/notification/friend-requests/$", consumers.FriendRequestConsumer.as_asgi()), 
    re_path(r"ws/notification/new-friends/$", consumers.NewFriendConsumer.as_asgi()), 
    re_path(r"ws/notification/group-messages/$", consumers.GcNotificationConsumer.as_asgi()), 
]
