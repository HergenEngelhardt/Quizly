with open('quiz_app/tests.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Replace the ViewHelpersTestCase completely
new_helper_class = """class ViewHelpersTestCase(TestCase):
    \"\"\"Test cases for view helper functions.\"\"\"

    def setUp(self):
        \"\"\"Set up test data for view helpers.\"\"\"
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
        \"\"\"Test QuizDetailView get_user_quiz helper method.\"\"\"
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
        \"\"\"Test individual view helper functions.\"\"\"
        from .api.views import validate_quiz_creation_data, cleanup_quiz_creation
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


"""

# Find the lines to replace (329 to 378, 0-indexed)
start_idx = 329  # Line 330 in 1-indexed
end_idx = 378    # Line 379 in 1-indexed

# Replace the lines
new_lines = lines[:start_idx] + [new_helper_class] + lines[end_idx:]

with open('quiz_app/tests.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('ViewHelpersTestCase replaced successfully')
