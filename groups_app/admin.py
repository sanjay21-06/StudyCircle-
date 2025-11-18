from django.contrib import admin
from .models import Group, GroupMember, Doubt, DoubtReply


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'joined_at')


@admin.register(Doubt)
class DoubtAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'asked_by', 'directed_to', 'status', 'created_at')
    list_filter = ('status', 'group')


@admin.register(DoubtReply)
class DoubtReplyAdmin(admin.ModelAdmin):
    list_display = ('doubt', 'user', 'is_solution', 'created_at')
    list_filter = ('is_solution',)
