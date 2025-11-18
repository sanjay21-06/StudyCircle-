from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User

from .models import UserProfile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
)


class RegisterView(APIView):
    """
    Handles user signup.
    """

    def get(self, request):
        # This lets the browsable API show a simple message for GET
        return Response(
            {"detail": "Send a POST request with username, email, and password to register."}
        )

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    View and update the logged-in user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get or create a profile for the logged-in user
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile_data = UserProfileSerializer(profile).data
        user_data = UserSerializer(request.user).data

        return Response(
            {
                "user": user_data,
                "profile": profile_data
            },
            status=status.HTTP_200_OK
        )

    def put(self, request):
        # Update profile fields: bio, skills, interests
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profile updated successfully",
                    "profile": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
