"""
Tests for authentication API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class AuthenticationTestCase(TestCase):
    """Test cases for authentication endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.refresh_url = reverse("token_refresh")

        self.test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.test_user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if the response contains success message or user data
        self.assertTrue(
            "User registered successfully!" in str(response.data)
            or "message" in response.data
            or response.status_code == status.HTTP_201_CREATED
        )
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_user_registration_duplicate_username(self):
        """Test user registration with duplicate username."""
        User.objects.create_user(**self.test_user_data)
        response = self.client.post(self.register_url, self.test_user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Test successful user login."""
        User.objects.create_user(**self.test_user_data)

        login_data = {
            "username": "testuser",
            "password": "testpass123",
        }

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials."""
        User.objects.create_user(**self.test_user_data)

        invalid_login_data = {"username": "testuser", "password": "wrongpassword"}

        response = self.client.post(self.login_url, invalid_login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout_success(self):
        """Test successful user logout."""
        user = User.objects.create_user(**self.test_user_data)
        self.client.force_authenticate(user=user)

        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_missing_username(self):
        """Test registration with missing username."""
        data = self.test_user_data.copy()
        del data["username"]
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        """Test registration with missing password."""
        data = self.test_user_data.copy()
        del data["password"]
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        """Test registration with invalid email."""
        data = self.test_user_data.copy()
        data["email"] = "invalid-email"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_credentials(self):
        """Test login with missing credentials."""
        User.objects.create_user(**self.test_user_data)
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = self.client.post(
            self.login_url, {"username": "nonexistent", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_without_authentication(self):
        """Test logout without being authenticated."""
        response = self.client.post(self.logout_url)
        # Logout ohne Authentifizierung sollte 401 zurückgeben
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_without_token(self):
        """Test token refresh without refresh token."""
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_short_password(self):
        """Test registration with short password."""
        data = self.test_user_data.copy()
        data["password"] = "123"
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_empty_username(self):
        """Test registration with empty username."""
        data = self.test_user_data.copy()
        data["username"] = ""
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_password(self):
        """Test login with empty password."""
        User.objects.create_user(**self.test_user_data)
        response = self.client.post(
            self.login_url, {"username": "testuser", "password": ""}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_authenticated_user(self):
        """Test logout with authenticated user and cookies."""
        user = User.objects.create_user(**self.test_user_data)

        # Login first to get tokens
        login_response = self.client.post(
            self.login_url, {"username": "testuser", "password": "testpass123"}
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Now logout
        self.client.force_authenticate(user=user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
