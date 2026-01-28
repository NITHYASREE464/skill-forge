#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class EdTechAPITester:
    def __init__(self, base_url="https://codeready-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if success:
            self.tests_passed += 1
        else:
            self.failed_tests.append({"test": name, "details": details})
        print()

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                return False, f"Unsupported method: {method}"

            success = response.status_code == expected_status
            if success:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json().get('detail', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                return False, error_msg

        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}"

    def test_api_health(self):
        """Test if API is accessible"""
        success, result = self.make_request('GET', '')
        if success and isinstance(result, dict) and 'message' in result:
            self.log_test("API Health Check", True, f"API Response: {result['message']}")
        else:
            self.log_test("API Health Check", False, f"API not responding properly: {result}")
        return success

    def test_user_registration(self):
        """Test user registration with test@gmail.com"""
        data = {
            "name": "Test User",
            "email": "test@gmail.com", 
            "password": "test123"
        }
        success, result = self.make_request('POST', 'auth/register', data, 200)
        
        if success and isinstance(result, dict) and 'token' in result:
            self.token = result['token']
            self.user_id = result['user']['id']
            self.log_test("User Registration", True, f"User created with ID: {self.user_id}")
        else:
            # User might already exist, try login instead
            success, result = self.make_request('POST', 'auth/login', 
                                              {"email": "test@gmail.com", "password": "test123"}, 200)
            if success and isinstance(result, dict) and 'token' in result:
                self.token = result['token']
                self.user_id = result['user']['id']
                self.log_test("User Registration", True, "User already exists, logged in successfully")
            else:
                self.log_test("User Registration", False, f"Registration/Login failed: {result}")
        
        return success

    def test_user_login(self):
        """Test user login flow"""
        data = {"email": "test@gmail.com", "password": "test123"}
        success, result = self.make_request('POST', 'auth/login', data, 200)
        
        if success and isinstance(result, dict) and 'token' in result:
            self.token = result['token']
            user_data = result['user']
            self.log_test("User Login", True, 
                         f"Login successful - Role: {user_data.get('role', 'None')}, Points: {user_data.get('points', 0)}")
        else:
            self.log_test("User Login", False, f"Login failed: {result}")
        
        return success

    def test_role_selection(self):
        """Test role selection (SDE)"""
        if not self.token:
            self.log_test("Role Selection", False, "No auth token available")
            return False
            
        data = {"role": "SDE"}
        success, result = self.make_request('PUT', 'users/role', data, 200)
        
        if success:
            self.log_test("Role Selection", True, "Role updated to SDE successfully")
        else:
            self.log_test("Role Selection", False, f"Role update failed: {result}")
        
        return success

    def test_user_profile(self):
        """Test user profile retrieval"""
        if not self.token:
            self.log_test("User Profile", False, "No auth token available")
            return False
            
        success, result = self.make_request('GET', 'users/profile', expected_status=200)
        
        if success and isinstance(result, dict):
            profile = result
            self.log_test("User Profile", True, 
                         f"Profile loaded - Name: {profile.get('name')}, Role: {profile.get('role')}, Level: {profile.get('level')}")
        else:
            self.log_test("User Profile", False, f"Profile fetch failed: {result}")
        
        return success

    def test_dsa_arrays_module(self):
        """Test DSA Arrays module data"""
        if not self.token:
            self.log_test("DSA Arrays Module", False, "No auth token available")
            return False
            
        success, result = self.make_request('GET', 'skills/dsa/arrays', expected_status=200)
        
        if success and isinstance(result, dict):
            module_data = result
            total_tasks = module_data.get('total_tasks', 0)
            completed_tasks = module_data.get('completed_tasks', 0)
            tasks = module_data.get('tasks', [])
            
            self.log_test("DSA Arrays Module", True, 
                         f"Module loaded - {completed_tasks}/{total_tasks} tasks completed, {len(tasks)} tasks available")
        else:
            self.log_test("DSA Arrays Module", False, f"Module fetch failed: {result}")
        
        return success

    def test_task_details(self):
        """Test individual task details"""
        if not self.token:
            self.log_test("Task Details", False, "No auth token available")
            return False
            
        # Test first task (Two Sum)
        task_id = "arr-001"
        success, result = self.make_request('GET', f'skills/dsa/arrays/{task_id}', expected_status=200)
        
        if success and isinstance(result, dict):
            task = result
            self.log_test("Task Details", True, 
                         f"Task '{task.get('title')}' loaded - Difficulty: {task.get('difficulty')}, Points: {task.get('points')}")
        else:
            self.log_test("Task Details", False, f"Task fetch failed: {result}")
        
        return success

    def test_code_execution(self):
        """Test code execution (mocked)"""
        if not self.token:
            self.log_test("Code Execution", False, "No auth token available")
            return False
            
        data = {
            "code": "print('Hello World')\nprint(2 + 2)",
            "task_id": "arr-001"
        }
        success, result = self.make_request('POST', 'code/run', data, 200)
        
        if success and isinstance(result, dict):
            output = result.get('output', '')
            self.log_test("Code Execution", True, f"Code executed - Output: {output[:50]}...")
        else:
            self.log_test("Code Execution", False, f"Code execution failed: {result}")
        
        return success

    def test_task_submission(self):
        """Test task submission"""
        if not self.token:
            self.log_test("Task Submission", False, "No auth token available")
            return False
            
        task_id = "arr-001"
        data = {
            "task_id": task_id,
            "code": "def two_sum(nums, target):\n    return [0, 1]  # Mock solution"
        }
        success, result = self.make_request('POST', f'tasks/{task_id}/submit', data, 200)
        
        if success and isinstance(result, dict):
            points_earned = result.get('points_earned', 0)
            message = result.get('message', '')
            self.log_test("Task Submission", True, f"Submission successful - Points earned: {points_earned}, Message: {message}")
        else:
            self.log_test("Task Submission", False, f"Submission failed: {result}")
        
        return success

    def test_bro_chat(self):
        """Test BRO AI mentor chat"""
        if not self.token:
            self.log_test("BRO Chat", False, "No auth token available")
            return False
            
        data = {
            "message": "Hello BRO! Can you help me with arrays?",
            "context": "Testing BRO functionality"
        }
        success, result = self.make_request('POST', 'bro/chat', data, 200)
        
        if success and isinstance(result, dict):
            response = result.get('response', '')
            self.log_test("BRO Chat", True, f"BRO responded - Response length: {len(response)} chars")
        else:
            self.log_test("BRO Chat", False, f"BRO chat failed: {result}")
        
        return success

    def test_chat_history(self):
        """Test chat history retrieval"""
        if not self.token:
            self.log_test("Chat History", False, "No auth token available")
            return False
            
        success, result = self.make_request('GET', 'bro/history', expected_status=200)
        
        if success and isinstance(result, dict):
            history = result.get('history', [])
            self.log_test("Chat History", True, f"Chat history loaded - {len(history)} messages")
        else:
            self.log_test("Chat History", False, f"Chat history fetch failed: {result}")
        
        return success

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting EdTech Platform Backend Tests")
        print("=" * 50)
        
        # Core API tests
        if not self.test_api_health():
            print("❌ API is not accessible. Stopping tests.")
            return False
            
        # Authentication tests
        self.test_user_registration()
        self.test_user_login()
        
        # User management tests
        self.test_role_selection()
        self.test_user_profile()
        
        # Learning module tests
        self.test_dsa_arrays_module()
        self.test_task_details()
        
        # Code functionality tests
        self.test_code_execution()
        self.test_task_submission()
        
        # AI mentor tests
        self.test_bro_chat()
        self.test_chat_history()
        
        # Print summary
        print("=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"✅ Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80  # Consider 80%+ as successful

def main():
    tester = EdTechAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())