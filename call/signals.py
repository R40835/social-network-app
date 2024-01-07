from django.db.models.signals import post_save
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import CallSession
from users.models import User


@receiver(post_save, sender=CallSession)
def calling_user(sender, instance, created, **kwargs):
    """
    Firing signal upon user call and sending relevant 
    data to client through consumer.
    """
    if created and instance.ongoing:
        channel_layer = get_channel_layer()

        caller_id = instance.caller_id
        callee_id = instance.callee_id
        caller_name = f"{instance.caller_name}"
        callee_name = f"{instance.callee_name}"
        channel_name = f"{instance.channel_name}"
        caller = User.objects.get(pk=caller_id)
        profile_photo = f"{caller.profile_photo.url}" if caller.profile_photo else "/media/app/default-user.png"
        # Sending relevant data to the recipient channel
        group_name = f"call_notifications_{instance.callee_id}"

        event = {
            "type": "call.user",
            "notification": {
                "caller_id": caller_id,
                "caller": caller_name,
                "callee_id": callee_id,
                "callee": callee_name,
                "profile_photo": profile_photo,
                "channel_name": channel_name,
                "notification_type": "call",
            }
        }
        async_to_sync(channel_layer.group_send)(group_name, event)
