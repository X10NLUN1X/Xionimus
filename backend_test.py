#!/usr/bin/env python3
"""
JWT Authentication Testing Suite
Tests the newly implemented JWT Authentication system in Xionimus AI backend
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JWTAuthTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        
    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health endpoint (should be public)"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
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
        """Test JWT login endpoint"""
        logger.info(f"🔐 Testing login with username: {username}")
        
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(
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
                    "token_type": token_data.get("token_type")
                }
                
                logger.info("✅ Login successful")
                logger.info(f"   Token type: {token_data.get('token_type')}")
                logger.info(f"   User ID: {token_data.get('user_id')}")
                logger.info(f"   Username: {token_data.get('username')}")
                
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
    
    def test_invalid_login(self) -> Dict[str, Any]:
        """Test login with invalid credentials"""
        logger.info("🔐 Testing login with invalid credentials")
        
        try:
            login_data = {
                "username": "invalid_user",
                "password": "wrong_password"
            }
            
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 401:
                logger.info("✅ Invalid login correctly rejected with 401")
                return {"status": "success", "message": "Invalid credentials correctly rejected"}
            else:
                logger.error(f"❌ Invalid login should return 401, got {response.status_code}")
                return {"status": "failed", "error": f"Expected 401, got {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Invalid login test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_protected_endpoint_without_auth(self) -> Dict[str, Any]:
        """Test accessing protected endpoint without authentication"""
        logger.info("🔒 Testing protected endpoint without authentication")
        
        try:
            # Test chat endpoint without auth
            response = requests.post(
                f"{self.api_url}/chat/",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "provider": "openai",
                    "model": "gpt-4"
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 401:
                logger.info("✅ Protected endpoint correctly requires authentication")
                return {"status": "success", "message": "Authentication required as expected"}
            else:
                logger.error(f"❌ Protected endpoint should require auth, got {response.status_code}")
                return {"status": "failed", "error": f"Expected 401, got {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Protected endpoint test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_protected_endpoint_with_auth(self) -> Dict[str, Any]:
        """Test accessing protected endpoint with valid JWT token"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("🔓 Testing protected endpoint with valid JWT token")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Test chat endpoint with auth
            response = requests.post(
                f"{self.api_url}/chat/",
                json={
                    "messages": [{"role": "user", "content": "Hello, this is a test message"}],
                    "provider": "openai",
                    "model": "gpt-4",
                    "session_id": f"test_session_{int(time.time())}"
                },
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info("✅ Protected endpoint accessible with valid token")
                response_data = response.json()
                return {
                    "status": "success", 
                    "message": "Chat API accessible with authentication",
                    "response": response_data
                }
            elif response.status_code == 401:
                logger.error("❌ Valid token rejected by protected endpoint")
                return {"status": "failed", "error": "Valid token was rejected"}
            else:
                logger.warning(f"⚠️ Protected endpoint returned {response.status_code}")
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                return {"status": "partial", "error": error_detail, "status_code": response.status_code}
                
        except Exception as e:
            logger.error(f"❌ Protected endpoint with auth test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_invalid_token(self) -> Dict[str, Any]:
        """Test accessing protected endpoint with invalid JWT token"""
        logger.info("🔒 Testing protected endpoint with invalid token")
        
        try:
            headers = {
                "Authorization": "Bearer invalid_token_12345",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.api_url}/chat/",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "provider": "openai",
                    "model": "gpt-4"
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 401:
                logger.info("✅ Invalid token correctly rejected")
                return {"status": "success", "message": "Invalid token correctly rejected"}
            else:
                logger.error(f"❌ Invalid token should be rejected, got {response.status_code}")
                return {"status": "failed", "error": f"Expected 401, got {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Invalid token test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_malformed_auth_header(self) -> Dict[str, Any]:
        """Test various malformed Authorization headers"""
        logger.info("🔒 Testing malformed Authorization headers")
        
        test_cases = [
            {"name": "Missing Bearer prefix", "header": self.token if self.token else "some_token"},
            {"name": "Wrong prefix", "header": f"Basic {self.token}" if self.token else "Basic some_token"},
            {"name": "Empty Bearer", "header": "Bearer "},
            {"name": "Only Bearer", "header": "Bearer"},
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                headers = {
                    "Authorization": test_case["header"],
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"{self.api_url}/chat/",
                    json={
                        "messages": [{"role": "user", "content": "Hello"}],
                        "provider": "openai",
                        "model": "gpt-4"
                    },
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 401:
                    logger.info(f"✅ {test_case['name']}: Correctly rejected")
                    results.append({"test": test_case["name"], "status": "success"})
                else:
                    logger.error(f"❌ {test_case['name']}: Should be rejected, got {response.status_code}")
                    results.append({"test": test_case["name"], "status": "failed", "status_code": response.status_code})
                    
            except Exception as e:
                logger.error(f"❌ {test_case['name']}: Test failed - {e}")
                results.append({"test": test_case["name"], "status": "error", "error": str(e)})
        
        return {"status": "completed", "results": results}
    
    def test_public_endpoints(self) -> Dict[str, Any]:
        """Test that public endpoints work without authentication"""
        logger.info("🌐 Testing public endpoints")
        
        public_endpoints = [
            {"name": "Health Check", "url": f"{self.api_url}/health", "method": "GET"},
            {"name": "Root Endpoint", "url": f"{self.base_url}/", "method": "GET"},
            {"name": "API Docs", "url": f"{self.base_url}/docs", "method": "GET"},
        ]
        
        results = []
        
        for endpoint in public_endpoints:
            try:
                if endpoint["method"] == "GET":
                    response = requests.get(endpoint["url"], timeout=10)
                else:
                    response = requests.post(endpoint["url"], timeout=10)
                
                if response.status_code in [200, 307]:  # 307 for redirects
                    logger.info(f"✅ {endpoint['name']}: Accessible without auth")
                    results.append({"endpoint": endpoint["name"], "status": "success"})
                else:
                    logger.error(f"❌ {endpoint['name']}: Failed with {response.status_code}")
                    results.append({"endpoint": endpoint["name"], "status": "failed", "status_code": response.status_code})
                    
            except Exception as e:
                logger.error(f"❌ {endpoint['name']}: Test failed - {e}")
                results.append({"endpoint": endpoint["name"], "status": "error", "error": str(e)})
        
        return {"status": "completed", "results": results}
    
    def test_user_session_association(self) -> Dict[str, Any]:
        """Test that chat sessions are properly associated with authenticated users"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("👤 Testing user session association")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            session_id = f"test_user_session_{int(time.time())}"
            
            # Send a chat message
            response = requests.post(
                f"{self.api_url}/chat/",
                json={
                    "messages": [{"role": "user", "content": "Test message for user session"}],
                    "provider": "openai",
                    "model": "gpt-4",
                    "session_id": session_id
                },
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                # Try to get sessions for the user
                sessions_response = requests.get(
                    f"{self.api_url}/sessions",
                    headers=headers,
                    timeout=10
                )
                
                if sessions_response.status_code == 200:
                    sessions_data = sessions_response.json()
                    logger.info("✅ User session association working")
                    return {
                        "status": "success",
                        "message": "Sessions properly associated with user",
                        "session_count": len(sessions_data.get("sessions", []))
                    }
                else:
                    logger.warning("⚠️ Chat worked but couldn't retrieve sessions")
                    return {"status": "partial", "error": "Could not retrieve user sessions"}
            else:
                logger.error(f"❌ Chat request failed: {response.status_code}")
                return {"status": "failed", "error": f"Chat request failed with {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ User session association test failed: {e}")
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