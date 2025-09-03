"""
Utility functions for authentication.
"""

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from quiz_app.models import BlacklistedToken


def get_tokens_for_user(user):
    """
    Generate JWT tokens for user.
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_jwt_cookies(response, tokens):
    """
    Set JWT tokens as HTTP-only cookies.
    """
    access_token = tokens["access"]
    refresh_token = tokens["refresh"]

    # Set access token cookie
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )

    # Set refresh token cookie
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )

    return response


def clear_jwt_cookies(response):
    """
    Clear JWT cookies from response.
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


def blacklist_token(token):
    """
    Add token to blacklist.
    """
    try:
        BlacklistedToken.objects.create(token=str(token))
        return True
    except Exception:
        return False


def is_token_blacklisted(token):
    """
    Check if token is blacklisted.
    """
    return BlacklistedToken.objects.filter(token=str(token)).exists()
