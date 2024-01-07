from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from users.models import ActiveUser
from .models import Friendship


@receiver(post_save, sender=ActiveUser)
def active_user(sender, instance, created, **kwargs):
    """
    Firing signal upon user connection and sending relevant data to client 
    through consumer if the user is a friend (check done in the consumer).
    """
    # No signals fired upon creation, only on updates.
    channel_layer = get_channel_layer()

    if instance.is_online == True:
        is_active = True
    else:
        is_active = False

    user_id = instance.user_id
    user_name = f"{instance.user.first_name} {instance.user.last_name}"
    profile_photo = f"{instance.user.profile_photo.url}" if instance.user.profile_photo else "/media/app/default-user.png"

    # Sending relevant data to the recipient channel
    group_name = "active_users"
    event = {
        "type": "active.user",
        "user_id": user_id,
        "user_name": user_name,
        "profile_photo": profile_photo,
        "is_active": is_active,
        "trigger": "ActiveUser"
    }
    async_to_sync(channel_layer.group_send)(group_name, event)


@receiver(post_save, sender=Friendship)
def new_friend_active(sender, instance, created, **kwargs):
    """
    Firing signal upon friendship creation and sending notification data through 
    consumer to client who sent a friend request (check done in the consumer).
    """
    if created:
        channel_layer = get_channel_layer()
        user_status = ActiveUser.objects.get(user=instance.friend)
        
        if user_status.is_online == True:
            is_active = True
        else:
            is_active = False

        user_id = instance.friend_id
        user2_id = instance.user_id
        user_name = f"{instance.friend.first_name} {instance.friend.last_name}"
        profile_photo = f"{instance.friend.profile_photo.url}" if instance.friend.profile_photo else "/media/app/default-user.png"

        # Sending notification data to the recipient channel
        group_name = "active_users"
        event = {
            "type": "add.user",
            "user_id": user_id,
            "user2_id": user2_id,
            "user_name": user_name,
            "profile_photo": profile_photo,
            "is_active": is_active,
            "trigger": "Friendship"
        }
        async_to_sync(channel_layer.group_send)(group_name, event)


@receiver(pre_delete, sender=Friendship)
def friend_removed(sender, instance, **kwargs):
    """
    Firing signal upon friendship deletion and sending relevant data through consumer 
    to client to remove ex-friend from online friends (check done in the consumer).
    """
    channel_layer = get_channel_layer()    
    # Not active since user is not a friend anymore
    is_active = False
    user_id = instance.friend_id
    user2_id = instance.user_id
    user_name = f"{instance.friend.first_name} {instance.friend.last_name}"
    profile_photo = f"{instance.friend.profile_photo.url}" if instance.friend.profile_photo else "/media/app/default-user.png"

    # Sending relevant data to the recipient channel
    group_name = "active_users"
    event = {
        "type": "remove.user",
        "user_id": user_id,
        "user2_id": user2_id,
        "user_name": user_name,
        "profile_photo": profile_photo,
        "is_active": is_active,
        "trigger": "Friendship"
    }
    async_to_sync(channel_layer.group_send)(group_name, event)