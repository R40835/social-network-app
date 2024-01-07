"""
URL configuration for social_network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as password_reset_views
from users.views import sign_in
from users.forms import CustomPasswordResetForm, CustomSetPasswordForm

# imports to serve the media files
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sign_in, name="index"),
    path('users/', include('users.urls', namespace="users")),
    path('post/', include('post.urls', namespace="post")),
    path('friend/', include('friend.urls', namespace="friend")),
    path('chat/', include('chat.urls', namespace="chat")),
    path('notification/', include('notification.urls', namespace="notification")),
    path('call/', include('call.urls', namespace="call")),
    path("password-reset/", password_reset_views.PasswordResetView.as_view(
        template_name="password_reset/password_reset.html", 
        form_class=CustomPasswordResetForm), 
        name="password_reset"),
    path("password-reset/<uidb64>/<token>/", password_reset_views.PasswordResetConfirmView.as_view(
        template_name="password_reset/set_new_password.html", 
        form_class=CustomSetPasswordForm),
        name="password_reset_confirm"),
    path("password-reset-sent/", password_reset_views.PasswordResetDoneView.as_view(
        template_name="password_reset/password_reset_sent.html"), 
        name="password_reset_done"),
    path("password-reset-complete/", password_reset_views.PasswordResetCompleteView.as_view(
        template_name="password_reset/password_reset_complete.html"), 
        name="password_reset_complete"),
]

# Serving the media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += staticfiles_urlpatterns()


handler404 = 'users.views.error_404'