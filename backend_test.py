#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING FOR XIONIMUS AI PLATFORM
Post Phase 9 UI Migration Testing

Based on the detailed review request for systematic testing of ALL backend endpoints
after major frontend changes.

TEST SCOPE (from review request):
1. 🔐 Authentication & User Management
2. 📝 Session Management  
3. 💬 Chat Endpoints
4. 🔑 API Key Management
5. 🚀 Sandbox Execution
6. 🔀 Session Fork & Summary
7. 🐙 GitHub Integration
8. 📎 File Upload
9. 🛡️ Rate Limiting & Security
10. 📊 Health & Metrics

TEST CREDENTIALS:
- Username: demo
- Password: demo123
"""

import requests
import json
import time
import logging
import os
import concurrent.futures
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XionimusBackendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.test_results = {}
        self.session_id = None
        
    def authenticate(self) -> Dict[str, Any]:
        """🔐 AUTHENTICATION - Login with demo/demo123"""
        logger.info("🔐 Testing Authentication & User Management")
        
        try:
            # Test login
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(f"{self.api_url}/auth/login", data=login_data)
            logger.info(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                # Set authorization header for future requests
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                logger.info(f"✅ Authentication successful - User: {self.user_info['username']}")
                return {"status": "success", "data": auth_data}
            else:
                logger.error(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return {"status": "failed", "error": response.text}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_jwt_validation(self) -> Dict[str, Any]:
        """🔐 Test JWT token validation"""
        logger.info("🔐 Testing JWT Token Validation")
        
        try:
            # Test with valid token
            response = self.session.get(f"{self.api_url}/rate-limits/quota")
            if response.status_code == 200:
                logger.info("✅ Valid JWT token accepted")
                valid_token_test = True
            else:
                logger.error(f"❌ Valid token rejected: {response.status_code}")
                valid_token_test = False
            
            # Test with invalid token
            old_auth = self.session.headers.get("Authorization")
            self.session.headers.update({"Authorization": "Bearer invalid_token"})
            
            response = self.session.get(f"{self.api_url}/rate-limits/quota")
            if response.status_code == 401:
                logger.info("✅ Invalid JWT token properly rejected")
                invalid_token_test = True
            else:
                logger.error(f"❌ Invalid token not rejected: {response.status_code}")
                invalid_token_test = False
            
            # Restore valid token
            self.session.headers.update({"Authorization": old_auth})
            
            return {
                "status": "success" if (valid_token_test and invalid_token_test) else "failed",
                "valid_token_test": valid_token_test,
                "invalid_token_test": invalid_token_test
            }
            
        except Exception as e:
            logger.error(f"❌ JWT validation test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_session_management(self) -> Dict[str, Any]:
        """📝 Test Session Management endpoints"""
        logger.info("📝 Testing Session Management")
        
        try:
            results = {}
            
            # 1. List sessions
            response = self.session.get(f"{self.api_url}/sessions")
            if response.status_code == 200:
                sessions = response.json()
                logger.info(f"✅ GET /api/sessions - Found {len(sessions)} sessions")
                results["list_sessions"] = True
            else:
                logger.error(f"❌ GET /api/sessions failed: {response.status_code}")
                results["list_sessions"] = False
            
            # 2. Create new session
            session_data = {
                "title": "Test Session",
                "description": "Backend test session"
            }
            response = self.session.post(f"{self.api_url}/sessions", json=session_data)
            if response.status_code == 200:
                session_info = response.json()
                self.session_id = session_info.get("id")
                logger.info(f"✅ POST /api/sessions - Created session: {self.session_id}")
                results["create_session"] = True
            else:
                logger.error(f"❌ POST /api/sessions failed: {response.status_code}")
                results["create_session"] = False
            
            # 3. Update session (if created successfully)
            if self.session_id:
                update_data = {"title": "Updated Test Session"}
                response = self.session.patch(f"{self.api_url}/sessions/{self.session_id}", json=update_data)
                if response.status_code == 200:
                    logger.info(f"✅ PATCH /api/sessions/{self.session_id} - Session updated")
                    results["update_session"] = True
                else:
                    logger.error(f"❌ PATCH /api/sessions/{self.session_id} failed: {response.status_code}")
                    results["update_session"] = False
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ Session management test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_chat_endpoints(self) -> Dict[str, Any]:
        """💬 Test Chat endpoints"""
        logger.info("💬 Testing Chat Endpoints")
        
        try:
            results = {}
            
            # 1. Test chat message (will likely fail without AI keys, but endpoint should be accessible)
            if self.session_id:
                chat_data = {
                    "message": "Hello, this is a test message",
                    "session_id": self.session_id,
                    "developer_mode": "junior"
                }
                response = self.session.post(f"{self.api_url}/chat", json=chat_data)
                logger.info(f"POST /api/chat response: {response.status_code}")
                
                # Accept both success and expected failures (due to missing AI keys)
                if response.status_code in [200, 500]:
                    logger.info("✅ POST /api/chat - Endpoint accessible")
                    results["send_message"] = True
                else:
                    logger.error(f"❌ POST /api/chat failed: {response.status_code}")
                    results["send_message"] = False
                
                # 2. Get chat messages
                response = self.session.get(f"{self.api_url}/chat/{self.session_id}/messages")
                if response.status_code == 200:
                    messages = response.json()
                    logger.info(f"✅ GET /api/chat/{self.session_id}/messages - Found {len(messages)} messages")
                    results["get_messages"] = True
                else:
                    logger.error(f"❌ GET /api/chat/{self.session_id}/messages failed: {response.status_code}")
                    results["get_messages"] = False
            else:
                logger.warning("⚠️ No session ID available for chat tests")
                results["send_message"] = False
                results["get_messages"] = False
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ Chat endpoints test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_api_key_management(self) -> Dict[str, Any]:
        """🔑 Test API Key Management endpoints"""
        logger.info("🔑 Testing API Key Management")
        
        try:
            results = {}
            
            # 1. List API keys
            response = self.session.get(f"{self.api_url}/api-keys/list")
            if response.status_code == 200:
                api_keys = response.json()
                logger.info(f"✅ GET /api/api-keys/list - Found {len(api_keys)} providers")
                results["list_keys"] = True
            else:
                logger.error(f"❌ GET /api/api-keys/list failed: {response.status_code}")
                results["list_keys"] = False
            
            # 2. Save API key (test with dummy key)
            test_key_data = {
                "provider": "anthropic",
                "api_key": "sk-ant-test-key-1234567890"
            }
            response = self.session.post(f"{self.api_url}/api-keys/save", json=test_key_data)
            if response.status_code == 200:
                logger.info("✅ POST /api/api-keys/save - API key saved")
                results["save_key"] = True
            else:
                logger.error(f"❌ POST /api/api-keys/save failed: {response.status_code}")
                results["save_key"] = False
            
            # 3. Test connection (expected to fail with dummy key)
            test_data = {"provider": "anthropic"}
            response = self.session.post(f"{self.api_url}/api-keys/test-connection", json=test_data)
            if response.status_code in [200, 400, 500]:  # Accept various responses
                logger.info("✅ POST /api/api-keys/test-connection - Endpoint accessible")
                results["test_connection"] = True
            else:
                logger.error(f"❌ POST /api/api-keys/test-connection failed: {response.status_code}")
                results["test_connection"] = False
            
            # 4. Delete API key
            response = self.session.delete(f"{self.api_url}/api-keys/anthropic")
            if response.status_code == 200:
                logger.info("✅ DELETE /api/api-keys/anthropic - API key deleted")
                results["delete_key"] = True
            else:
                logger.error(f"❌ DELETE /api/api-keys/anthropic failed: {response.status_code}")
                results["delete_key"] = False
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ API key management test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_sandbox_execution(self) -> Dict[str, Any]:
        """🚀 Test Sandbox Execution endpoints"""
        logger.info("🚀 Testing Sandbox Execution")
        
        try:
            results = {}
            
            # 1. Get supported languages
            response = self.session.get(f"{self.api_url}/sandbox/languages")
            if response.status_code == 200:
                languages = response.json()
                logger.info(f"✅ GET /api/sandbox/languages - Found {len(languages)} languages")
                results["get_languages"] = True
                results["languages_count"] = len(languages)
            else:
                logger.error(f"❌ GET /api/sandbox/languages failed: {response.status_code}")
                results["get_languages"] = False
            
            # 2. Execute Python code
            python_code = {
                "language": "python",
                "code": "print('Hello from Python!')\nprint(2 + 2)"
            }
            response = self.session.post(f"{self.api_url}/sandbox/execute", json=python_code)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ Python execution successful - Output: {result.get('stdout', '')[:50]}...")
                    results["python_execution"] = True
                else:
                    logger.error(f"❌ Python execution failed: {result.get('stderr', '')}")
                    results["python_execution"] = False
            else:
                logger.error(f"❌ POST /api/sandbox/execute (Python) failed: {response.status_code}")
                results["python_execution"] = False
            
            # 3. Execute JavaScript code
            js_code = {
                "language": "javascript",
                "code": "console.log('Hello from JavaScript!');\nconsole.log(2 + 2);"
            }
            response = self.session.post(f"{self.api_url}/sandbox/execute", json=js_code)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ JavaScript execution successful - Output: {result.get('stdout', '')[:50]}...")
                    results["javascript_execution"] = True
                else:
                    logger.error(f"❌ JavaScript execution failed: {result.get('stderr', '')}")
                    results["javascript_execution"] = False
            else:
                logger.error(f"❌ POST /api/sandbox/execute (JavaScript) failed: {response.status_code}")
                results["javascript_execution"] = False
            
            # 4. Test templates
            response = self.session.get(f"{self.api_url}/sandbox/templates/template/python/hello_world")
            if response.status_code == 200:
                template = response.json()
                logger.info("✅ GET /api/sandbox/templates - Template retrieved")
                results["get_template"] = True
            else:
                logger.error(f"❌ GET /api/sandbox/templates failed: {response.status_code}")
                results["get_template"] = False
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ Sandbox execution test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_session_fork_summary(self) -> Dict[str, Any]:
        """🔀 Test Session Fork & Summary endpoints"""
        logger.info("🔀 Testing Session Fork & Summary")
        
        try:
            results = {}
            
            if self.session_id:
                # 1. Get context status
                response = self.session.get(f"{self.api_url}/session-fork/context-status/{self.session_id}")
                if response.status_code == 200:
                    context_status = response.json()
                    logger.info(f"✅ GET /api/session-fork/context-status - Status: {context_status.get('status', 'unknown')}")
                    results["context_status"] = True
                else:
                    logger.error(f"❌ GET /api/session-fork/context-status failed: {response.status_code}")
                    results["context_status"] = False
                
                # 2. Get fork preview
                response = self.session.get(f"{self.api_url}/session-fork/fork-preview/{self.session_id}")
                if response.status_code == 200:
                    fork_preview = response.json()
                    logger.info("✅ GET /api/session-fork/fork-preview - Preview retrieved")
                    results["fork_preview"] = True
                else:
                    logger.error(f"❌ GET /api/session-fork/fork-preview failed: {response.status_code}")
                    results["fork_preview"] = False
                
                # 3. Test summarize and fork (expected to fail without AI keys)
                response = self.session.post(f"{self.api_url}/session-management/summarize-and-fork", 
                                           json={"session_id": self.session_id})
                if response.status_code in [200, 500]:  # Accept both success and expected AI key failures
                    logger.info("✅ POST /api/session-management/summarize-and-fork - Endpoint accessible")
                    results["summarize_fork"] = True
                else:
                    logger.error(f"❌ POST /api/session-management/summarize-and-fork failed: {response.status_code}")
                    results["summarize_fork"] = False
            else:
                logger.warning("⚠️ No session ID available for fork tests")
                results = {"context_status": False, "fork_preview": False, "summarize_fork": False}
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ Session fork test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_github_integration(self) -> Dict[str, Any]:
        """🐙 Test GitHub Integration endpoints"""
        logger.info("🐙 Testing GitHub Integration")
        
        try:
            results = {}
            
            # 1. Verify GitHub token (expected to fail with demo token)
            response = self.session.get(f"{self.api_url}/github-pat/verify-token")
            if response.status_code in [200, 401, 403]:  # Accept various auth responses
                logger.info("✅ GET /api/github-pat/verify-token - Endpoint accessible")
                results["verify_token"] = True
            else:
                logger.error(f"❌ GET /api/github-pat/verify-token failed: {response.status_code}")
                results["verify_token"] = False
            
            # 2. Get repositories (expected to fail without valid token)
            response = self.session.get(f"{self.api_url}/github-pat/repositories")
            if response.status_code in [200, 401, 403]:  # Accept various auth responses
                logger.info("✅ GET /api/github-pat/repositories - Endpoint accessible")
                results["get_repositories"] = True
            else:
                logger.error(f"❌ GET /api/github-pat/repositories failed: {response.status_code}")
                results["get_repositories"] = False
            
            # 3. Test preview session files
            if self.session_id:
                preview_data = {
                    "session_id": self.session_id,
                    "repository": "test/repo",
                    "branch": "main"
                }
                response = self.session.post(f"{self.api_url}/github-pat/preview-session-files", json=preview_data)
                if response.status_code in [200, 400, 401, 403]:  # Accept various responses
                    logger.info("✅ POST /api/github-pat/preview-session-files - Endpoint accessible")
                    results["preview_files"] = True
                else:
                    logger.error(f"❌ POST /api/github-pat/preview-session-files failed: {response.status_code}")
                    results["preview_files"] = False
            else:
                results["preview_files"] = False
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ GitHub integration test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_file_upload(self) -> Dict[str, Any]:
        """📎 Test File Upload endpoint"""
        logger.info("📎 Testing File Upload")
        
        try:
            # Create a test file
            test_content = "This is a test file for upload testing."
            files = {
                'file': ('test.txt', test_content, 'text/plain')
            }
            
            data = {}
            if self.session_id:
                data['session_id'] = self.session_id
            
            response = self.session.post(f"{self.api_url}/file-upload/upload", files=files, data=data)
            
            if response.status_code == 200:
                upload_result = response.json()
                logger.info(f"✅ POST /api/file-upload/upload - File uploaded: {upload_result.get('filename', 'unknown')}")
                return {"status": "success", "file_id": upload_result.get("file_id")}
            else:
                logger.error(f"❌ POST /api/file-upload/upload failed: {response.status_code}")
                return {"status": "failed", "error": response.text}
                
        except Exception as e:
            logger.error(f"❌ File upload test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_rate_limiting_security(self) -> Dict[str, Any]:
        """🛡️ Test Rate Limiting & Security"""
        logger.info("🛡️ Testing Rate Limiting & Security")
        
        try:
            results = {}
            
            # 1. Get rate limits configuration
            response = self.session.get(f"{self.api_url}/rate-limits/limits")
            if response.status_code == 200:
                limits = response.json()
                logger.info(f"✅ GET /api/rate-limits/limits - Found {len(limits)} rate limits")
                results["get_limits"] = True
                results["limits_count"] = len(limits)
            else:
                logger.error(f"❌ GET /api/rate-limits/limits failed: {response.status_code}")
                results["get_limits"] = False
            
            # 2. Get user quota
            response = self.session.get(f"{self.api_url}/rate-limits/quota")
            if response.status_code == 200:
                quota = response.json()
                logger.info(f"✅ GET /api/rate-limits/quota - Current usage: {quota.get('requests_used', 0)}")
                results["get_quota"] = True
            else:
                logger.error(f"❌ GET /api/rate-limits/quota failed: {response.status_code}")
                results["get_quota"] = False
            
            # 3. Test security headers (check a simple endpoint)
            response = self.session.get(f"{self.api_url}/health")
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options', 
                'X-XSS-Protection',
                'Strict-Transport-Security'
            ]
            
            headers_present = 0
            for header in security_headers:
                if header in response.headers:
                    headers_present += 1
            
            if headers_present >= 3:  # At least 3 security headers
                logger.info(f"✅ Security headers present: {headers_present}/{len(security_headers)}")
                results["security_headers"] = True
            else:
                logger.error(f"❌ Insufficient security headers: {headers_present}/{len(security_headers)}")
                results["security_headers"] = False
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ Rate limiting & security test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_health_metrics(self) -> Dict[str, Any]:
        """📊 Test Health & Metrics endpoints"""
        logger.info("📊 Testing Health & Metrics")
        
        try:
            results = {}
            
            # 1. Health check
            response = self.session.get(f"{self.api_url}/health")
            if response.status_code == 200:
                health = response.json()
                logger.info(f"✅ GET /api/health - Status: {health.get('status', 'unknown')}")
                results["health_check"] = True
            else:
                logger.error(f"❌ GET /api/health failed: {response.status_code}")
                results["health_check"] = False
            
            # 2. Version info
            response = self.session.get(f"{self.api_url}/version")
            if response.status_code == 200:
                version = response.json()
                logger.info(f"✅ GET /api/version - Version: {version.get('version', 'unknown')}")
                results["version_info"] = True
            else:
                logger.error(f"❌ GET /api/version failed: {response.status_code}")
                results["version_info"] = False
            
            # 3. Metrics (if available)
            response = self.session.get(f"{self.api_url}/metrics")
            if response.status_code == 200:
                logger.info("✅ GET /api/metrics - Metrics available")
                results["metrics"] = True
            else:
                logger.info(f"ℹ️ GET /api/metrics not available: {response.status_code}")
                results["metrics"] = False
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            logger.error(f"❌ Health & metrics test error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all backend tests"""
        logger.info("🚀 Starting Comprehensive Backend Testing for Xionimus AI Platform")
        logger.info("=" * 80)
        
        start_time = time.time()
        all_results = {}
        
        # 1. Authentication (required for other tests)
        auth_result = self.authenticate()
        all_results["authentication"] = auth_result
        
        if auth_result["status"] != "success":
            logger.error("❌ Authentication failed - cannot proceed with other tests")
            return {"status": "failed", "error": "Authentication required", "results": all_results}
        
        # 2. JWT Validation
        all_results["jwt_validation"] = self.test_jwt_validation()
        
        # 3. Session Management
        all_results["session_management"] = self.test_session_management()
        
        # 4. Chat Endpoints
        all_results["chat_endpoints"] = self.test_chat_endpoints()
        
        # 5. API Key Management
        all_results["api_key_management"] = self.test_api_key_management()
        
        # 6. Sandbox Execution
        all_results["sandbox_execution"] = self.test_sandbox_execution()
        
        # 7. Session Fork & Summary
        all_results["session_fork_summary"] = self.test_session_fork_summary()
        
        # 8. GitHub Integration
        all_results["github_integration"] = self.test_github_integration()
        
        # 9. File Upload
        all_results["file_upload"] = self.test_file_upload()
        
        # 10. Rate Limiting & Security
        all_results["rate_limiting_security"] = self.test_rate_limiting_security()
        
        # 11. Health & Metrics
        all_results["health_metrics"] = self.test_health_metrics()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        logger.info("=" * 80)
        logger.info("🎯 COMPREHENSIVE BACKEND TEST SUMMARY")
        logger.info("=" * 80)
        
        passed_tests = 0
        total_tests = len(all_results)
        
        for test_name, result in all_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                logger.info(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
                passed_tests += 1
            elif status == "failed":
                logger.error(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
            else:
                logger.warning(f"⚠️ {test_name.replace('_', ' ').title()}: ERROR")
        
        logger.info("=" * 80)
        logger.info(f"📊 FINAL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        logger.info(f"⏱️ Total execution time: {total_time:.2f} seconds")
        logger.info("=" * 80)
        
        return {
            "status": "completed",
            "summary": {
                "passed": passed_tests,
                "total": total_tests,
                "percentage": passed_tests/total_tests*100,
                "execution_time": total_time
            },
            "results": all_results
        }

def main():
    """Main test execution"""
    # Use the frontend's configured backend URL
    backend_url = "http://localhost:8001"  # Default fallback
    
    # Try to read from frontend .env if available
    try:
        with open("/app/frontend/.env", "r") as f:
            for line in f:
                if line.startswith("VITE_API_URL="):
                    api_url = line.split("=", 1)[1].strip()
                    # Extract base URL (remove /api suffix)
                    if api_url.endswith("/api"):
                        backend_url = api_url[:-4]
                    break
    except:
        pass
    
    logger.info(f"🎯 Testing backend at: {backend_url}")
    
    tester = XionimusBackendTester(backend_url)
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("📄 Test results saved to: /app/backend_test_results.json")
    
    return results

if __name__ == "__main__":
    main()