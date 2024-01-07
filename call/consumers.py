import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from users.models import User


class CallNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.callee_id = str(self.scope['user'].pk) 
        self.room_group_name = f"call_notifications_{self.callee_id}"

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
        json_text_data = json.loads(text_data)
        notification = json_text_data['notification']
        caller_id = notification['caller_id']
        caller_photo = notification['caller_photo']
        notification_type = notification['notification_type']

        caller_name = await self.get_caller_name(caller_id)

        if notification_type == 'missed-call':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'missed.call',
                    'notification': {
                        'notification_type': 'missed-call', 
                        'caller_id': caller_id,
                        'caller_name': caller_name,
                        'caller_photo': caller_photo
                    }
                }
            )

    async def call_user(self, event):
        """
        Sending relevant data to client to trigger call notifications.
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

    async def missed_call(self, event):
        """
        Notifying users about missed calls.
        """
        notification = event['notification']

        await self.send(text_data=json.dumps
            (
                {
                    'notification': notification
                }
            )
        )

    @staticmethod
    @database_sync_to_async
    def get_caller_name(user_id):
        """
        Getting user full name bu the latter's pk.
        """
        caller = User.objects.get(pk=user_id)
        return f"{caller.first_name} {caller.last_name}"



class DeclineCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Connecting user to Websocket.
        """
        self.callee_id = str(self.scope['user'].pk) 
        self.room_group_name = f"call_declined" 

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
        json_text_data = json.loads(text_data)
        notification = json_text_data['notification']
        caller_id = notification['caller_id']
        notification_type = notification['notification_type']

        if notification_type == 'decline':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'decline.call',
                    'notification': {
                        'notification_type': 'decline', 
                        'caller_id': caller_id,
                    }
                }
            )

    async def decline_call(self, event):
        """
        Sending a signal to stop the call if the callee declines.
        """
        notification = event['notification']

        # Send data to the websocket
        await self.send(text_data=json.dumps
            (
                {
                    'notification': notification
                }
            )
        )

