from django.db import models
from django.contrib.auth.models import User
from markupfield.fields import MarkupField


class Post(models.Model):
    """
    A blog post.
    """

    creator = models.ForeignKey(User, related_name='posts')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100)
    summary = models.TextField()
    body = MarkupField()

    tags = models.ManyToManyField('Tag', related_name='tagged_posts')


class Tag(models.Model):
    slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField()
