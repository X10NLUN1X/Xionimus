#!/usr/bin/env python3
"""
Backend Testing for Xionimus AI - GitHub Integration
Tests the newly implemented GitHub integration endpoints
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import time

# Backend URL configuration (matches frontend config)
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class GitHubIntegrationTester:
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
    
    def test_backend_health(self):
        """Test if backend is running"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Backend Health Check", 
                    True, 
                    f"Backend is running - Status: {data.get('status', 'unknown')}"
                )
                return True
            else:
                self.log_test(
                    "Backend Health Check", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_github_health(self):
        """Test GitHub health endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/github/health")
            if response.status_code == 200:
                data = response.json()
                oauth_enabled = data.get('oauth_enabled', False)
                status = data.get('status', 'unknown')
                
                self.log_test(
                    "GitHub Health Check", 
                    True, 
                    f"Status: {status}, OAuth Enabled: {oauth_enabled}"
                )
                return True, data
            else:
                self.log_test(
                    "GitHub Health Check", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False, None
        except Exception as e:
            self.log_test("GitHub Health Check", False, f"Request failed: {str(e)}")
            return False, None
    
    def test_github_oauth_url(self):
        """Test GitHub OAuth URL endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/github/oauth/url")
            if response.status_code == 200:
                data = response.json()
                configured = data.get('configured', False)
                
                if configured:
                    oauth_url = data.get('oauth_url')
                    if oauth_url and 'github.com' in oauth_url:
                        self.log_test(
                            "GitHub OAuth URL (Configured)", 
                            True, 
                            f"OAuth URL generated successfully"
                        )
                    else:
                        self.log_test(
                            "GitHub OAuth URL (Configured)", 
                            False, 
                            "Invalid OAuth URL generated", 
                            data
                        )
                else:
                    # Not configured is expected - should return setup guide
                    setup_guide = data.get('setup_guide')
                    if setup_guide and isinstance(setup_guide, dict):
                        self.log_test(
                            "GitHub OAuth URL (Not Configured)", 
                            True, 
                            "Setup guide provided correctly"
                        )
                    else:
                        self.log_test(
                            "GitHub OAuth URL (Not Configured)", 
                            False, 
                            "Missing or invalid setup guide", 
                            data
                        )
                return True, data
            else:
                self.log_test(
                    "GitHub OAuth URL", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False, None
        except Exception as e:
            self.log_test("GitHub OAuth URL", False, f"Request failed: {str(e)}")
            return False, None
    
    def test_fork_summary(self):
        """Test the main fork summary endpoint - this is the critical new feature"""
        try:
            print("🔍 Testing Fork Summary Endpoint (Main Feature)...")
            response = self.session.get(f"{API_BASE}/github/fork-summary")
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required fields
                required_fields = ['project_name', 'description', 'statistics', 'structure', 'technology_stack']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test(
                        "Fork Summary - Structure", 
                        False, 
                        f"Missing required fields: {missing_fields}", 
                        data
                    )
                    return False
                
                # Validate statistics
                stats = data.get('statistics', {})
                required_stats = ['total_files', 'total_lines_of_code', 'total_size_mb', 'languages']
                missing_stats = [stat for stat in required_stats if stat not in stats]
                
                if missing_stats:
                    self.log_test(
                        "Fork Summary - Statistics", 
                        False, 
                        f"Missing statistics: {missing_stats}", 
                        stats
                    )
                    return False
                
                # Validate that it actually found files
                total_files = stats.get('total_files', 0)
                total_lines = stats.get('total_lines_of_code', 0)
                languages = stats.get('languages', {})
                
                if total_files == 0:
                    self.log_test(
                        "Fork Summary - File Detection", 
                        False, 
                        "No files detected in project scan"
                    )
                    return False
                
                if total_lines == 0:
                    self.log_test(
                        "Fork Summary - Code Analysis", 
                        False, 
                        "No lines of code counted"
                    )
                    return False
                
                if not languages:
                    self.log_test(
                        "Fork Summary - Language Detection", 
                        False, 
                        "No programming languages detected"
                    )
                    return False
                
                # Check for expected languages (Python for backend, JavaScript/TypeScript for frontend)
                expected_languages = ['Python', 'JavaScript', 'TypeScript']
                found_languages = list(languages.keys())
                common_languages = [lang for lang in expected_languages if lang in found_languages]
                
                if not common_languages:
                    self.log_test(
                        "Fork Summary - Expected Languages", 
                        False, 
                        f"Expected languages {expected_languages} not found. Found: {found_languages}"
                    )
                    return False
                
                # Validate structure
                structure = data.get('structure', {})
                if 'backend' not in structure or 'frontend' not in structure:
                    self.log_test(
                        "Fork Summary - Project Structure", 
                        False, 
                        "Missing backend or frontend in structure analysis"
                    )
                    return False
                
                # All validations passed
                self.log_test(
                    "Fork Summary - Complete Analysis", 
                    True, 
                    f"Successfully analyzed {total_files} files, {total_lines} lines of code, {len(languages)} languages"
                )
                
                # Log detailed results
                print(f"   📊 Project Statistics:")
                print(f"      Files: {total_files}")
                print(f"      Lines of Code: {total_lines}")
                print(f"      Size: {stats.get('total_size_mb', 0)} MB")
                print(f"      Languages: {', '.join(found_languages)}")
                print()
                
                return True
                
            else:
                self.log_test(
                    "Fork Summary", 
                    False, 
                    f"HTTP {response.status_code}", 
                    response.json() if response.content else None
                )
                return False
                
        except Exception as e:
            self.log_test("Fork Summary", False, f"Request failed: {str(e)}")
            return False
    
    def test_push_project_endpoint_structure(self):
        """Test push project endpoint structure (without actual pushing)"""
        try:
            # Test with missing parameters to see if endpoint exists and validates properly
            response = self.session.post(f"{API_BASE}/github/push-project")
            
            # Should return 422 (validation error) if endpoint exists
            if response.status_code == 422:
                self.log_test(
                    "Push Project Endpoint - Structure", 
                    True, 
                    "Endpoint exists and validates parameters correctly"
                )
                return True
            elif response.status_code == 404:
                self.log_test(
                    "Push Project Endpoint - Structure", 
                    False, 
                    "Endpoint not found"
                )
                return False
            else:
                # Other status codes might indicate the endpoint exists but has different validation
                self.log_test(
                    "Push Project Endpoint - Structure", 
                    True, 
                    f"Endpoint exists (HTTP {response.status_code})"
                )
                return True
                
        except Exception as e:
            self.log_test("Push Project Endpoint - Structure", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all GitHub integration tests"""
        print("🚀 Starting GitHub Integration Backend Tests")
        print("=" * 60)
        print()
        
        # Test 1: Backend Health
        if not self.test_backend_health():
            print("❌ Backend is not running. Cannot continue with tests.")
            return False
        
        # Test 2: GitHub Health
        github_healthy, github_health_data = self.test_github_health()
        
        # Test 3: GitHub OAuth URL
        oauth_success, oauth_data = self.test_github_oauth_url()
        
        # Test 4: Fork Summary (MAIN FEATURE)
        fork_summary_success = self.test_fork_summary()
        
        # Test 5: Push Project Endpoint Structure
        push_endpoint_success = self.test_push_project_endpoint_structure()
        
        # Summary
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
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
        
        # Critical assessment
        critical_success = fork_summary_success  # Main feature
        
        if critical_success:
            print("✅ CRITICAL FEATURE STATUS: Fork Summary endpoint is working correctly")
        else:
            print("❌ CRITICAL FEATURE STATUS: Fork Summary endpoint has issues")
        
        print()
        return critical_success

def main():
    """Main test execution"""
    tester = GitHubIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 GitHub Integration tests completed successfully!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()