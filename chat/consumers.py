import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import RoomMessage, Room, DirectMessage, PrivateConversation
from users.models import User 

from django.db.models import Q
from django.utils import timezone

from datetime import datetime


class RoomChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        """
        Receiving data from client then sending it back.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Get the current time in UTC timezone
        current_time = timezone.now()
        # Convert the current time to our desired format
        timestamp = current_time.strftime("%d/%m/%Y at %H:%M")

        # Not processing empty messages
        if message != "" and message.isspace() == False:
            # save room message
            await self.save_message_to_database(message)
            
            # Send message to room group 
            await self.channel_layer.group_send(
                self.room_group_name, 
                { 
                    "type": "chat.message",
                    "message": message, 
                    "sender_id": int(self.scope["user"].id),
                    "name": f"{self.scope['user'].first_name} {self.scope['user'].last_name}",
                    "profile_photo": f"{self.scope['user'].profile_photo.url}" if self.scope['user'].profile_photo else None,
                    "timestamp": timestamp
                }
            )

    async def chat_message(self, event):
        """
        Sending data from server to client.
        """
        # Data to be sent
        message = event["message"]
        sender_id = event["sender_id"]
        profile_photo = event["profile_photo"]
        username = event["name"]
        timestamp = event["timestamp"]

        # Preventing the submission of empty messages
        if message != "" and message.isspace() == False:
            # Send message to WebSocket
            await self.send(text_data=json.dumps
                (
                    {
                        "message": message,
                        "sender_id": sender_id,
                        "name": username,
                        "profile_photo": profile_photo,
                        "timestamp": timestamp
                    }
                )
            )
    
    @database_sync_to_async
    def save_message_to_database(self, message):
        """
        Saving messages received from client in the database.
        """
        try:
            room = Room.objects.get(pk=self.room_id)
            room.readers = []
            room.readers = [self.scope['user'].id] 
            room.latest_message_timestamp = timezone.now()
            room.save()

            message = RoomMessage.objects.create(
                user=self.scope['user'], # sender
                room=room, 
                content=message,
            )
        except Room.DoesNotExist:
            pass


class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.sender = self.scope["user"] # first user
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"] # second user id
        self.receiver = await self.get_user_by_id(self.user_id)

        if self.sender == self.receiver:
            raise ValueError("Can't send a message to yourself.")

        if self.sender and self.receiver:
            # Create a unique channel name for DM
            self.dm_group_name = f'dm_{min(self.sender.id, self.receiver.id)}_{max(self.sender.id, self.receiver.id)}'
            # Join DM 
            await self.channel_layer.group_add(self.dm_group_name, self.channel_name)

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        # Leave DM 
        await self.channel_layer.group_discard(self.dm_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receiving data from client then sending it back.
        """
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Get the current time in UTC timezone
        current_time = timezone.now()
        # Convert the current time to our desired format
        timestamp = current_time.strftime("%d/%m/%Y at %H:%M")
        
        if message != "" and message.isspace() == False:
            # Save dm 
            await self.save_message_to_database(message)

            # Send dm 
            await self.channel_layer.group_send(
                self.dm_group_name, 
                {
                    "type": "chat.message",
                    "message": message, 
                    "sender_id": int(self.sender.id),
                    "name": f"{self.scope['user'].first_name} {self.scope['user'].last_name}",
                    "timestamp": timestamp
                }
            )

    async def chat_message(self, event):
        """
        Sending data from server to client.
        """
        # Data to be sent
        message = event["message"]
        sender_id = event["sender_id"]
        username = event["name"]
        timestamp = event["timestamp"]

        if message != "" and message.isspace() == False:
            # Sending message to WebSocket
            await self.send(text_data=json.dumps
                (
                    {
                    "message": message,
                    "sender_id": sender_id,
                    "name": username,
                    "timestamp": timestamp
                    }
                )
            )
    
    @database_sync_to_async
    def save_message_to_database(self, message):
        """
        Saving messages received from client in the database.
        """
        try:
            conversation = PrivateConversation.objects.get(
                Q(user=self.sender) & Q(participant=self.receiver) | 
                Q(user=self.receiver) & Q(participant=self.sender)
            )
            conversation.latest_message_timestamp = timezone.now()
            conversation.save()
        except PrivateConversation.DoesNotExist:
            conversation = PrivateConversation.objects.create(
                user=self.sender,
                participant=self.receiver
            )

        DirectMessage.objects.create(
            conversation_id=conversation.id,
            sender=self.sender,
            recipient=self.receiver, 
            content=message
        )

    @database_sync_to_async
    def get_user_by_id(self, user_id):
        """
        Getting a user object by querying the database based on a user PK.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            self.close()

