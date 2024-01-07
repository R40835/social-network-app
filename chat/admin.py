from django.contrib import admin
from .models import DirectMessage, RoomMessage, PrivateConversation, Room

admin.site.register(RoomMessage)
admin.site.register(Room)
admin.site.register(DirectMessage)
admin.site.register(PrivateConversation)