from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import FriendRequest
from .serializers import FriendRequestSerializer
from accounts.serializers import UserSerializer

from .models import Post, Comment, PostInteraction          # added for line 156
from .serializers import PostSerializer, CommentSerializer

class SendFriendRequestView(APIView):
    """
    Send a friend request to another user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')

        if not receiver_id:
            return Response(
                {"detail": "receiver_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if str(request.user.id) == str(receiver_id):
            return Response(
                {"detail": "You cannot send a friend request to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Receiver user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if a pending or accepted request already exists
        existing = FriendRequest.objects.filter(
            sender=request.user,
            receiver=receiver,
        ).exclude(status='rejected').first()

        if existing:
            return Response(
                {"detail": "Friend request already sent or already friends."},
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_request = FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver
        )

        return Response(
            {
                "message": "Friend request sent.",
                "request": FriendRequestSerializer(friend_request).data
            },
            status=status.HTTP_201_CREATED
        )


class PendingFriendRequestsView(APIView):
    """
    List all pending friend requests received by the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = FriendRequest.objects.filter(
            receiver=request.user,
            status='pending'
        ).order_by('-created_at')

        serializer = FriendRequestSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RespondFriendRequestView(APIView):
    """
    Accept or reject a friend request.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        action = request.data.get('action')  # 'accept' or 'reject'

        try:
            fr = FriendRequest.objects.get(id=pk, receiver=request.user)
        except FriendRequest.DoesNotExist:
            return Response(
                {"detail": "Friend request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if action not in ['accept', 'reject']:
            return Response(
                {"detail": "Invalid action. Use 'accept' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == 'accept':
            fr.status = 'accepted'
        else:
            fr.status = 'rejected'

        fr.save()

        return Response(
            {
                "message": f"Friend request {action}ed.",
                "request": FriendRequestSerializer(fr).data
            },
            status=status.HTTP_200_OK
        )


class FriendsListView(APIView):
    """
    List all friends of the logged-in user.
    We consider any accepted FriendRequest as a friendship.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Requests where current user is the sender
        sent = FriendRequest.objects.filter(
            sender=request.user,
            status='accepted'
        )

        # Requests where current user is the receiver
        received = FriendRequest.objects.filter(
            receiver=request.user,
            status='accepted'
        )

        friend_users = set()

        for fr in sent:
            friend_users.add(fr.receiver)

        for fr in received:
            friend_users.add(fr.sender)

        serializer = UserSerializer(friend_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostListCreateView(APIView):
    """
    GET: list all posts
    POST: create a new post
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        content = request.data.get('content')
        post_type = request.data.get('post_type', 'question')
        group_id = request.data.get('group_id', None)
        image = request.FILES.get('image', None)

        if not content:
            return Response({"detail": "Content is required."}, status=400)

        group = None
        if group_id:
            from groups_app.models import Group
            try:
                group = Group.objects.get(id=group_id)
            except Group.DoesNotExist:
                return Response({"detail": "Invalid group ID."}, status=404)

        post = Post.objects.create(
            author=request.user,
            content=content,
            post_type=post_type,
            group=group,
            image=image
        )

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentCreateView(APIView):
    """
    POST: Add comment to a post
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        text = request.data.get('text')
        if not text:
            return Response({"detail": "Comment text required"}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"}, status=404)

        comment = Comment.objects.create(post=post, user=request.user, text=text)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReactionView(APIView):
    """
    POST: React to a post (helpful / not_clear)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        reaction = request.data.get('reaction')

        if reaction not in ['helpful', 'not_clear']:
            return Response({"detail": "Invalid reaction type."}, status=400)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"}, status=404)

        existing = PostInteraction.objects.filter(post=post, user=request.user).first()

        if existing:
            existing.reaction = reaction
            existing.save()
            message = "Reaction updated."
        else:
            PostInteraction.objects.create(post=post, user=request.user, reaction=reaction)
            message = "Reaction added."

        return Response({"message": message}, status=200)
