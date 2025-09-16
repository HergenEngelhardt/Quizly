"""
Simple JWT authentication using HTTP cookies.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from django.contrib.auth import get_user_model
from auth_app.utils import is_token_blacklisted


class JWTCookieAuthentication(JWTAuthentication):
    """
    JWT authentication that reads tokens from cookies.

    Extends the default JWT authentication to work with HTTP-only cookies
    instead of Authorization headers.
    """

    def authenticate(self, request):
        """
        Authenticate user using JWT token from cookies.

        Args:
            request: HTTP request object

        Returns:
            tuple: (user, token) if authentication successful, None otherwise

        Raises:
            None
        """
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])

        if raw_token is None:
            return None

        if is_token_blacklisted(raw_token):
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except TokenError:
            return None

    def get_user(self, validated_token):
        """
        Get user from validated JWT token.

        Args:
            validated_token: Validated JWT token object

        Returns:
            User: Django user object

        Raises:
            InvalidToken: If token is invalid or user not found
        """
        try:
            user_id = validated_token.get("user_id")
        except KeyError:
            raise InvalidToken("Token missing user identification")

        try:
            User = get_user_model()
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise InvalidToken("User not found")

        if not user.is_active:
            raise InvalidToken("User is inactive")

        return user
