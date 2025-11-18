from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User

from .models import Group, GroupMember, Doubt, DoubtReply #added DoubtListCreateView class before the GroupListCreateView class at "line 196"

from .serializers import GroupSerializer, GroupMemberSerializer, DoubtSerializer, DoubtReplySerializer

class DoubtListCreateView(APIView):
    """
    GET: list doubts (optionally filter by group_id)
    POST: create a new doubt in a group, optionally directed to a specific user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group_id = request.query_params.get('group_id')

        doubts = Doubt.objects.all().order_by('-created_at')
        if group_id:
            doubts = doubts.filter(group_id=group_id)

        serializer = DoubtSerializer(doubts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        group_id = request.data.get('group_id')
        title = request.data.get('title')
        body = request.data.get('body')
        directed_to_id = request.data.get('directed_to_id')

        if not group_id or not title or not body:
            return Response(
                {"detail": "group_id, title and body are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check group exists
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"detail": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check the asker is a member of the group
        if not GroupMember.objects.filter(group=group, user=request.user).exists():
            return Response(
                {"detail": "You must be a member of this group to ask a doubt."},
                status=status.HTTP_403_FORBIDDEN
            )

        directed_to = None
        if directed_to_id:
            try:
                directed_to = User.objects.get(id=directed_to_id)
            except User.DoesNotExist:
                return Response(
                    {"detail": "Target user not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Ensure directed_to is also a member of the group
            if not GroupMember.objects.filter(group=group, user=directed_to).exists():
                return Response(
                    {"detail": "Target user is not a member of this group."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        doubt = Doubt.objects.create(
            group=group,
            asked_by=request.user,
            directed_to=directed_to,
            title=title,
            body=body
        )

        serializer = DoubtSerializer(doubt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyAssignedDoubtsView(APIView):
    """
    List doubts that are directed specifically to the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doubts = Doubt.objects.filter(
            directed_to=request.user
        ).order_by('-created_at')

        serializer = DoubtSerializer(doubts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoubtReplyCreateView(APIView):
    """
    POST: add a reply to a doubt.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, doubt_id):
        text = request.data.get('text')

        if not text:
            return Response(
                {"detail": "Reply text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            doubt = Doubt.objects.get(id=doubt_id)
        except Doubt.DoesNotExist:
            return Response(
                {"detail": "Doubt not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only members of the group can reply
        if not GroupMember.objects.filter(group=doubt.group, user=request.user).exists():
            return Response(
                {"detail": "You must be a member of this group to reply."},
                status=status.HTTP_403_FORBIDDEN
            )

        reply = DoubtReply.objects.create(
            doubt=doubt,
            user=request.user,
            text=text
        )

        serializer = DoubtReplySerializer(reply)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MarkSolutionView(APIView):
    """
    POST: mark a reply as solution for a given doubt.
    Only the user who asked the doubt can mark the solution.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, doubt_id):
        reply_id = request.data.get('reply_id')

        if not reply_id:
            return Response(
                {"detail": "reply_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            doubt = Doubt.objects.get(id=doubt_id)
        except Doubt.DoesNotExist:
            return Response(
                {"detail": "Doubt not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only asker can mark solution
        if doubt.asked_by != request.user:
            return Response(
                {"detail": "Only the person who asked the doubt can mark a solution."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            reply = DoubtReply.objects.get(id=reply_id, doubt=doubt)
        except DoubtReply.DoesNotExist:
            return Response(
                {"detail": "Reply not found for this doubt."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Unmark previous solutions
        DoubtReply.objects.filter(doubt=doubt, is_solution=True).update(is_solution=False)

        reply.is_solution = True
        reply.save()

        doubt.status = 'answered'
        doubt.save()

        return Response(
            {"message": "Solution marked successfully."},
            status=status.HTTP_200_OK
        )


# before the previous classes were added
class GroupListCreateView(APIView):
    """
    GET: List all groups.
    POST: Create a new group.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        groups = Group.objects.all().order_by('-created_at')
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', '')

        if not name:
            return Response(
                {"detail": "Group name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        group = Group.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )

        # Add creator as group member
        GroupMember.objects.create(group=group, user=request.user)

        serializer = GroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserGroupsView(APIView):
    """
    List groups where the logged-in user is a member.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = GroupMember.objects.filter(user=request.user)
        groups = [m.group for m in memberships]
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JoinGroupView(APIView):
    """
    Join a group by its ID.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"detail": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if already a member
        existing = GroupMember.objects.filter(group=group, user=request.user).first()
        if existing:
            return Response(
                {"detail": "You are already a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership = GroupMember.objects.create(group=group, user=request.user)
        serializer = GroupMemberSerializer(membership)

        return Response(
            {
                "message": "Joined group successfully.",
                "membership": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class LeaveGroupView(APIView):
    """
    Leave a group by its ID.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"detail": "Group not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        membership = GroupMember.objects.filter(group=group, user=request.user).first()
        if not membership:
            return Response(
                {"detail": "You are not a member of this group."},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.delete()

        return Response(
            {"message": "Left group successfully."},
            status=status.HTTP_200_OK
        )
