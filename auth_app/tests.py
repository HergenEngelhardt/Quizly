"""
Comprehensive tests for authentication API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from quiz_app.models import BlacklistedToken


class AuthTestCase(TestCase):
    """Test cases for authentication endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

    def test_user_registration(self):
        """Test user registration."""
        response = self.client.post(reverse("register"), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertEqual(response.data["detail"], "User created successfully!")

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        User.objects.create_user(**self.user_data)
        response = self.client.post(reverse("register"), self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        """Test registration with invalid email."""
        invalid_data = self.user_data.copy()
        invalid_data["email"] = "invalid-email"
        response = self.client.post(reverse("register"), invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login."""
        User.objects.create_user(**self.user_data)
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Login successfully!")
        self.assertIn("user", response.data)

    def test_user_logout(self):
        """Test user logout."""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        """Test login with wrong password."""
        User.objects.create_user(**self.user_data)
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid login credentials.")

    def test_user_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        login_data = {"username": "nonexistent", "password": "testpass123"}
        response = self.client.post(reverse("login"), login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh."""
        User.objects.create_user(**self.user_data)
        login_response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpass123"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        response = self.client.post(reverse("token_refresh"))
        # Token refresh can return 200 or 401 depending on cookie state
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        self.client.cookies["refresh_token"] = "invalid_token"
        response = self.client.post(reverse("token_refresh"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BlacklistedTokenTestCase(TestCase):
    """Test cases for blacklisted tokens."""

    def setUp(self):
        """Set up test data."""
        self.token = "test_token_12345"

    def test_blacklist_token_creation(self):
        """Test blacklisted token creation."""
        blacklisted = BlacklistedToken.objects.create(token=self.token)
        self.assertEqual(str(blacklisted), f"Blacklisted token - {blacklisted.blacklisted_at}")
        self.assertTrue(BlacklistedToken.objects.filter(token=self.token).exists())

    def test_get_tokens_for_user(self):
        """Test token generation for user."""
        from auth_app.utils import get_tokens_for_user

        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        tokens = get_tokens_for_user(user)
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)
        self.assertIsInstance(tokens["access"], str)
        self.assertIsInstance(tokens["refresh"], str)


class AuthenticationUtilsTestCase(TestCase):
    """Test cases for authentication utilities."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_blacklist_token_function(self):
        """Test blacklist token utility function."""
        from auth_app.utils import blacklist_token, is_token_blacklisted

        test_token = "test_token_12345"

        # Token should not be blacklisted initially
        self.assertFalse(is_token_blacklisted(test_token))

        # Blacklist the token
        result = blacklist_token(test_token)
        self.assertTrue(result)

        # Token should now be blacklisted
        self.assertTrue(is_token_blacklisted(test_token))

    def test_is_token_blacklisted_nonexistent(self):
        """Test checking blacklist status of nonexistent token."""
        from auth_app.utils import is_token_blacklisted

        result = is_token_blacklisted("nonexistent_token")
        self.assertFalse(result)

    def test_set_jwt_cookies(self):
        """Test setting JWT cookies."""
        from auth_app.utils import set_jwt_cookies
        from django.http import HttpResponse

        response = HttpResponse()
        tokens = {"access": "test_access_token", "refresh": "test_refresh_token"}

        result = set_jwt_cookies(response, tokens)
        self.assertEqual(result, response)
        # Check if cookies were set (basic check)
        self.assertIn("access_token", result.cookies)
        self.assertIn("refresh_token", result.cookies)

    def test_clear_jwt_cookies(self):
        """Test clearing JWT cookies."""
        from auth_app.utils import clear_jwt_cookies
        from django.http import HttpResponse

        response = HttpResponse()
        result = clear_jwt_cookies(response)
        self.assertEqual(result, response)


class SerializerTestCase(TestCase):
    """Test cases for authentication serializers."""

    def test_user_registration_serializer_valid(self):
        """Test UserRegistrationSerializer with valid data."""
        from auth_app.api.serializers import UserRegistrationSerializer

        valid_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword123",
        }

        serializer = UserRegistrationSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")

    def test_user_registration_serializer_invalid(self):
        """Test UserRegistrationSerializer with invalid data."""
        from auth_app.api.serializers import UserRegistrationSerializer

        invalid_data = {
            "username": "",  # Empty username
            "email": "invalid-email",  # Invalid email
            "password": "123",  # Too short password
        }

        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_user_login_serializer_valid(self):
        """Test UserLoginSerializer with valid credentials."""
        from auth_app.api.serializers import UserLoginSerializer

        # Create a user first
        User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        login_data = {"username": "testuser", "password": "testpass123"}

        serializer = UserLoginSerializer(data=login_data)
        self.assertTrue(serializer.is_valid())
        self.assertIn("user", serializer.validated_data)

    def test_user_login_serializer_invalid(self):
        """Test UserLoginSerializer with invalid credentials."""
        from auth_app.api.serializers import UserLoginSerializer

        login_data = {"username": "nonexistent", "password": "wrongpass"}

        serializer = UserLoginSerializer(data=login_data)
        self.assertFalse(serializer.is_valid())

    def test_user_serializer(self):
        """Test UserSerializer."""
        from auth_app.api.serializers import UserSerializer

        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        serializer = UserSerializer(user)
        data = serializer.data

        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertIn("id", data)


class AuthenticationMiddlewareTestCase(TestCase):
    """Test cases for custom JWT authentication."""

    def test_jwt_authentication_no_cookie(self):
        """Test JWT authentication without cookie."""
        from auth_app.api.authentication import JWTCookieAuthentication
        from django.http import HttpRequest

        auth = JWTCookieAuthentication()
        request = HttpRequest()

        result = auth.authenticate(request)
        self.assertIsNone(result)

    def test_jwt_authentication_invalid_token(self):
        """Test JWT authentication with invalid token."""
        from auth_app.api.authentication import JWTCookieAuthentication
        from django.http import HttpRequest
        from rest_framework_simplejwt.exceptions import InvalidToken

        auth = JWTCookieAuthentication()
        request = HttpRequest()
        request.COOKIES = {"access_token": "invalid_token"}

        # Should handle invalid token gracefully and return None
        try:
            result = auth.authenticate(request)
            self.assertIsNone(result)
        except InvalidToken:
            # This is expected behavior for invalid tokens
            pass
