from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Group, GroupMember, Doubt, DoubtReply # added doubt & doubtreply at "line 28"
from accounts.serializers import UserSerializer



class GroupSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_by', 'created_at', 'members_count']

    def get_members_count(self, obj):
        return GroupMember.objects.filter(group=obj).count()


class GroupMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GroupMember
        fields = ['id', 'group', 'user', 'joined_at']


class DoubtReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoubtReply
        fields = ['id', 'user', 'text', 'is_solution', 'created_at']


class DoubtSerializer(serializers.ModelSerializer):
    asked_by = UserSerializer(read_only=True)
    directed_to = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    replies = DoubtReplySerializer(many=True, read_only=True)

    class Meta:
        model = Doubt
        fields = [
            'id',
            'title',
            'body',
            'group',
            'asked_by',
            'directed_to',
            'status',
            'created_at',
            'replies',
        ]

