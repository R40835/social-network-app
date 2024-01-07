from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def call_duration_format(time):
    hours, remainder = divmod(time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '{:02}:{:02}:{:02}'.format(hours, minutes, seconds)

