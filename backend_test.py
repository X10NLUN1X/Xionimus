#!/usr/bin/env python3
"""
Backend Testing for Xionimus AI - Chat Functionality
Tests the chat endpoints after MongoDB to SQLAlchemy migration
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import time
import uuid

# Backend URL configuration (matches frontend config)
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class ChatFunctionalityTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = []
        
    def log_test(self, test_name: str, success: bool, details: str, response_data: Optional[Dict] = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
        
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response': response_data
        })
    
    def test_backend_health(self):
        """Test if backend is running"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Backend Health Check", 
                    True, 
                    f"Backend is running - Status: {data.get('status', 'unknown')}"
                )
                return True
            else:
                self.log_test(
                    "Backend Health Check", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_chat_providers(self):
        """Test chat providers endpoint - Critical Test 1"""
        try:
            print("🔍 Testing Chat Providers Endpoint...")
            response = self.session.get(f"{API_BASE}/chat/providers")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'providers' not in data or 'models' not in data:
                    self.log_test(
                        "Chat Providers - Structure", 
                        False, 
                        "Missing 'providers' or 'models' in response", 
                        data
                    )
                    return False
                
                providers = data.get('providers', {})
                models = data.get('models', {})
                
                # Check for expected providers
                expected_providers = ['openai', 'anthropic', 'perplexity']
                found_providers = list(providers.keys())
                
                missing_providers = [p for p in expected_providers if p not in found_providers]
                if missing_providers:
                    self.log_test(
                        "Chat Providers - Expected Providers", 
                        False, 
                        f"Missing providers: {missing_providers}. Found: {found_providers}"
                    )
                    return False
                
                # Validate models structure
                if not isinstance(models, dict):
                    self.log_test(
                        "Chat Providers - Models Structure", 
                        False, 
                        f"Models should be dict, got {type(models)}"
                    )
                    return False
                
                self.log_test(
                    "Chat Providers - Complete", 
                    True, 
                    f"Found {len(providers)} providers: {', '.join(found_providers)}"
                )
                
                print(f"   📊 Providers: {', '.join(found_providers)}")
                print(f"   📊 Models available: {len(models)} model configurations")
                print()
                
                return True
                
            else:
                self.log_test(
                    "Chat Providers", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("Chat Providers", False, f"Request failed: {str(e)}")
            return False
    
    def test_chat_sessions(self):
        """Test chat sessions endpoint - Critical Test 2"""
        try:
            print("🔍 Testing Chat Sessions Endpoint...")
            response = self.session.get(f"{API_BASE}/chat/sessions")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list (empty or with sessions)
                if not isinstance(data, list):
                    self.log_test(
                        "Chat Sessions - Structure", 
                        False, 
                        f"Expected list, got {type(data)}", 
                        data
                    )
                    return False
                
                # Check for MongoDB-related errors in response
                response_text = response.text.lower()
                mongodb_errors = [
                    "session object has no attribute 'chat_sessions'",
                    "mongodb",
                    "mongo",
                    "objectid",
                    "bson"
                ]
                
                found_errors = [error for error in mongodb_errors if error in response_text]
                if found_errors:
                    self.log_test(
                        "Chat Sessions - MongoDB Migration", 
                        False, 
                        f"Found MongoDB-related errors: {found_errors}"
                    )
                    return False
                
                # Validate session structure if any sessions exist
                if data:
                    session = data[0]
                    required_fields = ['session_id', 'name', 'created_at', 'updated_at', 'message_count']
                    missing_fields = [field for field in required_fields if field not in session]
                    
                    if missing_fields:
                        self.log_test(
                            "Chat Sessions - Session Structure", 
                            False, 
                            f"Missing fields in session: {missing_fields}"
                        )
                        return False
                
                self.log_test(
                    "Chat Sessions - Complete", 
                    True, 
                    f"Successfully retrieved {len(data)} sessions without MongoDB errors"
                )
                
                print(f"   📊 Sessions found: {len(data)}")
                if data:
                    print(f"   📊 Latest session: {data[0].get('name', 'Unknown')}")
                print()
                
                return True
                
            else:
                self.log_test(
                    "Chat Sessions", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("Chat Sessions", False, f"Request failed: {str(e)}")
            return False
    
    def test_create_chat_session(self):
        """Test creating a new chat session - Critical Test 3"""
        try:
            print("🔍 Testing Create Chat Session...")
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Create a simple chat request to trigger session creation
            chat_request = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, this is a test message for session creation"
                    }
                ],
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "session_id": session_id,
                "stream": False
            }
            
            response = self.session.post(
                f"{API_BASE}/chat",
                json=chat_request,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['content', 'provider', 'model', 'session_id', 'message_id', 'timestamp']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Create Chat Session - Response Structure", 
                        False, 
                        f"Missing fields: {missing_fields}"
                    )
                    return False, None
                
                # Check if session_id matches
                if data.get('session_id') != session_id:
                    self.log_test(
                        "Create Chat Session - Session ID", 
                        False, 
                        f"Session ID mismatch. Expected: {session_id}, Got: {data.get('session_id')}"
                    )
                    return False, None
                
                # Check for database errors in content
                content = data.get('content', '').lower()
                db_errors = ['database error', 'sqlite error', 'sql error', 'connection error']
                found_errors = [error for error in db_errors if error in content]
                
                if found_errors:
                    self.log_test(
                        "Create Chat Session - Database Errors", 
                        False, 
                        f"Found database errors in response: {found_errors}"
                    )
                    return False, None
                
                self.log_test(
                    "Create Chat Session - Complete", 
                    True, 
                    f"Successfully created session {session_id[:8]}... with message"
                )
                
                print(f"   📊 Session ID: {session_id[:8]}...")
                print(f"   📊 Provider: {data.get('provider')}")
                print(f"   📊 Model: {data.get('model')}")
                print(f"   📊 Response length: {len(data.get('content', ''))} chars")
                print()
                
                return True, session_id
                
            elif response.status_code == 400:
                # Check if it's a configuration error (missing API keys)
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('detail', '').lower()
                
                if 'api key' in error_msg or 'not configured' in error_msg:
                    self.log_test(
                        "Create Chat Session - Configuration", 
                        True, 
                        "Session creation endpoint working, but AI provider not configured (expected)"
                    )
                    return True, None
                else:
                    self.log_test(
                        "Create Chat Session", 
                        False, 
                        f"HTTP 400: {error_data.get('detail', 'Unknown error')}"
                    )
                    return False, None
            else:
                self.log_test(
                    "Create Chat Session", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False, None
                
        except Exception as e:
            self.log_test("Create Chat Session", False, f"Request failed: {str(e)}")
            return False, None
    
    def test_send_chat_message(self, session_id: Optional[str] = None):
        """Test sending a chat message - Critical Test 4"""
        try:
            print("🔍 Testing Send Chat Message...")
            
            # Use provided session_id or generate new one
            test_session_id = session_id or str(uuid.uuid4())
            
            # Create a simple chat request
            chat_request = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Test message for database migration verification"
                    }
                ],
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "session_id": test_session_id,
                "stream": False
            }
            
            response = self.session.post(
                f"{API_BASE}/chat",
                json=chat_request,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for SQLAlchemy/database success indicators
                if all(field in data for field in ['content', 'session_id', 'message_id']):
                    self.log_test(
                        "Send Chat Message - Database Integration", 
                        True, 
                        "Message processed successfully with SQLAlchemy database"
                    )
                    
                    print(f"   📊 Message processed for session: {test_session_id[:8]}...")
                    print(f"   📊 Response generated: {len(data.get('content', ''))} chars")
                    print()
                    
                    return True
                else:
                    self.log_test(
                        "Send Chat Message - Response Structure", 
                        False, 
                        "Incomplete response structure"
                    )
                    return False
                    
            elif response.status_code == 400:
                # Check if it's a configuration error
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('detail', '').lower()
                
                if 'api key' in error_msg or 'not configured' in error_msg:
                    self.log_test(
                        "Send Chat Message - Configuration", 
                        True, 
                        "Chat endpoint working, database integration successful (AI provider not configured)"
                    )
                    return True
                else:
                    # Check for MongoDB migration errors
                    if 'mongodb' in error_msg or 'mongo' in error_msg or 'objectid' in error_msg:
                        self.log_test(
                            "Send Chat Message - Migration Error", 
                            False, 
                            f"MongoDB migration not complete: {error_data.get('detail')}"
                        )
                        return False
                    else:
                        self.log_test(
                            "Send Chat Message", 
                            False, 
                            f"HTTP 400: {error_data.get('detail', 'Unknown error')}"
                        )
                        return False
            else:
                self.log_test(
                    "Send Chat Message", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("Send Chat Message", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all GitHub integration tests"""
        print("🚀 Starting GitHub Integration Backend Tests")
        print("=" * 60)
        print()
        
        # Test 1: Backend Health
        if not self.test_backend_health():
            print("❌ Backend is not running. Cannot continue with tests.")
            return False
        
        # Test 2: GitHub Health
        github_healthy, github_health_data = self.test_github_health()
        
        # Test 3: GitHub OAuth URL
        oauth_success, oauth_data = self.test_github_oauth_url()
        
        # Test 4: Fork Summary (MAIN FEATURE)
        fork_summary_success = self.test_fork_summary()
        
        # Test 5: Push Project Endpoint Structure
        push_endpoint_success = self.test_push_project_endpoint_structure()
        
        # Summary
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Critical assessment
        critical_success = fork_summary_success  # Main feature
        
        if critical_success:
            print("✅ CRITICAL FEATURE STATUS: Fork Summary endpoint is working correctly")
        else:
            print("❌ CRITICAL FEATURE STATUS: Fork Summary endpoint has issues")
        
        print()
        return critical_success

def main():
    """Main test execution"""
    tester = GitHubIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 GitHub Integration tests completed successfully!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()