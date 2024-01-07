from django.contrib import admin
from .models import FriendRequest, Friendship

admin.site.register(FriendRequest)
admin.site.register(Friendship)