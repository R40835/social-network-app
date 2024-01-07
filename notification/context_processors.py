from .models import PostNotification, NewFriendNotification
from chat.models import DirectMessage, RoomMessage, Room
from call.models import CallNotification
from django.db.models import Q, F, Exists


def unread_notification_count(request):
    """
    Getting the current user's unread post notifications count.
    """
    user = request.user 
    if user.is_authenticated:
        unread_count =  PostNotification.objects.filter(
                Q(is_read=False) & Q(recipient=user.id)
            ).count()
        return {"unread_notification_count": unread_count}
    else:
        return {"unread_notification_count": 0}
    

def unread_newfriend_count(request):
    """
    Getting the current user's unread friend-request approval notifications count.
    """
    user = request.user 
    if user.is_authenticated:
        unread_count =  NewFriendNotification.objects.filter(
                Q(is_read=False) & Q(sender_id=user.id)
            ).count()
        return {"unread_newfriend_count": unread_count}
    else:
        return {"unread_newfriend_count": 0}
    

def unread_message_count(request):
    """
    Getting the current user's unread DM notifications count.
    """
    user = request.user 
    if user.is_authenticated:
        unread_count =  DirectMessage.objects.filter(
                Q(is_read=False) & Q(recipient=user.id)
            ).count()
        return {"unread_message_count": unread_count}
    else:
        return {"unread_message_count": 0}
    

def unread_group_message_count(request):
    """
    Getting the current user's unread group message notifications count.
    """
    user = request.user 
    if user.is_authenticated:
        # user rooms
        user_rooms = Room.objects.filter(
            members__contains=[
                str(user.pk)
            ]
        )
        # rooms where user didn't read the message
        user_rooms = user_rooms.exclude(
            readers__contains=[
                str(user.pk)
            ]
        )
        # rooms that have messages
        unread_count = user_rooms.annotate(
            has_messages=Exists(
                RoomMessage.objects.filter(
                    room=F('pk')
                )
            )
        ).count()
        return {"unread_group_message_count": unread_count}
    else:
        return {"unread__group_message_count": 0}
    

def missed_calls_count(request):
    """
    Getting the current user's missed calls count.
    """
    user = request.user
    if user.is_authenticated:
        try:
            missed_calls = CallNotification.objects.filter(
                callee_id=user.id, 
                call_session__call_answered=False,
                call_session__ongoing=False,
                is_seen=False
            ).count()
            return {"missed_calls_count": missed_calls}
        except CallNotification.DoesNotExist:
            return {"missed_calls_count": 0}
    else:
        return {"missed_calls_count": 0} 