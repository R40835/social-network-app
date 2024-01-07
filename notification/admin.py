from django.contrib import admin
from .models import PostNotification, NewFriendNotification

admin.site.register(PostNotification)
admin.site.register(NewFriendNotification)