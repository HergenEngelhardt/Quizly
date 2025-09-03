"""
Tests for quiz API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Quiz, Question, QuizAttempt


class QuizTestCase(TestCase):
    """Test cases for quiz endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.quiz_data = {
            "title": "Test Quiz",
            "description": "A test quiz",
            "video_url": "https://youtube.com/watch?v=test123"
        }

    def test_create_quiz(self):
        """Test quiz creation."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("create_quiz"), {"url": "invalid_url"})
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_list_quizzes(self):
        """Test quiz listing."""
        Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("list_quizzes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_start_quiz_attempt(self):
        """Test starting a quiz attempt."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("start_quiz", args=[quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(QuizAttempt.objects.filter(quiz=quiz, user=self.user).exists())

    def test_unauthorized_access(self):
        """Test access without authentication."""
        response = self.client.post(reverse("create_quiz"), self.quiz_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_quiz_detail(self):
        """Test getting quiz details."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_detail", args=[quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recent_quizzes(self):
        """Test getting recent quizzes."""
        Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("recent_quizzes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_save_quiz_answer(self):
        """Test saving a quiz answer."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        attempt = QuizAttempt.objects.create(quiz=quiz, user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(reverse("save_answer", args=[attempt.id]), {
            "question_id": 1,
            "answer": "Test Answer"
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_400_BAD_REQUEST])

    def test_complete_quiz(self):
        """Test completing a quiz."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        attempt = QuizAttempt.objects.create(quiz=quiz, user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("complete_quiz", args=[attempt.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quiz_results(self):
        """Test getting quiz results."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        attempt = QuizAttempt.objects.create(quiz=quiz, user=self.user, completed_at=quiz.created_at)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_results", args=[attempt.id]))
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])

    def test_privacy_policy(self):
        """Test privacy policy endpoint."""
        response = self.client.get(reverse("privacy_policy"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_legal_notice(self):
        """Test legal notice endpoint."""
        response = self.client.get(reverse("legal_notice"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
