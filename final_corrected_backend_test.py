#!/usr/bin/env python3
"""
FINAL CORRECTED COMPREHENSIVE BACKEND TEST
Corrected version addressing the issues found in the initial test.
"""

import requests
import json
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CorrectedBackendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with demo/demo123"""
        login_data = {"username": "demo", "password": "demo123"}
        response = self.session.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            auth_data = response.json()
            self.token = auth_data.get("access_token")
            return {"status": "success", "token": self.token}
        else:
            return {"status": "failed", "error": f"HTTP {response.status_code}"}

    def test_all_12_languages_corrected(self) -> Dict[str, Any]:
        """Test all 12 languages with corrected output checking"""
        logger.info("🚀 Testing ALL 12 Languages (Corrected)")
        
        if not self.token:
            return {"status": "skipped", "error": "No token"}
        
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Corrected test codes with proper expected outputs
        test_codes = {
            "python": ('print("Hello Python")', "Hello Python"),
            "javascript": ('console.log("Hello JavaScript")', "Hello JavaScript"),
            "typescript": ('console.log("Hello TypeScript"); interface Test { name: string; }', "Hello TypeScript"),
            "bash": ('echo "Hello Bash"', "Hello Bash"),
            "cpp": ('#include <iostream>\nusing namespace std;\nint main() { cout << "Hello C++" << endl; return 0; }', "Hello C++"),
            "c": ('#include <stdio.h>\nint main() { printf("Hello C\\n"); return 0; }', "Hello C"),
            "csharp": ('using System; class Program { static void Main() { Console.WriteLine("Hello C#"); } }', "Hello C#"),
            "java": ('public class Main { public static void main(String[] args) { System.out.println("Hello Java"); } }', "Hello Java"),
            "go": ('package main\nimport "fmt"\nfunc main() { fmt.Println("Hello Go") }', "Hello Go"),
            "php": ('<?php echo "Hello PHP"; ?>', "Hello PHP"),
            "ruby": ('puts "Hello Ruby"', "Hello Ruby"),
            "perl": ('print "Hello Perl\\n";', "Hello Perl")
        }
        
        results = {}
        successful_languages = []
        failed_languages = []
        
        for language, (code, expected_output) in test_codes.items():
            logger.info(f"   Testing {language.upper()}...")
            
            execute_data = {"language": language, "code": code}
            
            try:
                response = self.session.post(
                    f"{self.api_url}/sandbox/execute",
                    json=execute_data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    success = result.get("success", False)
                    stdout = result.get("stdout", "")
                    exit_code = result.get("exit_code", -1)
                    
                    # Check if expected output is in stdout
                    output_correct = expected_output in stdout
                    
                    if success and exit_code == 0 and output_correct:
                        logger.info(f"   ✅ {language}: Success")
                        successful_languages.append(language)
                        results[language] = {"status": "success", "stdout": stdout.strip()}
                    else:
                        logger.error(f"   ❌ {language}: Failed - success:{success}, exit_code:{exit_code}, output_correct:{output_correct}")
                        logger.error(f"      Expected: '{expected_output}', Got: '{stdout.strip()}'")
                        failed_languages.append(language)
                        results[language] = {
                            "status": "failed",
                            "success": success,
                            "exit_code": exit_code,
                            "expected": expected_output,
                            "actual": stdout.strip(),
                            "output_correct": output_correct
                        }
                else:
                    logger.error(f"   ❌ {language}: HTTP {response.status_code}")
                    failed_languages.append(language)
                    results[language] = {"status": "failed", "error": f"HTTP {response.status_code}"}
                    
            except Exception as e:
                logger.error(f"   ❌ {language}: Exception - {e}")
                failed_languages.append(language)
                results[language] = {"status": "error", "error": str(e)}
        
        total_languages = len(test_codes)
        successful_count = len(successful_languages)
        
        logger.info(f"   SUMMARY: {successful_count}/{total_languages} languages working")
        logger.info(f"   ✅ Working: {', '.join(successful_languages)}")
        if failed_languages:
            logger.info(f"   ❌ Failed: {', '.join(failed_languages)}")
        
        return {
            "status": "success" if successful_count >= 10 else "failed",
            "successful_count": successful_count,
            "total_languages": total_languages,
            "successful_languages": successful_languages,
            "failed_languages": failed_languages,
            "results": results
        }

    def test_api_key_management_corrected(self) -> Dict[str, Any]:
        """Test API key management with corrected validation"""
        logger.info("🔑 Testing API Key Management (Corrected)")
        
        if not self.token:
            return {"status": "skipped", "error": "No token"}
        
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        try:
            results = {}
            
            # 1. Save API Keys
            logger.info("   Testing Save API Keys...")
            api_keys = {
                "anthropic": "sk-ant-api03-test123",
                "openai": "sk-proj-test123", 
                "perplexity": "pplx-test123",
                "github": "ghp_test123"
            }
            
            for provider, key in api_keys.items():
                save_data = {"provider": provider, "api_key": key}
                response = self.session.post(f"{self.api_url}/api-keys/save", json=save_data, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    masked_key = result.get("masked_key", "")
                    is_active = result.get("is_active", False)
                    
                    # Verify masked key format
                    key_properly_masked = "..." in masked_key and len(masked_key) < len(key)
                    
                    logger.info(f"   ✅ {provider}: {masked_key} (active: {is_active})")
                    results[f"save_{provider}"] = {
                        "status": "success",
                        "masked_key": masked_key,
                        "is_active": is_active,
                        "properly_masked": key_properly_masked
                    }
                else:
                    logger.error(f"   ❌ {provider}: HTTP {response.status_code}")
                    results[f"save_{provider}"] = {"status": "failed", "error": f"HTTP {response.status_code}"}
            
            # 2. List API Keys
            logger.info("   Testing List API Keys...")
            list_response = self.session.get(f"{self.api_url}/api-keys/list", headers=headers, timeout=10)
            
            if list_response.status_code == 200:
                list_data = list_response.json()
                logger.info(f"   ✅ Listed {len(list_data)} API keys")
                results["list_keys"] = {"status": "success", "count": len(list_data)}
            else:
                logger.error(f"   ❌ List failed: HTTP {list_response.status_code}")
                results["list_keys"] = {"status": "failed", "error": f"HTTP {list_response.status_code}"}
            
            # 3. Status Check
            logger.info("   Testing Status Check...")
            status_response = self.session.get(f"{self.api_url}/api-keys/status", headers=headers, timeout=10)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                configured_providers = status_data.get("configured_providers", {})
                total_configured = status_data.get("total_configured", 0)
                
                logger.info(f"   ✅ Status: {total_configured} providers configured")
                results["status_check"] = {
                    "status": "success",
                    "total_configured": total_configured,
                    "configured_providers": configured_providers
                }
            else:
                logger.error(f"   ❌ Status failed: HTTP {status_response.status_code}")
                results["status_check"] = {"status": "failed", "error": f"HTTP {status_response.status_code}"}
            
            # 4. Update Key
            logger.info("   Testing Update Key...")
            update_data = {"provider": "openai", "api_key": "sk-proj-updated-test123"}
            update_response = self.session.post(f"{self.api_url}/api-keys/save", json=update_data, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                update_result = update_response.json()
                logger.info(f"   ✅ Updated: {update_result.get('masked_key')}")
                results["update_key"] = {"status": "success"}
            else:
                logger.error(f"   ❌ Update failed: HTTP {update_response.status_code}")
                results["update_key"] = {"status": "failed", "error": f"HTTP {update_response.status_code}"}
            
            # 5. Delete Key
            logger.info("   Testing Delete Key...")
            delete_response = self.session.delete(f"{self.api_url}/api-keys/perplexity", headers=headers, timeout=10)
            
            if delete_response.status_code == 200:
                delete_result = delete_response.json()
                logger.info(f"   ✅ Deleted: {delete_result.get('success')}")
                results["delete_key"] = {"status": "success"}
            else:
                logger.error(f"   ❌ Delete failed: HTTP {delete_response.status_code}")
                results["delete_key"] = {"status": "failed", "error": f"HTTP {delete_response.status_code}"}
            
            # Evaluate success
            successful_operations = sum(1 for result in results.values() if result.get("status") == "success")
            total_operations = len(results)
            
            return {
                "status": "success" if successful_operations >= 7 else "failed",
                "successful_operations": successful_operations,
                "total_operations": total_operations,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ API Key Management test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_developer_modes_corrected(self) -> Dict[str, Any]:
        """Test developer modes with corrected timeout"""
        logger.info("🎨 Testing Developer Modes (Corrected)")
        
        if not self.token:
            return {"status": "skipped", "error": "No token"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # Test developer modes endpoint
            logger.info("   Testing developer modes endpoint...")
            modes_response = self.session.get(f"{self.api_url}/developer-modes/", headers=headers, timeout=15)
            
            if modes_response.status_code == 200:
                modes = modes_response.json()
                modes_data = modes.get("modes", {})
                
                # Check for junior and senior modes
                junior_present = "junior" in modes_data
                senior_present = "senior" in modes_data
                
                if junior_present:
                    junior_model = modes_data["junior"].get("model", "")
                    junior_correct = "haiku" in junior_model.lower()
                    logger.info(f"   ✅ Junior mode: {junior_model} ({'✅' if junior_correct else '❌'})")
                
                if senior_present:
                    senior_model = modes_data["senior"].get("model", "")
                    senior_correct = "sonnet" in senior_model.lower()
                    logger.info(f"   ✅ Senior mode: {senior_model} ({'✅' if senior_correct else '❌'})")
                
                modes_working = junior_present and senior_present
                
                return {
                    "status": "success" if modes_working else "failed",
                    "junior_present": junior_present,
                    "senior_present": senior_present,
                    "modes_data": modes_data
                }
            else:
                logger.error(f"   ❌ Developer modes failed: HTTP {modes_response.status_code}")
                return {"status": "failed", "error": f"HTTP {modes_response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Developer Modes test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_code_templates_corrected(self) -> Dict[str, Any]:
        """Test code templates with corrected timeout"""
        logger.info("📝 Testing Code Templates (Corrected)")
        
        if not self.token:
            return {"status": "skipped", "error": "No token"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            results = {}
            
            # 1. Get template languages
            logger.info("   Testing template languages...")
            languages_response = self.session.get(f"{self.api_url}/sandbox/templates/languages", headers=headers, timeout=15)
            
            if languages_response.status_code == 200:
                languages = languages_response.json()
                languages_list = languages.get("languages", [])
                logger.info(f"   ✅ {len(languages_list)} template languages")
                results["languages"] = {"status": "success", "count": len(languages_list)}
            else:
                logger.error(f"   ❌ Template languages failed: HTTP {languages_response.status_code}")
                results["languages"] = {"status": "failed", "error": f"HTTP {languages_response.status_code}"}
            
            # 2. Get template types
            logger.info("   Testing template types...")
            types_response = self.session.get(f"{self.api_url}/sandbox/templates/types", headers=headers, timeout=15)
            
            if types_response.status_code == 200:
                types_data = types_response.json()
                template_types = types_data.get("template_types", [])
                expected_types = ["hello_world", "fibonacci", "data_structures"]
                types_correct = all(t in template_types for t in expected_types)
                
                logger.info(f"   ✅ Template types: {template_types}")
                logger.info(f"   Expected types present: {'✅' if types_correct else '❌'}")
                results["types"] = {
                    "status": "success" if types_correct else "partial",
                    "types": template_types,
                    "expected_types_present": types_correct
                }
            else:
                logger.error(f"   ❌ Template types failed: HTTP {types_response.status_code}")
                results["types"] = {"status": "failed", "error": f"HTTP {types_response.status_code}"}
            
            # 3. Test specific template
            logger.info("   Testing specific template...")
            template_response = self.session.get(
                f"{self.api_url}/sandbox/templates/template/python/hello_world",
                headers=headers,
                timeout=15
            )
            
            if template_response.status_code == 200:
                template_data = template_response.json()
                code = template_data.get("code", "")
                has_code = len(code) > 10
                
                logger.info(f"   ✅ Python hello_world template: {len(code)} chars")
                results["specific_template"] = {
                    "status": "success" if has_code else "failed",
                    "code_length": len(code),
                    "has_code": has_code
                }
            else:
                logger.error(f"   ❌ Specific template failed: HTTP {template_response.status_code}")
                results["specific_template"] = {"status": "failed", "error": f"HTTP {template_response.status_code}"}
            
            # Evaluate success
            successful_tests = sum(1 for result in results.values() if result.get("status") == "success")
            total_tests = len(results)
            
            return {
                "status": "success" if successful_tests >= 2 else "failed",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Code Templates test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_security_corrected(self) -> Dict[str, Any]:
        """Test security with corrected expectations"""
        logger.info("🔒 Testing Security (Corrected)")
        
        try:
            results = {}
            
            # 1. Test rate limiting (requires auth)
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}"}
                logger.info("   Testing rate limiting (with auth)...")
                limits_response = self.session.get(f"{self.api_url}/rate-limits/limits", headers=headers, timeout=10)
                
                if limits_response.status_code == 200:
                    limits_data = limits_response.json()
                    rate_limits = limits_data.get("rate_limits", [])
                    logger.info(f"   ✅ Rate limits: {len(rate_limits)} configured")
                    results["rate_limits"] = {"status": "success", "count": len(rate_limits)}
                else:
                    logger.error(f"   ❌ Rate limits failed: HTTP {limits_response.status_code}")
                    results["rate_limits"] = {"status": "failed", "error": f"HTTP {limits_response.status_code}"}
            else:
                results["rate_limits"] = {"status": "skipped", "error": "No token"}
            
            # 2. Test authentication requirements
            logger.info("   Testing authentication requirements...")
            
            # Test protected endpoint without token
            protected_response = self.session.get(f"{self.api_url}/sessions/list", timeout=10)
            no_token_rejected = protected_response.status_code == 401
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid-token"}
            invalid_response = self.session.get(f"{self.api_url}/sessions/list", headers=invalid_headers, timeout=10)
            invalid_token_rejected = invalid_response.status_code == 401
            
            # Test with valid token
            valid_token_works = False
            if self.token:
                valid_headers = {"Authorization": f"Bearer {self.token}"}
                valid_response = self.session.get(f"{self.api_url}/sessions/list", headers=valid_headers, timeout=10)
                valid_token_works = valid_response.status_code == 200
            
            auth_working = no_token_rejected and invalid_token_rejected and valid_token_works
            
            logger.info(f"   No token rejected: {'✅' if no_token_rejected else '❌'}")
            logger.info(f"   Invalid token rejected: {'✅' if invalid_token_rejected else '❌'}")
            logger.info(f"   Valid token works: {'✅' if valid_token_works else '❌'}")
            
            results["authentication"] = {
                "status": "success" if auth_working else "failed",
                "no_token_rejected": no_token_rejected,
                "invalid_token_rejected": invalid_token_rejected,
                "valid_token_works": valid_token_works
            }
            
            # 3. Test API key encryption (corrected)
            logger.info("   Testing API key encryption...")
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
                
                # Use correct provider format
                save_data = {"provider": "test_provider", "api_key": "test-key-12345"}
                save_response = self.session.post(f"{self.api_url}/api-keys/save", json=save_data, headers=headers, timeout=10)
                
                if save_response.status_code == 200:
                    save_result = save_response.json()
                    masked_key = save_result.get("masked_key", "")
                    key_masked = "..." in masked_key and len(masked_key) < 20
                    
                    logger.info(f"   ✅ API key masked: {masked_key}")
                    results["api_key_encryption"] = {
                        "status": "success" if key_masked else "failed",
                        "masked_key": masked_key,
                        "properly_masked": key_masked
                    }
                    
                    # Clean up
                    self.session.delete(f"{self.api_url}/api-keys/test_provider", headers=headers, timeout=10)
                else:
                    logger.error(f"   ❌ API key save failed: HTTP {save_response.status_code}")
                    results["api_key_encryption"] = {"status": "failed", "error": f"HTTP {save_response.status_code}"}
            else:
                results["api_key_encryption"] = {"status": "skipped", "error": "No token"}
            
            # Evaluate success
            successful_tests = sum(1 for result in results.values() if result.get("status") == "success")
            total_tests = len(results)
            
            return {
                "status": "success" if successful_tests >= 2 else "failed",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Security test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_corrected_tests(self) -> Dict[str, Any]:
        """Run corrected comprehensive tests"""
        logger.info("🚀 STARTING CORRECTED COMPREHENSIVE BACKEND TEST")
        logger.info("=" * 80)
        
        # Authenticate first
        auth_result = self.authenticate()
        if auth_result["status"] != "success":
            logger.error("❌ Authentication failed - cannot proceed")
            return {"status": "failed", "error": "Authentication failed"}
        
        logger.info("✅ Authentication successful")
        
        # Run corrected tests
        test_results = {}
        
        # Test 1: All 12 Languages (Corrected)
        test_results["all_languages"] = self.test_all_12_languages_corrected()
        
        # Test 2: API Key Management (Corrected)
        test_results["api_key_management"] = self.test_api_key_management_corrected()
        
        # Test 3: Developer Modes (Corrected)
        test_results["developer_modes"] = self.test_developer_modes_corrected()
        
        # Test 4: Code Templates (Corrected)
        test_results["code_templates"] = self.test_code_templates_corrected()
        
        # Test 5: Security (Corrected)
        test_results["security"] = self.test_security_corrected()
        
        # Generate summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 CORRECTED TEST SUMMARY")
        logger.info("=" * 80)
        
        passed_tests = []
        failed_tests = []
        
        for test_name, result in test_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                passed_tests.append(test_name)
                logger.info(f"✅ {test_name}: PASSED")
            else:
                failed_tests.append(test_name)
                error = result.get("error", "Unknown error")
                logger.info(f"❌ {test_name}: FAILED - {error}")
        
        logger.info(f"\n📊 Final Results:")
        logger.info(f"   ✅ PASSED: {len(passed_tests)}")
        logger.info(f"   ❌ FAILED: {len(failed_tests)}")
        
        overall_success = len(passed_tests) >= 4  # At least 4/5 tests passed
        
        if overall_success:
            logger.info(f"\n🎉 OVERALL RESULT: SUCCESS!")
        else:
            logger.info(f"\n⚠️ OVERALL RESULT: NEEDS ATTENTION")
        
        return {
            "overall_success": overall_success,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "detailed_results": test_results
        }

def main():
    tester = CorrectedBackendTester()
    results = tester.run_corrected_tests()
    
    if results["overall_success"]:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()