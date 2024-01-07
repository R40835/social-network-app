import uuid

from django.db import models
from django.utils import timezone

from users.models import User


class CallSession(models.Model):
    caller_id = models.CharField(
        max_length=255,
    )
    caller_name = models.CharField(
        max_length=255,
    )
    callee_id = models.CharField(
        max_length=255,
    )
    callee_name = models.CharField(
        max_length=255,
    )
    channel_name = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )
    call_answered = models.BooleanField(
        default=False
    )
    ongoing = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.caller_name} (ID: {self.caller_id}) is on a call with {self.callee_name} (ID: {self.callee_id})"


class CallNotification(models.Model):
    call_session = models.ForeignKey(
        CallSession,
        on_delete=models.CASCADE,
        related_name="call_session"
    )
    caller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="caller"
    )
    callee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="callee"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    start_time = models.DateTimeField(
        auto_now_add=True,
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True
    )
    call_duration = models.DurationField(
        blank=True,
        null=True
    )
    is_seen = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"caller {self.caller.id}, callee {self.callee.id}"
    
    def set_end_time(self):
        self.end_time = timezone.now()

    def calculate_call_duration(self):
        if self.end_time:
            self.call_duration = self.end_time - self.start_time
        else:
            self.call_duration = None

    def save(self, *args, **kwargs):
        self.calculate_call_duration()
        super().save(*args, **kwargs)
