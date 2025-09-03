"""
Simple authentication views for the Quizly API.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import login
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .utils import get_tokens_for_user, set_jwt_cookies, clear_jwt_cookies


def _handle_registration(request):
    """
    Handle user registration logic.

    Args:
        request: HTTP request with user data

    Returns:
        Response: Registration response

    Raises:
        None
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"detail": "User created successfully!"}, 
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user account.

    Args:
        request: HTTP request with username, email, and password

    Returns:
        Response: Success message or validation errors

    Raises:
        ValidationError: If user data is invalid
    """
    try:
        return _handle_registration(request)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _handle_login(request):
    """
    Handle user login logic.

    Args:
        request: HTTP request with credentials

    Returns:
        Response: Login response with user data and tokens

    Raises:
        None
    """
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"detail": "Invalid login credentials."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    
    user = serializer.validated_data["user"]
    login(request, user)
    tokens = get_tokens_for_user(user)
    user_data = UserSerializer(user).data

    response = Response(
        {"detail": "Login successfully!", "user": user_data},
        status=status.HTTP_200_OK,
    )
    return set_jwt_cookies(response, tokens)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login user and create JWT tokens.

    Args:
        request: HTTP request with username and password

    Returns:
        Response: Login success with user data and JWT cookies

    Raises:
        ValidationError: If credentials are invalid
    """
    try:
        return _handle_login(request)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user and clear JWT tokens.

    Args:
        request: HTTP request with JWT tokens in cookies

    Returns:
        Response: Logout success message with cleared cookies

    Raises:
        None
    """
    try:
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        return clear_jwt_cookies(response)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _handle_token_refresh(request):
    """
    Handle token refresh logic.

    Args:
        request: HTTP request with refresh token

    Returns:
        Response: New access token response

    Raises:
        TokenError: If refresh token is invalid
    """
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


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token using refresh token.

    Args:
        request: HTTP request with refresh token in cookies

    Returns:
        Response: New access token or error message

    Raises:
        TokenError: If refresh token is invalid
    """
    try:
        return _handle_token_refresh(request)
    except Exception:
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
