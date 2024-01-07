import json
import time

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q 

from .models import CallSession, CallNotification
from users.models import User

from agora_token_builder import RtcTokenBuilder
from django.conf import settings


@login_required
def get_app(request):
    channel_name = request.GET.get('channel_name')

    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE
    return JsonResponse({'app_id': app_id, 'app_certificate': app_certificate})


@login_required
def call_room(request, remote_user_id):
    """
    One-to-one call room.
    """
    remote_user = User.objects.get(pk=remote_user_id)
    remote_user_photo = remote_user.profile_photo

    context = {
        'remote_user_photo': remote_user_photo
    }
    return render(request, 'call/call_room.html', context)


@login_required
def calls_history(request): 
    """
    User calls history page.
    """
    user_id = request.user.id
    
    calls = CallNotification.objects.filter(
        Q(caller_id=user_id) | Q(callee_id=user_id)
    ).order_by('-timestamp')
    # missed instead of call_answered in counts!
    paginator = Paginator(calls, 5) 
    page_number = request.GET.get('page')
    calls = paginator.get_page(page_number)

    context = {
        "calls": calls
    }
    return render(request, "call/calls_history.html", context)


@login_required
def call(request, call_notification_id):
    """
    Set calls as seen after visting the calls' history page.
    """
    call = CallNotification.objects.get(
        pk=call_notification_id
    )
    call.is_seen = True
    call.save()

    context = {
        "call": call
    }
    return render(request, "call/call.html", context)


@csrf_exempt
def start_call(request):
    """
    Initiating a one-to-one call.
    """
    data = json.loads(request.body)
    callee_reachable = True

    callee = User.objects.get(pk=data['callee_id'])

    # check if the callee is on a call
    call_session = CallSession.objects.filter(
        Q(caller_id=data["callee_id"], ongoing=True) | 
        Q(callee_id=data["callee_id"], ongoing=True)
    ) 
    if call_session.exists(): 
        callee_reachable = False 

    if callee_reachable:
        call_session = CallSession.objects.create(
            caller_name=data['caller_name'],
            caller_id=data['caller_id'],
            callee_name=data['callee_name'],
            callee_id=data["callee_id"],
        )
        
        CallNotification.objects.create(
            call_session=call_session,
            caller=request.user,
            callee=callee
        )

        return JsonResponse(
                {
                    'callee_reachable': callee_reachable,
                    'caller_id': call_session.caller_id, 
                    'callee_id': call_session.callee_id, 
                    'channel_name': f'{call_session.channel_name}'
                }, 
                safe=False
            )
    else: 
        call_session = CallSession.objects.create(
            caller_name=data['caller_name'],
            caller_id=data['caller_id'],
            callee_name=data['callee_name'],
            callee_id=data["callee_id"],
            ongoing=False
        )
        call_notification = CallNotification.objects.create(
            call_session=call_session,
            caller=request.user,
            callee=callee
        )

        return JsonResponse(
            {
                'callee_reachable': callee_reachable, 
                'callee_photo': f'{call_notification.callee.profile_photo.url}' if call_notification.callee.profile_photo else None, 
                'callee_name': f'{call_notification.callee.first_name} {call_notification.callee.last_name}'
            }, 
            safe=False
        )


@login_required
def generate_token(request): 
    """
    Generating a token for the user joining the call room.
    """
    app_id = settings.AGORA_APP_ID
    app_certificate = settings.AGORA_APP_CERTIFICATE

    channel_name = request.GET.get('channel')
    user_id = request.user.id
    expiration_in_seconds = 3600
    current_timestamp = int(time.time())
    privilege_expired_in_seconds = current_timestamp + expiration_in_seconds
    role = 1

    token = RtcTokenBuilder \
    .buildTokenWithUid(
        app_id, 
        app_certificate, 
        channel_name, 
        user_id, 
        role, 
        privilege_expired_in_seconds
    )

    return JsonResponse({'token': token, 'uid': user_id}, safe=False)


@login_required
def handle_current_user_join(request):
    """
    Adding the caller to the call session.
    """ 
    user_id = request.GET.get('user_id')
    channel_name = request.GET.get('channel_name')


    call_session = CallSession.objects.get(
        channel_name=channel_name
    )
    if int(user_id) == int(call_session.caller_id):
        name = call_session.caller_name
    elif int(user_id) == int(call_session.callee_id):
        name = call_session.callee_name

    return JsonResponse({'name': name}, safe=False)


@login_required
def handle_remote_user_join(request):
    """
    Adding the callee to the call session.
    """ 
    user_id = request.GET.get('user_id')
    channel_name = request.GET.get('channel_name')

    call_session = CallSession.objects.get(channel_name=channel_name)
    call_session.call_answered = True 
    call_session.save()

    if int(user_id) == int(call_session.caller_id):
        name = call_session.caller_name
    elif int(user_id) == int(call_session.callee_id):
        name = call_session.callee_name
    return JsonResponse({'name': name}, safe=False)


@login_required
def hang_up(request):
    """
    Ending a call.
    """
    user_id = request.GET.get('user_id')
    channel_name = request.GET.get('channel_name')
    try:
        call_session = CallSession.objects.get(channel_name=channel_name)
        call_session.ongoing = False 
        call_session.save()

        call_notification = CallNotification.objects.get(call_session_id=call_session.pk)
        if call_session.call_answered:
            call_notification.set_end_time()
            call_notification.save()

    except CallSession.DoesNotExist:
        return JsonResponse({'call_status': 'Call Ended'}, safe=False)
    return JsonResponse({'call_status': 'Call Ended'}, safe=False)