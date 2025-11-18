from django.urls import path

from .views import (
    GroupListCreateView,
    UserGroupsView,
    JoinGroupView,
    LeaveGroupView,
    DoubtListCreateView,
    MyAssignedDoubtsView,
    DoubtReplyCreateView,
    MarkSolutionView,
)


urlpatterns = [
    path('groups/', GroupListCreateView.as_view(), name='group_list_create'),
    path('groups/my/', UserGroupsView.as_view(), name='user_groups'),
    path('groups/<int:group_id>/join/', JoinGroupView.as_view(), name='join_group'),
    path('groups/<int:group_id>/leave/', LeaveGroupView.as_view(), name='leave_group'),

    # Doubts
    path('doubts/', DoubtListCreateView.as_view(), name='doubt_list_create'),
    path('doubts/assigned/', MyAssignedDoubtsView.as_view(), name='my_assigned_doubts'),
    path('doubts/<int:doubt_id>/reply/', DoubtReplyCreateView.as_view(), name='doubt_reply'),
    path('doubts/<int:doubt_id>/solution/', MarkSolutionView.as_view(), name='mark_solution'),
]
