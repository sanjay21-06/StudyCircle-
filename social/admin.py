from django.contrib import admin
from .models import FriendRequest, Post, Comment, PostInteraction

admin.site.register([FriendRequest, Post, Comment, PostInteraction])

