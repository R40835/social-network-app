"""
ASGI config for social_network project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""
import os
from django.urls import re_path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from notification.routing import websocket_urlpatterns as notification_websocket_urlpatterns
from friend.routing import websocket_urlpatterns as friend_websocket_urlpatterns
from call.routing import websocket_urlpatterns as call_websocket_urlpatterns
from post.routing import http_urlpatterns as post_http_urlpatterns

django_asgi_app = get_asgi_application()

asgi_app_http_url = [
    re_path(r"", django_asgi_app),
]

application = ProtocolTypeRouter(
    {
        # "http": django_asgi_app,
        "http": URLRouter(
            post_http_urlpatterns + 
            asgi_app_http_url
        ),

        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    chat_websocket_urlpatterns + 
                    notification_websocket_urlpatterns + 
                    friend_websocket_urlpatterns +
                    call_websocket_urlpatterns
                )
            )
        ),
    }
)


