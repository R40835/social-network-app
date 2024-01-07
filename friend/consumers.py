import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from django.db.models import Q
from .models import Friendship


class ActiveUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.user_id = self.scope["user"].pk
        self.active_users_group_name = "active_users"

        await self.channel_layer.group_add(self.active_users_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        await self.channel_layer.group_discard(self.active_users_group_name, self.channel_name)

    async def active_user(self, event):
        """
        Called from signals.py to show the client friends 
        who just logged in (when a friend is online).
        """
        user_id = event["user_id"] # Any user that logs in or out
        user_name = event["user_name"]
        profile_photo = event["profile_photo"]
        is_active = event["is_active"]
        trigger = event["trigger"]

        is_friend = await self.check_friendship(user_id)

        if is_friend and self.user_id != user_id:
            await self.send(text_data=json.dumps
                (
                    {
                        "user_id": user_id,
                        "user_name": user_name,
                        "profile_photo": profile_photo,
                        "is_active": is_active,
                        "trigger": trigger
                    }
                )
            )

    async def add_user(self, event):
        """
        Called from signals.py to show the client new 
        friends (when a friend request is accepted).
        """
        user_id = event["user_id"] # User that accepted a friend request and is online
        user2_id = event["user2_id"] # User whose friend request was accepted by an online user
        user_name = event["user_name"]
        profile_photo = event["profile_photo"]
        is_active = event["is_active"]
        trigger = event["trigger"]

        is_friend = await self.check_friendship(user_id)

        if (is_friend and self.user_id != user_id and self.user_id == user2_id) or (is_friend and self.user_id != user2_id and self.user_id == user_id):
            await self.send(text_data=json.dumps
                (
                    {
                        "user_id": user_id,
                        "user2_id": user2_id,
                        "user_name": user_name,
                        "profile_photo": profile_photo,
                        "is_active": is_active,
                        "trigger": trigger
                    }
                )
            )

    async def remove_user(self, event):
        """
        called from signals.py when a friendship is ended so that 
        ex-friend won't appear as an online friends anymore.
        """
        user_id = event["user_id"] # User that removed a friend
        user2_id = event["user2_id"] # User who was removed
        user_name = event["user_name"]
        profile_photo = event["profile_photo"]
        trigger = event["trigger"]

        if (self.user_id != user_id and self.user_id == user2_id) or (self.user_id != user2_id and self.user_id == user_id):
            await self.send(text_data=json.dumps
                (
                    {
                        "user_id": user_id,
                        "user2_is": user2_id,
                        "user_name": user_name,
                        "profile_photo": profile_photo,
                        "is_active": False,
                        "trigger": trigger
                    }
                )
            )

    @database_sync_to_async
    def check_friendship(self, user_id):
        """
        Checking based on a PK whether the user 
        queried is friend with the current user.
        """
        friendship = Friendship.objects.filter(
                Q(user_id=self.user_id) & Q(friend_id=user_id)
            ).exists()
        if friendship:
            return True
        return False