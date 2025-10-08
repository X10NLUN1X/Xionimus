#!/usr/bin/env python3
"""
Comprehensive Health Endpoints Testing for Xionimus AI Backend
Focus on testing the newly added health check endpoints and Windows compatibility fixes
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8001"
FRONTEND_ENV_PATH = "/app/frontend/.env"

def get_backend_url():
    """Get backend URL from frontend .env file"""
    try:
        with open(FRONTEND_ENV_PATH, 'r') as f:
            for line in f:
                if line.startswith('VITE_API_URL='):
                    url = line.split('=', 1)[1].strip()
                    # Remove /api suffix for base URL
                    return url.replace('/api', '')
    except:
        pass
    return BASE_URL

BACKEND_URL = get_backend_url()

class HealthEndpointsTest:
    def __init__(self):
        self.results = []
        self.backend_url = BACKEND_URL
        self.session = requests.Session()
        self.session.timeout = 10
        
    def log_result(self, test_name: str, success: bool, details: str, response_data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
    
    def test_health_live_endpoint(self):
        """Test GET /api/v1/health/live - Liveness probe (no auth required)"""
        try:
            response = self.session.get(f"{self.backend_url}/api/v1/health/live")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ["status", "timestamp", "uptime_seconds"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Health Live Endpoint",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Verify status is "alive"
                if data.get("status") != "alive":
                    self.log_result(
                        "Health Live Endpoint",
                        False,
                        f"Expected status 'alive', got '{data.get('status')}'",
                        data
                    )
                    return
                
                # Verify uptime is reasonable
                uptime = data.get("uptime_seconds", 0)
                if uptime < 0:
                    self.log_result(
                        "Health Live Endpoint",
                        False,
                        f"Invalid uptime: {uptime}",
                        data
                    )
                    return
                
                self.log_result(
                    "Health Live Endpoint",
                    True,
                    f"Liveness probe working correctly. Status: {data['status']}, Uptime: {uptime}s",
                    data
                )
            else:
                self.log_result(
                    "Health Live Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Health Live Endpoint",
                False,
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_health_ready_endpoint(self):
        """Test GET /api/v1/health/ready - Readiness probe"""
        try:
            response = self.session.get(f"{self.backend_url}/api/v1/health/ready")
            
            # Readiness can return 200 (ready) or 503 (not ready)
            if response.status_code in [200, 503]:
                data = response.json()
                
                # Verify required fields
                required_fields = ["status", "timestamp", "checks"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Health Ready Endpoint",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Verify checks structure
                checks = data.get("checks", {})
                expected_checks = ["database", "redis", "mongodb"]
                
                for check_name in expected_checks:
                    if check_name not in checks:
                        self.log_result(
                            "Health Ready Endpoint",
                            False,
                            f"Missing check: {check_name}",
                            data
                        )
                        return
                    
                    check_data = checks[check_name]
                    if "status" not in check_data or "healthy" not in check_data:
                        self.log_result(
                            "Health Ready Endpoint",
                            False,
                            f"Invalid check structure for {check_name}",
                            data
                        )
                        return
                
                # Count healthy services
                healthy_count = sum(1 for check in checks.values() if check.get("healthy", False))
                total_count = len(checks)
                
                status_msg = f"Readiness probe working. Status: {data['status']}, Healthy services: {healthy_count}/{total_count}"
                
                # Check specific service statuses
                db_status = checks.get("database", {}).get("status", "unknown")
                redis_status = checks.get("redis", {}).get("status", "unknown")
                mongo_status = checks.get("mongodb", {}).get("status", "unknown")
                
                status_msg += f" (DB: {db_status}, Redis: {redis_status}, MongoDB: {mongo_status})"
                
                self.log_result(
                    "Health Ready Endpoint",
                    True,
                    status_msg,
                    data
                )
            else:
                self.log_result(
                    "Health Ready Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Health Ready Endpoint",
                False,
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_health_startup_endpoint(self):
        """Test GET /api/v1/health/startup - Startup probe"""
        try:
            response = self.session.get(f"{self.backend_url}/api/v1/health/startup")
            
            # Startup can return 200 (ready) or 503 (not ready)
            if response.status_code in [200, 503]:
                data = response.json()
                
                # Verify required fields (same as readiness)
                required_fields = ["status", "timestamp", "checks"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Health Startup Endpoint",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                self.log_result(
                    "Health Startup Endpoint",
                    True,
                    f"Startup probe working. Status: {data['status']}",
                    data
                )
            else:
                self.log_result(
                    "Health Startup Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Health Startup Endpoint",
                False,
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_health_metrics_endpoint(self):
        """Test GET /api/v1/health/metrics - System metrics"""
        try:
            response = self.session.get(f"{self.backend_url}/api/v1/health/metrics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields
                required_fields = ["status", "timestamp", "uptime_seconds", "system", "platform", "python_version"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Health Metrics Endpoint",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                # Verify system metrics structure
                system = data.get("system", {})
                required_system_fields = ["cpu_percent", "memory", "disk"]
                missing_system_fields = [field for field in required_system_fields if field not in system]
                
                if missing_system_fields:
                    self.log_result(
                        "Health Metrics Endpoint",
                        False,
                        f"Missing system fields: {missing_system_fields}",
                        data
                    )
                    return
                
                # Verify memory structure
                memory = system.get("memory", {})
                required_memory_fields = ["total", "available", "percent", "used"]
                missing_memory_fields = [field for field in required_memory_fields if field not in memory]
                
                if missing_memory_fields:
                    self.log_result(
                        "Health Metrics Endpoint",
                        False,
                        f"Missing memory fields: {missing_memory_fields}",
                        data
                    )
                    return
                
                # Extract key metrics
                cpu_percent = system.get("cpu_percent", 0)
                memory_percent = memory.get("percent", 0)
                platform = data.get("platform", "unknown")
                uptime = data.get("uptime_seconds", 0)
                
                metrics_summary = f"CPU: {cpu_percent}%, Memory: {memory_percent}%, Platform: {platform}, Uptime: {uptime}s"
                
                self.log_result(
                    "Health Metrics Endpoint",
                    True,
                    f"System metrics working correctly. {metrics_summary}",
                    data
                )
            else:
                self.log_result(
                    "Health Metrics Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Health Metrics Endpoint",
                False,
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_backend_service_running(self):
        """Test that backend service is running on correct port"""
        try:
            response = self.session.get(f"{self.backend_url}/")
            
            if response.status_code == 200:
                data = response.json()
                
                if "Xionimus AI Backend" in data.get("message", ""):
                    self.log_result(
                        "Backend Service Running",
                        True,
                        f"Backend service running correctly on {self.backend_url}",
                        data
                    )
                else:
                    self.log_result(
                        "Backend Service Running",
                        False,
                        f"Unexpected response from root endpoint",
                        data
                    )
            else:
                self.log_result(
                    "Backend Service Running",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Backend Service Running",
                False,
                f"Cannot connect to backend: {str(e)}",
                {"error": str(e)}
            )
    
    def test_authentication_system(self):
        """Test that authentication system is working"""
        try:
            # Test login endpoint
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(f"{self.backend_url}/api/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if "access_token" in data:
                    token = data["access_token"]
                    
                    # Test protected endpoint with token
                    headers = {"Authorization": f"Bearer {token}"}
                    protected_response = self.session.get(f"{self.backend_url}/api/auth/me", headers=headers)
                    
                    if protected_response.status_code == 200:
                        user_data = protected_response.json()
                        self.log_result(
                            "Authentication System",
                            True,
                            f"Authentication working correctly. User: {user_data.get('username', 'unknown')}",
                            {"login_success": True, "user": user_data}
                        )
                    else:
                        self.log_result(
                            "Authentication System",
                            False,
                            f"Protected endpoint failed: HTTP {protected_response.status_code}",
                            {"login_success": True, "protected_endpoint_error": protected_response.text}
                        )
                else:
                    self.log_result(
                        "Authentication System",
                        False,
                        "Login successful but no access_token in response",
                        data
                    )
            else:
                self.log_result(
                    "Authentication System",
                    False,
                    f"Login failed: HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Authentication System",
                False,
                f"Authentication test failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_windows_compatibility(self):
        """Test Windows compatibility - check for sys import errors and path handling"""
        try:
            # Test an endpoint that would use system-specific functionality
            response = self.session.get(f"{self.backend_url}/api/v1/health/metrics")
            
            if response.status_code == 200:
                data = response.json()
                platform = data.get("platform", "unknown")
                
                # Check if platform detection is working
                if platform != "unknown":
                    self.log_result(
                        "Windows Compatibility - Platform Detection",
                        True,
                        f"Platform detection working: {platform}",
                        {"platform": platform}
                    )
                else:
                    self.log_result(
                        "Windows Compatibility - Platform Detection",
                        False,
                        "Platform detection not working",
                        data
                    )
                
                # Check if system metrics are available (tests psutil and other system modules)
                system = data.get("system", {})
                if system and "cpu_percent" in system and "memory" in system:
                    self.log_result(
                        "Windows Compatibility - System Modules",
                        True,
                        "System modules (psutil) working correctly",
                        {"system_metrics_available": True}
                    )
                else:
                    self.log_result(
                        "Windows Compatibility - System Modules",
                        False,
                        "System modules not working properly",
                        {"system": system}
                    )
            else:
                self.log_result(
                    "Windows Compatibility",
                    False,
                    f"Cannot test Windows compatibility: HTTP {response.status_code}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_result(
                "Windows Compatibility",
                False,
                f"Windows compatibility test failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_error_handling(self):
        """Test proper error handling and responses"""
        try:
            # Test invalid endpoint
            response = self.session.get(f"{self.backend_url}/api/nonexistent")
            
            if response.status_code == 404:
                try:
                    data = response.json()
                    if "detail" in data:
                        self.log_result(
                            "Error Handling - 404 Response",
                            True,
                            "404 errors properly formatted as JSON",
                            data
                        )
                    else:
                        self.log_result(
                            "Error Handling - 404 Response",
                            False,
                            "404 response missing 'detail' field",
                            data
                        )
                except:
                    self.log_result(
                        "Error Handling - 404 Response",
                        False,
                        "404 response is not valid JSON",
                        {"text": response.text}
                    )
            else:
                self.log_result(
                    "Error Handling - 404 Response",
                    False,
                    f"Expected 404, got {response.status_code}",
                    {"status_code": response.status_code}
                )
            
            # Test unauthorized access
            response = self.session.get(f"{self.backend_url}/api/auth/me")
            
            if response.status_code == 401:
                try:
                    data = response.json()
                    if "detail" in data:
                        self.log_result(
                            "Error Handling - 401 Response",
                            True,
                            "401 errors properly formatted as JSON",
                            data
                        )
                    else:
                        self.log_result(
                            "Error Handling - 401 Response",
                            False,
                            "401 response missing 'detail' field",
                            data
                        )
                except:
                    self.log_result(
                        "Error Handling - 401 Response",
                        False,
                        "401 response is not valid JSON",
                        {"text": response.text}
                    )
            else:
                self.log_result(
                    "Error Handling - 401 Response",
                    False,
                    f"Expected 401, got {response.status_code}",
                    {"status_code": response.status_code}
                )
                
        except Exception as e:
            self.log_result(
                "Error Handling",
                False,
                f"Error handling test failed: {str(e)}",
                {"error": str(e)}
            )
    
    def test_legacy_health_endpoint(self):
        """Test legacy /api/health endpoint for backward compatibility"""
        try:
            response = self.session.get(f"{self.backend_url}/api/health")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify required fields for legacy endpoint
                required_fields = ["status", "version", "platform", "timestamp"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result(
                        "Legacy Health Endpoint",
                        False,
                        f"Missing required fields: {missing_fields}",
                        data
                    )
                    return
                
                self.log_result(
                    "Legacy Health Endpoint",
                    True,
                    f"Legacy health endpoint working. Status: {data.get('status')}, Version: {data.get('version')}",
                    data
                )
            else:
                self.log_result(
                    "Legacy Health Endpoint",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                    {"status_code": response.status_code, "text": response.text}
                )
                
        except Exception as e:
            self.log_result(
                "Legacy Health Endpoint",
                False,
                f"Request failed: {str(e)}",
                {"error": str(e)}
            )
    
    def run_all_tests(self):
        """Run all health endpoint tests"""
        print("🔍 XIONIMUS AI BACKEND - HEALTH ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Core health endpoints (CRITICAL)
        print("\n🏥 HEALTH CHECK ENDPOINTS (CRITICAL)")
        print("-" * 40)
        self.test_health_live_endpoint()
        self.test_health_ready_endpoint()
        self.test_health_startup_endpoint()
        self.test_health_metrics_endpoint()
        self.test_legacy_health_endpoint()
        
        # Backend services
        print("\n🚀 BACKEND SERVICES")
        print("-" * 40)
        self.test_backend_service_running()
        self.test_authentication_system()
        
        # Windows compatibility
        print("\n🪟 WINDOWS COMPATIBILITY")
        print("-" * 40)
        self.test_windows_compatibility()
        
        # Error handling
        print("\n⚠️ ERROR HANDLING")
        print("-" * 40)
        self.test_error_handling()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS ({passed_tests}):")
            for result in self.results:
                if result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        # Determine overall status
        if success_rate >= 90:
            print("🎉 OVERALL STATUS: EXCELLENT - All critical systems working")
        elif success_rate >= 75:
            print("✅ OVERALL STATUS: GOOD - Most systems working correctly")
        elif success_rate >= 50:
            print("⚠️ OVERALL STATUS: NEEDS ATTENTION - Some critical issues found")
        else:
            print("❌ OVERALL STATUS: CRITICAL ISSUES - Major problems detected")
        
        return self.results

def main():
    """Main test execution"""
    tester = HealthEndpointsTest()
    results = tester.run_all_tests()
    
    # Save results to file
    with open("/app/health_endpoints_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: /app/health_endpoints_test_results.json")
    
    # Return exit code based on results
    failed_count = sum(1 for result in results if not result["success"])
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())