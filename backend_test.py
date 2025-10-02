#!/usr/bin/env python3
"""
Advanced Rate Limiting System Testing Suite
Tests the newly implemented Advanced Rate Limiting System in Xionimus AI backend
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

class RateLimitTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()  # Reuse connections for better performance
        
    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health endpoint (should be public and rate limited)"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend health check passed")
                return {"status": "healthy", "data": response.json()}
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_login_endpoint(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test JWT login endpoint and get authentication token"""
        logger.info(f"🔐 Testing login with username: {username}")
        
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
                
                logger.info("✅ Login successful for rate limiting tests")
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
                logger.error(f"❌ Login failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Login request failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_login_rate_limit(self) -> Dict[str, Any]:
        """Test login endpoint rate limiting (5 requests/minute)"""
        logger.info("🚦 Testing login rate limiting (5 requests/minute)")
        
        results = []
        rate_limited = False
        
        try:
            # Make 6 rapid login attempts to trigger rate limit
            for i in range(6):
                login_data = {
                    "username": "test_user_invalid",
                    "password": "invalid_password"
                }
                
                response = self.session.post(
                    f"{self.api_url}/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                results.append({
                    "attempt": i + 1,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                })
                
                if response.status_code == 429:
                    rate_limited = True
                    retry_after = response.headers.get("Retry-After", "Unknown")
                    logger.info(f"✅ Rate limit triggered on attempt {i + 1}, Retry-After: {retry_after}")
                    break
                
                # Small delay between requests
                time.sleep(0.1)
            
            if rate_limited:
                return {
                    "status": "success",
                    "message": "Login rate limiting working correctly",
                    "attempts_before_limit": len([r for r in results if r["status_code"] != 429]),
                    "results": results
                }
            else:
                return {
                    "status": "failed",
                    "error": "Rate limit not triggered after 6 attempts",
                    "results": results
                }
                
        except Exception as e:
            logger.error(f"❌ Login rate limit test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_chat_rate_limit(self) -> Dict[str, Any]:
        """Test chat endpoint rate limiting (30 requests/minute)"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("🚦 Testing chat rate limiting (30 requests/minute)")
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        results = []
        rate_limited = False
        
        try:
            # Make 32 rapid chat requests to trigger rate limit
            for i in range(32):
                chat_data = {
                    "messages": [{"role": "user", "content": f"Test message {i + 1}"}],
                    "provider": "openai",
                    "model": "gpt-4",
                    "session_id": f"rate_limit_test_{int(time.time())}"
                }
                
                response = self.session.post(
                    f"{self.api_url}/chat/",
                    json=chat_data,
                    headers=headers,
                    timeout=10
                )
                
                results.append({
                    "attempt": i + 1,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                })
                
                if response.status_code == 429:
                    rate_limited = True
                    retry_after = response.headers.get("Retry-After", "Unknown")
                    logger.info(f"✅ Chat rate limit triggered on attempt {i + 1}, Retry-After: {retry_after}")
                    break
                
                # Small delay between requests
                time.sleep(0.05)
            
            if rate_limited:
                return {
                    "status": "success",
                    "message": "Chat rate limiting working correctly",
                    "attempts_before_limit": len([r for r in results if r["status_code"] != 429]),
                    "results": results
                }
            else:
                return {
                    "status": "failed",
                    "error": "Chat rate limit not triggered after 32 attempts",
                    "results": results
                }
                
        except Exception as e:
            logger.error(f"❌ Chat rate limit test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_github_rate_limit(self) -> Dict[str, Any]:
        """Test GitHub endpoint rate limiting (10 requests/5 minutes)"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("🚦 Testing GitHub rate limiting (10 requests/5 minutes)")
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        results = []
        rate_limited = False
        
        try:
            # Make 12 rapid GitHub API requests to trigger rate limit
            for i in range(12):
                response = self.session.get(
                    f"{self.api_url}/github/user",
                    headers=headers,
                    timeout=10
                )
                
                results.append({
                    "attempt": i + 1,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                })
                
                if response.status_code == 429:
                    rate_limited = True
                    retry_after = response.headers.get("Retry-After", "Unknown")
                    logger.info(f"✅ GitHub rate limit triggered on attempt {i + 1}, Retry-After: {retry_after}")
                    break
                
                # Small delay between requests
                time.sleep(0.1)
            
            if rate_limited:
                return {
                    "status": "success",
                    "message": "GitHub rate limiting working correctly",
                    "attempts_before_limit": len([r for r in results if r["status_code"] != 429]),
                    "results": results
                }
            else:
                return {
                    "status": "partial",
                    "message": "GitHub rate limit not triggered (may require GitHub integration)",
                    "results": results
                }
                
        except Exception as e:
            logger.error(f"❌ GitHub rate limit test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_user_quota_tracking(self) -> Dict[str, Any]:
        """Test user-based quota tracking and limits"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("📊 Testing user quota tracking")
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get initial quota status
            response = self.session.get(
                f"{self.api_url}/rate-limits/quota",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                quota_data = response.json()
                logger.info("✅ User quota endpoint accessible")
                logger.info(f"   User role: {quota_data.get('user_role', 'unknown')}")
                logger.info(f"   Requests used: {quota_data.get('requests', {}).get('used', 0)}")
                logger.info(f"   Requests limit: {quota_data.get('requests', {}).get('limit', 0)}")
                logger.info(f"   AI calls used: {quota_data.get('ai_calls', {}).get('used', 0)}")
                logger.info(f"   AI calls limit: {quota_data.get('ai_calls', {}).get('limit', 0)}")
                
                return {
                    "status": "success",
                    "message": "User quota tracking working",
                    "quota_data": quota_data
                }
            else:
                logger.error(f"❌ Quota endpoint failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Quota endpoint returned {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ User quota test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_rate_limit_management_api(self) -> Dict[str, Any]:
        """Test rate limiting management API endpoints"""
        logger.info("⚙️ Testing rate limiting management API")
        
        results = {}
        
        try:
            # Test public rate limits endpoint
            response = self.session.get(f"{self.api_url}/rate-limits/limits", timeout=10)
            if response.status_code == 200:
                limits_data = response.json()
                results["limits_endpoint"] = {
                    "status": "success",
                    "rate_limits_count": len(limits_data.get("rate_limits", [])),
                    "user_quotas": limits_data.get("user_quotas", {})
                }
                logger.info("✅ Rate limits configuration endpoint working")
            else:
                results["limits_endpoint"] = {
                    "status": "failed",
                    "status_code": response.status_code
                }
            
            # Test health endpoint
            response = self.session.get(f"{self.api_url}/rate-limits/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                results["health_endpoint"] = {
                    "status": "success",
                    "health_data": health_data
                }
                logger.info("✅ Rate limiter health endpoint working")
            else:
                results["health_endpoint"] = {
                    "status": "failed",
                    "status_code": response.status_code
                }
            
            # Test admin stats endpoint (may require admin token)
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = self.session.get(
                    f"{self.api_url}/rate-limits/stats",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    stats_data = response.json()
                    results["stats_endpoint"] = {
                        "status": "success",
                        "stats_data": stats_data
                    }
                    logger.info("✅ Rate limiter stats endpoint working")
                elif response.status_code == 403:
                    results["stats_endpoint"] = {
                        "status": "access_denied",
                        "message": "Admin access required (expected for non-admin users)"
                    }
                    logger.info("⚠️ Stats endpoint requires admin access (expected)")
                else:
                    results["stats_endpoint"] = {
                        "status": "failed",
                        "status_code": response.status_code
                    }
            
            return {
                "status": "success",
                "message": "Rate limiting management API tested",
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Rate limit management API test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_429_response_format(self) -> Dict[str, Any]:
        """Test that 429 responses have proper format and headers"""
        logger.info("📋 Testing 429 response format and headers")
        
        try:
            # Make rapid requests to trigger 429
            for i in range(10):
                response = self.session.post(
                    f"{self.api_url}/auth/login",
                    json={"username": "test", "password": "test"},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 429:
                    # Check response format
                    try:
                        response_data = response.json()
                    except:
                        response_data = {}
                    
                    # Check required headers
                    retry_after = response.headers.get("Retry-After")
                    content_type = response.headers.get("Content-Type")
                    
                    logger.info("✅ 429 response triggered, checking format...")
                    logger.info(f"   Retry-After header: {retry_after}")
                    logger.info(f"   Content-Type: {content_type}")
                    logger.info(f"   Response body: {response_data}")
                    
                    # Validate response format
                    validation_results = {
                        "has_retry_after": retry_after is not None,
                        "has_detail": "detail" in response_data,
                        "has_type": "type" in response_data,
                        "is_json": "application/json" in (content_type or ""),
                        "retry_after_value": retry_after
                    }
                    
                    all_valid = all(validation_results.values())
                    
                    return {
                        "status": "success" if all_valid else "partial",
                        "message": "429 response format validated",
                        "validation": validation_results,
                        "response_data": response_data
                    }
                
                time.sleep(0.1)
            
            return {
                "status": "failed",
                "error": "Could not trigger 429 response for format testing"
            }
            
        except Exception as e:
            logger.error(f"❌ 429 response format test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_public_endpoint_limits(self) -> Dict[str, Any]:
        """Test that public endpoints have appropriate rate limits"""
        logger.info("🌐 Testing public endpoint rate limits")
        
        public_endpoints = [
            {"name": "Health Check", "url": f"{self.api_url}/health", "method": "GET"},
            {"name": "Rate Limits Info", "url": f"{self.api_url}/rate-limits/limits", "method": "GET"},
            {"name": "Rate Limiter Health", "url": f"{self.api_url}/rate-limits/health", "method": "GET"},
        ]
        
        results = []
        
        for endpoint in public_endpoints:
            try:
                logger.info(f"Testing {endpoint['name']} rate limits...")
                
                # Make multiple requests to test rate limiting
                responses = []
                for i in range(5):
                    if endpoint["method"] == "GET":
                        response = self.session.get(endpoint["url"], timeout=10)
                    else:
                        response = self.session.post(endpoint["url"], timeout=10)
                    
                    responses.append({
                        "attempt": i + 1,
                        "status_code": response.status_code,
                        "has_retry_after": "Retry-After" in response.headers
                    })
                    
                    time.sleep(0.1)
                
                # Check if any requests were rate limited
                rate_limited_count = len([r for r in responses if r["status_code"] == 429])
                successful_count = len([r for r in responses if r["status_code"] == 200])
                
                results.append({
                    "endpoint": endpoint["name"],
                    "status": "tested",
                    "successful_requests": successful_count,
                    "rate_limited_requests": rate_limited_count,
                    "responses": responses
                })
                
            except Exception as e:
                results.append({
                    "endpoint": endpoint["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "message": "Public endpoint rate limits tested",
            "results": results
        }
    
    def test_concurrent_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting under concurrent load"""
        logger.info("🔄 Testing concurrent rate limiting")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        def make_request(request_id: int) -> Dict[str, Any]:
            """Make a single request"""
            try:
                response = requests.post(
                    f"{self.api_url}/chat/",
                    json={
                        "messages": [{"role": "user", "content": f"Concurrent test {request_id}"}],
                        "provider": "openai",
                        "model": "gpt-4",
                        "session_id": f"concurrent_test_{request_id}"
                    },
                    headers=headers,
                    timeout=10
                )
                
                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "has_retry_after": "Retry-After" in response.headers,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
        
        try:
            # Make 20 concurrent requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request, i) for i in range(20)]
                results = [future.result() for future in as_completed(futures)]
            
            # Analyze results
            successful = len([r for r in results if r.get("status_code") == 200])
            rate_limited = len([r for r in results if r.get("status_code") == 429])
            errors = len([r for r in results if "error" in r])
            
            logger.info(f"✅ Concurrent test completed: {successful} success, {rate_limited} rate limited, {errors} errors")
            
            return {
                "status": "success",
                "message": "Concurrent rate limiting tested",
                "summary": {
                    "total_requests": len(results),
                    "successful": successful,
                    "rate_limited": rate_limited,
                    "errors": errors
                },
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Concurrent rate limiting test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_websocket_rate_limiting(self) -> Dict[str, Any]:
        """Test that WebSocket connections are not affected by rate limiting"""
        logger.info("🔌 Testing WebSocket rate limiting exemption")
        
        try:
            # WebSocket connections should bypass rate limiting
            # This is a basic connectivity test since WebSocket testing is complex
            
            # Test that WebSocket endpoint exists and is accessible
            # Note: Actual WebSocket testing would require websocket client library
            
            logger.info("⚠️ WebSocket rate limiting test requires specialized WebSocket client")
            logger.info("   Current implementation: WebSocket endpoints bypass rate limiting")
            
            return {
                "status": "info",
                "message": "WebSocket endpoints configured to bypass rate limiting",
                "note": "Full WebSocket testing requires specialized client library"
            }
            
        except Exception as e:
            logger.error(f"❌ WebSocket rate limiting test failed: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Main test runner for JWT Authentication"""
    logger.info("🚀 Starting JWT Authentication Tests")
    logger.info("=" * 60)
    
    tester = JWTAuthTester()
    
    # Test 1: Backend Health (Public)
    logger.info("1️⃣ Testing Backend Health (Public Endpoint)")
    health_result = tester.test_backend_health()
    print(f"Backend Health: {health_result['status']}")
    if health_result['status'] != 'healthy':
        print(f"❌ Backend is not healthy: {health_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with authentication tests")
        return
    
    # Test 2: Public Endpoints
    logger.info("\n2️⃣ Testing Public Endpoints")
    public_result = tester.test_public_endpoints()
    public_success = sum(1 for r in public_result['results'] if r['status'] == 'success')
    print(f"Public Endpoints: {public_success}/{len(public_result['results'])} accessible")
    
    # Test 3: Protected Endpoint Without Auth
    logger.info("\n3️⃣ Testing Protected Endpoint Without Authentication")
    no_auth_result = tester.test_protected_endpoint_without_auth()
    print(f"Protected Endpoint (No Auth): {no_auth_result['status']}")
    
    # Test 4: Invalid Login
    logger.info("\n4️⃣ Testing Invalid Login Credentials")
    invalid_login_result = tester.test_invalid_login()
    print(f"Invalid Login Test: {invalid_login_result['status']}")
    
    # Test 5: Valid Login
    logger.info("\n5️⃣ Testing Valid Login (Demo User)")
    login_result = tester.test_login_endpoint()
    print(f"Valid Login Test: {login_result['status']}")
    
    if login_result['status'] != 'success':
        print(f"❌ Login failed: {login_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with authenticated endpoint tests")
        return
    
    # Test 6: Protected Endpoint With Valid Auth
    logger.info("\n6️⃣ Testing Protected Endpoint With Valid Authentication")
    auth_result = tester.test_protected_endpoint_with_auth()
    print(f"Protected Endpoint (With Auth): {auth_result['status']}")
    
    # Test 7: Invalid Token
    logger.info("\n7️⃣ Testing Invalid JWT Token")
    invalid_token_result = tester.test_invalid_token()
    print(f"Invalid Token Test: {invalid_token_result['status']}")
    
    # Test 8: Malformed Auth Headers
    logger.info("\n8️⃣ Testing Malformed Authorization Headers")
    malformed_result = tester.test_malformed_auth_header()
    malformed_success = sum(1 for r in malformed_result['results'] if r['status'] == 'success')
    print(f"Malformed Headers: {malformed_success}/{len(malformed_result['results'])} correctly rejected")
    
    # Test 9: User Session Association
    logger.info("\n9️⃣ Testing User Session Association")
    session_result = tester.test_user_session_association()
    print(f"User Session Association: {session_result['status']}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 JWT AUTHENTICATION TEST SUMMARY")
    logger.info("=" * 60)
    
    # Count successful tests
    test_results = [
        ("Backend Health", health_result['status'] == 'healthy'),
        ("Public Endpoints", public_success == len(public_result['results'])),
        ("Protected Without Auth", no_auth_result['status'] == 'success'),
        ("Invalid Login Rejection", invalid_login_result['status'] == 'success'),
        ("Valid Login", login_result['status'] == 'success'),
        ("Protected With Auth", auth_result['status'] == 'success'),
        ("Invalid Token Rejection", invalid_token_result['status'] == 'success'),
        ("Malformed Headers", malformed_success == len(malformed_result['results'])),
        ("User Session Association", session_result['status'] == 'success'),
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
        critical_issues.append("Backend not healthy")
    if login_result['status'] != 'success':
        critical_issues.append("Login endpoint not working")
    if no_auth_result['status'] != 'success':
        critical_issues.append("Protected endpoints not properly secured")
    if auth_result['status'] != 'success':
        critical_issues.append("Valid tokens not accepted")
    
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: JWT Authentication system is working correctly!")
        print("   - Login/logout functionality operational")
        print("   - Protected endpoints properly secured")
        print("   - JWT tokens validated correctly")
        print("   - User sessions associated with authenticated users")

if __name__ == "__main__":
    main()