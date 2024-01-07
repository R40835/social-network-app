from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q 
from django.core.paginator import Paginator

from users.models import User
from .models import Friendship, FriendRequest
from users.models import ActiveUser
from notification.models import NewFriendNotification


@login_required
def friends(request, user_id):
    """
    Getting all friends for a user based on their PK.
    """
    user = User.objects.get(pk=user_id)
    friends = Friendship.objects.filter(
        user_id=user_id
    )

    items_per_page = 9
    paginator = Paginator(friends, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "user": user,
        "page": page,
    }
    return render(request, "friend/friends.html", context)


@login_required
def send_cancel_friend_request(request, recipient_id):
    """
    Send or Cancel a friend request depending on whether 
    a friend request was sent already or not.
    """
    sender = request.user
    recipient = User.objects.get(pk=recipient_id)
    existing_request, new_request = FriendRequest.objects.get_or_create(user=sender, recipient=recipient)
    if new_request:
        return JsonResponse({"response": "added"})
    else:
        existing_request.delete()
        return JsonResponse({"response": "canceled"})


@login_required
def remove_send_cancel_friend(request, friend_id):
    """
    Remove a friend, Send, or Cancel a friend request 
    depending on concerned users relationship.
    """
    user = request.user
    friend = User.objects.get(pk=friend_id)
    try:
        existing_friend = Friendship.objects.get(
            Q(user=user) & Q(friend=friend)
        )
        stranger = False
    except Friendship.DoesNotExist:
        stranger = True
    if stranger:
        # send request
        existing_request, new_request = FriendRequest.objects.get_or_create(user=user, recipient=friend)
        if new_request:
            return JsonResponse({"response": "added"})
        else:
            existing_request.delete()
            return JsonResponse({"response": "canceled"})
    elif existing_friend:
        user.remove_friend(friend)
        return JsonResponse({"response": "removed"})
    
@login_required
def send_friend_request(request, recipient_id):
    """
    Send a friend request based on user PK.
    """
    sender = request.user
    recipient = User.objects.get(pk=recipient_id)
    FriendRequest.objects.create(
        user=sender, 
        recipient=recipient
    )
    return JsonResponse({"response": "added"})


@login_required
def cancel_friend_request(request, request_id):
    """
    Cancel a friend request based on user PK.
    """
    sender = request.user
    friend_request = FriendRequest.objects.get(
        Q(user=sender) & Q(pk=request_id)
    )
    friend_request.delete()
    return JsonResponse({"response": "canceled"})


@login_required
def decline_friend_request(request, request_id):
    """
    Decline a friend request based on user PK.
    """
    user = request.user
    friend_request = FriendRequest.objects.get(
        Q(recipient=user) & Q(pk=request_id)
    )
    friend_request.delete()
    return JsonResponse({"response": "declined"})


@login_required
def accept_friend(request, sender_id):
    """
    Accept a friend request based on user PK.
    """
    user = request.user
    # friend request sender
    new_friend = User.objects.get(pk=sender_id)
    user.accept_friend(new_friend)
    NewFriendNotification.objects.create(
        sender_id=sender_id,
        accepter_id=user.id,
    )
    return JsonResponse({"response": "accepted"})


@login_required
def remove_friend(request, friend_id):
    """
    Remove a friend based on user PK.
    """
    user = request.user
    friend = User.objects.get(pk=friend_id)
    user.remove_friend(friend)
    return JsonResponse({"response": "removed"})


@login_required
def received_friend_requests(request):
    """
    Getting all friend requests received for the current user.
    """
    user = request.user
    friend_requests = FriendRequest.objects.filter(recipient=user)
    friend_requests.update(is_read=True)

    items_per_page = 3
    paginator = Paginator(friend_requests, items_per_page)
    page_number = request.GET.get('page')
    friend_requests = paginator.get_page(page_number)

    context = {
        "friend_requests": friend_requests
    }
    return render(request, "friend/friend_requests.html", context)
    

@login_required
def online_friends_page(request):
    """
    Getting all friends online for current user (view).
    """
    user = request.user
    friends =  Friendship.objects.filter(
        user_id=user.id
    )
    # Get the user IDs from the friends list
    friend_user_ids = friends.values_list('friend_id', flat=True)

    # Filter ActiveUser instances
    online_friends = [active_user.user for active_user in ActiveUser.objects.filter(user_id__in=friend_user_ids, is_online=True)]

    items_per_page = 10
    paginator = Paginator(online_friends, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "page": page
    }
    return render(request, "friend/online_friends.html", context)


@login_required
def user_online_friends(request):
    """
    Getting all friends online for current user (data).
    """
    friend_ids = [friend.friend_id for friend in Friendship.objects.filter(user_id=request.user.id)]
    active_users = ActiveUser.objects.filter(user_id__in=friend_ids, is_online=True).select_related("user")
    active_users = {
        active_user.user.id: f"{active_user.user.first_name} {active_user.user.last_name}"  for active_user in active_users
    }
    return JsonResponse({"active_users": active_users})


@login_required
def unread_friend_requests(request):
    """
    Getting current user's friend requests count.
    """
    user = request.user
    friend_requests = FriendRequest.objects.filter(
        Q(recipient=user) & Q(is_read=False)
    ).count()
    return JsonResponse({"friend_request_count": friend_requests})
