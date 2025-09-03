"""
Tests for quiz API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Quiz, Question


class QuizTestCase(TestCase):
    """
    Test cases for quiz endpoints.
    """

    def setUp(self):
        """
        Set up test data.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="TestPassword123!"
        )
        self.client.force_authenticate(user=self.user)

        self.create_quiz_url = reverse("create_quiz")
        self.list_quizzes_url = reverse("list_quizzes")
        self.quiz_detail_url = lambda quiz_id: reverse(
            "quiz_detail", kwargs={"quiz_id": quiz_id}
        )

        # Create test quiz
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            description="Test Description",
            video_url="https://www.youtube.com/watch?v=test",
            user=self.user,
        )

        # Create test questions
        for i in range(3):
            Question.objects.create(
                quiz=self.quiz,
                question_title=f"Test Question {i+1}",
                question_options=["Option A", "Option B", "Option C", "Option D"],
                answer="Option A",
            )

    def test_list_quizzes_success(self):
        """
        Test successful quiz listing.
        """
        response = self.client.get(self.list_quizzes_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Quiz")

    def test_get_quiz_success(self):
        """
        Test successful quiz retrieval.
        """
        url = self.quiz_detail_url(self.quiz.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Quiz")
        self.assertEqual(len(response.data["questions"]), 3)

    def test_get_quiz_not_found(self):
        """
        Test quiz retrieval with invalid ID.
        """
        # Use non-existent integer ID instead of UUID
        url = self.quiz_detail_url(99999)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_quiz_success(self):
        """
        Test successful quiz update.
        """
        url = self.quiz_detail_url(self.quiz.id)
        update_data = {
            "title": "Updated Quiz Title",
            "description": "Updated Description",
            "video_url": "https://www.youtube.com/watch?v=updated",
        }

        response = self.client.put(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Quiz Title")

    def test_partial_update_quiz_success(self):
        """
        Test successful partial quiz update.
        """
        url = self.quiz_detail_url(self.quiz.id)
        update_data = {"title": "Partially Updated Title"}

        response = self.client.patch(url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Partially Updated Title")
        self.assertEqual(response.data["description"], "Test Description")

    def test_delete_quiz_success(self):
        """
        Test successful quiz deletion.
        """
        url = self.quiz_detail_url(self.quiz.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=self.quiz.id).exists())

    def test_unauthorized_access(self):
        """
        Test unauthorized access to quiz endpoints.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_quizzes_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
