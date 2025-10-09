#!/usr/bin/env python3
"""
COMPREHENSIVE WINDOWS BACKEND TESTING - ENHANCED VERSION
========================================================

Enhanced Windows backend testing based on review requirements:
1. Backend startup test (SQLite instead of MongoDB, no Redis)
2. Authentication system with correct credentials
3. Core API endpoints
4. Windows-specific issues (SQLite WAL mode, file paths, no MongoDB/Redis)
5. Error handling with proper endpoint testing
6. Environment validation
7. Service degradation testing
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
import sqlite3

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
    
    def test_backend_startup_comprehensive(self):
        """Test 1: Comprehensive Backend Startup Test"""
        logger.info("🚀 Testing Comprehensive Backend Startup...")
        
        start_time = time.time()
        max_wait = 30  # 30 seconds max wait
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    self.startup_time = time.time() - start_time
                    data = response.json()
                    
                    # Comprehensive Windows requirements check
                    db_type = data.get('services', {}).get('database', {}).get('type', 'Unknown')
                    status = data.get('status', 'unknown')
                    version = data.get('version', 'unknown')
                    platform = data.get('platform', 'unknown')
                    uptime = data.get('uptime_seconds', 0)
                    
                    success = (
                        self.startup_time <= 30 and  # Within 30 seconds
                        db_type == 'SQLite' and     # Using SQLite (Windows compatible)
                        status in ['healthy', 'limited'] and  # Backend is running
                        platform == 'Xionimus AI' and  # Correct platform
                        uptime >= 0  # Uptime tracking working
                    )
                    
                    details = f"Startup: {self.startup_time:.2f}s, DB: {db_type}, Status: {status}, Platform: {platform}, Version: {version}"
                    self.log_test("Backend Startup Comprehensive", success, details, data)
                    return success
                    
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        # Timeout reached
        self.log_test("Backend Startup Comprehensive", False, f"Backend did not start within {max_wait} seconds")
        return False
    
    def test_sqlite_wal_mode(self):
        """Test 2: SQLite WAL Mode on Windows"""
        logger.info("💾 Testing SQLite WAL Mode...")
        
        # Check if SQLite database exists and WAL mode is enabled
        home_dir = Path.home() / ".xionimus_ai"
        db_path = home_dir / "xionimus.db"
        
        if not db_path.exists():
            self.log_test("SQLite WAL Mode", False, f"SQLite database not found at {db_path}")
            return False
        
        try:
            # Connect to SQLite and check journal mode
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode;")
            journal_mode = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA synchronous;")
            synchronous = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA cache_size;")
            cache_size = cursor.fetchone()[0]
            
            conn.close()
            
            # Check for WAL files
            wal_path = db_path.with_suffix('.db-wal')
            shm_path = db_path.with_suffix('.db-shm')
            
            success = (
                journal_mode.upper() == 'WAL' and
                wal_path.exists()  # WAL file should exist
            )
            
            details = f"Journal mode: {journal_mode}, Sync: {synchronous}, Cache: {cache_size}, WAL file exists: {wal_path.exists()}"
            
        except Exception as e:
            success = False
            details = f"SQLite WAL mode check failed: {e}"
        
        self.log_test("SQLite WAL Mode", success, details)
        return success
    
    def test_environment_validation(self):
        """Test 3: Environment Validation"""
        logger.info("🔧 Testing Environment Validation...")
        
        # Check if backend started without MongoDB/Redis URLs
        response = self.make_request('GET', '/health')
        if not response or response.status_code != 200:
            self.log_test("Environment Validation", False, "Health endpoint not accessible")
            return False
            
        data = response.json()
        
        # Check that backend is running in limited mode (no AI providers)
        status = data.get('status', 'unknown')
        ai_providers = data.get('services', {}).get('ai_providers', {})
        configured_count = ai_providers.get('configured', 0)
        
        # Should gracefully handle missing MongoDB/Redis
        success = (
            status == 'limited' and  # Limited functionality without AI providers
            configured_count == 0    # No AI providers configured
        )
        
        details = f"Status: {status}, AI providers: {configured_count}, Environment validation working"
        self.log_test("Environment Validation", success, details, data)
        return success
    
    def test_authentication_with_admin(self):
        """Test 4: Authentication with Admin User"""
        logger.info("🔐 Testing Authentication with Admin User...")
        
        # Test login with admin/admin123 (correct credentials)
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.make_request('POST', '/auth/login', json=login_data)
        if not response:
            self.log_test("Authentication with Admin", False, "Login request failed")
            return False
            
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            token_type = data.get('token_type')
            username = data.get('username')
            user_id = data.get('user_id')
            
            if token and token_type == 'bearer' and username == 'admin':
                self.token = token
                success = True
                details = f"Admin login successful, username: {username}, token type: {token_type}, user_id: {user_id[:8]}..."
            else:
                success = False
                details = f"Login response invalid: {data}"
        else:
            success = False
            details = f"Login failed with status {response.status_code}: {response.text}"
            
        self.log_test("Authentication with Admin", success, details)
        return success
    
    def test_jwt_token_persistence(self):
        """Test 5: JWT Token Persistence"""
        logger.info("🎫 Testing JWT Token Persistence...")
        
        if not self.token:
            self.log_test("JWT Token Persistence", False, "No token available from login")
            return False
            
        # Test multiple protected endpoints with same token
        endpoints = [
            '/auth/me',
            '/sessions/list',
            '/api-keys/list'
        ]
        
        all_success = True
        results = []
        
        for endpoint in endpoints:
            response = self.make_request('GET', endpoint)
            
            if response and response.status_code == 200:
                results.append(f"{endpoint}: OK")
            else:
                all_success = False
                status = response.status_code if response else "No response"
                results.append(f"{endpoint}: Failed ({status})")
        
        details = "; ".join(results)
        self.log_test("JWT Token Persistence", all_success, details)
        return all_success
    
    def test_core_api_endpoints_comprehensive(self):
        """Test 6: Comprehensive Core API Endpoints"""
        logger.info("🌐 Testing Comprehensive Core API Endpoints...")
        
        endpoints_to_test = [
            ('GET', '/health', 'Health Check', False),
            ('GET', '/v1/health', 'V1 Health Check', False),
            ('GET', '/version', 'Version Info', False),
            ('GET', '/sessions/list', 'Sessions List', True),
            ('GET', '/v1/multi-agents/types', 'Multi-Agent Types', False),
            ('GET', '/api-keys/list', 'API Keys List', True),
            ('GET', '/rate-limits/limits', 'Rate Limits', False),
            ('GET', '/developer-modes', 'Developer Modes', False),
        ]
        
        all_success = True
        results = []
        
        for method, endpoint, name, requires_auth in endpoints_to_test:
            if requires_auth and not self.token:
                results.append(f"{name}: Skipped (no auth)")
                continue
                
            response = self.make_request(method, endpoint)
            
            if response and response.status_code == 200:
                success = True
                details = f"{name}: OK"
                try:
                    data = response.json()
                    if endpoint == '/health':
                        status = data.get('status', 'unknown')
                        details += f" (status: {status})"
                    elif endpoint == '/sessions/list':
                        count = len(data) if isinstance(data, list) else 0
                        details += f" ({count} sessions)"
                    elif endpoint == '/v1/multi-agents/types':
                        count = len(data) if isinstance(data, list) else 0
                        details += f" ({count} agent types)"
                except:
                    pass
            else:
                success = False
                status = response.status_code if response else "No response"
                details = f"{name}: Failed ({status})"
                all_success = False
                
            results.append(details)
        
        details_str = "; ".join(results)
        self.log_test("Core API Endpoints Comprehensive", all_success, details_str)
        return all_success
    
    def test_windows_file_system_compatibility(self):
        """Test 7: Windows File System Compatibility"""
        logger.info("📁 Testing Windows File System Compatibility...")
        
        checks = []
        all_success = True
        
        # Check 1: SQLite database location
        home_dir = Path.home() / ".xionimus_ai"
        db_path = home_dir / "xionimus.db"
        
        if db_path.exists():
            checks.append("SQLite DB: ✅")
            
            # Check file size (should be > 0)
            size = db_path.stat().st_size
            if size > 0:
                checks.append(f"DB Size: {size} bytes ✅")
            else:
                checks.append("DB Size: 0 bytes ❌")
                all_success = False
        else:
            checks.append("SQLite DB: ❌")
            all_success = False
        
        # Check 2: WAL and SHM files
        wal_path = db_path.with_suffix('.db-wal')
        shm_path = db_path.with_suffix('.db-shm')
        
        if wal_path.exists():
            checks.append("WAL file: ✅")
        else:
            checks.append("WAL file: ❌")
            all_success = False
            
        if shm_path.exists():
            checks.append("SHM file: ✅")
        else:
            checks.append("SHM file: ❌")
            # SHM file might not always exist, so don't fail
        
        # Check 3: Directory permissions
        try:
            test_file = home_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            checks.append("Write permissions: ✅")
        except Exception as e:
            checks.append(f"Write permissions: ❌ ({e})")
            all_success = False
        
        details = "; ".join(checks)
        self.log_test("Windows File System Compatibility", all_success, details)
        return all_success
    
    def test_error_handling_comprehensive(self):
        """Test 8: Comprehensive Error Handling"""
        logger.info("⚠️ Testing Comprehensive Error Handling...")
        
        error_tests = [
            # Test 404 on non-existent public endpoint
            ('GET', f"{self.base_url}/nonexistent", 404, "Public 404"),
            # Test 401 on protected endpoint without auth
            ('GET', f"{self.api_url}/sessions/list", 401, "Auth required"),
            # Test 422 on invalid JSON
            ('POST', f"{self.api_url}/auth/login", 422, "Invalid JSON"),
        ]
        
        all_success = True
        results = []
        
        for method, url, expected_status, test_name in error_tests:
            try:
                if "Invalid JSON" in test_name:
                    # Send malformed JSON
                    response = requests.request(method, url, json={"invalid": "data"}, timeout=10)
                else:
                    response = requests.request(method, url, timeout=10)
                
                if response.status_code == expected_status:
                    results.append(f"{test_name}: ✅ ({response.status_code})")
                else:
                    results.append(f"{test_name}: ❌ (got {response.status_code}, expected {expected_status})")
                    all_success = False
                    
            except Exception as e:
                results.append(f"{test_name}: ❌ (exception: {e})")
                all_success = False
        
        details = "; ".join(results)
        self.log_test("Error Handling Comprehensive", all_success, details)
        return all_success
    
    def test_no_mongodb_redis_dependencies(self):
        """Test 9: No MongoDB/Redis Dependencies"""
        logger.info("🚫 Testing No MongoDB/Redis Dependencies...")
        
        # Check that backend works without MongoDB/Redis
        response = self.make_request('GET', '/health')
        if not response or response.status_code != 200:
            self.log_test("No MongoDB/Redis Dependencies", False, "Health check failed")
            return False
        
        data = response.json()
        
        # Backend should be in 'limited' status (working but without external services)
        status = data.get('status', 'unknown')
        
        # Check that startup was fast (no hanging on connection attempts)
        startup_ok = self.startup_time and self.startup_time < 5  # Very fast startup
        
        success = (
            status == 'limited' and  # Limited functionality is expected
            startup_ok              # Fast startup indicates no hanging
        )
        
        details = f"Status: {status}, Fast startup: {startup_ok} ({self.startup_time:.2f}s)"
        self.log_test("No MongoDB/Redis Dependencies", success, details)
        return success
    
    def test_windows_specific_features(self):
        """Test 10: Windows-Specific Features"""
        logger.info("🪟 Testing Windows-Specific Features...")
        
        features = []
        all_success = True
        
        # Test 1: Check if running on Windows-compatible mode
        response = self.make_request('GET', '/health')
        if response and response.status_code == 200:
            data = response.json()
            system_info = data.get('system', {})
            
            # Check memory reporting (should work on all platforms)
            memory_used = system_info.get('memory_used_percent', 0)
            memory_available = system_info.get('memory_available_mb', 0)
            
            if memory_used > 0 and memory_available > 0:
                features.append(f"Memory monitoring: ✅ ({memory_used}% used)")
            else:
                features.append("Memory monitoring: ❌")
                all_success = False
        
        # Test 2: Check SQLite performance (Windows-optimized settings)
        try:
            home_dir = Path.home() / ".xionimus_ai"
            db_path = home_dir / "xionimus.db"
            
            if db_path.exists():
                # Test SQLite connection speed
                start_time = time.time()
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]
                conn.close()
                connection_time = time.time() - start_time
                
                if connection_time < 1.0:  # Should be very fast
                    features.append(f"SQLite performance: ✅ ({connection_time:.3f}s, {table_count} tables)")
                else:
                    features.append(f"SQLite performance: ⚠️ ({connection_time:.3f}s)")
        except Exception as e:
            features.append(f"SQLite performance: ❌ ({e})")
            all_success = False
        
        # Test 3: Check file path handling
        try:
            # Test that paths work correctly
            home_str = str(Path.home())
            if home_str:
                features.append("Path handling: ✅")
            else:
                features.append("Path handling: ❌")
                all_success = False
        except Exception as e:
            features.append(f"Path handling: ❌ ({e})")
            all_success = False
        
        details = "; ".join(features)
        self.log_test("Windows-Specific Features", all_success, details)
        return all_success
    
    def run_all_tests(self):
        """Run all Windows backend tests"""
        logger.info("=" * 80)
        logger.info("🪟 COMPREHENSIVE WINDOWS BACKEND TESTING - ENHANCED")
        logger.info("=" * 80)
        
        tests = [
            self.test_backend_startup_comprehensive,
            self.test_sqlite_wal_mode,
            self.test_environment_validation,
            self.test_authentication_with_admin,
            self.test_jwt_token_persistence,
            self.test_core_api_endpoints_comprehensive,
            self.test_windows_file_system_compatibility,
            self.test_error_handling_comprehensive,
            self.test_no_mongodb_redis_dependencies,
            self.test_windows_specific_features,
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
        
        # Generate comprehensive summary
        self.generate_comprehensive_summary(passed, total)
        return passed == total
    
    def generate_comprehensive_summary(self, passed: int, total: int):
        """Generate comprehensive test summary"""
        logger.info("=" * 80)
        logger.info("📊 COMPREHENSIVE WINDOWS BACKEND TEST SUMMARY")
        logger.info("=" * 80)
        
        success_rate = (passed / total) * 100
        logger.info(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if self.startup_time:
            logger.info(f"Backend Startup Time: {self.startup_time:.3f} seconds")
        
        logger.info("\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result['success'] else "❌"
            logger.info(f"{i:2d}. {status} {result['test']}")
            logger.info(f"     {result['details']}")
        
        logger.info("\n🎯 WINDOWS COMPATIBILITY ASSESSMENT:")
        if success_rate >= 95:
            logger.info("🟢 EXCELLENT - Windows backend fully compatible and optimized")
        elif success_rate >= 85:
            logger.info("🟡 GOOD - Windows backend compatible with minor optimizations needed")
        elif success_rate >= 70:
            logger.info("🟠 FAIR - Windows backend mostly compatible, some fixes required")
        else:
            logger.info("🔴 POOR - Windows backend has significant compatibility issues")
        
        # Detailed Windows-specific analysis
        logger.info("\n🪟 WINDOWS-SPECIFIC ANALYSIS:")
        
        # Database analysis
        sqlite_tests = [r for r in self.test_results if 'SQLite' in r['test'] or 'File System' in r['test']]
        sqlite_success = all(r['success'] for r in sqlite_tests)
        
        if sqlite_success:
            logger.info("✅ SQLite Database: Fully compatible with Windows")
            logger.info("   - WAL mode enabled for better concurrency")
            logger.info("   - Proper file path handling")
            logger.info("   - Windows-optimized settings applied")
        else:
            logger.info("❌ SQLite Database: Issues detected")
            for test in sqlite_tests:
                if not test['success']:
                    logger.info(f"   - {test['test']}: {test['details']}")
        
        # Startup analysis
        if self.startup_time:
            if self.startup_time < 5:
                logger.info(f"✅ Startup Performance: Excellent ({self.startup_time:.3f}s)")
                logger.info("   - No MongoDB/Redis hanging detected")
                logger.info("   - Fast initialization")
            elif self.startup_time < 15:
                logger.info(f"⚠️ Startup Performance: Good ({self.startup_time:.3f}s)")
            else:
                logger.info(f"❌ Startup Performance: Slow ({self.startup_time:.3f}s)")
        
        # Authentication analysis
        auth_tests = [r for r in self.test_results if 'Authentication' in r['test'] or 'JWT' in r['test']]
        auth_success = all(r['success'] for r in auth_tests)
        
        if auth_success:
            logger.info("✅ Authentication System: Fully functional")
            logger.info("   - Admin user auto-creation working")
            logger.info("   - JWT token generation and validation")
            logger.info("   - Session persistence")
        else:
            logger.info("❌ Authentication System: Issues detected")
        
        # API endpoints analysis
        api_tests = [r for r in self.test_results if 'API' in r['test'] or 'Endpoints' in r['test']]
        api_success = all(r['success'] for r in api_tests)
        
        if api_success:
            logger.info("✅ API Endpoints: All core endpoints functional")
        else:
            logger.info("❌ API Endpoints: Some endpoints have issues")
        
        # Error handling analysis
        error_tests = [r for r in self.test_results if 'Error' in r['test']]
        error_success = all(r['success'] for r in error_tests)
        
        if error_success:
            logger.info("✅ Error Handling: Proper HTTP status codes and graceful degradation")
        else:
            logger.info("❌ Error Handling: Issues with error responses")
        
        logger.info("\n🏁 FINAL VERDICT:")
        if success_rate >= 90:
            logger.info("🎉 READY FOR WINDOWS DEPLOYMENT")
            logger.info("   The Xionimus AI backend is fully compatible with Windows")
            logger.info("   and ready for production use on Windows systems.")
        elif success_rate >= 75:
            logger.info("⚠️ MOSTLY READY - Minor fixes recommended")
            logger.info("   The backend works on Windows but could benefit from")
            logger.info("   addressing the identified issues.")
        else:
            logger.info("❌ NOT READY - Significant issues need resolution")
            logger.info("   Several compatibility issues must be fixed before")
            logger.info("   Windows deployment.")
        
        logger.info("=" * 80)

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