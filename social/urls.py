from django.urls import path
from .views import (
    SendFriendRequestView,
    PendingFriendRequestsView,
    RespondFriendRequestView,
    FriendsListView,
)

urlpatterns = [
    path('friends/send/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friends/requests/', PendingFriendRequestsView.as_view(), name='pending_friend_requests'),
    path('friends/requests/<int:pk>/respond/', RespondFriendRequestView.as_view(), name='respond_friend_request'),
    path('friends/', FriendsListView.as_view(), name='friends_list'),
]

#added later
from .views import (
    PostListCreateView,
    CommentCreateView,
    ReactionView,
)

urlpatterns += [
    path('posts/', PostListCreateView.as_view(), name='post_list_create'),
    path('posts/<int:post_id>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('posts/<int:post_id>/react/', ReactionView.as_view(), name='post_reaction'),
]
