from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    content = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
    
    def like_count(self):
        return Like.objects.filter(liked_post=self).count()


class Like(models.Model):
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followed_users")

    # Ensures that user follows another user no more than once
    class Meta:
        unique_together = [["follower", "followed"]]