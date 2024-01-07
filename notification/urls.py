from django.urls import path
from notification import views

app_name="notification"

urlpatterns = [
    path("user-notifications/", views.notifications, name="all-notifications"),
    path("view-post-notification/<post_id>/", views.view_post_notification, name="view-post-notification"),
    path("view-friend-notification/<user_id>/<accepter_id>", views.view_friend_notification, name="view-friend-notification"),
    path("unread-notification-count/", views.unread_notifications, name="unread-notifications"),
    path("unread-message-count/", views.unread_messages, name="unread-messages"),
    path("unread-group-message-count/", views.unread_group_messages, name="unread-group-messages"),
    path("missed-calls-count/", views.missed_calls, name="missed-calls-count"),
]
