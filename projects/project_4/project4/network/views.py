import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Post, Like, Follower


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj,
        "paginator": paginator,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def new_post(request):
    if request.method == "POST":
        user = request.user
        content = request.POST.get("content")

        if content:
            Post.objects.create(created_by=user, content=content)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/new_post.html", {
                "message": "Post content required"
            })
        
    return render(request, "network/new_post.html")


def profile_page(request, username):

    # Take user profile information
    user = User.objects.get(username=username)
    followers = user.followers.all()
    followed = user.followed_users.all()
    user_posts = Post.objects.filter(created_by=user.id)

    # Showing follow/unfollow button depends on user
    flag = False
    if request.user.username != username and request.user.is_authenticated:
        flag = True
    
    # Checking relationship for initial button state
    is_following = False
    if request.user.is_authenticated:
        following_relationship = Follower.objects.filter(follower=request.user, followed=user)
        is_following = following_relationship.exists()

    post_list = user_posts
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile_page.html", {
        "user": user,
        "followers": followers.count(),
        "followed": followed.count(),
        "flag": flag,
        "is_following": is_following,
        "page_obj": page_obj,
        "paginator": paginator
    })


@csrf_exempt
@login_required
def follow_unfollow(request, profile_user_id):
    if request.method == 'POST':
        # Take information about user and profile user
        user = User.objects.get(id=request.user.id)
        profile_user = User.objects.get(id=profile_user_id)
        relationship = Follower.objects.filter(follower=user, followed=profile_user)

        if relationship.exists():
            relationship.delete()
            return JsonResponse({"message":"unfollowed"})
        else:
            Follower.objects.create(follower=user, followed=profile_user)
            return JsonResponse({"message":"followed"})


@csrf_exempt
def follow_unfollow_count(request, profile_user_id):
    user = User.objects.get(id=profile_user_id)
    followers = user.followers.all()
    followed = user.followed_users.all()
    return JsonResponse({
            "followers_count":f"{followers.count()}",
            "followed_count": f"{followed.count()}"
        })


@login_required
def following(request):

    # Completed with help of ddb

    # filter followers to current user
    followed_users = Follower.objects.filter(follower=request.user).values_list('followed', flat=True)

    # Take the posts by filtered users using __in method
    posts = Post.objects.filter(created_by__in=followed_users)
    return render(request, "network/following.html", {
        "posts": posts,
    })


@csrf_exempt
@login_required
def edit_post(request):
    if request.method == "PUT":

        # Take information about updated post
        data = json.loads(request.body)

        # Udpate post
        try:
            post_id = data['post_id']
            updated_content = data['updated_content']
        except KeyError:
            return JsonResponse({"message": "Required data not provided"}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Requested post not exist"}, status=404)
        
        if post.created_by != request.user:
            return JsonResponse({"message": "You can't edit current Post"}, status=400)
        
        if post.content != data["updated_content"]:
            post.content = updated_content
            post.save()
        else:
            return JsonResponse({"message": "Post content not changed"}, status=400)

        return JsonResponse({"message": "Post updated"}, status=200)


@csrf_exempt
@login_required
def like_unlike(request):
    if request.method == "POST":
        
        # Take information about liked post
        data = json.loads(request.body)

        # Validation
        try:
            post_id = data['post_id']
        except KeyError:
            return JsonResponse({"message": "Required data not provided"}, status=400)
        
        post = Post.objects.get(id=post_id)
        liked_post = Like.objects.filter(liked_by=request.user, liked_post=post)

        # Like/Unlike
        if not liked_post.exists():
            Like.objects.create(liked_by=request.user, liked_post=post)
            return JsonResponse({'message': "Liked"}, status=200)
        else:
            liked_post.delete()
            return JsonResponse({'message': "Unliked"}, status=200)
        
            
        
