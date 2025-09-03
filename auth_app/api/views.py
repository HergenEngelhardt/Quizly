"""
Authentication views for Quizly API.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import login
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .utils import (
    get_tokens_for_user,
    set_jwt_cookies,
    clear_jwt_cookies,
    blacklist_token,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user.
    """
    try:
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user and set JWT cookies.
    """
    try:
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)

            tokens = get_tokens_for_user(user)
            user_data = UserSerializer(user).data

            response = Response(
                {"detail": "Login successfully!", "user": user_data},
                status=status.HTTP_200_OK,
            )

            return set_jwt_cookies(response, tokens)

        return Response(
            {"detail": "Invalid login credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user and blacklist tokens.
    """
    try:
        # Get tokens from cookies
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")

        # Blacklist tokens if they exist
        if access_token:
            blacklist_token(access_token)
        if refresh_token:
            blacklist_token(refresh_token)

        response = Response(
            {
                "detail": "Log-Out successfully! All Tokens will be deleted. "
                "Refresh token is now invalid."
            },
            status=status.HTTP_200_OK,
        )

        return clear_jwt_cookies(response)

    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token using refresh token.
    """
    try:
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            response = Response(
                {"detail": "Token refreshed", "access": new_access_token},
                status=status.HTTP_200_OK,
            )

            # Set new access token cookie
            response.set_cookie(
                "access_token",
                new_access_token,
                httponly=True,
                secure=not request.get_host().startswith("localhost"),
                samesite="Lax",
            )

            return response

        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
