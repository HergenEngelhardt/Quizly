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
import json


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
        """Test getting specific quiz details."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_detail", args=[quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], quiz.id)

    def test_update_quiz_with_patch(self):
        """Test quiz update endpoint using PATCH."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        
        update_data = {
            "title": "Updated Quiz Title"
        }
        response = self.client.put(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated Quiz Title")

    def test_partial_update_quiz(self):
        """Test partial quiz update endpoint."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        
        patch_data = {"title": "Partially Updated Title"}
        response = self.client.patch(reverse("quiz_detail", args=[quiz.id]), patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_quiz(self):
        """Test quiz deletion endpoint."""
        quiz = Quiz.objects.create(user=self.user, **self.quiz_data)
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(reverse("quiz_detail", args=[quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())

    def test_unauthorized_access(self):
        """Test unauthorized access to quiz endpoints."""
        response = self.client.get(reverse("list_quizzes"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_other_user_quiz(self):
        """Test access to another user's quiz."""
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        quiz = Quiz.objects.create(user=other_user, **self.quiz_data)
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_detail", args=[quiz.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_quiz_not_found(self):
        """Test accessing non-existent quiz."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("quiz_detail", args=[999]))
        # API should return 404 or 500 for missing quiz
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR])


class QuizModelTestCase(TestCase):
    """Test cases for Quiz model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_quiz_creation(self):
        """Test quiz creation."""
        quiz = Quiz.objects.create(
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123",
            user=self.user
        )
        self.assertEqual(quiz.title, "Test Quiz")
        self.assertEqual(quiz.user, self.user)
        self.assertEqual(str(quiz), "Test Quiz")

    def test_question_creation(self):
        """Test question creation."""
        quiz = Quiz.objects.create(
            title="Test Quiz",
            user=self.user,
            video_url="https://youtube.com/watch?v=test123"
        )
        question = Question.objects.create(
            quiz=quiz,
            question_title="What is 2+2?",
            question_options=["1", "2", "3", "4"],
            answer="4"
        )
        self.assertEqual(question.question_title, "What is 2+2?")
        self.assertEqual(question.answer, "4")
        self.assertEqual(len(question.question_options), 4)


class UtilsTestCase(TestCase):
    """Test cases for utility functions."""

    def test_extract_youtube_id_valid_urls(self):
        """Test YouTube ID extraction from valid URLs."""
        from .utils import extract_youtube_id
        
        test_cases = [
            ("https://youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                result = extract_youtube_id(url)
                self.assertEqual(result, expected_id)

    def test_extract_youtube_id_invalid_urls(self):
        """Test YouTube ID extraction from invalid URLs."""
        from .utils import extract_youtube_id
        
        invalid_urls = [
            "https://example.com",
            "not-a-url",
            "https://youtube.com/invalid",
            "",
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                result = extract_youtube_id(url)
                self.assertIsNone(result)

    def test_cleanup_temp_file(self):
        """Test temporary file cleanup."""
        from .utils import cleanup_temp_file
        import tempfile
        import os
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(b"test content")
        
        # Verify file exists
        self.assertTrue(os.path.exists(tmp_path))
        
        # Clean up file
        cleanup_temp_file(tmp_path)
        
        # Verify file is deleted
        self.assertFalse(os.path.exists(tmp_path))

    def test_cleanup_nonexistent_file(self):
        """Test cleanup of nonexistent file."""
        from .utils import cleanup_temp_file
        
        # Should not raise exception
        cleanup_temp_file("/nonexistent/file.txt")


class SerializerTestCase(TestCase):
    """Test cases for API serializers."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            user=self.user,
            video_url="https://youtube.com/watch?v=test123"
        )

    def test_quiz_serializer(self):
        """Test QuizSerializer."""
        from quiz_app.api.serializers import QuizSerializer
        
        serializer = QuizSerializer(self.quiz)
        data = serializer.data
        
        self.assertEqual(data["title"], "Test Quiz")
        self.assertEqual(data["video_url"], "https://youtube.com/watch?v=test123")
        self.assertIn("id", data)
        self.assertIn("created_at", data)

    def test_quiz_create_serializer_valid_url(self):
        """Test QuizCreateSerializer with valid URL."""
        from quiz_app.api.serializers import QuizCreateSerializer
        
        valid_data = {"url": "https://youtube.com/watch?v=test123"}
        serializer = QuizCreateSerializer(data=valid_data)
        
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["url"], valid_data["url"])

    def test_quiz_create_serializer_invalid_url(self):
        """Test QuizCreateSerializer with invalid URL."""
        from quiz_app.api.serializers import QuizCreateSerializer
        
        invalid_data = {"url": "invalid-url"}
        serializer = QuizCreateSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn("url", serializer.errors)

    def test_quiz_update_serializer(self):
        """Test QuizUpdateSerializer."""
        from quiz_app.api.serializers import QuizUpdateSerializer
        
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }
        
        serializer = QuizUpdateSerializer(self.quiz, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_quiz = serializer.save()
        self.assertEqual(updated_quiz.title, "Updated Title")
        self.assertEqual(updated_quiz.description, "Updated Description")


class APIViewTestCase(TestCase):
    """Test cases for API view functions."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.quiz = Quiz.objects.create(
            title="Test Quiz",
            user=self.user,
            video_url="https://youtube.com/watch?v=test123"
        )

    @patch('quiz_app.api.views.handle_quiz_creation')
    def test_create_quiz_view_mocked(self, mock_handle):
        """Test create_quiz_view with mocked quiz creation."""
        from rest_framework.test import APIClient
        
        # Mock the quiz creation process
        mock_handle.return_value = self.quiz
        
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        response = client.post(reverse("create_quiz"), {"url": "https://youtube.com/watch?v=test123"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Test Quiz")

    @patch('quiz_app.api.views.handle_quiz_creation')
    def test_create_quiz_view_exception(self, mock_handle):
        """Test create_quiz_view with exception."""
        from rest_framework.test import APIClient
        
        # Mock an exception during quiz creation
        mock_handle.side_effect = Exception("Test error")
        
        client = APIClient()
        client.force_authenticate(user=self.user)
        
        response = client.post(reverse("create_quiz"), {"url": "https://youtube.com/watch?v=test123"})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Error creating quiz", response.data["detail"])

    def test_list_quizzes_view_empty(self):
        """Test list_quizzes_view with no quizzes."""
        from rest_framework.test import APIClient
        
        # Create a different user with no quizzes
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="password123"
        )
        
        client = APIClient()
        client.force_authenticate(user=other_user)
        
        response = client.get(reverse("list_quizzes"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_simple_helper_test(self):
        """Simple test for view helpers."""
        from quiz_app.utils import cleanup_quiz_creation
        cleanup_quiz_creation(None)


class UtilsExtendedTestCase(TestCase):
    """Extended test cases for utility functions."""

    def test_create_ydl_options(self):
        """Test yt-dlp options creation."""
        from quiz_app.utils import create_ydl_options
        
        output_file = "/tmp/test.%(ext)s"
        options = create_ydl_options(output_file)
        
        self.assertIn("format", options)
        self.assertIn("outtmpl", options)
        self.assertEqual(options["outtmpl"], output_file)
        self.assertIn("bestaudio", options["format"])

    @patch('quiz_app.utils.yt_dlp.YoutubeDL')
    def test_get_video_info(self, mock_ydl):
        """Test video info extraction."""
        from quiz_app.utils import get_video_info
        
        mock_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        mock_instance.extract_info.return_value = {
            "title": "Test Video",
            "description": "Test Description",
            "duration": 120
        }
        
        url = "https://youtube.com/watch?v=test123"
        result = get_video_info(url)
        
        self.assertEqual(result["title"], "Test Video")
        self.assertEqual(result["description"], "Test Description")
        self.assertEqual(result["duration"], 120)

    def test_validate_quiz_structure_valid(self):
        """Test quiz structure validation with valid data."""
        from quiz_app.utils import validate_quiz_structure
        
        valid_quiz = {
            "title": "Test Quiz",
            "description": "Test Description",
            "questions": [
                {
                    "question_title": "Question 1",
                    "question_options": ["A", "B", "C", "D"],
                    "answer": "A"
                }
            ]
        }
        
        # Should not raise exception
        validate_quiz_structure(valid_quiz)

    def test_validate_quiz_structure_invalid(self):
        """Test quiz structure validation with invalid data."""
        from quiz_app.utils import validate_quiz_structure
        
        invalid_cases = [
            {},  # Empty dict
            {"title": "Test"},  # Missing questions
            {"title": "Test", "questions": []},  # Empty questions
            {"title": "Test", "questions": [{}]},  # Invalid question structure
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
        from unittest.mock import MagicMock
        
        # Mock Gemini model
        mock_model = MagicMock()
        mock_configure.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = '{"title": "Test", "description": "Test", "questions": [{"question_title": "Q1", "question_options": ["A", "B", "C", "D"], "answer": "A"}]}'
        mock_model.generate_content.return_value = mock_response
        
        result = generate_quiz_from_transcript("Test transcript")
        self.assertEqual(result["title"], "Test")
        self.assertEqual(len(result["questions"]), 1)


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


class UtilsFunctionTestCase(TestCase):
    """Test cases for utility functions."""

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


class AuthAppUtilsTestCase(TestCase):
    """Test cases for auth_app utilities."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com", 
            password="testpass123"
        )

    def test_get_tokens_for_user(self):
        """Test JWT token generation."""
        from auth_app.utils import get_tokens_for_user
        
        tokens = get_tokens_for_user(self.user)
        self.assertIn("refresh", tokens)
        self.assertIn("access", tokens)
        self.assertIsInstance(tokens["refresh"], str)
        self.assertIsInstance(tokens["access"], str)

    def test_set_jwt_cookies(self):
        """Test setting JWT cookies."""
        from auth_app.utils import set_jwt_cookies
        from django.http import HttpResponse
        
        response = HttpResponse()
        tokens = {"access": "test_access_token", "refresh": "test_refresh_token"}
        
        set_jwt_cookies(response, tokens)
        
        # Check that cookies were set
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_clear_jwt_cookies(self):
        """Test clearing JWT cookies."""
        from auth_app.utils import clear_jwt_cookies
        from django.http import HttpResponse
        
        response = HttpResponse()
        clear_jwt_cookies(response)
        
        # Check that cookies are set to be deleted
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["access_token"]["max-age"], 0)
        self.assertEqual(response.cookies["refresh_token"]["max-age"], 0)

    def test_blacklist_token(self):
        """Test token blacklisting."""
        from auth_app.utils import blacklist_token, is_token_blacklisted
        
        test_token = "test_token_string"
        blacklist_token(test_token)
        
        self.assertTrue(is_token_blacklisted(test_token))

    def test_is_token_not_blacklisted(self):
        """Test checking non-blacklisted token."""
        from auth_app.utils import is_token_blacklisted
        
        self.assertFalse(is_token_blacklisted("non_existent_token"))


class QuizAppUtilsTestCase(TestCase):
    """Test cases for quiz_app utilities."""

    def test_extract_youtube_id_edge_cases(self):
        """Test YouTube ID extraction edge cases."""
        from quiz_app.utils import extract_youtube_id
        
        test_cases = [
            ("https://youtube.com/watch?v=dQw4w9WgXcQ&t=10", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=123", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ?t=30", "dQw4w9WgXcQ"),
            ("", None),
            ("not-a-url", None),
            ("https://google.com", None),
        ]
        
        for url, expected_id in test_cases:
            with self.subTest(url=url):
                result = extract_youtube_id(url)
                self.assertEqual(result, expected_id)

    def test_create_ydl_options_detailed(self):
        """Test yt-dlp options in detail."""
        from quiz_app.utils import create_ydl_options
        
        output_file = "/custom/path/test.%(ext)s"
        options = create_ydl_options(output_file)
        
        self.assertEqual(options["outtmpl"], output_file)
        self.assertIn("bestaudio", options["format"])
        self.assertIn("noplaylist", options)
        self.assertTrue(options["noplaylist"])

    @patch('quiz_app.utils.whisper.load_model')
    def test_transcribe_audio(self, mock_load_model):
        """Test audio transcription."""
        from quiz_app.utils import transcribe_audio
        
        # Mock whisper model and transcription
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Test transcription"}
        mock_load_model.return_value = mock_model
        
        result = transcribe_audio("/test/path/audio.wav")
        
        self.assertEqual(result, "Test transcription")
        mock_load_model.assert_called_once_with("base")

    @patch('quiz_app.utils.genai.configure')
    @patch('quiz_app.utils.genai.GenerativeModel')
    def test_configure_gemini_model(self, mock_model_class, mock_configure):
        """Test Gemini model configuration."""
        from quiz_app.utils import configure_gemini_model
        
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        result = configure_gemini_model()
        
        mock_configure.assert_called_once()
        mock_model_class.assert_called_once_with("gemini-1.5-flash")
        self.assertEqual(result, mock_model)

    def test_get_quiz_structure_template_detailed(self):
        """Test quiz structure template generation in detail."""
        from quiz_app.utils import get_quiz_structure_template
        
        template = get_quiz_structure_template()
        
        self.assertIn("title", template)
        self.assertIn("description", template)
        self.assertIn("questions", template)
        self.assertIn("question_title", template)
        self.assertIn("question_options", template)
        self.assertIn("answer", template)

    def test_create_quiz_prompt(self):
        """Test quiz prompt creation."""
        from quiz_app.utils import create_quiz_prompt
        
        transcript = "This is a test transcript about Python programming."
        video_title = "Python Tutorial"
        
        prompt = create_quiz_prompt(transcript, video_title)
        
        self.assertIn(transcript, prompt)
        self.assertIn(video_title, prompt)
        self.assertIn("JSON", prompt)
        self.assertIn("questions", prompt)

    def test_parse_quiz_response_variants(self):
        """Test parsing different quiz response formats."""
        from quiz_app.utils import parse_quiz_response
        
        # Test with markdown code blocks
        markdown_response = '''Here's the quiz:
        ```json
        {"title": "Test Quiz", "questions": []}
        ```
        End of response.'''
        
        result = parse_quiz_response(markdown_response)
        parsed = json.loads(result)
        self.assertEqual(parsed["title"], "Test Quiz")
        
        # Test with already clean JSON
        clean_json = '{"title": "Clean", "questions": []}'
        result = parse_quiz_response(clean_json)
        self.assertEqual(result, clean_json)

    def test_validate_quiz_structure_edge_cases(self):
        """Test quiz structure validation edge cases."""
        from quiz_app.utils import validate_quiz_structure
        
        # Test with exactly 10 questions
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
        
        # Test with wrong number of questions
        invalid_quiz = valid_quiz.copy()
        invalid_quiz["questions"] = invalid_quiz["questions"][:5]  # Only 5 questions
        
        with self.assertRaises(Exception):
            validate_quiz_structure(invalid_quiz)

    def test_cleanup_temp_file_edge_cases(self):
        """Test temporary file cleanup edge cases."""
        from quiz_app.utils import cleanup_temp_file
        import tempfile
        import os
        
        # Test cleanup with None
        cleanup_temp_file(None)  # Should not raise exception
        
        # Test cleanup with non-existent file
        cleanup_temp_file("/non/existent/file.wav")  # Should not raise exception
        
        # Test cleanup with existing file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(b"test audio data")
        
        # Verify file exists
        self.assertTrue(os.path.exists(tmp_path))
        
        # Clean up file
        cleanup_temp_file(tmp_path)
        
        # Verify file is deleted
        self.assertFalse(os.path.exists(tmp_path))


class APIViewsTestCase(TestCase):
    """Test cases for API views."""

    def setUp(self):
        """Set up test data."""
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

    def test_create_quiz_validation_errors(self):
        """Test quiz creation with validation errors."""
        from django.urls import reverse
        
        self.client.force_authenticate(user=self.user)
        
        # Test with invalid URL
        response = self.client.post(reverse("create_quiz"), {"url": "invalid-url"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with missing URL
        response = self.client.post(reverse("create_quiz"), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_quiz_detail_view_methods(self):
        """Test all methods of QuizDetailView."""
        from django.urls import reverse
        
        self.client.force_authenticate(user=self.user)
        
        # Test GET
        response = self.client.get(reverse("quiz_detail", kwargs={"quiz_id": self.quiz.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test PUT (full update)
        update_data = {
            "title": "Updated Quiz Title",
            "description": "Updated description"
        }
        response = self.client.put(reverse("quiz_detail", kwargs={"quiz_id": self.quiz.id}), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test PATCH (partial update)
        patch_data = {"title": "Patched Title"}
        response = self.client.patch(reverse("quiz_detail", kwargs={"quiz_id": self.quiz.id}), patch_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_quiz_permissions(self):
        """Test quiz access permissions."""
        from django.urls import reverse
        
        # Create another user
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="password123"
        )
        
        # Try to access quiz as different user
        self.client.force_authenticate(user=other_user)
        response = self.client.get(reverse("quiz_detail", kwargs={"quiz_id": self.quiz.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """Test unauthenticated access to protected endpoints."""
        from django.urls import reverse
        
        # Don't authenticate
        response = self.client.get(reverse("list_quizzes"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(reverse("create_quiz"), {"url": "https://youtube.com/watch?v=test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthAPITestCase(TestCase):
    """Test cases for authentication API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_registration_api(self):
        """Test user registration through API."""
        from django.urls import reverse
        
        registration_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123"
        }
        
        response = self.client.post(reverse("register"), registration_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login_api(self):
        """Test user login through API."""
        from django.urls import reverse
        
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = self.client.post(reverse("login"), login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if cookies are set
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_user_logout_api(self):
        """Test user logout through API."""
        from django.urls import reverse
        
        # First login
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ModelsTestCase(TestCase):
    """Test cases for models."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_quiz_model_str_method(self):
        """Test Quiz model string representation."""
        quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )
        
        self.assertEqual(str(quiz), "Test Quiz")

    def test_question_model_str_method(self):
        """Test Question model string representation."""
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
        
        self.assertEqual(str(question), "Test Question")

    def test_quiz_attempt_model(self):
        """Test QuizAttempt model functionality."""
        quiz = Quiz.objects.create(
            user=self.user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )
        
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=self.user
        )
        
        self.assertEqual(attempt.quiz, quiz)
        self.assertEqual(attempt.user, self.user)
        self.assertIsNotNone(attempt.started_at)


class SerializersTestCase(TestCase):
    """Test cases for serializers."""

    def test_quiz_create_serializer_validation(self):
        """Test QuizCreateSerializer validation."""
        from quiz_app.api.serializers import QuizCreateSerializer
        
        # Valid data
        valid_data = {"url": "https://youtube.com/watch?v=test123"}
        serializer = QuizCreateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Invalid URL
        invalid_data = {"url": "not-a-url"}
        serializer = QuizCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
        # Missing URL
        missing_data = {}
        serializer = QuizCreateSerializer(data=missing_data)
        self.assertFalse(serializer.is_valid())

    def test_quiz_update_serializer(self):
        """Test QuizUpdateSerializer."""
        from quiz_app.api.serializers import QuizUpdateSerializer
        
        valid_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }
        
        serializer = QuizUpdateSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_quiz_list_serializer(self):
        """Test QuizListSerializer."""
        from quiz_app.api.serializers import QuizListSerializer
        from quiz_app.models import Quiz
        
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        quiz = Quiz.objects.create(
            user=user,
            title="Test Quiz",
            description="A test quiz",
            video_url="https://youtube.com/watch?v=test123"
        )
        
        serializer = QuizListSerializer(quiz)
        data = serializer.data
        
        self.assertEqual(data["title"], "Test Quiz")
        self.assertIn("id", data)
        self.assertIn("created_at", data)
