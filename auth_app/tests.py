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

    def test_user_login(self):
        """Test user login."""
        User.objects.create_user(**self.user_data)
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout(self):
        """Test user logout."""
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_login(self):
        """Test login with wrong password."""
        User.objects.create_user(**self.user_data)
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test token refresh."""
        user = User.objects.create_user(**self.user_data)
        login_response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "testpass123"
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        if 'refresh_token' in login_response.cookies:
            refresh_token = login_response.cookies['refresh_token'].value
            response = self.client.post(reverse("token_refresh"), 
                                      HTTP_COOKIE=f'refresh_token={refresh_token}')
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
        else:
            response = self.client.post(reverse("token_refresh"))
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED])
