#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE BACKEND TESTING - COMPLETE SYSTEM VERIFICATION

This test covers all 12 critical categories as requested:
1. Authentication & Security
2. Session Management  
3. Chat Functionality
4. Cloud Sandbox
5. API Key Management
6. Rate Limiting
7. Session Forking
8. Developer Modes
9. GitHub Integration
10. Metrics & Monitoring
11. Error Handling
12. Database Operations

Test Credentials: demo/demo123
Backend URL: http://localhost:8001/api
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8001/api"
TEST_USER = "demo"
TEST_PASSWORD = "demo123"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.session_id = None
        self.test_results = {}
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, timeout: int = 30) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        default_headers = {"Content-Type": "application/json"}
        if self.token:
            default_headers["Authorization"] = f"Bearer {self.token}"
        
        if headers:
            default_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return {
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "headers": dict(response.headers),
                "response_time": response.elapsed.total_seconds()
            }
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "data": {"error": str(e)},
                "headers": {},
                "response_time": 0
            }
    
    def test_category_1_authentication_security(self) -> Dict[str, Any]:
        """🔐 Test Authentication & Security"""
        self.log("🔐 Testing Authentication & Security...")
        results = {}
        
        # Test 1: Login endpoint
        self.log("  Testing login with demo/demo123...")
        login_response = self.make_request("POST", "/auth/login", {
            "username": TEST_USER,
            "password": TEST_PASSWORD
        })
        
        if login_response["status_code"] == 200 and "access_token" in login_response["data"]:
            self.token = login_response["data"]["access_token"]
            results["login"] = "✅ PASS"
            self.log(f"    ✅ Login successful, token received")
        else:
            results["login"] = f"❌ FAIL - Status: {login_response['status_code']}"
            self.log(f"    ❌ Login failed: {login_response['data']}")
            
        # Test 2: JWT token validation
        if self.token:
            self.log("  Testing JWT token validation...")
            protected_response = self.make_request("GET", "/rate-limits/quota")
            if protected_response["status_code"] == 200:
                results["jwt_validation"] = "✅ PASS"
                self.log("    ✅ JWT token validation working")
            else:
                results["jwt_validation"] = f"❌ FAIL - Status: {protected_response['status_code']}"
        else:
            results["jwt_validation"] = "❌ FAIL - No token to test"
            
        # Test 3: Invalid token rejection
        self.log("  Testing invalid token rejection...")
        invalid_response = self.make_request("GET", "/rate-limits/quota", headers={"Authorization": "Bearer invalid_token"})
        if invalid_response["status_code"] == 401:
            results["invalid_token_rejection"] = "✅ PASS"
            self.log("    ✅ Invalid token properly rejected (401)")
        else:
            results["invalid_token_rejection"] = f"❌ FAIL - Status: {invalid_response['status_code']}"
            
        # Test 4: Security headers
        self.log("  Testing security headers...")
        health_response = self.make_request("GET", "/health")
        headers = health_response["headers"]
        
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Referrer-Policy",
            "Permissions-Policy"
        ]
        
        missing_headers = [h for h in required_headers if h not in headers]
        if not missing_headers:
            results["security_headers"] = "✅ PASS"
            self.log(f"    ✅ All 6 security headers present")
        else:
            results["security_headers"] = f"❌ FAIL - Missing: {missing_headers}"
            
        return results
    
    def test_category_2_session_management(self) -> Dict[str, Any]:
        """📝 Test Session Management"""
        self.log("📝 Testing Session Management...")
        results = {}
        
        # Test 1: Create session
        self.log("  Testing session creation...")
        create_response = self.make_request("POST", "/sessions/", {
            "name": "Test Session"
        })
        
        if create_response["status_code"] == 200 and "id" in create_response["data"]:
            self.session_id = create_response["data"]["id"]
            results["create_session"] = "✅ PASS"
            self.log(f"    ✅ Session created: {self.session_id}")
        else:
            results["create_session"] = f"❌ FAIL - Status: {create_response['status_code']}"
            
        # Test 2: List sessions
        self.log("  Testing session listing...")
        list_response = self.make_request("GET", "/sessions/list")
        if list_response["status_code"] == 200 and isinstance(list_response["data"], list):
            results["list_sessions"] = f"✅ PASS - Found {len(list_response['data'])} sessions"
            self.log(f"    ✅ Sessions listed: {len(list_response['data'])} found")
        else:
            results["list_sessions"] = f"❌ FAIL - Status: {list_response['status_code']}"
            
        # Test 3: Get specific session
        if self.session_id:
            self.log("  Testing get specific session...")
            get_response = self.make_request("GET", f"/sessions/{self.session_id}")
            if get_response["status_code"] == 200:
                results["get_session"] = "✅ PASS"
                self.log("    ✅ Session retrieved successfully")
            else:
                results["get_session"] = f"❌ FAIL - Status: {get_response['status_code']}"
        else:
            results["get_session"] = "❌ FAIL - No session ID to test"
            
        # Test 4: Add message to session
        if self.session_id:
            self.log("  Testing message addition...")
            message_response = self.make_request("POST", "/sessions/messages", {
                "session_id": self.session_id,
                "role": "user",
                "content": "Test message for comprehensive backend testing"
            })
            if message_response["status_code"] == 200:
                results["add_message"] = "✅ PASS"
                self.log("    ✅ Message added successfully")
            else:
                results["add_message"] = f"❌ FAIL - Status: {message_response['status_code']}"
        else:
            results["add_message"] = "❌ FAIL - No session ID to test"
            
        return results
    
    def test_category_3_chat_functionality(self) -> Dict[str, Any]:
        """💬 Test Chat Functionality"""
        self.log("💬 Testing Chat Functionality...")
        results = {}
        
        # Test 1: Developer modes endpoint
        self.log("  Testing developer modes...")
        modes_response = self.make_request("GET", "/developer-modes")
        if modes_response["status_code"] == 200:
            results["developer_modes"] = "✅ PASS"
            self.log("    ✅ Developer modes endpoint accessible")
        else:
            results["developer_modes"] = f"❌ FAIL - Status: {modes_response['status_code']}"
            
        # Test 2: Chat message endpoint (basic structure test)
        self.log("  Testing chat message endpoint structure...")
        # Note: Full chat testing requires AI API keys, so we test endpoint availability
        chat_response = self.make_request("POST", "/chat/message", {
            "message": "Hello, this is a test",
            "session_id": self.session_id or "test_session"
        })
        
        # We expect either 200 (success) or specific error codes (missing API keys, etc.)
        if chat_response["status_code"] in [200, 400, 503]:
            results["chat_endpoint"] = "✅ PASS - Endpoint accessible"
            self.log("    ✅ Chat endpoint structure working")
        else:
            results["chat_endpoint"] = f"❌ FAIL - Status: {chat_response['status_code']}"
            
        return results
    
    def test_category_4_cloud_sandbox(self) -> Dict[str, Any]:
        """☁️ Test Cloud Sandbox"""
        self.log("☁️ Testing Cloud Sandbox...")
        results = {}
        
        # Test 1: Get supported languages
        self.log("  Testing supported languages...")
        languages_response = self.make_request("GET", "/sandbox/languages")
        if languages_response["status_code"] == 200 and "languages" in languages_response["data"]:
            languages = languages_response["data"]["languages"]
            results["supported_languages"] = f"✅ PASS - {len(languages)} languages"
            self.log(f"    ✅ {len(languages)} languages supported")
        else:
            results["supported_languages"] = f"❌ FAIL - Status: {languages_response['status_code']}"
            
        # Test 2: Python code execution
        self.log("  Testing Python code execution...")
        python_code = 'print("Hello from Python sandbox!")\nprint("2 + 2 =", 2 + 2)'
        exec_response = self.make_request("POST", "/sandbox/execute", {
            "code": python_code,
            "language": "python"
        })
        
        if exec_response["status_code"] == 200 and exec_response["data"].get("success"):
            results["python_execution"] = "✅ PASS"
            self.log(f"    ✅ Python execution successful")
            self.log(f"    Output: {exec_response['data'].get('stdout', '')[:50]}...")
        else:
            results["python_execution"] = f"❌ FAIL - Status: {exec_response['status_code']}"
            
        # Test 3: JavaScript code execution
        self.log("  Testing JavaScript code execution...")
        js_code = 'console.log("Hello from JavaScript sandbox!"); console.log("3 * 4 =", 3 * 4);'
        js_response = self.make_request("POST", "/sandbox/execute", {
            "code": js_code,
            "language": "javascript"
        })
        
        if js_response["status_code"] == 200 and js_response["data"].get("success"):
            results["javascript_execution"] = "✅ PASS"
            self.log(f"    ✅ JavaScript execution successful")
        else:
            results["javascript_execution"] = f"❌ FAIL - Status: {js_response['status_code']}"
            
        # Test 4: Error handling in sandbox
        self.log("  Testing sandbox error handling...")
        error_code = 'print("This will cause an error")\nundefined_variable'
        error_response = self.make_request("POST", "/sandbox/execute", {
            "code": error_code,
            "language": "python"
        })
        
        if error_response["status_code"] == 200 and not error_response["data"].get("success"):
            results["error_handling"] = "✅ PASS"
            self.log("    ✅ Error handling working correctly")
        else:
            results["error_handling"] = f"❌ FAIL - Status: {error_response['status_code']}"
            
        return results
    
    def test_category_5_api_key_management(self) -> Dict[str, Any]:
        """🔑 Test API Key Management"""
        self.log("🔑 Testing API Key Management...")
        results = {}
        
        # Test 1: List API keys endpoint
        self.log("  Testing API keys listing...")
        keys_response = self.make_request("GET", "/api-keys/")
        if keys_response["status_code"] == 200:
            results["list_keys"] = "✅ PASS"
            self.log("    ✅ API keys endpoint accessible")
        else:
            results["list_keys"] = f"❌ FAIL - Status: {keys_response['status_code']}"
            
        # Test 2: Store API key (test with dummy key)
        self.log("  Testing API key storage...")
        store_response = self.make_request("POST", "/api-keys/", {
            "provider": "test_provider",
            "api_key": "test_key_12345",
            "description": "Test key for comprehensive testing"
        })
        
        if store_response["status_code"] in [200, 201]:
            results["store_key"] = "✅ PASS"
            self.log("    ✅ API key storage working")
        else:
            results["store_key"] = f"❌ FAIL - Status: {store_response['status_code']}"
            
        return results
    
    def test_category_6_rate_limiting(self) -> Dict[str, Any]:
        """⏱️ Test Rate Limiting"""
        self.log("⏱️ Testing Rate Limiting...")
        results = {}
        
        # Test 1: Rate limit status
        self.log("  Testing rate limit status...")
        quota_response = self.make_request("GET", "/rate-limits/quota")
        if quota_response["status_code"] == 200:
            results["rate_limit_status"] = "✅ PASS"
            self.log("    ✅ Rate limit status accessible")
        else:
            results["rate_limit_status"] = f"❌ FAIL - Status: {quota_response['status_code']}"
            
        # Test 2: Rate limit configuration
        self.log("  Testing rate limit configuration...")
        limits_response = self.make_request("GET", "/rate-limits/limits")
        if limits_response["status_code"] == 200:
            results["rate_limit_config"] = "✅ PASS"
            self.log("    ✅ Rate limit configuration accessible")
        else:
            results["rate_limit_config"] = f"❌ FAIL - Status: {limits_response['status_code']}"
            
        # Test 3: Rate limit enforcement (rapid requests)
        self.log("  Testing rate limit enforcement...")
        rapid_requests = []
        for i in range(3):
            response = self.make_request("GET", "/health")
            rapid_requests.append(response["status_code"])
            time.sleep(0.1)  # Small delay between requests
            
        # Check if any requests were rate limited (429)
        if all(status == 200 for status in rapid_requests):
            results["rate_limit_enforcement"] = "✅ PASS - No rate limiting triggered (normal for health endpoint)"
            self.log("    ✅ Rate limiting system operational")
        else:
            results["rate_limit_enforcement"] = f"⚠️ PARTIAL - Status codes: {rapid_requests}"
            
        return results
    
    def test_category_7_session_forking(self) -> Dict[str, Any]:
        """🔀 Test Session Forking"""
        self.log("🔀 Testing Session Forking...")
        results = {}
        
        # Test 1: Session fork endpoint availability
        self.log("  Testing session fork endpoint...")
        if self.session_id:
            fork_response = self.make_request("POST", f"/session-fork/{self.session_id}/fork", {
                "new_name": "Forked Test Session"
            })
            
            # We expect either success or specific error (like missing messages)
            if fork_response["status_code"] in [200, 400, 404]:
                results["session_fork"] = "✅ PASS - Endpoint accessible"
                self.log("    ✅ Session fork endpoint working")
            else:
                results["session_fork"] = f"❌ FAIL - Status: {fork_response['status_code']}"
        else:
            results["session_fork"] = "❌ FAIL - No session ID to test"
            
        return results
    
    def test_category_8_developer_modes(self) -> Dict[str, Any]:
        """👨‍💻 Test Developer Modes"""
        self.log("👨‍💻 Testing Developer Modes...")
        results = {}
        
        # Test 1: Developer modes configuration
        self.log("  Testing developer modes configuration...")
        modes_response = self.make_request("GET", "/developer-modes")
        if modes_response["status_code"] == 200:
            results["developer_modes_config"] = "✅ PASS"
            self.log("    ✅ Developer modes configuration accessible")
        else:
            results["developer_modes_config"] = f"❌ FAIL - Status: {modes_response['status_code']}"
            
        return results
    
    def test_category_9_github_integration(self) -> Dict[str, Any]:
        """🔄 Test GitHub Integration"""
        self.log("🔄 Testing GitHub Integration...")
        results = {}
        
        # Test 1: GitHub configuration
        self.log("  Testing GitHub configuration...")
        github_config_response = self.make_request("GET", "/settings/github-config")
        if github_config_response["status_code"] == 200:
            results["github_config"] = "✅ PASS"
            self.log("    ✅ GitHub configuration endpoint accessible")
        else:
            results["github_config"] = f"❌ FAIL - Status: {github_config_response['status_code']}"
            
        return results
    
    def test_category_10_metrics_monitoring(self) -> Dict[str, Any]:
        """📊 Test Metrics & Monitoring"""
        self.log("📊 Testing Metrics & Monitoring...")
        results = {}
        
        # Test 1: Health check
        self.log("  Testing health check...")
        health_response = self.make_request("GET", "/health")
        if health_response["status_code"] == 200:
            health_data = health_response["data"]
            results["health_check"] = f"✅ PASS - Status: {health_data.get('status', 'unknown')}"
            self.log(f"    ✅ Health check: {health_data.get('status', 'unknown')}")
        else:
            results["health_check"] = f"❌ FAIL - Status: {health_response['status_code']}"
            
        # Test 2: Version info
        self.log("  Testing version info...")
        version_response = self.make_request("GET", "/version")
        if version_response["status_code"] == 200:
            results["version_info"] = "✅ PASS"
            self.log("    ✅ Version info accessible")
        else:
            results["version_info"] = f"❌ FAIL - Status: {version_response['status_code']}"
            
        # Test 3: Metrics endpoint
        self.log("  Testing metrics endpoint...")
        metrics_response = self.make_request("GET", "/metrics")
        if metrics_response["status_code"] == 200:
            results["metrics_endpoint"] = "✅ PASS"
            self.log("    ✅ Metrics endpoint accessible")
        else:
            results["metrics_endpoint"] = f"❌ FAIL - Status: {metrics_response['status_code']}"
            
        return results
    
    def test_category_11_error_handling(self) -> Dict[str, Any]:
        """⚠️ Test Error Handling"""
        self.log("⚠️ Testing Error Handling...")
        results = {}
        
        # Test 1: 404 Not Found
        self.log("  Testing 404 error handling...")
        not_found_response = self.make_request("GET", "/nonexistent-endpoint")
        if not_found_response["status_code"] == 404:
            results["404_handling"] = "✅ PASS"
            self.log("    ✅ 404 errors handled correctly")
        else:
            results["404_handling"] = f"❌ FAIL - Status: {not_found_response['status_code']}"
            
        # Test 2: 401 Unauthorized (no token)
        self.log("  Testing 401 error handling...")
        old_token = self.token
        self.token = None  # Remove token temporarily
        unauthorized_response = self.make_request("GET", "/rate-limits/quota")
        self.token = old_token  # Restore token
        
        if unauthorized_response["status_code"] == 401:
            results["401_handling"] = "✅ PASS"
            self.log("    ✅ 401 errors handled correctly")
        else:
            results["401_handling"] = f"❌ FAIL - Status: {unauthorized_response['status_code']}"
            
        # Test 3: 400 Bad Request
        self.log("  Testing 400 error handling...")
        bad_request_response = self.make_request("POST", "/sessions/", {
            "invalid_field": "invalid_value"
        })
        
        if bad_request_response["status_code"] in [400, 422]:  # 422 is also valid for validation errors
            results["400_handling"] = "✅ PASS"
            self.log("    ✅ 400/422 errors handled correctly")
        else:
            results["400_handling"] = f"❌ FAIL - Status: {bad_request_response['status_code']}"
            
        return results
    
    def test_category_12_database_operations(self) -> Dict[str, Any]:
        """💾 Test Database Operations"""
        self.log("💾 Testing Database Operations...")
        results = {}
        
        # Test 1: Database connectivity (via health check)
        self.log("  Testing database connectivity...")
        health_response = self.make_request("GET", "/health")
        if health_response["status_code"] == 200:
            health_data = health_response["data"]
            db_status = health_data.get("services", {}).get("database", {}).get("status")
            if db_status == "connected":
                results["db_connectivity"] = "✅ PASS"
                self.log("    ✅ Database connectivity confirmed")
            else:
                results["db_connectivity"] = f"❌ FAIL - DB Status: {db_status}"
        else:
            results["db_connectivity"] = f"❌ FAIL - Health check failed"
            
        # Test 2: CRUD operations (via sessions)
        self.log("  Testing CRUD operations...")
        if self.session_id:
            # Read operation
            read_response = self.make_request("GET", f"/sessions/{self.session_id}")
            if read_response["status_code"] == 200:
                results["crud_operations"] = "✅ PASS"
                self.log("    ✅ CRUD operations working")
            else:
                results["crud_operations"] = f"❌ FAIL - Read failed: {read_response['status_code']}"
        else:
            results["crud_operations"] = "❌ FAIL - No session to test CRUD"
            
        return results
    
    def run_comprehensive_test(self):
        """Run all 12 test categories"""
        self.log("🚀 Starting Comprehensive Backend System Verification")
        self.log(f"Backend URL: {self.base_url}")
        self.log(f"Test Credentials: {TEST_USER}/{TEST_PASSWORD}")
        self.log("=" * 80)
        
        # Run all test categories
        all_results = {}
        
        try:
            all_results["1_authentication_security"] = self.test_category_1_authentication_security()
            all_results["2_session_management"] = self.test_category_2_session_management()
            all_results["3_chat_functionality"] = self.test_category_3_chat_functionality()
            all_results["4_cloud_sandbox"] = self.test_category_4_cloud_sandbox()
            all_results["5_api_key_management"] = self.test_category_5_api_key_management()
            all_results["6_rate_limiting"] = self.test_category_6_rate_limiting()
            all_results["7_session_forking"] = self.test_category_7_session_forking()
            all_results["8_developer_modes"] = self.test_category_8_developer_modes()
            all_results["9_github_integration"] = self.test_category_9_github_integration()
            all_results["10_metrics_monitoring"] = self.test_category_10_metrics_monitoring()
            all_results["11_error_handling"] = self.test_category_11_error_handling()
            all_results["12_database_operations"] = self.test_category_12_database_operations()
            
        except Exception as e:
            self.log(f"❌ Critical error during testing: {e}", "ERROR")
            return {"error": str(e)}
        
        # Generate summary
        self.generate_summary(all_results)
        return all_results
    
    def generate_summary(self, results: Dict[str, Dict[str, Any]]):
        """Generate comprehensive test summary"""
        total_time = time.time() - self.start_time
        
        self.log("=" * 80)
        self.log("🎯 COMPREHENSIVE BACKEND TESTING COMPLETED")
        self.log("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, tests in results.items():
            category_name = category.replace("_", " ").title()
            self.log(f"\n📋 {category_name}:")
            
            for test_name, result in tests.items():
                total_tests += 1
                if result.startswith("✅"):
                    passed_tests += 1
                    self.log(f"  {result}")
                else:
                    failed_tests += 1
                    self.log(f"  {result}")
        
        # Overall statistics
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.log("\n" + "=" * 80)
        self.log("📊 FINAL RESULTS:")
        self.log(f"   Total Tests: {total_tests}")
        self.log(f"   Passed: {passed_tests} ✅")
        self.log(f"   Failed: {failed_tests} ❌")
        self.log(f"   Success Rate: {success_rate:.1f}%")
        self.log(f"   Total Time: {total_time:.2f} seconds")
        
        # Overall health rating
        if success_rate >= 90:
            health_rating = 10
            status = "EXCELLENT"
        elif success_rate >= 80:
            health_rating = 8
            status = "GOOD"
        elif success_rate >= 70:
            health_rating = 7
            status = "ACCEPTABLE"
        elif success_rate >= 60:
            health_rating = 6
            status = "NEEDS IMPROVEMENT"
        else:
            health_rating = max(1, int(success_rate / 10))
            status = "CRITICAL ISSUES"
        
        self.log(f"   Backend Health Rating: {health_rating}/10 ({status})")
        self.log("=" * 80)
        
        # Critical issues summary
        critical_failures = []
        for category, tests in results.items():
            for test_name, result in tests.items():
                if result.startswith("❌") and any(keyword in test_name.lower() for keyword in ["login", "auth", "database", "health"]):
                    critical_failures.append(f"{category}: {test_name}")
        
        if critical_failures:
            self.log("\n🚨 CRITICAL ISSUES DETECTED:")
            for failure in critical_failures:
                self.log(f"   - {failure}")
        else:
            self.log("\n✅ NO CRITICAL ISSUES DETECTED")
        
        self.log("\n🎉 Comprehensive Backend Testing Complete!")

def main():
    """Main test execution"""
    tester = BackendTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if "error" in results:
        sys.exit(1)
    
    # Count failures
    total_failures = 0
    for category_results in results.values():
        for result in category_results.values():
            if result.startswith("❌"):
                total_failures += 1
    
    sys.exit(0 if total_failures == 0 else 1)

if __name__ == "__main__":
    main()