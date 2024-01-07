from django.urls import path
from friend import views

app_name="friend"

urlpatterns = [
    path("friends-list/<user_id>", views.friends, name="friends-list"),
    path("friend-requests/", views.received_friend_requests, name="friend-requests"),
    path("send-request/<request_id>", views.send_friend_request, name="send-request"),
    path("decline-request/<request_id>", views.decline_friend_request, name="decline-request"),
    path("send-cancel-request/<recipient_id>", views.send_cancel_friend_request, name="send-cancel-request"),
    path("cancel-request/<request_id>", views.cancel_friend_request, name="cancel-request"),
    path("accept-request/<sender_id>", views.accept_friend, name="accept-request"),
    path("remove-friend/<friend_id>", views.remove_friend, name="remove-friend"),
    path("remove-send-cancel-request/<friend_id>", views.remove_send_cancel_friend, name="remove-send-cancel-request"),
    path("online-friends/", views.user_online_friends, name="online-friends"),
    path("online-friends-page/", views.online_friends_page, name="online-friends-page"),
    path("unread-friend-request-count/", views.unread_friend_requests, name="online-friends"),
]
