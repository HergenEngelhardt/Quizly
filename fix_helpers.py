with open('quiz_app/tests.py', 'r') as f:
    content = f.read()

# Fix the ViewHelpersTestCase problems
# 1. Fix the get_user_quiz test - it returns a tuple
old_helper_test_1 = '''          # Test valid access
          quiz = view.get_user_quiz(self.quiz.id, self.user)
          self.assertEqual(quiz.id, self.quiz.id)

          # Test access to non-existent quiz
          with self.assertRaises(Exception):
              view.get_user_quiz(999, self.user)'''

new_helper_test_1 = '''          # Test valid access
          quiz, error_response = view.get_user_quiz(self.quiz.id, self.user)
          self.assertIsNone(error_response)
          self.assertEqual(quiz.id, self.quiz.id)

          # Test access to non-existent quiz
          quiz, error_response = view.get_user_quiz(999, self.user)
          self.assertIsNotNone(error_response)
          self.assertIsNone(quiz)'''

content = content.replace(old_helper_test_1, new_helper_test_1)

# 2. Fix the validate_quiz_creation_data test - need to add request.data
old_helper_test_2 = '''          # Test validate_quiz_creation_data
          request = factory.post('/', {"url": "https://youtube.com/watch?v=test"})
          url, error = validate_quiz_creation_data(request)'''

new_helper_test_2 = '''          # Test validate_quiz_creation_data
          request = factory.post('/', {"url": "https://youtube.com/watch?v=test"}, format='json')
          request.data = {"url": "https://youtube.com/watch?v=test"}
          url, error = validate_quiz_creation_data(request)'''

content = content.replace(old_helper_test_2, new_helper_test_2)

with open('quiz_app/tests.py', 'w') as f:
    f.write(content)

print('ViewHelpersTestCase fixed successfully')
