from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar')
    location = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    follower = models.ManyToManyField(User, related_name='following_user')
    following = models.ManyToManyField(User, related_name='followed_by_user')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE)
    comment = models.CharField(max_length=200)
    date_time = models.DateTimeField(auto_now=True)


class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_photos')
    file_name = models.ImageField(upload_to='photos')
    caption = models.CharField(max_length=2000, blank=True)
    location = models.CharField(max_length=200, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField(User, related_name='user_likes_photo')
    mentions = models.ManyToManyField(User, related_name='mentioned_by_photo')


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=200)
    content = models.JSONField()


class Tag(models.Model):
    name = models.CharField(max_length=50)
    photo = models.ManyToManyField(Photo)
