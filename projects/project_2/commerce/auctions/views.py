from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Listing, Bid, Comment, Category, Watchlist, Winner
from .forms import ListingForm, CommentForm


def index(request):

    # winners = Winner.objects.all()
    # listings = Listing.objects.all()

    # listing_items = []
    # for listing in listings:
    #     if winners:
    #         for winner in winners:
    #             if listing.id != winner.listing.id:
    #                 listing_items.append(listing)
    #     else:
    #         listing_items.append(listing)


    # Simplified with help of ddb 
    listing_items = Listing.objects.exclude(winner__isnull=False)


    return render(request, "auctions/index.html", {
        "listing_items": listing_items,
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            # Checking optional fields
            description = form.cleaned_data["description"] if "description" in form.cleaned_data else None
            image = form.cleaned_data["image"] if "image" in form.cleaned_data else None
            category_id = form.cleaned_data["category"] if "category" in form.cleaned_data else None
            category = Category.objects.get(id=category_id) if category_id else None

            # Add new listing
            listing = Listing(
                created_by = request.user,
                title = form.cleaned_data["title"],
                description = description,
                image = image,
                category = category,
            )
            listing.save()

            bid = Bid(
                user = request.user,
                listing = listing,
                amount = form.cleaned_data["bid"]
            )
            bid.save()

            # Return to Active listing page
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create_listing.html", {
        "form": ListingForm()
    })


def listing_page(request, listing_id):
    # Fetch chosen listing from database and pass to Template
    listing_item = Listing.objects.get(pk=listing_id)

    # Check watchlist to change state of the button
    if request.user.is_authenticated:
        exists_on_watchlist = Watchlist.objects.filter(users=request.user, listing=listing_item).exists()
    else:
        exists_on_watchlist = False

    try:
        winner = Winner.objects.get(listing=listing_item)
    except ObjectDoesNotExist:
        winner = None

    if winner and request.user == winner.user:
        messages.info(request, f"{winner.user} winner of auction")
    elif winner:
        messages.info(request, "Current listing no longer available")

    return render(request, "auctions/listing_page.html", {
        "listing_item": listing_item,
        "exists_on_watchlist": exists_on_watchlist,
        "winner": winner,
        "form": CommentForm(),
        "comments": Comment.objects.all().order_by("-timestamp"),
    })


@login_required
def watchlist(request):
    # Retrieve all Watchlist objects for the current user
    watchlist_objects = Watchlist.objects.filter(users=request.user)
    
    # Create an empty list to store the listing objects
    watchlist_listings = []
    
    # Loop through each Watchlist object and extract the listing
    for watchlist_obj in watchlist_objects:
        listing_obj = watchlist_obj.listing
        watchlist_listings.append(listing_obj)
    
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_listings
    })


@login_required
def change_watchlist(request, listing_id):
    if request.method == "POST":
        
        existing_watchlist = Watchlist.objects.filter(users=request.user, listing=Listing.objects.get(pk=listing_id))
        
        # If user have item in watchlist, delete item. Otwerwise create
        if existing_watchlist:
            existing_watchlist.delete()
            messages.success(request, "Deleted from watchlist")
        else:
            # Create new watclist object then add to watchlist current user
            watchlist = Watchlist.objects.create(listing=Listing.objects.get(pk=listing_id))
            watchlist.users.add(request.user)
            messages.success(request, "Added to watchlist")

    # Redirects to current listing
    return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))


@login_required
def place_bid(request, listing_id):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(pk=listing_id)
        latest_bid = listing.highest_bid()

        # Backend validation of bid form
        try:
            bid_amount = int(request.POST["amount"])
        except ValueError:
            messages.warning(request, "Input must be a number")
            return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))

        if bid_amount <= int(latest_bid.amount):
            messages.warning(request, "Bid must be higher than current amount")
        else:
            Bid.objects.create(user=user, listing=listing, amount=bid_amount)
            messages.success(request, "Bid added")
    
    return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))


@login_required
def close_auction(request, listing_id):

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)

        # User validation
        if listing.created_by != request.user:
            messages.warning(request, "Auction can be closed by creator")
            HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))
        else:
            bid = listing.highest_bid()
            Winner.objects.create(user=bid.user, listing=Listing.objects.get(pk=listing_id))

    return HttpResponseRedirect(reverse("index"))


@login_required
def add_comment(request, listing_id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]

            comment = Comment(
                user = request.user,
                listing = Listing.objects.get(pk=listing_id),
                content = content,
            )
            comment.save()
    
    return HttpResponseRedirect(reverse("listing_page", args=(listing_id,)))


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
    })


def category(request, name):

    listing_items = Listing.objects.filter(category__name=name).exclude(winner__isnull=False)

    return render(request, "auctions/category.html", {
        "listing_items": listing_items,
        "category_name": name
    })