from django.db import models
from django.contrib.auth.models import User

from post.models import Post, Like, Comment


class PostNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('Like', 'Like'),
        ('Comment', 'Comment'),
    )
    post = models.ForeignKey(
        'post.Post', 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    sender = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='notifications_received'
    )
    notification_type = models.CharField(
        max_length=10, 
        choices=NOTIFICATION_TYPES
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    is_read = models.BooleanField(
        default=False
    )

    def mark_as_read(self):
        """
        Marking post notification as read.
        """
        self.is_read = True
        self.save()

    def __str__(self):
        """
        String representation of the object.
        """
        return f"{self.sender} {self.notification_type} on {self.post}"

    class Meta:
        ordering = ['-timestamp']


class NewFriendNotification(models.Model):
    accepter = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='newfriend_notifications_received'
    )
    notification_type = models.CharField(
        blank=False,
        null=False,
        default='New-friend'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    is_read = models.BooleanField(
        default=False,
        blank=False,
        null=False
    )

    def mark_as_read(self):
        """
        Marking new friend notification as read.
        """
        self.is_read = True
        self.save()

    def __str__(self):
        """
        String representation of the object.
        """
        return f"{self.accepter} accepted {self.sender} friend request"

    class Meta:
        ordering = ['-timestamp']

