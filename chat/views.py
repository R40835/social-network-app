from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator

from .forms import RoomForm
from .models import Room, RoomMessage, DirectMessage, PrivateConversation
from users.models import User


@login_required
def create_room(request):
    """
    Creating a room.
    """
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.user = request.user  # room owner
            room.members = [request.user.id]
            room.readers = [request.user.id]
            room.save()
            room_id = room.pk

            return HttpResponseRedirect(reverse("chat:room", args=[room_id]))
    else:
        form = RoomForm()

    context = {
        "form": form
    }
    return render(request, "chat/create_room.html", context)


@login_required
def room(request, room_id):
    """
    Room view.
    """
    curr_room = Room.objects.get(pk=room_id)
    user_id = request.user.id

    # Add user as a member and reader if they join the room
    if not str(user_id) in curr_room.members:
        curr_room.members.append(user_id)
        curr_room.readers.append(user_id)
        curr_room.save()
    try:
        messages = RoomMessage.objects.filter(room=curr_room).order_by('-timestamp')
        if not str(user_id) in curr_room.readers: # readers are identified with their PKs
            curr_room.readers.append(user_id)
            curr_room.save()
        paginator = Paginator(messages, 10) 
        page_number = request.GET.get('page')
        last_messages = paginator.get_page(page_number)
        
        try:
            user_is_last_sender = messages[0].user_id == user_id
        except IndexError:
            user_is_last_sender = None
    except RoomMessage.DoesNotExist:
        messages = None
        user_is_last_sender = None

    context = {
        "room": curr_room,
        "room_id": room_id,
        "messages": last_messages,
        "user_is_last_sender": user_is_last_sender
    }
    return render(request, "chat/room.html", context)


@login_required
def direct_message(request, user_id):
    """
    Direct Message view.
    """
    participant1 = request.user
    participant2 = User.objects.get(pk=user_id)
    if participant1 == participant2:
        raise ValueError("Can't send a message to yourself.")
    try:
        conversation = PrivateConversation.objects.get(
            Q(user=participant1) & Q(participant=participant2) | 
            Q(user=participant2) & Q(participant=participant1)
        )
        messages = DirectMessage.objects.filter(
            Q(sender=participant1) & Q(conversation_id=conversation.id) | 
            Q(sender=participant2) & Q(conversation_id=conversation.id)
        ).order_by('-timestamp')

        if participant1 == messages[0].recipient:
            messages.update(is_read=True)

        paginator = Paginator(messages, 10) 
        page_number = request.GET.get('page')
        last_messages = paginator.get_page(page_number)

        try:
            user_is_last_sender = messages[0].sender_id == participant1.id
        except IndexError:
            user_is_last_sender = None
    except PrivateConversation.DoesNotExist:
        last_messages = None
        user_is_last_sender = None

    context = {
        "user_id": user_id,
        "messages": last_messages,
        "participant": participant2,
        "user_is_last_sender": user_is_last_sender
    }
    return render(request, "chat/direct_message.html", context)


@login_required
def get_rooms(request):
    """
    Public Rooms where current user isn't a member.
    """
    user = request.user
    rooms = Room.objects.exclude(
        members__contains=[user.pk]
    ).order_by("-latest_message_timestamp")

    items_per_page = 5
    paginator = Paginator(rooms, items_per_page) 
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)

    context = {
        "rooms": rooms
    }
    return render(request, "chat/rooms.html", context)


@login_required
def get_member(request, member_id):
    """
    Getting a user name based on their PK.
    """
    member = User.objects.get(pk=member_id)
    member_name = f"{member.first_name} {member.last_name}"
    member_profile_photo = f"{member.profile_photo.url}" if member.profile_photo else "/media/app/default-user.png"
    return JsonResponse({"member_name": member_name, "member_profile_photo": member_profile_photo})


@login_required
def get_conversations(request):
    """
    Getting all direct messages for current user.
    """
    sender = request.user
    conversations = PrivateConversation.objects.filter(
        Q(user=sender) | Q(participant=sender) 
    ).order_by('latest_message_timestamp').prefetch_related('directmessage_set')[::-1]
    paginator = Paginator(conversations, 5) 
    page_number = request.GET.get('page')
    conversations = paginator.get_page(page_number)

    context = {
        "conversations": conversations,
    }
    return render(request, "chat/conversations.html", context)


@login_required 
def get_user_rooms(request): 
    """
    Rooms where current user is a member.
    """
    user = request.user
    rooms = Room.objects.filter(
        members__contains=[user.pk]
    ).order_by('latest_message_timestamp').prefetch_related('roommessage_set')[::-1]

    items_per_page = 5
    paginator = Paginator(rooms, items_per_page) 
    page_number = request.GET.get('page')
    rooms = paginator.get_page(page_number)

    user_id = str(user.pk)
    context = {
        "rooms": rooms,
        "user_id": user_id
    }
    return render(request, "chat/user_rooms.html", context)


@login_required
def leave_room(request, room_id):
    """
    Leaving or deleting the room depends on whether the current 
    user is a normal member or the room owner, respectively.
    """
    user = request.user
    room =  Room.objects.get(pk=room_id)
    # user is an owner
    if room.user.pk == user.pk:
        room.delete()
        return HttpResponseRedirect(reverse("chat:rooms"))
    # user is a regular member
    else:
        member_id = str(user.pk)
        room.members.remove(member_id)
        room.save()
        return HttpResponseRedirect(reverse("chat:user-rooms"))
