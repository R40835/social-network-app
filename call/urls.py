from django.urls import path
from . import views

app_name = 'call'

urlpatterns = [
    path('get-app/', views.get_app, name='get-app'),
    path('call-room/<int:remote_user_id>', views.call_room, name='call-room'),
    path('calls-history/', views.calls_history, name='calls-history'),
    path('call/<int:call_notification_id>/', views.call, name='call'),
    path('start-call/', views.start_call, name='start-call'),
    path('generate-token/', views.generate_token, name='generate-token'),
    path('current-user-join/', views.handle_current_user_join, name='current-user-join'),
    path('remote-user-join/', views.handle_remote_user_join, name='remote-user-join'),
    path('hang-up/', views.hang_up, name='hang-up'),
]