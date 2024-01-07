from django.db import models


class FriendRequest(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="user_friend_request"
    )
    recipient = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="recipient_friend_request"
    )
    status = models.CharField(
        max_length=10, 
        default='pending'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    is_read = models.BooleanField(
        blank=False,
        null=False,
        default=False,
    )

    class Meta:
        
        unique_together = ("user", "recipient")


class Friendship(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="user_friendship"
    )
    friend = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="friend_friendship"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        
        unique_together = ("user", "friend")
