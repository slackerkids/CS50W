
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profile_page/<str:username>", views.profile_page, name="profile_page"),
    path("follow_unfollow/<int:profile_user_id>", views.follow_unfollow, name="follow_unfollow"),
    path("follow_unfollow_count/<int:profile_user_id>", views.follow_unfollow_count, name="follow_unfollow_count"),
    path("following", views.following, name="following"),
    path("edit_post", views.edit_post, name="edit_post"),
    path("like_unlike", views.like_unlike, name="like_inlike"),
]
