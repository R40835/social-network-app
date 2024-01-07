from django.db.models.signals import post_save
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import PostNotification, NewFriendNotification
from chat.models import DirectMessage, RoomMessage, Room
from friend.models import FriendRequest


@receiver(post_save, sender=PostNotification)
def post_interaction_notification(sender, instance, created, **kwargs):
    """
    Firing signal upon Post Notification creation and sending relevant data 
    through consumer to client to trigger the notification on the UI.
    """
    if created:
        channel_layer = get_channel_layer()
        sender_name = str(instance.sender.first_name) + " " + str(instance.sender.last_name)
        sender_profile_photo = f"{instance.sender.profile_photo.url}" if instance.sender.profile_photo else None,
        notification_type = f"{instance.notification_type}"

        data = {
            "notification": "post interaction", 
            "sender": sender_name,
            "profile_photo": sender_profile_photo,
            "notification_type": notification_type
        }

        # Sending notification to the recipient channel
        group_name = "pi_notifications_" + str(instance.recipient.pk)
        event = {
            "type": "post.interaction",
            "notification": data
        }
        async_to_sync(channel_layer.group_send)(group_name, event)


@receiver(post_save, sender=FriendRequest)
def friend_request_notification(sender, instance, created, **kwargs):
    """
    Firing signal upon Friend Request creation and sending relevant data 
    through consumer to client to trigger the notification on the UI.
    """
    if created:
        channel_layer = get_channel_layer()
        sender_name = str(instance.user.first_name) + " " + str(instance.user.last_name)
        sender_profile_photo = f"{instance.user.profile_photo.url}" if instance.user.profile_photo else None,


        data = {
            "notification": "friend request", 
            "sender": sender_name,
            "profile_photo": sender_profile_photo
        }

        # Sending notification to the recipient channel
        group_name =  "fr_notifications_" + str(instance.recipient.pk)
        event = {
            "type": "new.request",
            "notification": data
        }
        async_to_sync(channel_layer.group_send)(group_name, event)


@receiver(post_save, sender=NewFriendNotification)
def request_accepted_notification(sender, instance, created, **kwargs):
    """
    Firing signal upon New Friendship Notification creation and sending relevant data 
    through consumer to client to trigger the notification on the UI.
    """
    if created:
        channel_layer = get_channel_layer()
        sender_name = str(instance.accepter.first_name) + " " + str(instance.accepter.last_name)
        sender_profile_photo = f"{instance.accepter.profile_photo.url}" if instance.accepter.profile_photo else None,

        data = {
            "notification": "friend request accepted", 
            "sender": sender_name, # Notification sender; user who accepted the friend request
            "profile_photo": sender_profile_photo
        }

        # Sending notification to the recipient channel
        group_name = "nf_notifications_" + str(instance.sender.pk) 
        event = {
            "type": "new.friend",
            "notification": data,
        }
        async_to_sync(channel_layer.group_send)(group_name, event)


@receiver(post_save, sender=DirectMessage)
def direct_chat_notification(sender, instance, created, **kwargs):
    """
    Firing signal upon Direct Message creation and sending relevant data through consumer 
    to client to trigger the notification on the UI (check done in the consumer).
    """
    if created:
        channel_layer = get_channel_layer()
        sender_name = str(instance.sender.first_name) + " " + str(instance.sender.last_name)
        sender_id = str(instance.sender_id)
        sender_profile_photo = f"{instance.sender.profile_photo.url}" if instance.sender.profile_photo else None,

        data = {
            "notification": "message", 
            "action": "check", # To check if the user should be notified
            "sender": sender_name,
            "sender_id": sender_id,
            "profile_photo": sender_profile_photo
        }

        # Sending notification to the recipient channel
        group_name = "dm_notifications_" + str(instance.recipient.pk)
 
        event = {
            "type": "direct.message",
            "notification": data
        }
        async_to_sync(channel_layer.group_send)(group_name, event)


@receiver(post_save, sender=RoomMessage) 
def group_chat_notification(sender, instance, created, **kwargs):
    """
    Firing signal upon Room Message creation and sending relevant data through consumer 
    to client to trigger the notification on the UI (check done in the consumer).
    """
    if created:
        channel_layer = get_channel_layer()
        sender_name = str(instance.user.first_name) + " " + str(instance.user.last_name)

        room = Room.objects.get(pk=instance.room_id)
        members = room.members
        room_id = room.id
        sender_id = instance.user.pk
        sender_profile_photo = f"{instance.user.profile_photo.url}" if instance.user.profile_photo else None,

        data = {
            "notification": "message",
            "action": "check", # To check if the user should be notified
            "sender": sender_name,
            "sender_id": sender_id,
            "profile_photo": sender_profile_photo,
            "room_id": room_id,
        }

        # Sending data to client; data will be sent back to server (consumer) to check users to notify
        if members:
            for member in members:
                # Sending notification to the recipient channel
                group_name = "gc_notifications_" + str(member)
                event = {
                    "type": "group.message",
                    "notification": data,
                }
                async_to_sync(channel_layer.group_send)(group_name, event)
