"""
Comprehensive tests for quiz API endpoints.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Quiz, Question, QuizAttempt


class QuizTestCase(TestCase):
    """Test cases for quiz API endpoints."""

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

    def test_create_quiz_invalid_url(self):
        """Test quiz creation with invalid URL."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("create_quiz"), {"url": "invalid_url"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_quizzes(self):
        """Test quiz listing endpoint."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        Question.objects.create(
            quiz=quiz,
            question_title="Test Question",
            question_options=["A", "B", "C", "D"],
            answer="A"
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("list_quizzes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_quiz_detail(self):
        """Test quiz detail endpoint."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Quiz")

    def test_update_quiz(self):
        """Test quiz update endpoint."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        
        update_data = {
            "title": "Updated Test Quiz",
            "description": "An updated test quiz",
            "video_url": "https://youtube.com/watch?v=updated123"
        }
        
        self.client.force_authenticate(user=self.user)
        response = self.client.put(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Test Quiz")

    def test_partial_update_quiz(self):
        """Test quiz partial update endpoint."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}), {"title": "Patched Title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Patched Title")

    def test_delete_quiz(self):
        """Test quiz deletion endpoint."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())

    def test_unauthorized_access(self):
        """Test access without authentication."""
        response = self.client.get(reverse("list_quizzes"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_user_quiz(self):
        """Test accessing quiz of another user."""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        quiz = Quiz.objects.create(user=other_user, **self.quiz_data)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_quiz_not_found(self):
        """Test accessing non-existent quiz."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_detail", kwargs={"quiz_id": 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ModelTestCase(TestCase):
    """Test cases for models."""

    def setUp(self):
        """Set up test data for models."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_quiz_creation(self):
        """Test quiz model creation."""
        quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )
        self.assertTrue(isinstance(quiz, Quiz))
        self.assertEqual(quiz.__str__(), "Test Quiz - testuser")

    def test_question_creation(self):
        """Test question model creation."""
        quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )
        question = Question.objects.create(
            quiz=quiz,
            question_title="Test Question",
            question_options=["A", "B", "C", "D"],
            answer="A"
        )
        self.assertTrue(isinstance(question, Question))
        self.assertEqual(question.answer, "A")


class UtilsTestCase(TestCase):
    """Test cases for utility functions."""

    def test_extract_youtube_id_valid_urls(self):
        """Test YouTube ID extraction from valid URLs."""
        from quiz_app.utils import extract_youtube_id
        
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                self.assertEqual(extract_youtube_id(url), expected_id)

    def test_extract_youtube_id_invalid_urls(self):
        """Test YouTube ID extraction from invalid URLs."""
        from quiz_app.utils import extract_youtube_id
        
        invalid_urls = [
            "https://example.com",
            "not_a_url",
            "https://vimeo.com/123456",
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertIsNone(extract_youtube_id(url))

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_temp_file(self, mock_remove, mock_exists):
        """Test temporary file cleanup."""
        from quiz_app.utils import cleanup_temp_file
        
        mock_exists.return_value = True
        
        test_file = "/tmp/test_file.wav"
        cleanup_temp_file(test_file)
        
        mock_exists.assert_called_once_with(test_file)
        mock_remove.assert_called_once_with(test_file)

    @patch('os.path.exists')
    def test_cleanup_nonexistent_file(self, mock_exists):
        """Test cleanup of non-existent file."""
        from quiz_app.utils import cleanup_temp_file
        
        mock_exists.return_value = False
        
        # Should not raise exception
        cleanup_temp_file("/tmp/nonexistent.wav")
        mock_exists.assert_called_once()


class SerializerTestCase(TestCase):
    """Test cases for serializers."""

    def setUp(self):
        """Set up test data for serializers."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )

    def test_quiz_serializer(self):
        """Test QuizSerializer."""
        from .api.serializers import QuizSerializer
        
        serializer = QuizSerializer(instance=self.quiz)
        data = serializer.data
        
        self.assertEqual(data["title"], "Test Quiz")
        self.assertEqual(data["description"], "A test quiz")
        self.assertIn("questions", data)

    def test_quiz_create_serializer_valid_url(self):
        """Test QuizCreateSerializer with valid YouTube URL."""
        from .api.serializers import QuizCreateSerializer
        
        data = {"url": "https://youtube.com/watch?v=test123"}
        serializer = QuizCreateSerializer(data=data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["url"], data["url"])

    def test_quiz_create_serializer_invalid_url(self):
        """Test QuizCreateSerializer with invalid URL."""
        from .api.serializers import QuizCreateSerializer
        
        data = {"url": "https://example.com/not-youtube"}
        serializer = QuizCreateSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("url", serializer.errors)

    def test_quiz_update_serializer(self):
        """Test QuizUpdateSerializer."""
        from .api.serializers import QuizUpdateSerializer
        
        data = {
            "title": "Updated Title",
            "description": "Updated description",
            "video_url": "https://youtube.com/watch?v=updated123"
        }
        serializer = QuizUpdateSerializer(instance=self.quiz, data=data)
        
        self.assertTrue(serializer.is_valid())
        updated_quiz = serializer.save()
        self.assertEqual(updated_quiz.title, "Updated Title")


class MockedViewTestCase(TestCase):
    """Test cases for views with mocked dependencies."""

    def setUp(self):
        """Set up test data for mocked views."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    @patch('quiz_app.api.views.handle_quiz_creation')
    def test_create_quiz_view_mocked(self, mock_handle):
        """Test create quiz view with mocked dependencies."""
        mock_quiz = Quiz(
            id=1,
            title="Mocked Quiz",
            description="Mocked description",
            video_url="https://youtube.com/watch?v=mocked",
            user=self.user
        )
        mock_handle.return_value = mock_quiz
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("create_quiz"), {"url": "https://youtube.com/watch?v=test"})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_handle.assert_called_once()

    @patch('quiz_app.api.views.handle_quiz_creation')
    def test_create_quiz_view_exception(self, mock_handle):
        """Test create quiz view with exception."""
        mock_handle.side_effect = Exception("Test error")
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("create_quiz"), {"url": "https://youtube.com/watch?v=test"})
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Error creating quiz", response.data["detail"])

    def test_list_quizzes_view_empty(self):
        """Test list quizzes view with no quizzes."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("list_quizzes"))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class ViewHelpersTestCase(TestCase):
    """Test cases for view helper functions."""

    def setUp(self):
        """Set up test data for view helpers."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )

    def test_quiz_detail_view_get_user_quiz_helper(self):
        """Test QuizDetailView get_user_quiz helper method."""
        from .api.views import QuizDetailView

        view = QuizDetailView()

        # Test valid access
        quiz, error_response = view.get_user_quiz(self.quiz.id, self.user)
        self.assertIsNone(error_response)
        self.assertEqual(quiz.id, self.quiz.id)

        # Test access to non-existent quiz
        quiz, error_response = view.get_user_quiz(999, self.user)
        self.assertIsNotNone(error_response)
        self.assertIsNone(quiz)

    def test_view_helper_functions(self):
        """Test individual view helper functions."""
        from quiz_app.utils import validate_quiz_creation_data, cleanup_quiz_creation
        from rest_framework.test import APIRequestFactory

        factory = APIRequestFactory()

        # Test validate_quiz_creation_data with proper request.data
        request = factory.post('/', {"url": "https://youtube.com/watch?v=test"}, format='json')
        request.data = {"url": "https://youtube.com/watch?v=test"}
        url, error = validate_quiz_creation_data(request)
        self.assertIsNotNone(url)
        self.assertIsNone(error)

        # Test cleanup_quiz_creation
        cleanup_quiz_creation(None)  # Should not raise exception
        cleanup_quiz_creation("/tmp/test.wav")  # Should not raise exception


class UtilityFunctionTestCase(TestCase):
    """Test cases for utility functions."""

    def test_create_ydl_options(self):
        """Test yt-dlp options creation."""
        from quiz_app.utils import create_ydl_options
        
        output_file = "/tmp/audio.%(ext)s"
        options = create_ydl_options(output_file)
        
        self.assertEqual(options["outtmpl"], output_file)
        self.assertEqual(options["format"], "bestaudio/best")
        self.assertIn("postprocessors", options)

    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info(self, mock_ydl):
        """Test video info extraction."""
        from quiz_app.utils import get_video_info
        
        mock_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.return_value = {
            "title": "Test Video",
            "description": "Test Description",
            "duration": 300,
            "thumbnail": "http://example.com/thumb.jpg"
        }
        
        info = get_video_info("https://youtube.com/watch?v=test")
        
        self.assertEqual(info["title"], "Test Video")
        self.assertEqual(info["duration"], 300)

    def test_validate_quiz_structure_valid(self):
        """Test quiz structure validation with valid data."""
        from quiz_app.utils import validate_quiz_structure
        
        valid_quiz = {
            "title": "Test Quiz",
            "description": "Test Description",
            "questions": [
                {
                    "question_title": f"Question {i}",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A"
                } for i in range(1, 11)
            ]
        }
        
        # Should not raise exception
        validate_quiz_structure(valid_quiz)

    def test_validate_quiz_structure_invalid(self):
        """Test quiz structure validation with invalid data."""
        from quiz_app.utils import validate_quiz_structure
        
        invalid_cases = [
            {"questions": "not a list"},
            {"questions": []},  # Empty questions
            {"questions": [{"question_title": "Q1", "question_options": ["A", "B"], "answer": "A"}]},  # Wrong number of options
            {"questions": [{"question_title": "Q1", "question_options": ["A", "B", "C", "D"], "answer": "E"}]},  # Answer not in options
        ]
        
        for invalid_quiz in invalid_cases:
            with self.subTest(quiz=invalid_quiz):
                with self.assertRaises(Exception):
                    validate_quiz_structure(invalid_quiz)

    def test_parse_quiz_response(self):
        """Test parsing quiz response from AI."""
        from quiz_app.utils import parse_quiz_response
        import json
        
        json_response = '''```json
        {
            "title": "Test Quiz",
            "description": "Test Description",
            "questions": []
        }
        ```'''
        
        result = parse_quiz_response(json_response)
        parsed = json.loads(result)
        
        self.assertEqual(parsed["title"], "Test Quiz")
        self.assertEqual(parsed["description"], "Test Description")

    def test_parse_quiz_response_clean_json(self):
        """Test parsing clean JSON response."""
        from quiz_app.utils import parse_quiz_response
        
        clean_json = '{"title": "Test", "questions": []}'
        result = parse_quiz_response(clean_json)
        self.assertEqual(result, clean_json)

    @patch('quiz_app.utils.configure_gemini_model')
    def test_generate_quiz_from_transcript(self, mock_configure):
        """Test quiz generation from transcript."""
        from quiz_app.utils import generate_quiz_from_transcript
        
        # Mock Gemini model
        mock_model = MagicMock()
        mock_configure.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = '''{
            "title": "Test",
            "description": "Test",
            "questions": [
                {
                    "question_title": "Q1",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A"
                },
                {
                    "question_title": "Q2",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "B"
                },
                {
                    "question_title": "Q3",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "C"
                },
                {
                    "question_title": "Q4",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "D"
                },
                {
                    "question_title": "Q5",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A"
                },
                {
                    "question_title": "Q6",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "B"
                },
                {
                    "question_title": "Q7",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "C"
                },
                {
                    "question_title": "Q8",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "D"
                },
                {
                    "question_title": "Q9",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A"
                },
                {
                    "question_title": "Q10",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "B"
                }
            ]
        }'''
        mock_model.generate_content.return_value = mock_response
        
        result = generate_quiz_from_transcript("Test transcript")
        self.assertEqual(result["title"], "Test")
        self.assertEqual(len(result["questions"]), 10)

    def test_get_quiz_structure_template(self):
        """Test quiz structure template generation."""
        from quiz_app.utils import get_quiz_structure_template
        
        template = get_quiz_structure_template()
        self.assertIn("title", template)
        self.assertIn("questions", template)

    def test_get_quiz_requirements(self):
        """Test quiz requirements text generation."""
        from quiz_app.utils import get_quiz_requirements
        
        requirements = get_quiz_requirements()
        self.assertIn("4 distinct answer options", requirements)
        self.assertIn("valid JSON", requirements)


class QuizAttemptTestCase(TestCase):
    """Test cases for quiz attempt functionality."""

    def setUp(self):
        """Set up test data for quiz attempts."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            question_title="Test Question",
            question_options=["A", "B", "C", "D"],
            answer="A"
        )

    def test_start_quiz_attempt(self):
        """Test starting a new quiz attempt."""
        self.client.force_authenticate(user=self.user)
        url = reverse("start_quiz", kwargs={"quiz_id": self.quiz.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(QuizAttempt.objects.filter(quiz=self.quiz, user=self.user).exists())

    def test_save_quiz_answer(self):
        """Test saving quiz answers."""
        self.client.force_authenticate(user=self.user)
        
        # Create attempt
        attempt = QuizAttempt.objects.create(quiz=self.quiz, user=self.user)
        
        url = reverse("save_answer", kwargs={"attempt_id": attempt.id})
        data = {
            "question_id": self.question.id,
            "answer": "B"
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        attempt.refresh_from_db()
        self.assertEqual(attempt.answers[str(self.question.id)], "B")
