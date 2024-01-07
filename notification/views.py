from django.shortcuts import render
from django.db.models import Q, F, Exists, Count
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import PostNotification, NewFriendNotification
from post.models import Post, Comment
from chat.models import DirectMessage, RoomMessage, Room
from friend.models import Friendship
from users.models import User
from call.models import CallNotification

from operator import attrgetter
from itertools import chain


@login_required
def notifications(request):
    """
    Getting all notifications for current user (view).
    """
    user = request.user
    post_notifications = PostNotification.objects.filter(recipient=user)
    new_friend_notifications = NewFriendNotification.objects.filter(sender=user)

    notifications = sorted(
        chain(post_notifications, new_friend_notifications),
        key=attrgetter('timestamp'),
        reverse=True
    )

    items_per_page = 8
    paginator = Paginator(notifications, items_per_page)
    page_number = request.GET.get('page')
    page_data = paginator.get_page(page_number)

    context = {
        'page': page_data,
    }

    return render(request, 'notification/notifications.html', context)


@login_required
def view_post_notification(request, post_id):
    """
    Redirecting the user to a specific post from the notification view, 
    and marking the notification as read.
    """
    post = Post.objects.get(pk=post_id)
    notifications = PostNotification.objects.filter(post_id=post_id)
    notifications.update(is_read=True)
    comments = Comment.objects.filter(post_id=post.id)

    context = {
        'post': post,
        'comments': comments
    }
    return render(request, "post/post.html", context)


@login_required
def view_friend_notification(request, user_id, accepter_id):
    """
    Redirecting the user to their friends' list from the notification 
    view, when clicking on the friend-request-accepted notification.
    """
    notification = NewFriendNotification.objects.filter(
        sender_id=user_id,
        accepter_id=accepter_id
    )
    notification.update(is_read=True)

    user = User.objects.get(pk=user_id)
    friends = Friendship.objects.filter(
        user_id=user_id
    )

    items_per_page = 10
    paginator = Paginator(friends, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "user": user,
        "page": page,
    }
    return render(request, "friend/friends.html", context)


@login_required
def unread_notifications(request):
    """
    Getting the current user's unread post, and new friend notifications count.
    """
    if request.user.is_authenticated:

        unread_count =  PostNotification.objects.filter(
            Q(is_read=False) & Q(recipient=request.user.id)
        ).count()

        unread_newfriend_count =  NewFriendNotification.objects.filter(
            Q(is_read=False) & Q(sender_id=request.user.id)
        ).count()

        return JsonResponse(
            {
                "unread_notification_count": unread_count,
                "unread_newfriend_count": unread_newfriend_count
            }
        )
    return JsonResponse({"unread_notification_count": 0})


@login_required
def unread_messages(request):
    """
    Getting the current user's unread DM notifications count.
    """
    user = request.user
    if user.is_authenticated:

        unread_count = DirectMessage.objects.filter(
            Q(is_read=False) & Q(recipient_id=user.id)
        ).values('sender_id').annotate(unread_count=Count('sender_id')).count()


        return JsonResponse({"unread_message_count": unread_count})
    return JsonResponse({"unread_message_count": 0})


@login_required
def unread_group_messages(request):
    """
    Getting the current user's unread group message notifications count.
    """
    user = request.user 
    if user.is_authenticated:
        # User rooms
        user_rooms = Room.objects.filter(
            members__contains=[
                str(user.pk)
            ]
        )
        # Rooms where user didn't read the message
        user_rooms = user_rooms.exclude(
            readers__contains=[
                str(user.pk)
            ]
        )
        # Rooms that have messages
        unread_count = user_rooms.annotate(
            has_messages=Exists(
                RoomMessage.objects.filter(
                    room=F('pk')
                )
            )
        ).count()
        return JsonResponse({"unread_group_message_count": unread_count})
    return JsonResponse({"unread_group_message_count": 0})


@login_required
def missed_calls(request):
    """
    Getting the current user's missed calls count.
    """
    user = request.user
    if user.is_authenticated:

        calls_count =  CallNotification.objects.filter(
            Q(callee_id=user.pk) & Q(call_session__call_answered=False) & 
            Q(is_seen=False) & Q(call_session__ongoing=False)
        ).count()

        return JsonResponse({"missed_calls_count": calls_count})
    return JsonResponse({"missed_calls_count": 0})
