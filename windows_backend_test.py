#!/usr/bin/env python3
"""
COMPREHENSIVE WINDOWS BACKEND TESTING
=====================================

Tests Xionimus AI backend for Windows compatibility focusing on:
1. Backend startup test (SQLite instead of MongoDB, no Redis)
2. Authentication system 
3. Core API endpoints
4. Windows-specific issues (SQLite WAL mode, file paths, no MongoDB/Redis)
5. Error handling

Based on review request for Windows local deployment.
"""

import requests
import json
import time
import sys
import os
from pathlib import Path
import subprocess
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindowsBackendTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.test_results = []
        self.startup_time = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        logger.info(f"{status} - {test_name}: {details}")
        
    def make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with error handling"""
        url = f"{self.api_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            kwargs['headers'] = headers
            
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def test_backend_startup(self):
        """Test 1: Backend Startup Test"""
        logger.info("🚀 Testing Backend Startup...")
        
        start_time = time.time()
        max_wait = 30  # 30 seconds max wait
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    self.startup_time = time.time() - start_time
                    data = response.json()
                    
                    # Check for Windows-specific requirements
                    db_type = data.get('services', {}).get('database', {}).get('type', 'Unknown')
                    status = data.get('status', 'unknown')
                    
                    success = (
                        self.startup_time <= 30 and  # Within 30 seconds
                        db_type == 'SQLite' and     # Using SQLite (Windows compatible)
                        status in ['healthy', 'limited']  # Backend is running
                    )
                    
                    details = f"Startup time: {self.startup_time:.2f}s, DB: {db_type}, Status: {status}"
                    self.log_test("Backend Startup", success, details, data)
                    return success
                    
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        # Timeout reached
        self.log_test("Backend Startup", False, f"Backend did not start within {max_wait} seconds")
        return False
    
    def test_sqlite_database(self):
        """Test 2: SQLite Database Configuration"""
        logger.info("💾 Testing SQLite Database...")
        
        response = self.make_request('GET', '/health')
        if not response or response.status_code != 200:
            self.log_test("SQLite Database", False, "Health endpoint not accessible")
            return False
            
        data = response.json()
        services = data.get('services', {})
        database = services.get('database', {})
        
        db_type = database.get('type', '')
        db_status = database.get('status', '')
        
        # Check SQLite is being used and working
        success = (
            db_type == 'SQLite' and
            db_status == 'connected'
        )
        
        details = f"Type: {db_type}, Status: {db_status}"
        if database.get('error'):
            details += f", Error: {database['error']}"
            
        self.log_test("SQLite Database", success, details, database)
        return success
    
    def test_no_mongodb_redis_hanging(self):
        """Test 3: No MongoDB/Redis Hanging"""
        logger.info("🔍 Testing No MongoDB/Redis Hanging...")
        
        # Check that backend started quickly (already tested in startup)
        if self.startup_time and self.startup_time <= 30:
            success = True
            details = f"Backend started in {self.startup_time:.2f}s - no hanging detected"
        else:
            success = False
            details = "Backend startup took too long - possible hanging on MongoDB/Redis"
            
        self.log_test("No MongoDB/Redis Hanging", success, details)
        return success
    
    def test_authentication_system(self):
        """Test 4: Authentication System"""
        logger.info("🔐 Testing Authentication System...")
        
        # Test login with admin/admin123
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.make_request('POST', '/auth/login', json=login_data)
        if not response:
            self.log_test("Authentication System", False, "Login request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            token_type = data.get('token_type')
            
            if token and token_type == 'bearer':
                self.token = token
                success = True
                details = f"Login successful, token received (type: {token_type})"
            else:
                success = False
                details = f"Login response missing token or wrong type: {data}"
        else:
            success = False
            details = f"Login failed with status {response.status_code}: {response.text}"
            
        self.log_test("Authentication System", success, details)
        return success
    
    def test_jwt_token_validation(self):
        """Test 5: JWT Token Validation"""
        logger.info("🎫 Testing JWT Token Validation...")
        
        if not self.token:
            self.log_test("JWT Token Validation", False, "No token available from login")
            return False
            
        # Test protected endpoint with valid token
        response = self.make_request('GET', '/sessions/list')
        
        if response and response.status_code == 200:
            success = True
            details = "JWT token validation successful - protected endpoint accessible"
        else:
            success = False
            status = response.status_code if response else "No response"
            details = f"JWT token validation failed - status: {status}"
            
        self.log_test("JWT Token Validation", success, details)
        return success
    
    def test_core_api_endpoints(self):
        """Test 6: Core API Endpoints"""
        logger.info("🌐 Testing Core API Endpoints...")
        
        endpoints_to_test = [
            ('GET', '/health', 'Health Check'),
            ('GET', '/v1/health', 'V1 Health Check'),
            ('GET', '/sessions/list', 'Sessions List'),
            ('GET', '/v1/multi-agents/types', 'Multi-Agent Types'),
        ]
        
        all_success = True
        results = []
        
        for method, endpoint, name in endpoints_to_test:
            response = self.make_request(method, endpoint)
            
            if response and response.status_code == 200:
                success = True
                details = f"{name} - OK"
                try:
                    data = response.json()
                    if endpoint == '/health':
                        # Additional health check validation
                        status = data.get('status', 'unknown')
                        details += f" (status: {status})"
                except:
                    pass
            else:
                success = False
                status = response.status_code if response else "No response"
                details = f"{name} - Failed (status: {status})"
                all_success = False
                
            results.append(f"{details}")
        
        details_str = "; ".join(results)
        self.log_test("Core API Endpoints", all_success, details_str)
        return all_success
    
    def test_windows_file_paths(self):
        """Test 7: Windows File Path Handling"""
        logger.info("📁 Testing Windows File Path Handling...")
        
        # Check if SQLite database is created in user home directory
        from pathlib import Path
        home_dir = Path.home() / ".xionimus_ai"
        db_path = home_dir / "xionimus.db"
        
        success = db_path.exists()
        if success:
            details = f"SQLite database found at: {db_path}"
            # Check if WAL files exist (indicates WAL mode is working)
            wal_path = db_path.with_suffix('.db-wal')
            if wal_path.exists():
                details += " (WAL mode active)"
        else:
            details = f"SQLite database not found at expected path: {db_path}"
            
        self.log_test("Windows File Path Handling", success, details)
        return success
    
    def test_error_handling(self):
        """Test 8: Error Handling"""
        logger.info("⚠️ Testing Error Handling...")
        
        # Test invalid endpoint
        response = self.make_request('GET', '/nonexistent-endpoint')
        
        if response and response.status_code == 404:
            success = True
            details = "404 error handling working correctly"
        else:
            success = False
            status = response.status_code if response else "No response"
            details = f"Error handling failed - expected 404, got: {status}"
            
        self.log_test("Error Handling", success, details)
        return success
    
    def test_api_keys_missing_graceful_degradation(self):
        """Test 9: Graceful Degradation without API Keys"""
        logger.info("🔑 Testing Graceful Degradation without API Keys...")
        
        response = self.make_request('GET', '/health')
        if not response or response.status_code != 200:
            self.log_test("Graceful Degradation", False, "Health endpoint not accessible")
            return False
            
        data = response.json()
        ai_providers = data.get('services', {}).get('ai_providers', {})
        configured_count = ai_providers.get('configured', 0)
        status = data.get('status', 'unknown')
        
        # Should be 'limited' status when no AI providers configured
        success = (status == 'limited' and configured_count == 0)
        details = f"Status: {status}, AI providers configured: {configured_count}"
        
        self.log_test("Graceful Degradation", success, details, ai_providers)
        return success
    
    def test_admin_user_creation(self):
        """Test 10: Admin User Auto-Creation"""
        logger.info("👤 Testing Admin User Auto-Creation...")
        
        # We already tested login with admin/admin123 in authentication test
        # This test verifies the user was auto-created
        if self.token:
            # Test getting user info
            response = self.make_request('GET', '/auth/me')
            
            if response and response.status_code == 200:
                data = response.json()
                username = data.get('username', '')
                success = username == 'admin'
                details = f"Admin user found: {username}"
            else:
                success = False
                details = "Could not retrieve user info"
        else:
            success = False
            details = "No token available - admin user not created or login failed"
            
        self.log_test("Admin User Auto-Creation", success, details)
        return success
    
    def run_all_tests(self):
        """Run all Windows backend tests"""
        logger.info("=" * 70)
        logger.info("🪟 COMPREHENSIVE WINDOWS BACKEND TESTING")
        logger.info("=" * 70)
        
        tests = [
            self.test_backend_startup,
            self.test_sqlite_database,
            self.test_no_mongodb_redis_hanging,
            self.test_authentication_system,
            self.test_jwt_token_validation,
            self.test_core_api_endpoints,
            self.test_windows_file_paths,
            self.test_error_handling,
            self.test_api_keys_missing_graceful_degradation,
            self.test_admin_user_creation,
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                logger.error(f"Test {test_func.__name__} crashed: {e}")
                self.log_test(test_func.__name__, False, f"Test crashed: {e}")
        
        # Generate summary
        self.generate_summary(passed, total)
        return passed == total
    
    def generate_summary(self, passed: int, total: int):
        """Generate test summary"""
        logger.info("=" * 70)
        logger.info("📊 WINDOWS BACKEND TEST SUMMARY")
        logger.info("=" * 70)
        
        success_rate = (passed / total) * 100
        logger.info(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if self.startup_time:
            logger.info(f"Backend Startup Time: {self.startup_time:.2f} seconds")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            logger.info(f"{status} {result['test']}: {result['details']}")
        
        logger.info("\n🎯 WINDOWS COMPATIBILITY STATUS:")
        if success_rate >= 90:
            logger.info("✅ EXCELLENT - Windows backend fully compatible")
        elif success_rate >= 75:
            logger.info("⚠️ GOOD - Windows backend mostly compatible with minor issues")
        elif success_rate >= 50:
            logger.info("🔶 FAIR - Windows backend partially compatible, needs fixes")
        else:
            logger.info("❌ POOR - Windows backend has major compatibility issues")
        
        # Windows-specific findings
        logger.info("\n🪟 WINDOWS-SPECIFIC FINDINGS:")
        
        # Check SQLite usage
        sqlite_test = next((r for r in self.test_results if r['test'] == 'SQLite Database'), None)
        if sqlite_test and sqlite_test['success']:
            logger.info("✅ SQLite database working correctly (Windows compatible)")
        else:
            logger.info("❌ SQLite database issues detected")
        
        # Check startup time
        if self.startup_time and self.startup_time <= 30:
            logger.info(f"✅ Fast startup ({self.startup_time:.2f}s) - no MongoDB/Redis hanging")
        else:
            logger.info("❌ Slow startup detected - possible MongoDB/Redis connection issues")
        
        # Check file paths
        file_path_test = next((r for r in self.test_results if r['test'] == 'Windows File Path Handling'), None)
        if file_path_test and file_path_test['success']:
            logger.info("✅ Windows file path handling working correctly")
        else:
            logger.info("❌ Windows file path issues detected")
        
        logger.info("=" * 70)

def main():
    """Main test execution"""
    tester = WindowsBackendTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()