from django.urls import path
from post import views

app_name = "post"

urlpatterns = [
    path('feed/', views.feed, name="feed"),
    path("create-post/", views.create_post, name="create-post"),
    path("create-comment/<post_id>", views.create_comment, name="create-comment"),
    path("like-post/<post_id>", views.like_post, name="like-post"),
    path("unlike-post/<post_id>", views.unlike_post, name="unlike-post"),
    path("edit-post/<post_id>", views.edit_post, name="edit-post"),
    path("edit-comment/<comment_id>", views.edit_comment, name="edit-comment"),
    path("post/<post_id>", views.post, name="post"),
    path("delete-post/<post_id>", views.delete_post, name="delete-post"),
    path("delete-comment/<comment_id>", views.delete_comment, name="delete-comment"),
    path("likers/<post_id>", views.likers, name="likers"),
]

