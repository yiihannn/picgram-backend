from django.db import models
from django.contrib.auth.models import User
from graphql_relay import to_global_id


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatar')
    location = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    follower = models.ManyToManyField(User, related_name='following_user')
    following = models.ManyToManyField(User, related_name='followed_by_user')

    def username(self):
        return self.user.username

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def global_id(self):
        return to_global_id('UserNode', self.id)


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

    def photo_tags(self):
        return [tag.name for tag in self.tag_set.all()]

    def photo_comments(self):
        return [cmt.comment for cmt in self.comment_set.all()]

    def photo_url(self):
        return self.file_name.url

    def global_id(self):
        return to_global_id('PhotoNode', self.id)


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=200)
    content = models.JSONField()


class Tag(models.Model):
    name = models.CharField(max_length=50)
    photo = models.ManyToManyField(Photo)
