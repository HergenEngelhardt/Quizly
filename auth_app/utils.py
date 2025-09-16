"""
Utility functions for authentication app.
"""

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import login
from quiz_app.models import BlacklistedToken


def get_tokens_for_user(user):
    """Generate JWT tokens for user."""
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def _set_access_token_cookie(response, token):
    """Set access token cookie."""
    response.set_cookie(
        "access_token",
        token,
        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )


def _set_refresh_token_cookie(response, token):
    """Set refresh token cookie."""
    response.set_cookie(
        "refresh_token",
        token,
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
    )


def set_jwt_cookies(response, tokens):
    """Set JWT tokens as HTTP-only cookies."""
    _set_access_token_cookie(response, tokens["access"])
    _set_refresh_token_cookie(response, tokens["refresh"])
    return response


def clear_jwt_cookies(response):
    """Clear JWT cookies from response."""
    response.delete_cookie(
        "access_token",
        domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
        path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
    )
    response.delete_cookie(
        "refresh_token",
        domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
        path=settings.SIMPLE_JWT["AUTH_COOKIE_PATH"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"]
    )
    return response


def blacklist_token(token):
    """Add token to blacklist."""
    try:
        BlacklistedToken.objects.create(token=token)
        return True
    except Exception:
        return False


def is_token_blacklisted(token):
    """Check if token is blacklisted."""
    return BlacklistedToken.objects.filter(token=token).exists()


def handle_user_registration(serializer):
    """Handle user registration logic."""
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"detail": "User created successfully!"}, status=status.HTTP_201_CREATED
        )
    
    # Return specific validation errors instead of generic message
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def handle_user_login(serializer, request):
    """Handle user login logic."""
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED,
        )

    user = serializer.validated_data["user"]
    login(request, user)
    tokens = get_tokens_for_user(user)

    from auth_app.api.serializers import UserSerializer

    user_data = UserSerializer(user).data

    response = Response(
        {"detail": "Login successfully!", "user": user_data},
        status=status.HTTP_200_OK,
    )
    return set_jwt_cookies(response, tokens)


def handle_user_logout(request):
    """Handle user logout logic."""
    access_token = request.COOKIES.get("access_token")
    refresh_token = request.COOKIES.get("refresh_token")

    if access_token:
        blacklist_token(access_token)
    if refresh_token:
        blacklist_token(refresh_token)

    response = Response(
        {
            "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
        },
        status=status.HTTP_200_OK,
    )
    return clear_jwt_cookies(response)


def handle_token_refresh(request):
    """Handle token refresh logic."""
    refresh_token = request.COOKIES.get("refresh_token")

    if not refresh_token:
        return Response(
            {"detail": "Refresh token invalid or missing."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Check if refresh token is blacklisted
    if is_token_blacklisted(refresh_token):
        return Response(
            {"detail": "Refresh token invalid or missing."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)

        response = Response(
            {"detail": "Token refreshed", "access": new_access_token},
            status=status.HTTP_200_OK,
        )

        _set_access_token_cookie(response, new_access_token)
        return response

    except TokenError:
        return Response(
            {"detail": "Refresh token invalid or missing."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
