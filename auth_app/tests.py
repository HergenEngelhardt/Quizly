"""
Tests for authentication API endpoints.
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class AuthenticationTestCase(TestCase):
    """
    Test cases for authentication endpoints.
    """
    
    def setUp(self):
        """
        Set up test data.
        """
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.refresh_url = reverse('token_refresh')
        
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }
    
    def test_user_registration_success(self):
        """
        Test successful user registration.
        """
        response = self.client.post(self.register_url, self.test_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'User created successfully!')
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_user_registration_duplicate_username(self):
        """
        Test registration with duplicate username.
        """
        User.objects.create_user(**self.test_user_data)
        response = self.client.post(self.register_url, self.test_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_duplicate_email(self):
        """
        Test registration with duplicate email.
        """
        User.objects.create_user(**self.test_user_data)
        new_data = self.test_user_data.copy()
        new_data['username'] = 'different_user'
        response = self.client.post(self.register_url, new_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        """
        Test successful user login.
        """
        user = User.objects.create_user(**self.test_user_data)
        login_data = {
            'username': self.test_user_data['username'],
            'password': self.test_user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Login successfully!')
        self.assertIn('user', response.data)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
    
    def test_user_login_invalid_credentials(self):
        """
        Test login with invalid credentials.
        """
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_logout_success(self):
        """
        Test successful user logout.
        """
        user = User.objects.create_user(**self.test_user_data)
        self.client.force_authenticate(user=user)
        
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Log-Out successfully!', response.data['detail'])
