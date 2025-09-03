"""
Simple utility functions for JWT authentication.
"""

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


def get_tokens_for_user(user):
    """
    Create JWT tokens for a user.

    Args:
        user: Django user object

    Returns:
        dict: Dictionary with access and refresh tokens

    Raises:
        None
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def set_jwt_cookies(response, tokens):
    """
    Add JWT tokens to HTTP response as cookies.

    Args:
        response: Django HTTP response object
        tokens (dict): Dictionary with access and refresh tokens

    Returns:
        HttpResponse: Response with JWT cookies set

    Raises:
        None
    """
    access_token = tokens["access"]
    refresh_token = tokens["refresh"]

    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=not settings.DEBUG,
        samesite="Lax",
    )

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
    Remove JWT cookies from HTTP response.

    Args:
        response: Django HTTP response object

    Returns:
        HttpResponse: Response with cleared JWT cookies

    Raises:
        None
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
