from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"
    

class Listing(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctioneer")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=300, null=True)
    image = models.URLField(null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="categories", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.created_by}"
    
    def highest_bid(self):
        return self.bids.order_by('-amount').first()


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.IntegerField()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment {self.content} by {self.user}"
    


class Watchlist(models.Model):
    users = models.ManyToManyField(User)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)


class Winner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="winner", null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user} winner of {self.listing.title}"
    