with open('quiz_app/tests.py', 'r') as f:
    content = f.read()

# Replace the update_data section
old_data = '''        update_data = {
            "title": "Updated Test Quiz",
            "description": "An updated test quiz"
        }'''

new_data = '''        update_data = {
            "title": "Updated Test Quiz",
            "description": "An updated test quiz",
            "video_url": "https://youtube.com/watch?v=updated123"
        }'''

content = content.replace(old_data, new_data)

with open('quiz_app/tests.py', 'w') as f:
    f.write(content)

print('Update data modified successfully')
