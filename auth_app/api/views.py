"""
Authentication views for the Quizly API.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from auth_app.utils import (
    handle_user_registration,
    handle_user_login,
    handle_user_logout,
    handle_token_refresh,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """Register a new user account."""
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        return handle_user_registration(serializer)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """Login user and create JWT tokens."""
    try:
        serializer = UserLoginSerializer(data=request.data)
        return handle_user_login(serializer, request)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout user and clear JWT tokens."""
    try:
        return handle_user_logout(request)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """Refresh access token using refresh token."""
    try:
        return handle_token_refresh(request)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
