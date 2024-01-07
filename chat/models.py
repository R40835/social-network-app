from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField


class Room(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
    )
    members = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        null=True,
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        default="Unnamed"
    )
    topic = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        default="General"
    )
    latest_message_timestamp = models.DateTimeField(
        auto_now=True
    )
    # Unlike DMs, rooms with multiple recipients require tracking. Notify users not among the current readers.
    readers = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        null=True,
    )
    
    def save(self, *args, **kwargs):
        """
        Override the save method to handle room's topics not defiend.
        """
        if not self.topic:
            self.topic = "General"  # Set a default topic if not provided
        super(Room, self).save(*args, **kwargs)


class RoomMessage(models.Model):
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    content = models.TextField(
        blank=False,
        null=False,
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )


class PrivateConversation(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="participant1"
    )
    participant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="participant2"
    )
    latest_message_timestamp = models.DateTimeField(
        auto_now=True,
        blank=False,
        null=False
    )
    
    class Meta:
        unique_together = ("user", "participant")


class DirectMessage(models.Model):
    conversation = models.ForeignKey(
        PrivateConversation,
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipient"
    )
    content = models.TextField(
        blank=False,
        null=False
    )
    is_read = models.BooleanField(
        blank=False,
        null=False,
        default=False
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )