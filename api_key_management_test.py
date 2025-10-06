#!/usr/bin/env python3
"""
API Key Management Endpoints Testing
Tests the Xionimus AI backend API Key Management system
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Test credentials
TEST_USERNAME = "demo"
TEST_PASSWORD = "demo123"

class APIKeyManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_authentication(self):
        """Test 1: Authentication Flow"""
        print("\n🔐 Testing Authentication Flow...")
        
        try:
            # Test login
            login_data = {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.jwt_token = data["access_token"]
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.jwt_token}"
                    })
                    self.log_test("Authentication", True, f"JWT token obtained, user_id: {data.get('user_id', 'N/A')}")
                    return True
                else:
                    self.log_test("Authentication", False, "No access_token in response")
                    return False
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_api_keys_list_empty(self):
        """Test 2: List API Keys (initially empty)"""
        print("\n📋 Testing API Keys List (Empty State)...")
        
        try:
            response = self.session.get(f"{API_BASE}/api-keys/list")
            
            if response.status_code == 200:
                data = response.json()
                if "api_keys" in data and isinstance(data["api_keys"], list):
                    self.log_test("List API Keys (Empty)", True, f"Found {len(data['api_keys'])} API keys")
                    return True
                else:
                    self.log_test("List API Keys (Empty)", False, "Invalid response format")
                    return False
            else:
                self.log_test("List API Keys (Empty)", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("List API Keys (Empty)", False, f"Exception: {str(e)}")
            return False
    
    def test_save_anthropic_key(self):
        """Test 3: Save Anthropic API Key"""
        print("\n💾 Testing Save Anthropic API Key...")
        
        try:
            test_key = "sk-ant-test123456789"
            save_data = {
                "provider": "anthropic",
                "api_key": test_key
            }
            
            response = self.session.post(
                f"{API_BASE}/api-keys/save",
                json=save_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("provider") == "anthropic" and 
                    "masked_key" in data and 
                    data.get("is_active") == True):
                    masked_key = data["masked_key"]
                    self.log_test("Save Anthropic Key", True, f"Key saved, masked: {masked_key}")
                    return True
                else:
                    self.log_test("Save Anthropic Key", False, f"Invalid response data: {data}")
                    return False
            else:
                self.log_test("Save Anthropic Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Save Anthropic Key", False, f"Exception: {str(e)}")
            return False
    
    def test_save_openai_key(self):
        """Test 4: Save OpenAI API Key"""
        print("\n💾 Testing Save OpenAI API Key...")
        
        try:
            test_key = "sk-proj-test123456789"
            save_data = {
                "provider": "openai",
                "api_key": test_key
            }
            
            response = self.session.post(
                f"{API_BASE}/api-keys/save",
                json=save_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("provider") == "openai" and 
                    "masked_key" in data and 
                    data.get("is_active") == True):
                    masked_key = data["masked_key"]
                    self.log_test("Save OpenAI Key", True, f"Key saved, masked: {masked_key}")
                    return True
                else:
                    self.log_test("Save OpenAI Key", False, f"Invalid response data: {data}")
                    return False
            else:
                self.log_test("Save OpenAI Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Save OpenAI Key", False, f"Exception: {str(e)}")
            return False
    
    def test_api_keys_list_populated(self):
        """Test 5: List API Keys (with saved keys)"""
        print("\n📋 Testing API Keys List (Populated)...")
        
        try:
            response = self.session.get(f"{API_BASE}/api-keys/list")
            
            if response.status_code == 200:
                data = response.json()
                if "api_keys" in data and isinstance(data["api_keys"], list):
                    keys = data["api_keys"]
                    if len(keys) >= 2:  # Should have anthropic and openai
                        providers = [key["provider"] for key in keys]
                        masked_keys = [key["masked_key"] for key in keys]
                        self.log_test("List API Keys (Populated)", True, 
                                    f"Found {len(keys)} keys: {providers}, masked keys: {masked_keys}")
                        return True
                    else:
                        self.log_test("List API Keys (Populated)", False, f"Expected 2+ keys, got {len(keys)}")
                        return False
                else:
                    self.log_test("List API Keys (Populated)", False, "Invalid response format")
                    return False
            else:
                self.log_test("List API Keys (Populated)", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("List API Keys (Populated)", False, f"Exception: {str(e)}")
            return False
    
    def test_api_keys_status(self):
        """Test 6: Get API Keys Status"""
        print("\n📊 Testing API Keys Status...")
        
        try:
            response = self.session.get(f"{API_BASE}/api-keys/status")
            
            if response.status_code == 200:
                data = response.json()
                if ("configured_providers" in data and 
                    "total_configured" in data):
                    providers = data["configured_providers"]
                    total = data["total_configured"]
                    self.log_test("API Keys Status", True, 
                                f"Status: {providers}, total configured: {total}")
                    return True
                else:
                    self.log_test("API Keys Status", False, "Invalid response format")
                    return False
            else:
                self.log_test("API Keys Status", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("API Keys Status", False, f"Exception: {str(e)}")
            return False
    
    def test_connection_test_anthropic(self):
        """Test 7: Test Connection - Anthropic (Expected to fail without real key)"""
        print("\n🧪 Testing Connection Test - Anthropic...")
        
        try:
            test_data = {
                "provider": "anthropic"
            }
            
            response = self.session.post(
                f"{API_BASE}/api-keys/test-connection",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if ("success" in data and 
                    "provider" in data and 
                    "message" in data and
                    "tested_at" in data):
                    success = data["success"]
                    message = data["message"]
                    # Expected to fail with test key
                    self.log_test("Test Connection Anthropic", True, 
                                f"Test completed: success={success}, message='{message[:50]}...'")
                    return True
                else:
                    self.log_test("Test Connection Anthropic", False, "Invalid response format")
                    return False
            else:
                self.log_test("Test Connection Anthropic", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test Connection Anthropic", False, f"Exception: {str(e)}")
            return False
    
    def test_connection_test_openai(self):
        """Test 8: Test Connection - OpenAI (Expected to fail without real key)"""
        print("\n🧪 Testing Connection Test - OpenAI...")
        
        try:
            test_data = {
                "provider": "openai"
            }
            
            response = self.session.post(
                f"{API_BASE}/api-keys/test-connection",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if ("success" in data and 
                    "provider" in data and 
                    "message" in data and
                    "tested_at" in data):
                    success = data["success"]
                    message = data["message"]
                    # Expected to fail with test key
                    self.log_test("Test Connection OpenAI", True, 
                                f"Test completed: success={success}, message='{message[:50]}...'")
                    return True
                else:
                    self.log_test("Test Connection OpenAI", False, "Invalid response format")
                    return False
            else:
                self.log_test("Test Connection OpenAI", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Test Connection OpenAI", False, f"Exception: {str(e)}")
            return False
    
    def test_delete_anthropic_key(self):
        """Test 9: Delete Anthropic API Key"""
        print("\n🗑️ Testing Delete Anthropic API Key...")
        
        try:
            response = self.session.delete(f"{API_BASE}/api-keys/anthropic")
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") == True and 
                    "message" in data):
                    message = data["message"]
                    self.log_test("Delete Anthropic Key", True, f"Key deleted: {message}")
                    return True
                else:
                    self.log_test("Delete Anthropic Key", False, f"Invalid response data: {data}")
                    return False
            else:
                self.log_test("Delete Anthropic Key", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Delete Anthropic Key", False, f"Exception: {str(e)}")
            return False
    
    def test_validation_no_auth(self):
        """Test 10: Validation - No Authentication"""
        print("\n🔒 Testing Validation - No Authentication...")
        
        try:
            # Create session without auth header
            no_auth_session = requests.Session()
            
            response = no_auth_session.get(f"{API_BASE}/api-keys/list")
            
            if response.status_code == 401:
                self.log_test("Validation No Auth", True, "Correctly rejected unauthenticated request")
                return True
            else:
                self.log_test("Validation No Auth", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Validation No Auth", False, f"Exception: {str(e)}")
            return False
    
    def test_validation_invalid_provider(self):
        """Test 11: Validation - Invalid Provider"""
        print("\n❌ Testing Validation - Invalid Provider...")
        
        try:
            invalid_data = {
                "provider": "invalid_provider",
                "api_key": "test-key-123"
            }
            
            response = self.session.post(
                f"{API_BASE}/api-keys/save",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test("Validation Invalid Provider", True, "Correctly rejected invalid provider")
                return True
            else:
                self.log_test("Validation Invalid Provider", False, f"Expected 422, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Validation Invalid Provider", False, f"Exception: {str(e)}")
            return False
    
    def test_validation_short_key(self):
        """Test 12: Validation - Too Short API Key"""
        print("\n❌ Testing Validation - Too Short API Key...")
        
        try:
            invalid_data = {
                "provider": "openai",
                "api_key": "short"  # Less than 10 characters
            }
            
            response = self.session.post(
                f"{API_BASE}/api-keys/save",
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 422:  # Validation error
                self.log_test("Validation Short Key", True, "Correctly rejected short API key")
                return True
            else:
                self.log_test("Validation Short Key", False, f"Expected 422, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Validation Short Key", False, f"Exception: {str(e)}")
            return False
    
    def test_final_cleanup(self):
        """Test 13: Final Cleanup - Delete remaining keys"""
        print("\n🧹 Testing Final Cleanup...")
        
        try:
            # Delete OpenAI key if it exists
            response = self.session.delete(f"{API_BASE}/api-keys/openai")
            
            if response.status_code in [200, 404]:  # Success or not found
                self.log_test("Final Cleanup", True, "Cleanup completed successfully")
                return True
            else:
                self.log_test("Final Cleanup", False, f"Cleanup failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Final Cleanup", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API Key Management tests"""
        print("🚀 Starting API Key Management Endpoint Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USERNAME}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_authentication,
            self.test_api_keys_list_empty,
            self.test_save_anthropic_key,
            self.test_save_openai_key,
            self.test_api_keys_list_populated,
            self.test_api_keys_status,
            self.test_connection_test_anthropic,
            self.test_connection_test_openai,
            self.test_delete_anthropic_key,
            self.test_validation_no_auth,
            self.test_validation_invalid_provider,
            self.test_validation_short_key,
            self.test_final_cleanup
        ]
        
        # Run tests
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                self.test_results.append({
                    "test": test.__name__,
                    "success": False,
                    "details": f"Test crashed: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Failed tests details
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        print("\n✅ API Key Management Testing Complete!")
        return passed == total


def main():
    """Main test execution"""
    tester = APIKeyManagementTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()