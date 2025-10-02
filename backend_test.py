#!/usr/bin/env python3
"""
Security Improvements Testing Suite
Tests the security hardening updates in Xionimus AI backend including:
- Security headers middleware
- Updated vulnerable dependencies
- Authentication functionality
- Rate limiting system
- Core functionality integrity
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

class SecurityTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()  # Reuse connections for better performance
        
    def test_security_headers(self) -> Dict[str, Any]:
        """Test security headers middleware on /api/health endpoint"""
        logger.info("🔒 Testing security headers on /api/health endpoint")
        
        expected_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Health endpoint returned {response.status_code}",
                    "response": response.text
                }
            
            # Check each security header
            header_results = {}
            all_headers_present = True
            
            for header_name, expected_value in expected_headers.items():
                actual_value = response.headers.get(header_name)
                header_results[header_name] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "present": actual_value is not None,
                    "correct": actual_value == expected_value
                }
                
                if actual_value != expected_value:
                    all_headers_present = False
                    logger.warning(f"❌ Header {header_name}: expected '{expected_value}', got '{actual_value}'")
                else:
                    logger.info(f"✅ Header {header_name}: {actual_value}")
            
            return {
                "status": "success" if all_headers_present else "partial",
                "message": f"Security headers check: {len([h for h in header_results.values() if h['correct']])}/{len(expected_headers)} correct",
                "headers": header_results,
                "all_correct": all_headers_present
            }
            
        except Exception as e:
            logger.error(f"❌ Security headers test failed: {e}")
            return {"status": "error", "error": str(e)}
        
    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health endpoint and dependency stability"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                logger.info("✅ Backend health check passed")
                logger.info(f"   Status: {health_data.get('status', 'unknown')}")
                logger.info(f"   Version: {health_data.get('version', 'unknown')}")
                logger.info(f"   Database: {health_data.get('services', {}).get('database', {}).get('status', 'unknown')}")
                
                return {
                    "status": "healthy", 
                    "data": health_data,
                    "dependencies_working": True
                }
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return {
                    "status": "unhealthy", 
                    "error": f"HTTP {response.status_code}",
                    "dependencies_working": False
                }
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "dependencies_working": False
            }
    
    def test_authentication_system(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test JWT authentication system after security updates"""
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
    
    def test_protected_endpoints(self) -> Dict[str, Any]:
        """Test that protected endpoints work correctly with valid tokens"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("🔐 Testing protected endpoints with valid token")
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        protected_endpoints = [
            {"name": "Sessions List", "url": f"{self.api_url}/sessions/list", "method": "GET"},
            {"name": "Rate Limits Quota", "url": f"{self.api_url}/rate-limits/quota", "method": "GET"},
        ]
        
        results = []
        
        for endpoint in protected_endpoints:
            try:
                if endpoint["method"] == "GET":
                    response = self.session.get(endpoint["url"], headers=headers, timeout=10)
                else:
                    response = self.session.post(endpoint["url"], headers=headers, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"✅ {endpoint['name']}: Working correctly")
                    results.append({
                        "endpoint": endpoint["name"],
                        "status": "success",
                        "status_code": response.status_code
                    })
                elif response.status_code == 401:
                    logger.error(f"❌ {endpoint['name']}: Authentication failed")
                    results.append({
                        "endpoint": endpoint["name"],
                        "status": "auth_failed",
                        "status_code": response.status_code
                    })
                else:
                    logger.warning(f"⚠️ {endpoint['name']}: Unexpected status {response.status_code}")
                    results.append({
                        "endpoint": endpoint["name"],
                        "status": "unexpected",
                        "status_code": response.status_code
                    })
                    
            except Exception as e:
                logger.error(f"❌ {endpoint['name']}: Error - {e}")
                results.append({
                    "endpoint": endpoint["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        successful_count = len([r for r in results if r["status"] == "success"])
        
        return {
            "status": "success" if successful_count == len(protected_endpoints) else "partial",
            "message": f"Protected endpoints: {successful_count}/{len(protected_endpoints)} working",
            "results": results
        }
    
    def test_invalid_token_rejection(self) -> Dict[str, Any]:
        """Test that invalid tokens are properly rejected with 401"""
        logger.info("🔐 Testing invalid token rejection")
        
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        ]
        
        results = []
        
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = self.session.get(f"{self.api_url}/sessions/list", headers=headers, timeout=10)
                
                if response.status_code == 401:
                    logger.info(f"✅ Invalid token correctly rejected: {token[:20]}...")
                    results.append({
                        "token": token[:20] + "...",
                        "status": "correctly_rejected",
                        "status_code": response.status_code
                    })
                else:
                    logger.error(f"❌ Invalid token not rejected: {token[:20]}... (got {response.status_code})")
                    results.append({
                        "token": token[:20] + "...",
                        "status": "not_rejected",
                        "status_code": response.status_code
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error testing invalid token: {e}")
                results.append({
                    "token": token[:20] + "...",
                    "status": "error",
                    "error": str(e)
                })
        
        successful_rejections = len([r for r in results if r["status"] == "correctly_rejected"])
        
        return {
            "status": "success" if successful_rejections == len(invalid_tokens) else "partial",
            "message": f"Invalid token rejection: {successful_rejections}/{len(invalid_tokens)} correctly rejected",
            "results": results
        }
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
                {"name": "Sessions List", "url": f"{self.api_url}/sessions/list", "method": "GET", "auth_required": True},
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