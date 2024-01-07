from django import template
from ..models import Friendship, FriendRequest

register = template.Library()


@register.filter
def get_friends_with_prefetch(user, friend):
    friendships = Friendship.objects.filter(user=user).prefetch_related('friend')
    return friendships.filter(friend=friend).exists()


@register.filter
def get_sent_request_with_prefetch(sender, receiver):
    friendrequests = FriendRequest.objects.filter(user=sender).prefetch_related('user')
    return friendrequests.filter(recipient=receiver).exists()


@register.filter
def get_received_request_with_prefetch(receiver, sender):
    friendrequests = FriendRequest.objects.filter(recipient=receiver).prefetch_related('recipient')
    return friendrequests.filter(user=sender).exists()


@register.filter
def get_request_id_with_prefetch(sender, receiver):
    friendrequests = FriendRequest.objects.filter(user=sender).prefetch_related('user')
    return friendrequests.get(recipient=receiver).id
