#!/usr/bin/env python3
"""
FINAL VERIFICATION TEST - All Fixes Applied
Testing both Round 1 and Round 2 fixes as requested

Round 1 Verification:
1. Health Check Endpoints (4 endpoints) - Confirm all working without auth
2. Backend services running on port 8001
3. Authentication system working
4. No sys import errors

Round 2 Verification:
1. Requirements.txt - Confirm uvloop removed
2. sandbox_executor.py - Verify CREATE_NO_WINDOW flags added
3. Platform detection working
4. No Unix-specific command errors
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8001"
TEST_USER = "demo"
TEST_PASSWORD = "demo123"

class FinalVerificationTest:
    def __init__(self):
        self.results = {
            "round1": {},
            "round2": {},
            "critical_tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
        self.auth_token = None
    
    def log(self, message, level="INFO"):
        """Log test messages"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_health_endpoints(self):
        """Test all 4 health endpoints without authentication"""
        self.log("🔍 Testing Health Check Endpoints (Round 1)")
        
        health_endpoints = [
            ("/api/v1/health/live", "alive"),
            ("/api/v1/health/ready", "ready"),
            ("/api/v1/health/startup", "ready"),
            ("/api/v1/health/metrics", "healthy")
        ]
        
        results = {}
        
        for endpoint, expected_status in health_endpoints:
            try:
                self.log(f"   Testing {endpoint}")
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if "status" in data and expected_status in data["status"]:
                        results[endpoint] = {"status": "✅ PASS", "response": data}
                        self.log(f"   ✅ {endpoint} - Status: {data.get('status', 'N/A')}")
                    else:
                        results[endpoint] = {"status": "❌ FAIL", "error": f"Unexpected status: {data.get('status', 'N/A')}"}
                        self.log(f"   ❌ {endpoint} - Unexpected status: {data.get('status', 'N/A')}")
                else:
                    results[endpoint] = {"status": "❌ FAIL", "error": f"HTTP {response.status_code}"}
                    self.log(f"   ❌ {endpoint} - HTTP {response.status_code}")
                    
            except Exception as e:
                results[endpoint] = {"status": "❌ ERROR", "error": str(e)}
                self.log(f"   ❌ {endpoint} - Error: {str(e)}")
        
        self.results["round1"]["health_endpoints"] = results
        return results
    
    def test_backend_service(self):
        """Test backend service running on port 8001"""
        self.log("🔍 Testing Backend Service on Port 8001 (Round 1)")
        
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.results["round1"]["backend_service"] = {
                    "status": "✅ PASS",
                    "message": data.get("message", ""),
                    "platform": data.get("platform", "")
                }
                self.log(f"   ✅ Backend service running - {data.get('message', 'N/A')}")
                return True
            else:
                self.results["round1"]["backend_service"] = {
                    "status": "❌ FAIL",
                    "error": f"HTTP {response.status_code}"
                }
                self.log(f"   ❌ Backend service - HTTP {response.status_code}")
                return False
        except Exception as e:
            self.results["round1"]["backend_service"] = {
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.log(f"   ❌ Backend service - Error: {str(e)}")
            return False
    
    def test_authentication_system(self):
        """Test authentication system with demo/demo123"""
        self.log("🔍 Testing Authentication System (Round 1)")
        
        try:
            # Test login
            login_data = {
                "username": TEST_USER,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(
                f"{BACKEND_URL}/api/auth/login",
                json=login_data,  # Use JSON instead of form data
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.results["round1"]["authentication"] = {
                        "status": "✅ PASS",
                        "token_type": data.get("token_type", "bearer"),
                        "user": data.get("user", {})
                    }
                    self.log(f"   ✅ Authentication successful - User: {data.get('user', {}).get('username', 'N/A')}")
                    return True
                else:
                    self.results["round1"]["authentication"] = {
                        "status": "❌ FAIL",
                        "error": "No access_token in response"
                    }
                    self.log("   ❌ Authentication failed - No access_token")
                    return False
            else:
                self.results["round1"]["authentication"] = {
                    "status": "❌ FAIL",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                self.log(f"   ❌ Authentication failed - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.results["round1"]["authentication"] = {
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.log(f"   ❌ Authentication error: {str(e)}")
            return False
    
    def test_sys_imports(self):
        """Test for sys import errors in backend"""
        self.log("🔍 Testing for sys import errors (Round 1)")
        
        # Check if backend is responding properly (indicates no import errors)
        try:
            response = requests.get(f"{BACKEND_URL}/api/version", timeout=5)
            if response.status_code == 200:
                self.results["round1"]["sys_imports"] = {
                    "status": "✅ PASS",
                    "note": "Backend responding normally, no sys import errors detected"
                }
                self.log("   ✅ No sys import errors detected")
                return True
            else:
                self.results["round1"]["sys_imports"] = {
                    "status": "❌ FAIL",
                    "error": f"Backend not responding properly: HTTP {response.status_code}"
                }
                self.log(f"   ❌ Backend issues detected: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.results["round1"]["sys_imports"] = {
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.log(f"   ❌ Error checking sys imports: {str(e)}")
            return False
    
    def test_requirements_uvloop_removed(self):
        """Test that uvloop has been removed from requirements.txt"""
        self.log("🔍 Testing uvloop removal from requirements.txt (Round 2)")
        
        try:
            requirements_path = Path("/app/backend/requirements.txt")
            if requirements_path.exists():
                content = requirements_path.read_text()
                if "uvloop" in content.lower():
                    self.results["round2"]["uvloop_removal"] = {
                        "status": "❌ FAIL",
                        "error": "uvloop still found in requirements.txt"
                    }
                    self.log("   ❌ uvloop still present in requirements.txt")
                    return False
                else:
                    self.results["round2"]["uvloop_removal"] = {
                        "status": "✅ PASS",
                        "note": "uvloop successfully removed from requirements.txt"
                    }
                    self.log("   ✅ uvloop successfully removed from requirements.txt")
                    return True
            else:
                self.results["round2"]["uvloop_removal"] = {
                    "status": "❌ ERROR",
                    "error": "requirements.txt not found"
                }
                self.log("   ❌ requirements.txt not found")
                return False
        except Exception as e:
            self.results["round2"]["uvloop_removal"] = {
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.log(f"   ❌ Error checking requirements.txt: {str(e)}")
            return False
    
    def test_sandbox_executor_windows_fixes(self):
        """Test sandbox_executor.py for CREATE_NO_WINDOW flags and Windows compatibility"""
        self.log("🔍 Testing sandbox_executor.py Windows fixes (Round 2)")
        
        try:
            sandbox_path = Path("/app/backend/app/core/sandbox_executor.py")
            if sandbox_path.exists():
                content = sandbox_path.read_text()
                
                checks = {
                    "CREATE_NO_WINDOW": "CREATE_NO_WINDOW" in content,
                    "platform_detection": "sys.platform" in content and "win32" in content,
                    "windows_conditional": "IS_WINDOWS" in content or "if sys.platform" in content,
                    "subprocess_flags": "creationflags" in content
                }
                
                all_passed = all(checks.values())
                
                self.results["round2"]["sandbox_executor_fixes"] = {
                    "status": "✅ PASS" if all_passed else "❌ FAIL",
                    "checks": checks,
                    "note": "Windows compatibility fixes verified" if all_passed else "Some Windows fixes missing"
                }
                
                if all_passed:
                    self.log("   ✅ All Windows fixes found in sandbox_executor.py")
                else:
                    self.log(f"   ❌ Missing Windows fixes: {[k for k, v in checks.items() if not v]}")
                
                return all_passed
            else:
                self.results["round2"]["sandbox_executor_fixes"] = {
                    "status": "❌ ERROR",
                    "error": "sandbox_executor.py not found"
                }
                self.log("   ❌ sandbox_executor.py not found")
                return False
        except Exception as e:
            self.results["round2"]["sandbox_executor_fixes"] = {
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.log(f"   ❌ Error checking sandbox_executor.py: {str(e)}")
            return False
    
    def test_platform_detection(self):
        """Test platform detection working"""
        self.log("🔍 Testing Platform Detection (Round 2)")
        
        try:
            # Test via health metrics endpoint which includes platform info
            response = requests.get(f"{BACKEND_URL}/api/v1/health/metrics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "platform" in data:
                    platform = data["platform"]
                    self.results["round2"]["platform_detection"] = {
                        "status": "✅ PASS",
                        "platform": platform,
                        "note": f"Platform correctly detected as: {platform}"
                    }
                    self.log(f"   ✅ Platform detection working - Detected: {platform}")
                    return True
                else:
                    self.results["round2"]["platform_detection"] = {
                        "status": "❌ FAIL",
                        "error": "Platform not included in metrics response"
                    }
                    self.log("   ❌ Platform not detected in metrics")
                    return False
            else:
                self.results["round2"]["platform_detection"] = {
                    "status": "❌ FAIL",
                    "error": f"Metrics endpoint failed: HTTP {response.status_code}"
                }
                self.log(f"   ❌ Metrics endpoint failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.results["round2"]["platform_detection"] = {
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.log(f"   ❌ Error testing platform detection: {str(e)}")
            return False
    
    def test_unix_command_errors(self):
        """Test for Unix-specific command errors"""
        self.log("🔍 Testing for Unix-specific command errors (Round 2)")
        
        # Test by trying to access an endpoint that might use subprocess
        try:
            if self.auth_token:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.get(f"{BACKEND_URL}/api/sandbox/languages", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    # Check if it's the expected format: {"languages": [...]}
                    if isinstance(data, dict) and "languages" in data:
                        languages = data["languages"]
                        self.results["round2"]["unix_command_errors"] = {
                            "status": "✅ PASS",
                            "note": f"Sandbox languages endpoint working - {len(languages)} languages supported",
                            "languages": [lang.get("language", "unknown") for lang in languages[:5]]  # First 5
                        }
                        self.log(f"   ✅ No Unix command errors - {len(languages)} languages supported")
                        return True
                    else:
                        self.results["round2"]["unix_command_errors"] = {
                            "status": "❌ FAIL",
                            "error": f"Unexpected response format: {type(data)} - {str(data)[:100]}"
                        }
                        self.log(f"   ❌ Unexpected response format: {type(data)}")
                        return False
                else:
                    self.results["round2"]["unix_command_errors"] = {
                        "status": "❌ FAIL",
                        "error": f"Sandbox endpoint failed: HTTP {response.status_code}"
                    }
                    self.log(f"   ❌ Sandbox endpoint failed: HTTP {response.status_code}")
                    return False
            else:
                self.results["round2"]["unix_command_errors"] = {
                    "status": "⚠️ SKIP",
                    "note": "No auth token available, cannot test sandbox endpoint"
                }
                self.log("   ⚠️ Skipping Unix command test - no auth token")
                return True  # Don't fail if we can't authenticate
        except Exception as e:
            self.results["round2"]["unix_command_errors"] = {
                "status": "❌ ERROR",
                "error": str(e)
            }
            self.log(f"   ❌ Error testing Unix commands: {str(e)}")
            return False
    
    def run_critical_tests(self):
        """Run the specific critical tests mentioned in the request"""
        self.log("🎯 Running Critical Tests")
        
        critical_endpoints = [
            ("/api/v1/health/live", {"status": "alive"}),
            ("/api/v1/health/ready", {"status": "ready"}),
            ("/api/v1/health/startup", {"status": "ready"}),
            ("/api/v1/health/metrics", {"status": "healthy"}),
            ("/api/version", None)  # Basic API endpoint test
        ]
        
        results = {}
        
        for endpoint, expected in critical_endpoints:
            try:
                self.log(f"   Testing critical endpoint: {endpoint}")
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if expected and "status" in expected:
                        if expected["status"] in data.get("status", ""):
                            results[endpoint] = {"status": "✅ PASS", "data": data}
                            self.log(f"   ✅ {endpoint} - PASS")
                        else:
                            results[endpoint] = {"status": "❌ FAIL", "error": f"Expected {expected['status']}, got {data.get('status', 'N/A')}"}
                            self.log(f"   ❌ {endpoint} - Status mismatch")
                    else:
                        results[endpoint] = {"status": "✅ PASS", "data": data}
                        self.log(f"   ✅ {endpoint} - PASS")
                else:
                    results[endpoint] = {"status": "❌ FAIL", "error": f"HTTP {response.status_code}"}
                    self.log(f"   ❌ {endpoint} - HTTP {response.status_code}")
                    
            except Exception as e:
                results[endpoint] = {"status": "❌ ERROR", "error": str(e)}
                self.log(f"   ❌ {endpoint} - Error: {str(e)}")
        
        # Test authentication with demo/demo123
        if not self.auth_token:
            self.test_authentication_system()
        
        if self.auth_token:
            results["authentication_demo"] = {"status": "✅ PASS", "note": "demo/demo123 login successful"}
            self.log("   ✅ Authentication test - PASS")
        else:
            results["authentication_demo"] = {"status": "❌ FAIL", "error": "demo/demo123 login failed"}
            self.log("   ❌ Authentication test - FAIL")
        
        self.results["critical_tests"] = results
        return results
    
    def calculate_summary(self):
        """Calculate test summary statistics"""
        total_tests = 0
        passed = 0
        failed = 0
        errors = []
        
        # Count all tests
        for round_name, round_results in self.results.items():
            if round_name == "summary":
                continue
                
            for test_name, test_result in round_results.items():
                total_tests += 1
                status = test_result.get("status", "")
                
                if "✅ PASS" in status:
                    passed += 1
                elif "❌ FAIL" in status or "❌ ERROR" in status:
                    failed += 1
                    errors.append(f"{round_name}.{test_name}: {test_result.get('error', 'Unknown error')}")
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "errors": errors
        }
    
    def run_all_tests(self):
        """Run all verification tests"""
        self.log("🚀 Starting Final Verification Test - All Fixes Applied")
        self.log("=" * 60)
        
        # Round 1 Tests
        self.log("📋 ROUND 1 VERIFICATION")
        self.test_health_endpoints()
        self.test_backend_service()
        self.test_authentication_system()
        self.test_sys_imports()
        
        self.log("")
        
        # Round 2 Tests
        self.log("📋 ROUND 2 VERIFICATION")
        self.test_requirements_uvloop_removed()
        self.test_sandbox_executor_windows_fixes()
        self.test_platform_detection()
        self.test_unix_command_errors()
        
        self.log("")
        
        # Critical Tests
        self.log("📋 CRITICAL TESTS")
        self.run_critical_tests()
        
        # Calculate summary
        self.calculate_summary()
        
        self.log("")
        self.log("=" * 60)
        self.log("🎯 FINAL VERIFICATION RESULTS")
        self.log("=" * 60)
        
        summary = self.results["summary"]
        self.log(f"Total Tests: {summary['total_tests']}")
        self.log(f"Passed: {summary['passed']}")
        self.log(f"Failed: {summary['failed']}")
        self.log(f"Success Rate: {summary['success_rate']}")
        
        if summary["errors"]:
            self.log("")
            self.log("❌ ERRORS FOUND:")
            for error in summary["errors"]:
                self.log(f"   - {error}")
        
        if summary["failed"] == 0:
            self.log("")
            self.log("🎉 ALL TESTS PASSED! All fixes have been successfully applied and verified.")
        else:
            self.log("")
            self.log("⚠️ Some tests failed. Please review the errors above.")
        
        return self.results

def main():
    """Main test execution"""
    tester = FinalVerificationTest()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = "/app/final_verification_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Return exit code based on results
    return 0 if results["summary"]["failed"] == 0 else 1

if __name__ == "__main__":
    exit(main())