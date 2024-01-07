from django.urls import path
from chat import views

app_name="chat"

urlpatterns = [
    path("room/<int:room_id>/", views.room, name="room"),
    path("create-room/", views.create_room, name="create-room"),
    path("rooms/", views.get_rooms, name="rooms"),
    path("dm/<int:user_id>/", views.direct_message, name="dm"),
    path("messages/", views.get_conversations, name="messages"),
    path("user-rooms/", views.get_user_rooms, name="user-rooms"),
    path("room-member/<int:member_id>/", views.get_member, name="room-member"),
    path("leave-room/<int:room_id>/", views.leave_room, name="leave-room")
]
