from rest_framework import serializers
from django.contrib.auth.models import User

from .models import FriendRequest
from accounts.serializers import UserSerializer

from .models import Post, Comment, PostInteraction      # added for line 18

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    interactions_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'group', 'group_name', 'content',
            'post_type', 'image', 'created_at', 'comments', 'interactions_count'
        ]

    def get_interactions_count(self, obj):
        return obj.interactions.count()

