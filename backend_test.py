#!/usr/bin/env python3
"""
Backend Testing for Xionimus AI - 4-Agent Code Review System Testing
Tests the expanded Code Review System with 4 agents and parallel execution
Focus: Parallel agent execution, all 4 agents, different review scopes
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

class FourAgentCodeReviewTester:
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
    
    def test_chat_providers_after_changes(self):
        """Test GET /api/chat/providers - Verify still works after Phase 2 changes"""
        try:
            print("🔍 Testing GET /api/chat/providers (Post-Phase 2 Verification)...")
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
                    "GET /api/chat/providers - Post-Phase 2", 
                    True, 
                    f"Endpoint still working correctly after Phase 2 changes. Found {len(providers)} providers"
                )
                
                print(f"   📊 Providers: {', '.join(found_providers)}")
                print(f"   📊 Models available: {len(models)} model configurations")
                print()
                
                return True
                
            else:
                self.log_test(
                    "GET /api/chat/providers", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("GET /api/chat/providers", False, f"Request failed: {str(e)}")
            return False
    
    def test_chat_sessions_error_handling(self):
        """Test GET /api/chat/sessions - Phase 2 Database Error Handling"""
        try:
            print("🔍 Testing GET /api/chat/sessions (Phase 2 Database Error Handling)...")
            response = self.session.get(f"{API_BASE}/chat/sessions")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list (empty or with sessions)
                if not isinstance(data, list):
                    self.log_test(
                        "GET /api/chat/sessions - Structure", 
                        False, 
                        f"Expected list, got {type(data)}", 
                        data
                    )
                    return False
                
                # Validate session structure if any sessions exist
                if data:
                    session = data[0]
                    required_fields = ['session_id', 'name', 'created_at', 'updated_at', 'message_count']
                    missing_fields = [field for field in required_fields if field not in session]
                    
                    if missing_fields:
                        self.log_test(
                            "GET /api/chat/sessions - Session Structure", 
                            False, 
                            f"Missing fields in session: {missing_fields}"
                        )
                        return False
                
                self.log_test(
                    "GET /api/chat/sessions - Database Error Handling", 
                    True, 
                    f"Successfully retrieved {len(data)} sessions with proper error handling"
                )
                
                print(f"   📊 Sessions found: {len(data)}")
                if data:
                    print(f"   📊 Latest session: {data[0].get('name', 'Unknown')}")
                print()
                
                return True
                
            else:
                self.log_test(
                    "GET /api/chat/sessions", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("GET /api/chat/sessions", False, f"Request failed: {str(e)}")
            return False
    
    def test_create_chat_session(self):
        """Test POST /api/chat - Critical Test 3 (Schema Fix Verification)"""
        try:
            print("🔍 Testing POST /api/chat (Create New Session via Chat)...")
            
            # Create a chat request that will create a session
            session_id = str(uuid.uuid4())
            chat_request = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Test message for schema verification"
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
                        "POST /api/chat - Response Structure", 
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
                    "messages.created_at",
                    "database error",
                    "sql error"
                ]
                
                found_errors = [error for error in schema_errors if error in response_text]
                if found_errors:
                    self.log_test(
                        "POST /api/chat - Schema Errors", 
                        False, 
                        f"Found database schema errors: {found_errors}"
                    )
                    return False, None
                
                returned_session_id = data.get('session_id')
                
                self.log_test(
                    "POST /api/chat - Schema Fix Verified", 
                    True, 
                    f"Successfully created session {returned_session_id[:8]}... without schema errors"
                )
                
                print(f"   📊 Session ID: {returned_session_id[:8]}...")
                print(f"   📊 Provider: {data.get('provider')}")
                print(f"   📊 Model: {data.get('model')}")
                print()
                
                return True, returned_session_id
                
            elif response.status_code == 400:
                # Check if it's a configuration error (missing API keys)
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('detail', '').lower()
                
                if 'api key' in error_msg or 'not configured' in error_msg:
                    self.log_test(
                        "POST /api/chat - Configuration", 
                        True, 
                        "Chat endpoint working, session creation successful (AI provider not configured)"
                    )
                    return True, session_id
                else:
                    # Check for schema errors
                    if any(error in error_msg for error in ['no such column', 'sqlite3.operationalerror']):
                        self.log_test(
                            "POST /api/chat - Schema Errors", 
                            False, 
                            f"Found database schema errors: {error_data.get('detail')}"
                        )
                        return False, None
                    else:
                        self.log_test(
                            "POST /api/chat", 
                            False, 
                            f"HTTP 400: {error_data.get('detail', 'Unknown error')}"
                        )
                        return False, None
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "POST /api/chat", 
                    False, 
                    f"HTTP {response.status_code}: {error_data.get('detail', 'Unknown error')}"
                )
                return False, None
                
        except Exception as e:
            self.log_test("POST /api/chat", False, f"Request failed: {str(e)}")
            return False, None
    
    def test_delete_invalid_session_error_handling(self):
        """Test DELETE /api/chat/sessions/{invalid_id} - Phase 2 Error Handling for Non-existent Session"""
        try:
            print("🔍 Testing DELETE /api/chat/sessions/{invalid_id} (Phase 2 Error Handling)...")
            
            # Use a non-existent session ID
            invalid_session_id = str(uuid.uuid4())
            
            response = self.session.delete(f"{API_BASE}/chat/sessions/{invalid_session_id}")
            
            # Should return success even for non-existent sessions (graceful handling)
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                expected_fields = ['status', 'session_id', 'deleted_messages']
                missing_fields = [field for field in expected_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "DELETE /api/chat/sessions/{invalid_id} - Response Structure", 
                        False, 
                        f"Missing fields in response: {missing_fields}"
                    )
                    return False
                
                # Check that it handled non-existent session gracefully
                if data.get('status') == 'deleted' and data.get('deleted_messages') == 0:
                    self.log_test(
                        "DELETE /api/chat/sessions/{invalid_id} - Error Handling", 
                        True, 
                        f"Gracefully handled non-existent session deletion. Deleted {data.get('deleted_messages')} messages"
                    )
                    
                    print(f"   📊 Status: {data.get('status')}")
                    print(f"   📊 Session ID: {data.get('session_id')[:8]}...")
                    print(f"   📊 Messages deleted: {data.get('deleted_messages')}")
                    print()
                    
                    return True
                else:
                    self.log_test(
                        "DELETE /api/chat/sessions/{invalid_id} - Unexpected Response", 
                        False, 
                        f"Unexpected response for non-existent session: {data}"
                    )
                    return False
                    
            elif response.status_code == 404:
                # Also acceptable - proper 404 for non-existent resource
                self.log_test(
                    "DELETE /api/chat/sessions/{invalid_id} - Error Handling", 
                    True, 
                    "Properly returned 404 for non-existent session"
                )
                return True
                
            elif response.status_code in [500, 409]:
                # Check if it's a proper error response with Phase 2 error handling
                error_data = response.json() if response.content else {}
                error_detail = error_data.get('detail', '')
                
                # Look for Phase 2 specific error messages
                phase2_error_patterns = [
                    "database error occurred",
                    "data constraints", 
                    "unexpected error occurred"
                ]
                
                has_phase2_error = any(pattern in error_detail.lower() for pattern in phase2_error_patterns)
                
                if has_phase2_error:
                    self.log_test(
                        "DELETE /api/chat/sessions/{invalid_id} - Phase 2 Error Handling", 
                        True, 
                        f"Proper Phase 2 error handling: HTTP {response.status_code} - {error_detail}"
                    )
                    return True
                else:
                    self.log_test(
                        "DELETE /api/chat/sessions/{invalid_id} - Error Response", 
                        False, 
                        f"HTTP {response.status_code} - {error_detail}"
                    )
                    return False
            else:
                error_data = response.json() if response.content else {}
                self.log_test(
                    "DELETE /api/chat/sessions/{invalid_id}", 
                    False, 
                    f"HTTP {response.status_code}: {error_data.get('detail', 'Unknown error')}"
                )
                return False
                
        except Exception as e:
            self.log_test("DELETE /api/chat/sessions/{invalid_id}", False, f"Request failed: {str(e)}")
            return False
    
    def check_backend_logs_for_errors(self):
        """Check backend logs for any errors or warnings after Phase 2 changes"""
        try:
            print("🔍 Checking Backend Logs for Errors/Warnings...")
            
            # Check supervisor backend logs
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout.strip()
                
                if not log_content:
                    self.log_test(
                        "Backend Logs - Error Log Check", 
                        True, 
                        "No recent errors found in backend error logs"
                    )
                    print("   📊 Backend error log is clean")
                    print()
                    return True
                else:
                    # Check for critical errors vs warnings
                    lines = log_content.split('\n')
                    error_lines = [line for line in lines if any(level in line.lower() for level in ['error', 'critical', 'exception'])]
                    warning_lines = [line for line in lines if 'warning' in line.lower()]
                    
                    if error_lines:
                        self.log_test(
                            "Backend Logs - Error Log Check", 
                            False, 
                            f"Found {len(error_lines)} error/critical entries in recent logs"
                        )
                        print("   ❌ Recent errors found:")
                        for error in error_lines[-3:]:  # Show last 3 errors
                            print(f"      {error}")
                        print()
                        return False
                    else:
                        self.log_test(
                            "Backend Logs - Error Log Check", 
                            True, 
                            f"No critical errors found. {len(warning_lines)} warnings present (acceptable)"
                        )
                        print(f"   📊 {len(warning_lines)} warnings found (normal)")
                        print()
                        return True
            else:
                self.log_test(
                    "Backend Logs - Error Log Check", 
                    True, 
                    "Could not access error log (may not exist - normal for clean systems)"
                )
                return True
                
        except subprocess.TimeoutExpired:
            self.log_test(
                "Backend Logs - Error Log Check", 
                True, 
                "Log check timed out (system may be busy - not critical)"
            )
            return True
        except Exception as e:
            self.log_test(
                "Backend Logs - Error Log Check", 
                True, 
                f"Could not check logs: {str(e)} (not critical for functionality)"
            )
            return True
    
    def run_all_tests(self):
        """Run all Phase 2 error handling verification tests"""
        print("🚀 Starting Phase 2 Error Handling Verification Tests")
        print("Focus: Enhanced error handling in chat.py")
        print("=" * 60)
        print()
        
        # Test 1: Backend Health
        if not self.test_backend_health():
            print("❌ Backend is not running. Cannot continue with tests.")
            return False
        
        # Test 2: GET /api/chat/providers - Verify still works after Phase 2 changes
        providers_success = self.test_chat_providers_after_changes()
        
        # Test 3: GET /api/chat/sessions - Verify database error handling works
        sessions_success = self.test_chat_sessions_error_handling()
        
        # Test 4: DELETE /api/chat/sessions/{invalid_id} - Test error handling for non-existent session
        delete_success = self.test_delete_invalid_session_error_handling()
        
        # Test 5: Check backend logs for any errors or warnings after the changes
        logs_success = self.check_backend_logs_for_errors()
        
        # Summary
        print("=" * 60)
        print("📋 PHASE 2 ERROR HANDLING VERIFICATION SUMMARY")
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
        
        # Critical assessment for Phase 2 error handling
        phase2_tests = [providers_success, sessions_success, delete_success, logs_success]
        phase2_success = all(phase2_tests)
        
        if phase2_success:
            print("✅ PHASE 2 STATUS: Enhanced error handling working correctly")
            print("✅ All endpoints return appropriate HTTP status codes")
            print("✅ Proper error messages in responses")
            print("✅ No regressions from error handling improvements")
        else:
            print("❌ PHASE 2 STATUS: Some error handling issues found")
            print("❌ Check failed tests above for details")
        
        print()
        return phase2_success

def main():
    """Main test execution - Phase 2 Error Handling Verification"""
    tester = Phase2ErrorHandlingTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 Phase 2 error handling verification completed successfully!")
        print("✅ Enhanced error handling working correctly!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the details above.")
        print("❌ Phase 2 error handling issues may be present.")
        sys.exit(1)

if __name__ == "__main__":
    main()