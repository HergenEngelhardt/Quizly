"""
Custom JWT authentication using HTTP-only cookies.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from HTTP-only cookies.
    """

    def authenticate(self, request):
        """
        Authenticate user using JWT token from cookies.
        """
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            # Try to get token from cookies
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except TokenError:
            return None

    def get_user(self, validated_token):
        """
        Get user from validated token.
        """
        try:
            user_id = validated_token.get("user_id")
        except KeyError:
            raise InvalidToken("Token contained no recognizable user identification")

        try:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.get(**{User.USERNAME_FIELD: user_id})
        except User.DoesNotExist:
            raise InvalidToken("User not found")

        if not user.is_active:
            raise InvalidToken("User is inactive")

        return user
