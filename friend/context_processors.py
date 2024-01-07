from .models import Friendship, FriendRequest
from django.db.models import Q 


def user_friends(request):
    """
    Getting the current user's friends.
    """
    user = request.user 
    if user.is_authenticated:
        try:
            friends =  Friendship.objects.filter(
                user_id=user.id
            )
            return {"user_friendships": friends}
        except Friendship.DoesNotExist:
            return {"user_friendships": 0}
    else:
        return {"user_friendships": 0}
    

def friend_request_count(request):
    """
    Getting the current user's friend requests count.
    """
    user = request.user
    if user.is_authenticated:
        try:
            friend_requests = FriendRequest.objects.filter(
                Q(recipient_id=user.id) & Q(is_read=False)
            ).count()
            return {"friend_request_count": friend_requests}
        except FriendRequest.DoesNotExist:
            return {"friend_request_count": 0}
    else:
        return {"friend_request_count": 0}