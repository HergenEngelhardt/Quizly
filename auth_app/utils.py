"""
Utility functions for authentication app.
"""

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from quiz_app.models import BlacklistedToken


def get_tokens_for_user(user):
    """
    Generate JWT tokens for user.
    
    Args:
        user: Django user object
        
    Returns:
        dict: Access and refresh tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_jwt_cookies(response, tokens):
    """
    Set JWT tokens as HTTP-only cookies.
    
    Args:
        response: HTTP response object
        tokens: Dict with access and refresh tokens
        
    Returns:
        HttpResponse: The modified response object
    """
    response.set_cookie(
        'access_token',
        tokens['access'],
        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
        httponly=True,
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )
    response.set_cookie(
        'refresh_token',
        tokens['refresh'],
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        httponly=True,
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )
    return response


def clear_jwt_cookies(response):
    """
    Clear JWT cookies from response.
    
    Args:
        response: HTTP response object
        
    Returns:
        HttpResponse: The modified response object
    """
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


def blacklist_token(token):
    """
    Add token to blacklist.
    
    Args:
        token: JWT token string
        
    Returns:
        bool: True if successfully blacklisted
    """
    BlacklistedToken.objects.create(token=token)
    return True


def is_token_blacklisted(token):
    """
    Check if token is blacklisted.
    
    Args:
        token: JWT token string
        
    Returns:
        bool: True if blacklisted
    """
    return BlacklistedToken.objects.filter(token=token).exists()
