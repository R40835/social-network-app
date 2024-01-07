from django.urls import path
from users import views

app_name = "users"

urlpatterns = [
    path("sign-up/", views.sign_up, name="sign-up"),
    path("sign-in/", views.sign_in, name="sign-in"),
    path("sign-out/", views.sign_out, name="sign-out"),
    path("home/", views.home, name="home"),
    path("search-users/", views.search_user, name="search-user"),
    path("delete-account/", views.delete_user, name="delete-account"),
    path("edit-account/", views.edit_account, name="edit-account"),
    path("profile-photos/<user_id>/", views.photos, name="photos"),
    path("apply-profile-photo/<photo_id>/", views.apply_photo, name="apply-photo"),
    path('delete_photo/<photo_id>/', views.delete_photo, name='delete-photo'),
    path('password/', views.PasswordsChangeView.as_view(template_name='users/change_password.html'), name='change-password'),
    path("user-posts/<user_id>/", views.user_posts, name="user-posts"),
]