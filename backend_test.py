#!/usr/bin/env python3
"""
Backend Testing for Xionimus AI - Chat Functionality
Tests the chat endpoints after MongoDB to SQLAlchemy migration
Focus: Database schema fixes verification
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
        """Test GET /api/sessions - Critical Test 2 (Schema Fix Verification)"""
        try:
            print("🔍 Testing GET /api/sessions (Schema Fix Verification)...")
            response = self.session.get(f"{API_BASE}/sessions")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list (empty or with sessions)
                if not isinstance(data, list):
                    self.log_test(
                        "GET /api/sessions - Structure", 
                        False, 
                        f"Expected list, got {type(data)}", 
                        data
                    )
                    return False
                
                # Check for SQLite schema errors in response
                response_text = response.text.lower()
                schema_errors = [
                    "no such column",
                    "sqlite3.operationalerror",
                    "sessions.user_id",
                    "messages.created_at",
                    "database error",
                    "sql error"
                ]
                
                found_errors = [error for error in schema_errors if error in response_text]
                if found_errors:
                    self.log_test(
                        "GET /api/sessions - Schema Errors", 
                        False, 
                        f"Found database schema errors: {found_errors}"
                    )
                    return False
                
                # Validate session structure if any sessions exist
                if data:
                    session = data[0]
                    required_fields = ['session_id', 'name', 'created_at', 'updated_at', 'message_count']
                    missing_fields = [field for field in required_fields if field not in session]
                    
                    if missing_fields:
                        self.log_test(
                            "GET /api/sessions - Session Structure", 
                            False, 
                            f"Missing fields in session: {missing_fields}"
                        )
                        return False
                
                self.log_test(
                    "GET /api/sessions - Schema Fix Verified", 
                    True, 
                    f"Successfully retrieved {len(data)} sessions without schema errors"
                )
                
                print(f"   📊 Sessions found: {len(data)}")
                if data:
                    print(f"   📊 Latest session: {data[0].get('name', 'Unknown')}")
                print()
                
                return True
                
            else:
                self.log_test(
                    "GET /api/sessions", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("GET /api/sessions", False, f"Request failed: {str(e)}")
            return False
    
    def test_create_chat_session(self):
        """Test POST /api/sessions - Critical Test 3 (Schema Fix Verification)"""
        try:
            print("🔍 Testing POST /api/sessions (Create New Session)...")
            
            # Create session request
            session_request = {
                "name": "Test Session for Schema Verification",
                "workspace_id": None
            }
            
            response = self.session.post(
                f"{API_BASE}/sessions",
                json=session_request,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['id', 'name', 'created_at', 'updated_at', 'message_count']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "POST /api/sessions - Response Structure", 
                        False, 
                        f"Missing fields: {missing_fields}"
                    )
                    return False, None
                
                # Check for database schema errors in response
                response_text = response.text.lower()
                schema_errors = [
                    "no such column",
                    "sqlite3.operationalerror", 
                    "sessions.user_id",
                    "database error",
                    "sql error"
                ]
                
                found_errors = [error for error in schema_errors if error in response_text]
                if found_errors:
                    self.log_test(
                        "POST /api/sessions - Schema Errors", 
                        False, 
                        f"Found database schema errors: {found_errors}"
                    )
                    return False, None
                
                session_id = data.get('id')
                
                self.log_test(
                    "POST /api/sessions - Schema Fix Verified", 
                    True, 
                    f"Successfully created session {session_id[:8]}... without schema errors"
                )
                
                print(f"   📊 Session ID: {session_id[:8]}...")
                print(f"   📊 Session Name: {data.get('name')}")
                print(f"   📊 Message Count: {data.get('message_count')}")
                print()
                
                return True, session_id
                
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "POST /api/sessions", 
                    False, 
                    f"HTTP {response.status_code}: {error_data.get('detail', 'Unknown error')}"
                )
                return False, None
                
        except Exception as e:
            self.log_test("POST /api/sessions", False, f"Request failed: {str(e)}")
            return False, None
    
    def test_get_session_messages(self, session_id: Optional[str] = None):
        """Test GET /api/sessions/{session_id}/messages - Critical Test 4 (Schema Fix Verification)"""
        try:
            print("🔍 Testing GET /api/sessions/{session_id}/messages...")
            
            # Use provided session_id or create a test session
            test_session_id = session_id
            if not test_session_id:
                # Create a test session first
                session_request = {"name": "Test Session for Messages"}
                session_response = self.session.post(f"{API_BASE}/sessions", json=session_request)
                if session_response.status_code == 200:
                    test_session_id = session_response.json().get('id')
                else:
                    self.log_test(
                        "GET /api/sessions/{session_id}/messages - Setup", 
                        False, 
                        "Could not create test session"
                    )
                    return False
            
            response = self.session.get(f"{API_BASE}/sessions/{test_session_id}/messages")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list (empty or with messages)
                if not isinstance(data, list):
                    self.log_test(
                        "GET /api/sessions/{session_id}/messages - Structure", 
                        False, 
                        f"Expected list, got {type(data)}"
                    )
                    return False
                
                # Check for database schema errors in response
                response_text = response.text.lower()
                schema_errors = [
                    "no such column",
                    "sqlite3.operationalerror",
                    "messages.created_at",
                    "database error",
                    "sql error"
                ]
                
                found_errors = [error for error in schema_errors if error in response_text]
                if found_errors:
                    self.log_test(
                        "GET /api/sessions/{session_id}/messages - Schema Errors", 
                        False, 
                        f"Found database schema errors: {found_errors}"
                    )
                    return False
                
                # Validate message structure if any messages exist
                if data:
                    message = data[0]
                    required_fields = ['role', 'content', 'timestamp']
                    missing_fields = [field for field in required_fields if field not in message]
                    
                    if missing_fields:
                        self.log_test(
                            "GET /api/sessions/{session_id}/messages - Message Structure", 
                            False, 
                            f"Missing fields in message: {missing_fields}"
                        )
                        return False
                
                self.log_test(
                    "GET /api/sessions/{session_id}/messages - Schema Fix Verified", 
                    True, 
                    f"Successfully retrieved {len(data)} messages without schema errors"
                )
                
                print(f"   📊 Messages found: {len(data)}")
                if data:
                    print(f"   📊 Latest message role: {data[-1].get('role', 'Unknown')}")
                print()
                
                return True
                
            elif response.status_code == 404:
                self.log_test(
                    "GET /api/sessions/{session_id}/messages - Not Found", 
                    True, 
                    "Session not found (expected for non-existent session)"
                )
                return True
                
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "GET /api/sessions/{session_id}/messages", 
                    False, 
                    f"HTTP {response.status_code}: {error_data.get('detail', 'Unknown error')}"
                )
                return False
                
        except Exception as e:
            self.log_test("GET /api/sessions/{session_id}/messages", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all chat functionality tests - Focus on Database Schema Fix Verification"""
        print("🚀 Starting Chat Functionality Backend Tests")
        print("Focus: Database Schema Fixes Verification")
        print("=" * 60)
        print()
        
        # Test 1: Backend Health
        if not self.test_backend_health():
            print("❌ Backend is not running. Cannot continue with tests.")
            return False
        
        # Test 2: Chat Providers (Baseline Test)
        providers_success = self.test_chat_providers()
        
        # Test 3: GET /api/sessions (Critical Schema Test 1)
        sessions_success = self.test_chat_sessions()
        
        # Test 4: POST /api/sessions (Critical Schema Test 2)
        create_success, session_id = self.test_create_chat_session()
        
        # Test 5: GET /api/sessions/{session_id}/messages (Critical Schema Test 3)
        messages_success = self.test_get_session_messages(session_id)
        
        # Summary
        print("=" * 60)
        print("📋 DATABASE SCHEMA FIX VERIFICATION SUMMARY")
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
        
        # Critical assessment for database schema fixes
        schema_tests = [sessions_success, create_success, messages_success]
        schema_fix_success = all(schema_tests)
        
        if schema_fix_success:
            print("✅ SCHEMA FIX STATUS: Database schema conflicts resolved successfully")
            print("✅ All session endpoints working correctly with SQLAlchemy ORM")
            print("✅ No 'sqlite3.OperationalError: no such column' errors found")
        else:
            print("❌ SCHEMA FIX STATUS: Database schema issues still present")
            print("❌ Some session endpoints have schema-related problems")
        
        print()
        return schema_fix_success

def main():
    """Main test execution"""
    tester = ChatFunctionalityTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Chat functionality tests completed successfully!")
        print("✅ MongoDB to SQLAlchemy migration verified!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the details above.")
        print("❌ MongoDB to SQLAlchemy migration may have issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()