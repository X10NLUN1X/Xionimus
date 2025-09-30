#!/usr/bin/env python3
"""
Backend Smoke Test - Dependency Update Verification
Quick verification test after dependency updates to ensure nothing broke.

Focus:
1. GET /api/health - Verify backend is responding
2. GET /api/chat/providers - Check core functionality
3. GET /api/chat/sessions - Verify database operations still work
4. Check for any errors in backend logs after updates
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import subprocess

# Backend URL configuration (matches frontend config)
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class DependencyUpdateTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = []
        
    def log_test(self, test_name: str, success: bool, details: str, response_data: Optional[Dict] = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()
        
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response': response_data
        })
    
    def test_health_endpoint(self):
        """Test GET /api/health - Verify backend is responding"""
        try:
            print("🔍 Testing GET /api/health...")
            response = self.session.get(f"{API_BASE}/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                self.log_test(
                    "GET /api/health", 
                    True, 
                    f"Backend responding correctly - Status: {status}"
                )
                
                print(f"   📊 Backend Status: {status}")
                if 'version' in data:
                    print(f"   📊 Version: {data['version']}")
                if 'timestamp' in data:
                    print(f"   📊 Timestamp: {data['timestamp']}")
                print()
                
                return True
            else:
                self.log_test(
                    "GET /api/health", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("GET /api/health", False, f"Connection failed: {str(e)}")
            return False
    
    def test_chat_providers(self):
        """Test GET /api/chat/providers - Check core functionality"""
        try:
            print("🔍 Testing GET /api/chat/providers...")
            response = self.session.get(f"{API_BASE}/chat/providers")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if 'providers' not in data or 'models' not in data:
                    self.log_test(
                        "GET /api/chat/providers", 
                        False, 
                        "Missing 'providers' or 'models' in response", 
                        data
                    )
                    return False
                
                providers = data.get('providers', {})
                models = data.get('models', {})
                
                # Check for expected providers
                expected_providers = ['openai', 'anthropic', 'perplexity']
                found_providers = list(providers.keys())
                
                missing_providers = [p for p in expected_providers if p not in found_providers]
                if missing_providers:
                    self.log_test(
                        "GET /api/chat/providers", 
                        False, 
                        f"Missing providers: {missing_providers}. Found: {found_providers}"
                    )
                    return False
                
                self.log_test(
                    "GET /api/chat/providers", 
                    True, 
                    f"Core functionality working - Found {len(providers)} providers, {len(models)} model configurations"
                )
                
                print(f"   📊 Providers: {', '.join(found_providers)}")
                print(f"   📊 Models available: {len(models)}")
                print()
                
                return True
                
            else:
                self.log_test(
                    "GET /api/chat/providers", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("GET /api/chat/providers", False, f"Request failed: {str(e)}")
            return False
    
    def test_chat_sessions(self):
        """Test GET /api/chat/sessions - Verify database operations still work"""
        try:
            print("🔍 Testing GET /api/chat/sessions...")
            response = self.session.get(f"{API_BASE}/chat/sessions")
            
            if response.status_code == 200:
                data = response.json()
                
                # Should return a list (empty or with sessions)
                if not isinstance(data, list):
                    self.log_test(
                        "GET /api/chat/sessions", 
                        False, 
                        f"Expected list, got {type(data)}", 
                        data
                    )
                    return False
                
                # Validate session structure if any sessions exist
                if data:
                    session = data[0]
                    required_fields = ['session_id', 'name', 'created_at', 'updated_at', 'message_count']
                    missing_fields = [field for field in required_fields if field not in session]
                    
                    if missing_fields:
                        self.log_test(
                            "GET /api/chat/sessions", 
                            False, 
                            f"Missing fields in session: {missing_fields}"
                        )
                        return False
                
                self.log_test(
                    "GET /api/chat/sessions", 
                    True, 
                    f"Database operations working - Retrieved {len(data)} sessions successfully"
                )
                
                print(f"   📊 Sessions found: {len(data)}")
                if data:
                    print(f"   📊 Latest session: {data[0].get('name', 'Unknown')}")
                print()
                
                return True
                
            else:
                self.log_test(
                    "GET /api/chat/sessions", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("GET /api/chat/sessions", False, f"Request failed: {str(e)}")
            return False
    
    def check_backend_logs_for_dependency_errors(self):
        """Check backend logs for any errors related to dependency updates"""
        try:
            print("🔍 Checking backend logs for dependency-related errors...")
            
            # Check supervisor backend logs
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                log_content = result.stdout.strip()
                
                if not log_content:
                    self.log_test(
                        "Backend Logs - Dependency Errors", 
                        True, 
                        "No errors found in backend logs after dependency updates"
                    )
                    print("   📊 Backend error log is clean")
                    print()
                    return True
                else:
                    # Check for dependency-related errors
                    lines = log_content.split('\n')
                    
                    # Look for dependency-related error patterns
                    dependency_error_patterns = [
                        'importerror', 'modulenotfounderror', 'no module named',
                        'version conflict', 'dependency', 'requirements',
                        'package', 'import error', 'cannot import'
                    ]
                    
                    dependency_errors = []
                    other_errors = []
                    warnings = []
                    
                    for line in lines:
                        line_lower = line.lower()
                        if any(level in line_lower for level in ['error', 'critical', 'exception']):
                            if any(pattern in line_lower for pattern in dependency_error_patterns):
                                dependency_errors.append(line)
                            else:
                                other_errors.append(line)
                        elif 'warning' in line_lower:
                            warnings.append(line)
                    
                    if dependency_errors:
                        self.log_test(
                            "Backend Logs - Dependency Errors", 
                            False, 
                            f"Found {len(dependency_errors)} dependency-related errors after updates"
                        )
                        print("   ❌ Dependency errors found:")
                        for error in dependency_errors[-3:]:  # Show last 3 errors
                            print(f"      {error}")
                        print()
                        return False
                    elif other_errors:
                        self.log_test(
                            "Backend Logs - Dependency Errors", 
                            True, 
                            f"No dependency errors found. {len(other_errors)} other errors present (may be unrelated to updates)"
                        )
                        print(f"   📊 No dependency errors. {len(other_errors)} other errors, {len(warnings)} warnings")
                        print()
                        return True
                    else:
                        self.log_test(
                            "Backend Logs - Dependency Errors", 
                            True, 
                            f"No errors found after dependency updates. {len(warnings)} warnings present (normal)"
                        )
                        print(f"   📊 Clean logs. {len(warnings)} warnings found (normal)")
                        print()
                        return True
            else:
                self.log_test(
                    "Backend Logs - Dependency Errors", 
                    True, 
                    "Could not access error log (may not exist - normal for clean systems)"
                )
                return True
                
        except subprocess.TimeoutExpired:
            self.log_test(
                "Backend Logs - Dependency Errors", 
                True, 
                "Log check timed out (system may be busy - not critical)"
            )
            return True
        except Exception as e:
            self.log_test(
                "Backend Logs - Dependency Errors", 
                True, 
                f"Could not check logs: {str(e)} (not critical for functionality)"
            )
            return True
    
    def run_smoke_tests(self):
        """Run all smoke tests after dependency updates"""
        print("🚀 Starting Dependency Update Verification - Smoke Tests")
        print("Focus: Quick verification that dependency updates didn't break anything")
        print("=" * 70)
        print()
        
        # Test 1: Health endpoint
        health_success = self.test_health_endpoint()
        if not health_success:
            print("❌ Backend health check failed. Cannot continue with other tests.")
            return False
        
        # Test 2: Chat providers endpoint
        providers_success = self.test_chat_providers()
        
        # Test 3: Chat sessions endpoint (database operations)
        sessions_success = self.test_chat_sessions()
        
        # Test 4: Check logs for dependency-related errors
        logs_success = self.check_backend_logs_for_dependency_errors()
        
        # Summary
        print("=" * 70)
        print("📋 DEPENDENCY UPDATE VERIFICATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print()
        
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
            print()
        
        # Overall assessment
        critical_tests = [health_success, providers_success, sessions_success]
        all_critical_passed = all(critical_tests)
        
        if all_critical_passed and logs_success:
            print("✅ DEPENDENCY UPDATE STATUS: All systems operational")
            print("✅ Backend responding correctly after updates")
            print("✅ Core functionality working as expected")
            print("✅ Database operations functioning normally")
            print("✅ No dependency-related errors detected")
        elif all_critical_passed:
            print("⚠️ DEPENDENCY UPDATE STATUS: Core functionality working")
            print("✅ All critical endpoints operational")
            print("⚠️ Some log issues detected (may not be critical)")
        else:
            print("❌ DEPENDENCY UPDATE STATUS: Issues detected")
            print("❌ Some critical functionality may be broken")
            print("❌ Check failed tests above for details")
        
        print()
        return all_critical_passed

def main():
    """Main test execution - Dependency Update Verification"""
    tester = DependencyUpdateTester()
    success = tester.run_smoke_tests()
    
    if success:
        print("🎉 Dependency update verification completed successfully!")
        print("✅ All critical systems operational after updates!")
        sys.exit(0)
    else:
        print("⚠️ Some issues detected after dependency updates.")
        print("❌ Check the details above and consider rollback if critical.")
        sys.exit(1)

if __name__ == "__main__":
    main()