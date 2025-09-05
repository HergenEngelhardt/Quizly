with open('quiz_app/tests.py', 'r') as f:
    content = f.read()

# Remove debug prints
old_test = '''        response = self.client.put(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}), update_data, format='json')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)'''

new_test = '''        response = self.client.put(reverse("quiz_detail", kwargs={"quiz_id": quiz.id}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)'''

content = content.replace(old_test, new_test)

with open('quiz_app/tests.py', 'w') as f:
    f.write(content)

print('Debug output removed successfully')
