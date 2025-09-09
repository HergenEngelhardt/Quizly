#!/usr/bin/env python
"""
Test script to verify API compliance with specification.
This script tests all endpoints to ensure they match the exact specification.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_auth_endpoints():
    """Test authentication endpoints."""
    print("=== Testing Authentication Endpoints ===")
    
    # Test registration
    print("\n1. Testing POST /api/register/")
    register_data = {
        "username": "testuser",
        "password": "testpassword123",
        "email": "test@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register/", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Check if response matches spec: {"detail": "User created successfully!"}
        if response.status_code == 201:
            response_data = response.json()
            if response_data.get("detail") == "User created successfully!":
                print("✅ Register response matches specification")
            else:
                print("❌ Register response does NOT match specification")
                print(f"Expected: {{'detail': 'User created successfully!'}}")
                print(f"Got: {response_data}")
        
    except Exception as e:
        print(f"❌ Error testing register: {e}")
    
    # Test login
    print("\n2. Testing POST /api/login/")
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Check if response matches spec
        if response.status_code == 200:
            response_data = response.json()
            required_keys = ["detail", "user"]
            user_keys = ["id", "username", "email"]
            
            if (response_data.get("detail") == "Login successfully!" and 
                "user" in response_data and
                all(key in response_data["user"] for key in user_keys)):
                print("✅ Login response matches specification")
            else:
                print("❌ Login response does NOT match specification")
        
        # Store cookies for further tests
        cookies = response.cookies
        
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        cookies = None
    
    # Test logout
    print("\n3. Testing POST /api/logout/")
    try:
        response = requests.post(f"{BASE_URL}/logout/", cookies=cookies if cookies else {})
        print(f"Status: {response.status_code}")
        if response.content:
            print(f"Response: {response.json()}")
            
            # Check if response matches spec
            if response.status_code == 200:
                response_data = response.json()
                expected_detail = "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
                if response_data.get("detail") == expected_detail:
                    print("✅ Logout response matches specification")
                else:
                    print("❌ Logout response does NOT match specification")
                    print(f"Expected: {{'detail': '{expected_detail}'}}")
                    print(f"Got: {response_data}")
        
    except Exception as e:
        print(f"❌ Error testing logout: {e}")
    
    # Test token refresh
    print("\n4. Testing POST /api/token/refresh/")
    try:
        response = requests.post(f"{BASE_URL}/token/refresh/", cookies=cookies if cookies else {})
        print(f"Status: {response.status_code}")
        if response.content:
            print(f"Response: {response.json()}")
            
            # Check if response matches spec
            if response.status_code == 200:
                response_data = response.json()
                if (response_data.get("detail") == "Token refreshed" and 
                    "access" in response_data):
                    print("✅ Token refresh response matches specification")
                else:
                    print("❌ Token refresh response does NOT match specification")
        
    except Exception as e:
        print(f"❌ Error testing token refresh: {e}")

def test_quiz_endpoints():
    """Test quiz endpoints (requires authentication)."""
    print("\n=== Testing Quiz Endpoints ===")
    
    # First login to get authentication
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/login/", json=login_data)
        if login_response.status_code != 200:
            print("❌ Cannot test quiz endpoints - login failed")
            return
            
        cookies = login_response.cookies
        
        # Test create quiz
        print("\n1. Testing POST /api/createQuiz/")
        create_data = {
            "url": "https://www.youtube.com/watch?v=example"
        }
        
        response = requests.post(f"{BASE_URL}/createQuiz/", json=create_data, cookies=cookies)
        print(f"Status: {response.status_code}")
        if response.content:
            response_data = response.json()
            print(f"Response keys: {list(response_data.keys())}")
            
            # Check if response structure matches spec
            required_keys = ["id", "title", "description", "created_at", "updated_at", "video_url", "questions"]
            if response.status_code == 201 and all(key in response_data for key in required_keys):
                print("✅ Create quiz response structure matches specification")
                quiz_id = response_data["id"]
            else:
                print("❌ Create quiz response does NOT match specification")
                quiz_id = None
        
        # Test list quizzes
        print("\n2. Testing GET /api/quizzes/")
        response = requests.get(f"{BASE_URL}/quizzes/", cookies=cookies)
        print(f"Status: {response.status_code}")
        if response.content:
            response_data = response.json()
            print(f"Response type: {type(response_data)}")
            
            # Check if response is a list
            if response.status_code == 200 and isinstance(response_data, list):
                print("✅ List quizzes response matches specification (returns list)")
            else:
                print("❌ List quizzes response does NOT match specification")
        
        # Test get specific quiz
        if quiz_id:
            print(f"\n3. Testing GET /api/quizzes/{quiz_id}/")
            response = requests.get(f"{BASE_URL}/quizzes/{quiz_id}/", cookies=cookies)
            print(f"Status: {response.status_code}")
            if response.content:
                response_data = response.json()
                print(f"Response keys: {list(response_data.keys())}")
                
                # Check response structure
                required_keys = ["id", "title", "description", "created_at", "updated_at", "video_url", "questions"]
                if response.status_code == 200 and all(key in response_data for key in required_keys):
                    print("✅ Get quiz response structure matches specification")
                else:
                    print("❌ Get quiz response does NOT match specification")
            
            # Test update quiz (PUT)
            print(f"\n4. Testing PUT /api/quizzes/{quiz_id}/")
            update_data = {
                "title": "Updated Quiz Title",
                "description": "Updated Quiz Description", 
                "video_url": "https://www.youtube.com/watch?v=updated"
            }
            response = requests.put(f"{BASE_URL}/quizzes/{quiz_id}/", json=update_data, cookies=cookies)
            print(f"Status: {response.status_code}")
            if response.content:
                response_data = response.json()
                if response.status_code == 200:
                    print("✅ PUT quiz response status matches specification")
                else:
                    print("❌ PUT quiz response status does NOT match specification")
            
            # Test partial update quiz (PATCH)
            print(f"\n5. Testing PATCH /api/quizzes/{quiz_id}/")
            patch_data = {
                "title": "Partially Updated Title"
            }
            response = requests.patch(f"{BASE_URL}/quizzes/{quiz_id}/", json=patch_data, cookies=cookies)
            print(f"Status: {response.status_code}")
            if response.content:
                response_data = response.json()
                if response.status_code == 200:
                    print("✅ PATCH quiz response status matches specification")
                else:
                    print("❌ PATCH quiz response status does NOT match specification")
            
            # Test delete quiz
            print(f"\n6. Testing DELETE /api/quizzes/{quiz_id}/")
            response = requests.delete(f"{BASE_URL}/quizzes/{quiz_id}/", cookies=cookies)
            print(f"Status: {response.status_code}")
            if response.status_code == 204:
                print("✅ DELETE quiz response status matches specification")
            else:
                print("❌ DELETE quiz response status does NOT match specification")
        
    except Exception as e:
        print(f"❌ Error testing quiz endpoints: {e}")

if __name__ == "__main__":
    print("API Compliance Test")
    print("==================")
    print("This script tests if the API endpoints match the exact specification.")
    print("\nNote: Make sure the Django development server is running on localhost:8000")
    
    # Test endpoints
    test_auth_endpoints()
    test_quiz_endpoints()
    
    print("\n=== Test Summary ===")
    print("Check the output above for any ❌ marks indicating specification mismatches.")
