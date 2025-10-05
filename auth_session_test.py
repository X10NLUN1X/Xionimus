#!/usr/bin/env python3
"""
Authentication and Session Persistence Testing Suite
Tests the critical fixes for session persistence in Xionimus AI application:
1. Backend SECRET_KEY persistence verification
2. Login flow testing
3. Token persistence after backend restart (Critical)
4. Protected endpoint access
5. Backend configuration verification
"""

import requests
import json
import time
import logging
import os
import subprocess
import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthSessionTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()
        
    def test_backend_env_file(self) -> Dict[str, Any]:
        """Test 1: Verify .env file exists and SECRET_KEY is set"""
        logger.info("🔒 Test 1: Backend SECRET_KEY Persistence Test")
        
        env_file_path = "/app/backend/.env"
        
        try:
            # Check if .env file exists
            if not os.path.exists(env_file_path):
                return {
                    "status": "failed",
                    "error": f".env file not found at {env_file_path}",
                    "critical": True
                }
            
            # Read .env file and check for SECRET_KEY
            with open(env_file_path, 'r') as f:
                env_content = f.read()
            
            secret_key_found = False
            secret_key_value = None
            jwt_algorithm = None
            jwt_expire_minutes = None
            
            for line in env_content.split('\n'):
                line = line.strip()
                if line.startswith('SECRET_KEY=') and not line.startswith('#'):
                    secret_key_found = True
                    secret_key_value = line.split('=', 1)[1]
                elif line.startswith('JWT_ALGORITHM=') and not line.startswith('#'):
                    jwt_algorithm = line.split('=', 1)[1]
                elif line.startswith('JWT_EXPIRE_MINUTES=') and not line.startswith('#'):
                    jwt_expire_minutes = line.split('=', 1)[1]
            
            if not secret_key_found or not secret_key_value:
                return {
                    "status": "failed",
                    "error": "SECRET_KEY not found or empty in .env file",
                    "critical": True
                }
            
            # Validate SECRET_KEY length
            if len(secret_key_value) < 32:
                logger.warning(f"⚠️ SECRET_KEY is short ({len(secret_key_value)} chars)")
            
            logger.info(f"✅ .env file exists at {env_file_path}")
            logger.info(f"✅ SECRET_KEY is set (length: {len(secret_key_value)} chars)")
            logger.info(f"✅ JWT_ALGORITHM: {jwt_algorithm}")
            logger.info(f"✅ JWT_EXPIRE_MINUTES: {jwt_expire_minutes}")
            
            return {
                "status": "success",
                "env_file_exists": True,
                "secret_key_set": True,
                "secret_key_length": len(secret_key_value),
                "jwt_algorithm": jwt_algorithm,
                "jwt_expire_minutes": jwt_expire_minutes
            }
            
        except Exception as e:
            logger.error(f"❌ Error checking .env file: {e}")
            return {
                "status": "error",
                "error": str(e),
                "critical": True
            }
    
    def test_backend_startup(self) -> Dict[str, Any]:
        """Test backend starts successfully with .env configuration"""
        logger.info("🚀 Testing backend startup with .env configuration")
        
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info("✅ Backend started successfully")
                logger.info(f"   Status: {health_data.get('status', 'unknown')}")
                
                return {
                    "status": "success",
                    "backend_healthy": True,
                    "health_data": health_data
                }
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Backend returned {response.status_code}",
                    "critical": True
                }
                
        except Exception as e:
            logger.error(f"❌ Backend startup test failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "critical": True
            }
    
    def check_backend_logs_for_warnings(self) -> Dict[str, Any]:
        """Check backend logs for SECRET_KEY warnings"""
        logger.info("📋 Checking backend logs for SECRET_KEY warnings")
        
        try:
            # Check supervisor logs for backend
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            log_content = result.stdout
            
            # Look for temporary key warnings
            temp_key_warnings = []
            for line in log_content.split('\n'):
                if "temporary key" in line.lower() or "SECRET_KEY not set" in line:
                    temp_key_warnings.append(line.strip())
            
            if temp_key_warnings:
                logger.warning("⚠️ Found SECRET_KEY warnings in logs:")
                for warning in temp_key_warnings:
                    logger.warning(f"   {warning}")
                
                return {
                    "status": "warning",
                    "warnings_found": True,
                    "warnings": temp_key_warnings
                }
            else:
                logger.info("✅ No SECRET_KEY warnings found in logs")
                return {
                    "status": "success",
                    "warnings_found": False
                }
                
        except Exception as e:
            logger.warning(f"⚠️ Could not check backend logs: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def test_login_flow(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test 2: Login Flow Test"""
        logger.info(f"🔐 Test 2: Login Flow Test with {username}/{password}")
        
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
                
                # Verify response contains required fields
                required_fields = ["access_token", "token_type", "user_id", "username"]
                missing_fields = [field for field in required_fields if field not in token_data]
                
                if missing_fields:
                    return {
                        "status": "failed",
                        "error": f"Missing fields in response: {missing_fields}",
                        "response": token_data
                    }
                
                self.token = token_data.get("access_token")
                self.user_info = {
                    "user_id": token_data.get("user_id"),
                    "username": token_data.get("username"),
                    "token_type": token_data.get("token_type"),
                    "role": token_data.get("role", "user")
                }
                
                # Verify token is a valid JWT
                try:
                    # Decode without verification to check structure
                    header = jwt.get_unverified_header(self.token)
                    payload = jwt.decode(self.token, options={"verify_signature": False})
                    
                    logger.info("✅ Login successful")
                    logger.info(f"   User ID: {token_data.get('user_id')}")
                    logger.info(f"   Username: {token_data.get('username')}")
                    logger.info(f"   Token Type: {token_data.get('token_type')}")
                    logger.info(f"   JWT Algorithm: {header.get('alg')}")
                    logger.info(f"   JWT Subject: {payload.get('sub')}")
                    
                    return {
                        "status": "success",
                        "token": self.token,
                        "user_info": self.user_info,
                        "jwt_valid": True,
                        "jwt_header": header,
                        "jwt_payload": payload
                    }
                    
                except Exception as jwt_error:
                    logger.error(f"❌ Token is not a valid JWT: {jwt_error}")
                    return {
                        "status": "failed",
                        "error": f"Invalid JWT token: {jwt_error}",
                        "token": self.token
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
            logger.error(f"❌ Login flow test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_protected_endpoint_access(self) -> Dict[str, Any]:
        """Test 4: Protected Endpoint Access"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("🔐 Test 4: Protected Endpoint Access")
        
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Test /api/rate-limits/quota endpoint
            response = self.session.get(f"{self.api_url}/rate-limits/quota", headers=headers, timeout=10)
            
            if response.status_code == 200:
                quota_data = response.json()
                logger.info("✅ Protected endpoint access successful")
                logger.info(f"   Endpoint: /api/rate-limits/quota")
                logger.info(f"   Response: {json.dumps(quota_data, indent=2)}")
                
                return {
                    "status": "success",
                    "endpoint_accessible": True,
                    "response_data": quota_data
                }
            elif response.status_code == 401:
                logger.error("❌ Protected endpoint returned 401 - token invalid")
                return {
                    "status": "failed",
                    "error": "Token authentication failed",
                    "status_code": response.status_code,
                    "critical": True
                }
            else:
                logger.warning(f"⚠️ Protected endpoint returned unexpected status: {response.status_code}")
                return {
                    "status": "unexpected",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Protected endpoint test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_invalid_token_rejection(self) -> Dict[str, Any]:
        """Test invalid tokens are properly rejected"""
        logger.info("🔐 Testing invalid token rejection")
        
        try:
            invalid_token = "invalid_token_12345"
            headers = {"Authorization": f"Bearer {invalid_token}"}
            
            response = self.session.get(f"{self.api_url}/rate-limits/quota", headers=headers, timeout=10)
            
            if response.status_code == 401:
                logger.info("✅ Invalid token correctly rejected with 401")
                return {
                    "status": "success",
                    "invalid_token_rejected": True
                }
            else:
                logger.error(f"❌ Invalid token not rejected (got {response.status_code})")
                return {
                    "status": "failed",
                    "error": f"Invalid token not rejected, got {response.status_code}",
                    "critical": True
                }
                
        except Exception as e:
            logger.error(f"❌ Invalid token test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def restart_backend_service(self) -> Dict[str, Any]:
        """Restart backend service using supervisor"""
        logger.info("🔄 Restarting backend service...")
        
        try:
            # Restart backend using supervisor
            result = subprocess.run(
                ["sudo", "supervisorctl", "restart", "backend"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Backend service restarted successfully")
                
                # Wait for backend to be ready
                max_wait = 30
                wait_time = 0
                
                while wait_time < max_wait:
                    try:
                        response = self.session.get(f"{self.api_url}/health", timeout=5)
                        if response.status_code == 200:
                            logger.info(f"✅ Backend ready after {wait_time}s")
                            return {
                                "status": "success",
                                "restart_successful": True,
                                "ready_time": wait_time
                            }
                    except:
                        pass
                    
                    time.sleep(2)
                    wait_time += 2
                
                return {
                    "status": "failed",
                    "error": "Backend did not become ready after restart",
                    "critical": True
                }
            else:
                logger.error(f"❌ Backend restart failed: {result.stderr}")
                return {
                    "status": "failed",
                    "error": f"Restart command failed: {result.stderr}",
                    "critical": True
                }
                
        except Exception as e:
            logger.error(f"❌ Backend restart failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "critical": True
            }
    
    def test_token_persistence_after_restart(self) -> Dict[str, Any]:
        """Test 3: Token Persistence Test (Critical) - Most Important Test"""
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        logger.info("🔄 Test 3: Token Persistence After Backend Restart (CRITICAL)")
        logger.info(f"   Using token: {self.token[:20]}...")
        
        # Step 1: Verify token works before restart
        logger.info("   Step 1: Verify token works before restart")
        pre_restart_test = self.test_protected_endpoint_access()
        if pre_restart_test["status"] != "success":
            return {
                "status": "failed",
                "error": "Token not working before restart",
                "pre_restart_result": pre_restart_test,
                "critical": True
            }
        
        # Step 2: Restart backend
        logger.info("   Step 2: Restart backend service")
        restart_result = self.restart_backend_service()
        if restart_result["status"] != "success":
            return {
                "status": "failed",
                "error": "Backend restart failed",
                "restart_result": restart_result,
                "critical": True
            }
        
        # Step 3: Test token after restart
        logger.info("   Step 3: Test token after restart")
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(f"{self.api_url}/rate-limits/quota", headers=headers, timeout=10)
            
            if response.status_code == 200:
                quota_data = response.json()
                logger.info("✅ CRITICAL TEST PASSED: Token remains valid after backend restart!")
                logger.info("✅ SECRET_KEY persistence confirmed")
                logger.info(f"   Token still works: {self.token[:20]}...")
                
                return {
                    "status": "success",
                    "token_persistent": True,
                    "secret_key_persistent": True,
                    "post_restart_response": quota_data,
                    "critical_test_passed": True
                }
            elif response.status_code == 401:
                logger.error("❌ CRITICAL TEST FAILED: Token invalid after restart!")
                logger.error("❌ This indicates SECRET_KEY is not persistent")
                logger.error("❌ Users will be logged out on every backend restart")
                
                return {
                    "status": "failed",
                    "error": "Token invalid after restart - SECRET_KEY not persistent",
                    "token_persistent": False,
                    "secret_key_persistent": False,
                    "critical": True,
                    "critical_test_failed": True
                }
            else:
                logger.warning(f"⚠️ Unexpected response after restart: {response.status_code}")
                return {
                    "status": "unexpected",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Token persistence test failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "critical": True
            }

def main():
    """Main test runner for Authentication and Session Persistence"""
    logger.info("🔒 Starting Authentication and Session Persistence Testing")
    logger.info("=" * 80)
    
    tester = AuthSessionTester()
    
    # Test 1: Backend SECRET_KEY Persistence Test
    logger.info("\n1️⃣ Backend SECRET_KEY Persistence Test")
    env_result = tester.test_backend_env_file()
    print(f"Backend .env Configuration: {env_result['status']}")
    
    if env_result['status'] != 'success':
        print(f"❌ CRITICAL: {env_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed without proper .env configuration")
        return
    
    # Test backend startup
    startup_result = tester.test_backend_startup()
    print(f"Backend Startup: {startup_result['status']}")
    
    if startup_result['status'] != 'success':
        print(f"❌ CRITICAL: {startup_result.get('error', 'Unknown error')}")
        return
    
    # Check for SECRET_KEY warnings in logs
    log_result = tester.check_backend_logs_for_warnings()
    if log_result['status'] == 'warning':
        print("⚠️ Found SECRET_KEY warnings in backend logs")
    else:
        print("✅ No SECRET_KEY warnings in logs")
    
    # Test 2: Login Flow Test
    logger.info("\n2️⃣ Login Flow Test")
    login_result = tester.test_login_flow()
    print(f"Login Flow: {login_result['status']}")
    
    if login_result['status'] != 'success':
        print(f"❌ Login failed: {login_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with token persistence tests")
        return
    
    print(f"✅ JWT Token obtained: {login_result['token'][:20]}...")
    
    # Test 4: Protected Endpoint Access (before restart)
    logger.info("\n4️⃣ Protected Endpoint Access Test")
    protected_result = tester.test_protected_endpoint_access()
    print(f"Protected Endpoint Access: {protected_result['status']}")
    
    if protected_result['status'] != 'success':
        print(f"❌ Protected endpoint access failed: {protected_result.get('error', 'Unknown error')}")
    
    # Test invalid token rejection
    invalid_result = tester.test_invalid_token_rejection()
    print(f"Invalid Token Rejection: {invalid_result['status']}")
    
    # Test 3: Token Persistence Test (Critical)
    logger.info("\n3️⃣ Token Persistence Test (CRITICAL)")
    persistence_result = tester.test_token_persistence_after_restart()
    print(f"Token Persistence After Restart: {persistence_result['status']}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("🔒 AUTHENTICATION & SESSION PERSISTENCE TEST SUMMARY")
    logger.info("=" * 80)
    
    test_results = [
        ("Backend .env Configuration", env_result['status'] == 'success'),
        ("Backend Startup", startup_result['status'] == 'success'),
        ("Login Flow", login_result['status'] == 'success'),
        ("Protected Endpoint Access", protected_result['status'] == 'success'),
        ("Invalid Token Rejection", invalid_result['status'] == 'success'),
        ("Token Persistence (CRITICAL)", persistence_result['status'] == 'success'),
    ]
    
    successful_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall Results: {successful_tests}/{total_tests} tests passed")
    
    for test_name, success in test_results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    # Critical Issues
    critical_issues = []
    
    if env_result.get('critical'):
        critical_issues.append("Backend .env file missing or invalid")
    if startup_result.get('critical'):
        critical_issues.append("Backend startup failed")
    if login_result.get('status') != 'success':
        critical_issues.append("Login flow broken")
    if protected_result.get('critical'):
        critical_issues.append("Protected endpoint authentication failed")
    if invalid_result.get('critical'):
        critical_issues.append("Invalid token rejection not working")
    if persistence_result.get('critical'):
        critical_issues.append("Token persistence failed - SECRET_KEY not persistent")
    
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: Authentication and session persistence working correctly!")
        print("   ✅ Backend .env file properly configured")
        print("   ✅ SECRET_KEY is persistent across restarts")
        print("   ✅ Login flow returns valid JWT tokens")
        print("   ✅ Protected endpoints accessible with valid tokens")
        print("   ✅ Invalid tokens properly rejected")
        print("   ✅ Tokens remain valid after backend restart")
        print("   ✅ Session persistence implemented successfully")
    
    # Special focus on the critical test
    if persistence_result.get('critical_test_passed'):
        print(f"\n🎉 CRITICAL SUCCESS: Token persistence test passed!")
        print("   🔑 SECRET_KEY is properly persistent")
        print("   🔄 Users will stay logged in after backend restarts")
    elif persistence_result.get('critical_test_failed'):
        print(f"\n💥 CRITICAL FAILURE: Token persistence test failed!")
        print("   🔑 SECRET_KEY is NOT persistent")
        print("   🔄 Users will be logged out on every backend restart")

if __name__ == "__main__":
    main()