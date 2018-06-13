from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Story(models.Model):
    title = models.CharField(max_length=100)
    public = models.BooleanField(default=False)
    available = models.BooleanField(default=False)
    writers = models.ManyToManyField(User, through='StoryWriter')


class Snippet(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=False)
    text = models.TextField(max_length=1000)


class StoryWriter(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
