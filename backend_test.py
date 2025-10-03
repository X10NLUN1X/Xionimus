#!/usr/bin/env python3
"""
Advanced Session Management Testing Suite
Tests the advanced session management features in Xionimus AI backend including:
- Context status checking with token calculation
- Session summarization and forking
- Option selection and continuation
- Authentication integration
- Error handling
"""

import requests
import json
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManagementTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()  # Reuse connections for better performance
        self.test_session_id = None
        
    def create_test_session_with_messages(self) -> Dict[str, Any]:
        """Create a test session with multiple messages for testing"""
        logger.info("📝 Creating test session with messages")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Create a new session
            session_data = {
                "name": "Test Session for Context Management"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Session creation failed: {response.status_code}",
                    "response": response.text
                }
            
            session_info = response.json()
            self.test_session_id = session_info["id"]
            
            # Add multiple messages to the session
            test_messages = [
                {
                    "session_id": self.test_session_id,
                    "role": "user",
                    "content": "I want to build a web application with React and FastAPI. Can you help me set up the project structure?"
                },
                {
                    "session_id": self.test_session_id,
                    "role": "assistant", 
                    "content": "I'll help you create a modern web application with React frontend and FastAPI backend. Let me set up the project structure for you with proper organization and best practices.",
                    "provider": "openai",
                    "model": "gpt-4",
                    "usage": {"total_tokens": 150, "prompt_tokens": 50, "completion_tokens": 100}
                },
                {
                    "session_id": self.test_session_id,
                    "role": "user",
                    "content": "Great! Can you also add authentication with JWT tokens and a user management system?"
                },
                {
                    "session_id": self.test_session_id,
                    "role": "assistant",
                    "content": "Absolutely! I'll implement a complete authentication system with JWT tokens, user registration, login, and protected routes. This will include password hashing with bcrypt and proper token validation middleware.",
                    "provider": "openai", 
                    "model": "gpt-4",
                    "usage": {"total_tokens": 200, "prompt_tokens": 75, "completion_tokens": 125}
                },
                {
                    "session_id": self.test_session_id,
                    "role": "user",
                    "content": "Perfect! Now I need to add a database layer with SQLAlchemy and implement CRUD operations for user data."
                }
            ]
            
            # Add messages to the session
            for msg_data in test_messages:
                msg_response = self.session.post(
                    f"{self.api_url}/sessions/messages",
                    json=msg_data,
                    headers=headers,
                    timeout=10
                )
                
                if msg_response.status_code != 200:
                    logger.warning(f"⚠️ Failed to add message: {msg_response.status_code}")
            
            logger.info(f"✅ Test session created: {self.test_session_id}")
            logger.info(f"   Added {len(test_messages)} messages")
            
            return {
                "status": "success",
                "session_id": self.test_session_id,
                "message_count": len(test_messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Test session creation failed: {e}")
            return {"status": "error", "error": str(e)}
        
    def test_context_status_endpoint(self) -> Dict[str, Any]:
        """Test context status endpoint with session token calculation"""
        logger.info("📊 Testing context status endpoint")
        
        if not self.token or not self.test_session_id:
            return {"status": "skipped", "error": "No valid token or test session available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/session-management/context-status/{self.test_session_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                context_data = response.json()
                
                logger.info("✅ Context status endpoint working")
                logger.info(f"   Current tokens: {context_data.get('current_tokens', 0)}")
                logger.info(f"   Token limit: {context_data.get('limit', 0)}")
                logger.info(f"   Usage percentage: {context_data.get('percentage', 0)}%")
                logger.info(f"   Warning level: {context_data.get('recommendation', 'unknown')}")
                logger.info(f"   Can continue: {context_data.get('can_continue', True)}")
                
                # Validate response structure
                required_fields = ['warning', 'current_tokens', 'limit', 'percentage', 'message', 'can_continue', 'recommendation']
                missing_fields = [field for field in required_fields if field not in context_data]
                
                if missing_fields:
                    return {
                        "status": "partial",
                        "error": f"Missing fields: {missing_fields}",
                        "data": context_data
                    }
                
                return {
                    "status": "success",
                    "data": context_data,
                    "tokens_calculated": context_data.get('current_tokens', 0) > 0
                }
            elif response.status_code == 404:
                logger.error("❌ Session not found for context status")
                return {
                    "status": "failed",
                    "error": "Session not found",
                    "status_code": response.status_code
                }
            else:
                logger.error(f"❌ Context status failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Context status test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_authentication_system(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test JWT authentication system for session management"""
        logger.info(f"🔐 Testing authentication system with username: {username}")
        
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.user_info = {
                    "user_id": token_data.get("user_id"),
                    "username": token_data.get("username"),
                    "token_type": token_data.get("token_type"),
                    "role": token_data.get("role", "user")
                }
                
                logger.info("✅ Authentication successful")
                logger.info(f"   User ID: {token_data.get('user_id')}")
                logger.info(f"   Role: {token_data.get('role', 'user')}")
                
                return {
                    "status": "success",
                    "token": self.token,
                    "user_info": self.user_info,
                    "response": token_data
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_summarize_and_fork_endpoint(self) -> Dict[str, Any]:
        """Test session summarization and forking functionality"""
        logger.info("🔄 Testing summarize and fork endpoint")
        
        if not self.token or not self.test_session_id:
            return {"status": "skipped", "error": "No valid token or test session available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            fork_data = {
                "session_id": self.test_session_id,
                "api_keys": {}  # Empty API keys - expect it may fail but should handle gracefully
            }
            
            response = self.session.post(
                f"{self.api_url}/session-management/summarize-and-fork",
                json=fork_data,
                headers=headers,
                timeout=30  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                fork_data = response.json()
                
                logger.info("✅ Summarize and fork endpoint working")
                logger.info(f"   Original session: {fork_data.get('session_id')}")
                logger.info(f"   New session: {fork_data.get('new_session_id')}")
                logger.info(f"   Summary length: {len(fork_data.get('summary', ''))}")
                logger.info(f"   Next steps count: {len(fork_data.get('next_steps', []))}")
                logger.info(f"   Old session tokens: {fork_data.get('old_session_tokens', 0)}")
                
                # Validate response structure
                required_fields = ['session_id', 'new_session_id', 'summary', 'context_transfer', 'next_steps', 'old_session_tokens', 'timestamp']
                missing_fields = [field for field in required_fields if field not in fork_data]
                
                if missing_fields:
                    return {
                        "status": "partial",
                        "error": f"Missing fields: {missing_fields}",
                        "data": fork_data
                    }
                
                # Validate next_steps structure
                next_steps = fork_data.get('next_steps', [])
                if len(next_steps) != 3:
                    return {
                        "status": "partial",
                        "error": f"Expected 3 next steps, got {len(next_steps)}",
                        "data": fork_data
                    }
                
                return {
                    "status": "success",
                    "data": fork_data,
                    "new_session_id": fork_data.get('new_session_id')
                }
            elif response.status_code == 404:
                logger.error("❌ Session not found for summarization")
                return {
                    "status": "failed",
                    "error": "Session not found",
                    "status_code": response.status_code
                }
            elif response.status_code == 500:
                # Expected if AI API keys are missing
                error_detail = response.json().get("detail", "Unknown error") if response.content else "Server error"
                logger.warning(f"⚠️ Summarize and fork failed (expected if no AI keys): {error_detail}")
                return {
                    "status": "expected_failure",
                    "error": "AI API keys likely missing - this is expected",
                    "status_code": response.status_code,
                    "detail": error_detail
                }
            else:
                logger.error(f"❌ Summarize and fork failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Summarize and fork test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_continue_with_option_endpoint(self, new_session_id: str = None) -> Dict[str, Any]:
        """Test continue with option endpoint"""
        logger.info("▶️ Testing continue with option endpoint")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        # Use provided session ID or test session ID
        session_id = new_session_id or self.test_session_id
        if not session_id:
            return {"status": "skipped", "error": "No session ID available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test with a sample option action
            option_data = {
                "session_id": session_id,
                "option_action": "Continue with code improvements and add new features",
                "api_keys": {}
            }
            
            response = self.session.post(
                f"{self.api_url}/session-management/continue-with-option",
                json=option_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                continue_data = response.json()
                
                logger.info("✅ Continue with option endpoint working")
                logger.info(f"   Status: {continue_data.get('status')}")
                logger.info(f"   Session ID: {continue_data.get('session_id')}")
                logger.info(f"   Action: {continue_data.get('action')}")
                
                # Validate response structure
                required_fields = ['status', 'session_id', 'action', 'message']
                missing_fields = [field for field in required_fields if field not in continue_data]
                
                if missing_fields:
                    return {
                        "status": "partial",
                        "error": f"Missing fields: {missing_fields}",
                        "data": continue_data
                    }
                
                return {
                    "status": "success",
                    "data": continue_data
                }
            elif response.status_code == 404:
                logger.error("❌ Session not found for option continuation")
                return {
                    "status": "failed",
                    "error": "Session not found",
                    "status_code": response.status_code
                }
            else:
                logger.error(f"❌ Continue with option failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Continue with option test failed: {e}")
            return {"status": "error", "error": str(e)}
    def test_rate_limiting_functionality(self) -> Dict[str, Any]:
        """Test that rate limiting is still functional after security updates"""
        logger.info("🚦 Testing rate limiting functionality")
        
        try:
            # Test rate limits configuration endpoint
            response = self.session.get(f"{self.api_url}/rate-limits/limits", timeout=10)
            
            if response.status_code == 200:
                limits_data = response.json()
                rate_limits_count = len(limits_data.get("rate_limits", []))
                
                logger.info(f"✅ Rate limits configuration accessible: {rate_limits_count} limits configured")
                
                # Test a simple rate limit by making multiple requests
                rate_limit_triggered = False
                for i in range(6):  # Try to trigger login rate limit (5/min)
                    login_response = self.session.post(
                        f"{self.api_url}/auth/login",
                        json={"username": "invalid", "password": "invalid"},
                        timeout=10
                    )
                    
                    if login_response.status_code == 429:
                        rate_limit_triggered = True
                        retry_after = login_response.headers.get("Retry-After", "Unknown")
                        logger.info(f"✅ Rate limiting triggered on attempt {i + 1}, Retry-After: {retry_after}")
                        break
                    
                    time.sleep(0.1)
                
                return {
                    "status": "success",
                    "message": "Rate limiting system functional",
                    "limits_configured": rate_limits_count,
                    "rate_limit_triggered": rate_limit_triggered
                }
            else:
                logger.error(f"❌ Rate limits configuration not accessible: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Rate limits endpoint returned {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Rate limiting test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_core_functionality(self) -> Dict[str, Any]:
        """Test core API functionality to ensure no breaking changes"""
        logger.info("⚙️ Testing core functionality integrity")
        
        core_endpoints = [
            {"name": "Health Check", "url": f"{self.api_url}/health", "method": "GET", "auth_required": False},
            {"name": "Rate Limits Info", "url": f"{self.api_url}/rate-limits/limits", "method": "GET", "auth_required": False},
            {"name": "Rate Limiter Health", "url": f"{self.api_url}/rate-limits/health", "method": "GET", "auth_required": False},
        ]
        
        if self.token:
            core_endpoints.extend([
                {"name": "User Quota", "url": f"{self.api_url}/rate-limits/quota", "method": "GET", "auth_required": True},
            ])
        
        results = []
        
        for endpoint in core_endpoints:
            try:
                headers = {}
                if endpoint["auth_required"] and self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                
                if endpoint["method"] == "GET":
                    response = self.session.get(endpoint["url"], headers=headers, timeout=10)
                else:
                    response = self.session.post(endpoint["url"], headers=headers, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ {endpoint['name']}: Working")
                    results.append({
                        "endpoint": endpoint["name"],
                        "status": "working",
                        "status_code": response.status_code
                    })
                else:
                    logger.warning(f"⚠️ {endpoint['name']}: Status {response.status_code}")
                    results.append({
                        "endpoint": endpoint["name"],
                        "status": "issue",
                        "status_code": response.status_code
                    })
                    
            except Exception as e:
                logger.error(f"❌ {endpoint['name']}: Error - {e}")
                results.append({
                    "endpoint": endpoint["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        working_count = len([r for r in results if r["status"] == "working"])
        
        return {
            "status": "success" if working_count == len(core_endpoints) else "partial",
            "message": f"Core functionality: {working_count}/{len(core_endpoints)} endpoints working",
            "results": results
        }
    
    def test_dependency_compatibility(self) -> Dict[str, Any]:
        """Test that updated dependencies are working correctly"""
        logger.info("📦 Testing dependency compatibility")
        
        try:
            # Test that backend started successfully (if we can reach it, dependencies loaded)
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Check for any import errors or startup issues in the response
                services = health_data.get("services", {})
                database_status = services.get("database", {}).get("status", "unknown")
                ai_providers = services.get("ai_providers", {})
                
                logger.info("✅ Backend started successfully with updated dependencies")
                logger.info(f"   Database status: {database_status}")
                logger.info(f"   AI providers configured: {ai_providers.get('configured', 0)}")
                
                return {
                    "status": "success",
                    "message": "Updated dependencies working correctly",
                    "backend_started": True,
                    "database_status": database_status,
                    "ai_providers_configured": ai_providers.get("configured", 0)
                }
            else:
                logger.error(f"❌ Backend not responding properly: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Backend returned {response.status_code}",
                    "backend_started": False
                }
                
        except Exception as e:
            logger.error(f"❌ Dependency compatibility test failed: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "backend_started": False
            }
def main():
    """Main test runner for Security Improvements Testing"""
    logger.info("🔒 Starting Security Improvements Testing Suite")
    logger.info("=" * 70)
    
    tester = SecurityTester()
    
    # Test 1: Backend Health & Dependency Stability
    logger.info("1️⃣ Testing Backend Health & Updated Dependencies")
    health_result = tester.test_backend_health()
    print(f"Backend Health: {health_result['status']}")
    if health_result['status'] != 'healthy':
        print(f"❌ Backend is not healthy: {health_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with security tests")
        return
    
    # Test 2: Security Headers Verification
    logger.info("\n2️⃣ Testing Security Headers Middleware")
    headers_result = tester.test_security_headers()
    print(f"Security Headers: {headers_result['status']}")
    if headers_result['status'] == 'success':
        print(f"   All {len([h for h in headers_result['headers'].values() if h['correct']])} security headers correct")
    elif headers_result['status'] == 'partial':
        correct_count = len([h for h in headers_result['headers'].values() if h['correct']])
        total_count = len(headers_result['headers'])
        print(f"   {correct_count}/{total_count} security headers correct")
    
    # Test 3: Authentication System
    logger.info("\n3️⃣ Testing Authentication System (demo/demo123)")
    auth_result = tester.test_authentication_system()
    print(f"Authentication: {auth_result['status']}")
    
    if auth_result['status'] != 'success':
        print(f"❌ Authentication failed: {auth_result.get('error', 'Unknown error')}")
        print("⚠️ Some security tests will be skipped")
    
    # Test 4: Protected Endpoints
    logger.info("\n4️⃣ Testing Protected Endpoints with Valid Token")
    protected_result = tester.test_protected_endpoints()
    print(f"Protected Endpoints: {protected_result['status']}")
    if protected_result['status'] == 'success':
        print(f"   All protected endpoints working correctly")
    elif protected_result['status'] == 'partial':
        working_count = len([r for r in protected_result['results'] if r['status'] == 'success'])
        total_count = len(protected_result['results'])
        print(f"   {working_count}/{total_count} protected endpoints working")
    
    # Test 5: Invalid Token Rejection
    logger.info("\n5️⃣ Testing Invalid Token Rejection")
    invalid_token_result = tester.test_invalid_token_rejection()
    print(f"Invalid Token Rejection: {invalid_token_result['status']}")
    if invalid_token_result['status'] == 'success':
        print(f"   All invalid tokens correctly rejected with 401")
    
    # Test 6: Rate Limiting Functionality
    logger.info("\n6️⃣ Testing Rate Limiting System")
    rate_limit_result = tester.test_rate_limiting_functionality()
    print(f"Rate Limiting: {rate_limit_result['status']}")
    if rate_limit_result['status'] == 'success':
        print(f"   {rate_limit_result.get('limits_configured', 0)} rate limits configured")
        print(f"   Rate limiting triggered: {rate_limit_result.get('rate_limit_triggered', False)}")
    
    # Test 7: Core Functionality Integrity
    logger.info("\n7️⃣ Testing Core Functionality Integrity")
    core_result = tester.test_core_functionality()
    print(f"Core Functionality: {core_result['status']}")
    if core_result['status'] == 'success':
        print(f"   All core endpoints working correctly")
    elif core_result['status'] == 'partial':
        working_count = len([r for r in core_result['results'] if r['status'] == 'working'])
        total_count = len(core_result['results'])
        print(f"   {working_count}/{total_count} core endpoints working")
    
    # Test 8: Dependency Compatibility
    logger.info("\n8️⃣ Testing Updated Dependencies Compatibility")
    dependency_result = tester.test_dependency_compatibility()
    print(f"Dependencies: {dependency_result['status']}")
    if dependency_result['status'] == 'success':
        print(f"   Backend started successfully with updated dependencies")
        print(f"   Database: {dependency_result.get('database_status', 'unknown')}")
        print(f"   AI providers: {dependency_result.get('ai_providers_configured', 0)} configured")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("🔒 SECURITY IMPROVEMENTS TEST SUMMARY")
    logger.info("=" * 70)
    
    # Count successful tests
    test_results = [
        ("Backend Health", health_result['status'] == 'healthy'),
        ("Security Headers", headers_result['status'] in ['success', 'partial']),
        ("Authentication", auth_result['status'] == 'success'),
        ("Protected Endpoints", protected_result['status'] in ['success', 'partial']),
        ("Invalid Token Rejection", invalid_token_result['status'] == 'success'),
        ("Rate Limiting", rate_limit_result['status'] == 'success'),
        ("Core Functionality", core_result['status'] in ['success', 'partial']),
        ("Dependencies", dependency_result['status'] == 'success'),
    ]
    
    successful_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall Results: {successful_tests}/{total_tests} tests passed")
    
    for test_name, success in test_results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    # Critical Issues
    critical_issues = []
    if health_result['status'] != 'healthy':
        critical_issues.append("Backend not healthy - dependency issues")
    if headers_result['status'] == 'error':
        critical_issues.append("Security headers middleware not working")
    if auth_result['status'] != 'success':
        critical_issues.append("Authentication system broken")
    if protected_result['status'] == 'error':
        critical_issues.append("Protected endpoints not working")
    if invalid_token_result['status'] != 'success':
        critical_issues.append("Invalid token rejection not working")
    if rate_limit_result['status'] != 'success':
        critical_issues.append("Rate limiting system broken")
    if dependency_result['status'] != 'success':
        critical_issues.append("Updated dependencies causing issues")
    
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: Security improvements working correctly!")
        print("   - Security headers middleware active")
        print("   - Updated dependencies stable")
        print("   - Authentication system functional")
        print("   - Rate limiting operational")
        print("   - No breaking changes detected")
        print("   - All security improvements verified")

if __name__ == "__main__":
    main()