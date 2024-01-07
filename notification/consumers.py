import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chat.models import PrivateConversation, DirectMessage, RoomMessage, Room
from django.db.models import Q


class PostNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.user_id = str(self.scope['user'].pk)
        self.room_group_name = f"pi_notifications_{self.user_id}"

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receiving data from client then sending it back.
        """
        notification = json.loads(text_data)
        content = notification['notification']
        sender = notification['sender']
        sender_profile_photo = notification['profile_photo']
        notification_type = notification['notification_type']

        # Send data to the Websocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'post.interaction',
                'notification': {
                    'sender': sender,
                    'profile_photo': sender_profile_photo,
                    'notification_type': notification_type,
                    'notification': content
                }
            }
        )

    async def post_interaction(self, event):
        """
        Sending relevant data to client to trigger post-related notifications.
        """
        notification = event['notification']

        # Send data to the WebSocket
        await self.send(text_data=json.dumps
            (
                {
                    'notification': notification
                }
            )
        )


class FriendRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.user_id = str(self.scope['user'].pk)
        self.room_group_name = f"fr_notifications_{self.user_id}"

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receiving data from client then sending it back.
        """
        notification = json.loads(text_data)
        content = notification['notification']
        sender = notification['sender']
        sender_profile_photo = notification['profile_photo']

        # Send Data to the Websocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new.request',
                'notification': {
                    'sender': sender,
                    'profile_photo': sender_profile_photo,
                    'notification': content
                }
            }
        )

    async def new_request(self, event):
        """
        Sending relevant data to client to trigger friend-request-related notifications.
        """
        notification = event['notification']

        # Send data to the WebSocket
        await self.send(text_data=json.dumps
            (
                {
                    'notification': notification
                }
            )
        )


class NewFriendConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.user_id = str(self.scope['user'].pk)
        self.room_group_name = f"nf_notifications_{self.user_id}"

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receiving data from client then sending it back.
        """
        notification = json.loads(text_data)
        content = notification['notification']
        sender = notification['sender']
        sender_profile_photo = notification['profile_photo']

        # Send data to the Websocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new.friend',
                'notification': {
                    'sender': sender,
                    'profile_photo': sender_profile_photo,
                    'notification': content
                }
            }
        )

    async def new_friend(self, event):
        """
        Sending relevant data to client to trigger friend request approval notifications.
        """
        notification = event['notification']

        # Send data to the WebSocket
        await self.send(text_data=json.dumps
            (
                {
                    'notification': notification
                }
            )
        )


class DmNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.user_id = str(self.scope['user'].pk)
        self.room_group_name = f"dm_notifications_{self.user_id}"

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receiving data from client then sending it back.
        """
        text_data_json = json.loads(text_data)
        content = text_data_json['notification']
        sender = text_data_json['sender']
        sender_id = text_data_json['sender_id']
        sender_profile_photo = text_data_json['profile_photo']
        current_path = text_data_json['current_path']

        user2_id = await self.get_user_id(current_path)

        # Notifying user if not in the chat thread
        if user2_id != str(sender_id):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'direct.message',
                    'notification': {
                        'action': 'notification',
                        'sender_id': sender_id,
                        'sender': sender,
                        'profile_photo': sender_profile_photo,
                        'notification': content,
                    }
                }
            )
        else:
            # Marking message as read
            await self.mark_message_as_read(str(user2_id))

    async def direct_message(self, event):
        """
        Sending relevant data to client to trigger DM notifications.
        """
        notification = event['notification']

        # Send data to the WebSocket
        await self.send(text_data=json.dumps
            (
                {
                    'notification': notification,
                }
            )
        )

    @staticmethod
    async def get_user_id(path):
        """
        Getting the recipient's PK if the user is currently present in a DM.
        """
        return ''.join(c for c in path if c.isdigit()) if "/chat/dm/" in path else None

    @database_sync_to_async
    def mark_message_as_read(self, user2_id):
        """
        Marking messages as read.
        """
        user1_id = str(self.user_id)

        try:
            conversation = PrivateConversation.objects.get(
                Q(user_id=user1_id) & Q(participant_id=user2_id)
            )
        except PrivateConversation.DoesNotExist:
            conversation = PrivateConversation.objects.get(
                Q(user_id=user2_id) & Q(participant_id=user1_id)
            )
        messages = DirectMessage.objects.filter(
            Q(recipient_id=user1_id) & Q(conversation_id=conversation.id)
        ).order_by('-timestamp')
        messages.update(is_read=True)


class GcNotificationConsumer(AsyncWebsocketConsumer):        
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.user_id = str(self.scope['user'].pk)
        self.room_group_name = f"gc_notifications_{self.user_id}"

        # Join the room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        """
        Disconnecting user from Websocket.
        """
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Receiving data from client then sending it back.
        """
        notification = json.loads(text_data)
        content = notification['notification']
        notified_room_id = notification['room_id']
        sender = notification['sender']
        sender_id = notification['sender_id']
        sender_profile_photo = notification['profile_photo']
        current_path = notification['current_path']
        
        current_room_id = await self.get_room_id(current_path)

        # notify user if not currently in the room
        if str(notified_room_id) != current_room_id:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'group.message',
                    'notification': {
                        "action": "notification",
                        "sender": sender,
                        "sender_id": sender_id,
                        "profile_photo": sender_profile_photo,
                        "notification": content,
                        "room_id": notified_room_id
                    }
                }
            )
        else:
            await self.mark_message_as_read(notified_room_id, self.scope['user'].pk)

    async def group_message(self, event):
        """
        Sending relevant data to client to trigger group chat message notifications.
        """
        notification = event['notification']
        room_id = notification['room_id']

        sender = await self.get_sender(room_id)

        # only recipients get notified
        if self.user_id != str(sender.pk):
            # Send the message to the WebSocket
            await self.send(text_data=json.dumps
                (
                    {
                        'notification': notification,
                        # 'room_id': room_id
                    }
                )
            )

    @staticmethod
    @database_sync_to_async
    def get_sender(room_id): 
        """
        Getting the user who sent the last message 
        in a specific room based on the latter's PK.
        """
        try:
            message = RoomMessage.objects.filter(room_id=room_id).last()
            return message.user
        except RoomMessage.DoesNotExist:
            pass
    
    @staticmethod
    @database_sync_to_async
    def mark_message_as_read(room_id, reader):
        """
        Marking message as read by appending user object to the readers array field.
        """
        try:
            room = Room.objects.get(pk=room_id)
            room.readers.append(reader)
            room.save()
        except Room.DoesNotExist:
            pass

    @staticmethod
    async def get_room_id(path):
        """
        Getting the room's PK if the user is currently present in a room.
        """
        return ''.join(c for c in path if c.isdigit()) if "/chat/room/" in path else None