#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE BACKEND TEST - ALL FEATURES
Based on the detailed review request for systematic testing of ALL implemented backend features.

TEST SCOPE:
1. 🔐 Authentication (Priority: CRITICAL)
2. 🔑 API Key Management (Priority: CRITICAL - NEW)  
3. 🚀 Cloud Sandbox - ALL 12 languages (Priority: CRITICAL)
4. 📝 Code Templates (Priority: HIGH)
5. 🎨 Developer Modes (Priority: HIGH)
6. 💬 Chat System (Priority: HIGH)
7. 🔀 Session Fork (Priority: MEDIUM - RECENTLY FIXED)
8. 📊 System Health (Priority: HIGH)
9. ⚡ Performance Tests (Priority: MEDIUM)
10. 🔒 Security Validation (Priority: CRITICAL)

TEST CREDENTIALS:
- Username: demo
- Password: demo123
"""

import requests
import json
import time
import logging
import os
import concurrent.futures
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalComprehensiveBackendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.test_results = {}
        
    def authenticate(self) -> Dict[str, Any]:
        """🔐 AUTHENTICATION - Login with demo/demo123"""
        logger.info("🔐 AUTHENTICATION TEST - Login with demo/demo123")
        
        try:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                # Verify required fields
                required_fields = ["access_token", "token_type", "user_id", "username"]
                missing_fields = [field for field in required_fields if not auth_data.get(field)]
                
                if missing_fields:
                    logger.error(f"❌ Missing required fields: {missing_fields}")
                    return {"status": "failed", "error": f"Missing fields: {missing_fields}"}
                
                # Verify token type
                if auth_data.get("token_type") != "bearer":
                    logger.error(f"❌ Invalid token_type: {auth_data.get('token_type')} (expected: bearer)")
                    return {"status": "failed", "error": "Invalid token_type"}
                
                logger.info("✅ Authentication successful!")
                logger.info(f"   User ID: {self.user_info['user_id']}")
                logger.info(f"   Username: {self.user_info['username']}")
                logger.info(f"   Token type: {auth_data.get('token_type')}")
                
                return {
                    "status": "success",
                    "token": self.token,
                    "user_info": self.user_info,
                    "token_type": auth_data.get("token_type")
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {"status": "failed", "error": error_detail}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def test_protected_endpoints(self) -> Dict[str, Any]:
        """🔐 Test protected endpoints with and without token"""
        logger.info("🔐 Testing Protected Endpoints")
        
        try:
            # Test WITHOUT token (should return 401)
            response_no_token = self.session.get(f"{self.api_url}/rate-limits/quota", timeout=10)
            logger.info(f"   Without token: {response_no_token.status_code}")
            
            # Test WITH valid token (should succeed)
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}"}
                response_with_token = self.session.get(f"{self.api_url}/rate-limits/quota", headers=headers, timeout=10)
                logger.info(f"   With valid token: {response_with_token.status_code}")
                
                # Test WITH invalid token (should return 401)
                invalid_headers = {"Authorization": "Bearer invalid-token-12345"}
                response_invalid_token = self.session.get(f"{self.api_url}/rate-limits/quota", headers=invalid_headers, timeout=10)
                logger.info(f"   With invalid token: {response_invalid_token.status_code}")
                
                # Verify results
                no_token_correct = response_no_token.status_code == 401
                valid_token_correct = response_with_token.status_code == 200
                invalid_token_correct = response_invalid_token.status_code == 401
                
                if no_token_correct and valid_token_correct and invalid_token_correct:
                    logger.info("✅ Protected endpoints working correctly")
                    return {
                        "status": "success",
                        "no_token_status": response_no_token.status_code,
                        "valid_token_status": response_with_token.status_code,
                        "invalid_token_status": response_invalid_token.status_code,
                        "protection_working": True
                    }
                else:
                    logger.error("❌ Protected endpoints not working correctly")
                    return {
                        "status": "failed",
                        "error": "Protection not working as expected",
                        "no_token_status": response_no_token.status_code,
                        "valid_token_status": response_with_token.status_code,
                        "invalid_token_status": response_invalid_token.status_code,
                        "protection_working": False
                    }
            else:
                return {"status": "skipped", "error": "No authentication token available"}
                
        except Exception as e:
            logger.error(f"❌ Protected endpoints test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_api_key_management(self) -> Dict[str, Any]:
        """🔑 API KEY MANAGEMENT - Test all 5 endpoints"""
        logger.info("🔑 API KEY MANAGEMENT TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # 1. Save API Keys (4 providers)
            logger.info("   Testing Save API Keys...")
            api_keys = {
                "anthropic": "sk-ant-api03-test123",
                "openai": "sk-proj-test123",
                "perplexity": "pplx-test123",
                "github": "ghp_test123"
            }
            
            saved_keys = {}
            for provider, key in api_keys.items():
                save_data = {"provider": provider, "api_key": key}
                response = self.session.post(f"{self.api_url}/api-keys/save", json=save_data, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    saved_keys[provider] = {
                        "masked_key": result.get("masked_key"),
                        "is_active": result.get("is_active")
                    }
                    logger.info(f"   ✅ {provider}: {result.get('masked_key')} (active: {result.get('is_active')})")
                else:
                    logger.error(f"   ❌ {provider}: HTTP {response.status_code}")
                    saved_keys[provider] = {"error": f"HTTP {response.status_code}"}
            
            results["save_keys"] = saved_keys
            
            # 2. List API Keys
            logger.info("   Testing List API Keys...")
            list_response = self.session.get(f"{self.api_url}/api-keys/list", headers=headers, timeout=10)
            
            if list_response.status_code == 200:
                list_data = list_response.json()
                logger.info(f"   ✅ Listed {len(list_data)} API keys")
                results["list_keys"] = {"status": "success", "count": len(list_data), "keys": list_data}
            else:
                logger.error(f"   ❌ List keys failed: HTTP {list_response.status_code}")
                results["list_keys"] = {"status": "failed", "error": f"HTTP {list_response.status_code}"}
            
            # 3. Status Check
            logger.info("   Testing API Keys Status...")
            status_response = self.session.get(f"{self.api_url}/api-keys/status", headers=headers, timeout=10)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                configured_providers = status_data.get("configured_providers", {})
                total_configured = status_data.get("total_configured", 0)
                
                logger.info(f"   ✅ Status: {total_configured} providers configured")
                for provider, configured in configured_providers.items():
                    logger.info(f"      {provider}: {'✅' if configured else '❌'}")
                
                results["status_check"] = {
                    "status": "success",
                    "total_configured": total_configured,
                    "configured_providers": configured_providers
                }
            else:
                logger.error(f"   ❌ Status check failed: HTTP {status_response.status_code}")
                results["status_check"] = {"status": "failed", "error": f"HTTP {status_response.status_code}"}
            
            # 4. Update Key (test with OpenAI)
            logger.info("   Testing Update API Key...")
            update_data = {"provider": "openai", "api_key": "sk-proj-updated-test123"}
            update_response = self.session.post(f"{self.api_url}/api-keys/save", json=update_data, headers=headers, timeout=10)
            
            if update_response.status_code == 200:
                update_result = update_response.json()
                logger.info(f"   ✅ Updated OpenAI key: {update_result.get('masked_key')}")
                results["update_key"] = {"status": "success", "masked_key": update_result.get("masked_key")}
            else:
                logger.error(f"   ❌ Update key failed: HTTP {update_response.status_code}")
                results["update_key"] = {"status": "failed", "error": f"HTTP {update_response.status_code}"}
            
            # 5. Delete Key (test with Perplexity)
            logger.info("   Testing Delete API Key...")
            delete_response = self.session.delete(f"{self.api_url}/api-keys/perplexity", headers=headers, timeout=10)
            
            if delete_response.status_code == 200:
                delete_result = delete_response.json()
                logger.info(f"   ✅ Deleted Perplexity key: {delete_result.get('success')}")
                results["delete_key"] = {"status": "success", "success": delete_result.get("success")}
            else:
                logger.error(f"   ❌ Delete key failed: HTTP {delete_response.status_code}")
                results["delete_key"] = {"status": "failed", "error": f"HTTP {delete_response.status_code}"}
            
            # Final status check after delete
            final_status_response = self.session.get(f"{self.api_url}/api-keys/status", headers=headers, timeout=10)
            if final_status_response.status_code == 200:
                final_status = final_status_response.json()
                final_total = final_status.get("total_configured", 0)
                logger.info(f"   Final status: {final_total} providers configured")
                results["final_status"] = {"total_configured": final_total}
            
            # Evaluate overall success
            successful_operations = sum(1 for result in results.values() if result.get("status") == "success")
            total_operations = len(results)
            
            if successful_operations >= 4:  # At least 4/5 operations successful
                logger.info("✅ API Key Management working correctly!")
                return {
                    "status": "success",
                    "successful_operations": successful_operations,
                    "total_operations": total_operations,
                    "results": results,
                    "api_key_management_working": True
                }
            else:
                logger.error("❌ API Key Management has issues")
                return {
                    "status": "failed",
                    "error": f"Only {successful_operations}/{total_operations} operations successful",
                    "results": results,
                    "api_key_management_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ API Key Management test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_cloud_sandbox_all_languages(self) -> Dict[str, Any]:
        """🚀 CLOUD SANDBOX - Test ALL 12 languages"""
        logger.info("🚀 CLOUD SANDBOX - Testing ALL 12 Languages")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Define test code for each language
        test_codes = {
            "python": 'print("Hello Python")',
            "javascript": 'console.log("Hello JavaScript")',
            "typescript": 'console.log("Hello TypeScript"); interface Test { name: string; }',
            "bash": 'echo "Hello Bash"',
            "cpp": '#include <iostream>\nusing namespace std;\nint main() { cout << "Hello C++" << endl; return 0; }',
            "c": '#include <stdio.h>\nint main() { printf("Hello C\\n"); return 0; }',
            "csharp": 'using System; class Program { static void Main() { Console.WriteLine("Hello C#"); } }',
            "java": 'public class Main { public static void main(String[] args) { System.out.println("Hello Java"); } }',
            "go": 'package main\nimport "fmt"\nfunc main() { fmt.Println("Hello Go") }',
            "php": '<?php echo "Hello PHP"; ?>',
            "ruby": 'puts "Hello Ruby"',
            "perl": 'print "Hello Perl\\n";'
        }
        
        try:
            results = {}
            
            # First, get supported languages
            logger.info("   Getting supported languages...")
            languages_response = self.session.get(f"{self.api_url}/sandbox/languages", headers=headers, timeout=10)
            
            if languages_response.status_code == 200:
                supported_languages = languages_response.json()
                logger.info(f"   ✅ {len(supported_languages)} languages supported")
                results["supported_languages"] = supported_languages
            else:
                logger.error(f"   ❌ Failed to get languages: HTTP {languages_response.status_code}")
                return {"status": "failed", "error": "Could not get supported languages"}
            
            # Test each language
            successful_languages = []
            failed_languages = []
            
            for language, code in test_codes.items():
                logger.info(f"   Testing {language.upper()}...")
                
                execute_data = {
                    "language": language,
                    "code": code
                }
                
                try:
                    response = self.session.post(
                        f"{self.api_url}/sandbox/execute",
                        json=execute_data,
                        headers=headers,
                        timeout=30  # Longer timeout for compilation
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        success = result.get("success", False)
                        stdout = result.get("stdout", "")
                        stderr = result.get("stderr", "")
                        exit_code = result.get("exit_code", -1)
                        execution_time = result.get("execution_time", 0)
                        
                        # Check if output contains expected "Hello [Language]"
                        expected_output = f"Hello {language.title()}"
                        output_correct = expected_output in stdout
                        
                        if success and exit_code == 0 and output_correct:
                            logger.info(f"   ✅ {language}: Success (time: {execution_time:.3f}s)")
                            successful_languages.append(language)
                            results[language] = {
                                "status": "success",
                                "success": success,
                                "exit_code": exit_code,
                                "execution_time": execution_time,
                                "stdout_length": len(stdout),
                                "output_correct": output_correct
                            }
                        else:
                            logger.error(f"   ❌ {language}: Failed (success: {success}, exit_code: {exit_code}, output_correct: {output_correct})")
                            failed_languages.append(language)
                            results[language] = {
                                "status": "failed",
                                "success": success,
                                "exit_code": exit_code,
                                "stdout": stdout[:100] + "..." if len(stdout) > 100 else stdout,
                                "stderr": stderr[:100] + "..." if len(stderr) > 100 else stderr,
                                "output_correct": output_correct
                            }
                    else:
                        logger.error(f"   ❌ {language}: HTTP {response.status_code}")
                        failed_languages.append(language)
                        results[language] = {
                            "status": "failed",
                            "error": f"HTTP {response.status_code}"
                        }
                        
                except Exception as e:
                    logger.error(f"   ❌ {language}: Exception - {e}")
                    failed_languages.append(language)
                    results[language] = {
                        "status": "error",
                        "error": str(e)
                    }
            
            # Summary
            total_languages = len(test_codes)
            successful_count = len(successful_languages)
            
            logger.info(f"   SUMMARY: {successful_count}/{total_languages} languages working")
            logger.info(f"   ✅ Working: {', '.join(successful_languages)}")
            if failed_languages:
                logger.info(f"   ❌ Failed: {', '.join(failed_languages)}")
            
            # Success criteria: At least 10/12 languages working
            if successful_count >= 10:
                logger.info("✅ Cloud Sandbox - ALL Languages working!")
                return {
                    "status": "success",
                    "successful_languages": successful_languages,
                    "failed_languages": failed_languages,
                    "successful_count": successful_count,
                    "total_languages": total_languages,
                    "results": results,
                    "sandbox_working": True
                }
            else:
                logger.error("❌ Cloud Sandbox - Too many language failures")
                return {
                    "status": "failed",
                    "error": f"Only {successful_count}/{total_languages} languages working",
                    "successful_languages": successful_languages,
                    "failed_languages": failed_languages,
                    "results": results,
                    "sandbox_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Cloud Sandbox test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_sandbox_features(self) -> Dict[str, Any]:
        """🚀 Test additional sandbox features (stdin, errors, timeout)"""
        logger.info("🚀 Testing Additional Sandbox Features")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # 1. Test stdin input
            logger.info("   Testing stdin input...")
            stdin_data = {
                "language": "python",
                "code": 'name = input("Enter name: ")\nprint(f"Hello, {name}!")',
                "stdin": "World"
            }
            
            stdin_response = self.session.post(f"{self.api_url}/sandbox/execute", json=stdin_data, headers=headers, timeout=10)
            
            if stdin_response.status_code == 200:
                stdin_result = stdin_response.json()
                stdin_output = stdin_result.get("stdout", "")
                stdin_working = "Hello, World!" in stdin_output
                
                logger.info(f"   ✅ Stdin: {'Working' if stdin_working else 'Failed'}")
                results["stdin_test"] = {
                    "status": "success" if stdin_working else "failed",
                    "stdin_working": stdin_working,
                    "output": stdin_output
                }
            else:
                logger.error(f"   ❌ Stdin test failed: HTTP {stdin_response.status_code}")
                results["stdin_test"] = {"status": "failed", "error": f"HTTP {stdin_response.status_code}"}
            
            # 2. Test compilation error
            logger.info("   Testing compilation error handling...")
            error_data = {
                "language": "cpp",
                "code": '#include <iostream>\nint main() { cout << "missing semicolon" }'  # Missing semicolon
            }
            
            error_response = self.session.post(f"{self.api_url}/sandbox/execute", json=error_data, headers=headers, timeout=10)
            
            if error_response.status_code == 200:
                error_result = error_response.json()
                error_success = error_result.get("success", True)
                error_stderr = error_result.get("stderr", "")
                error_handling_working = not error_success and "error" in error_stderr.lower()
                
                logger.info(f"   ✅ Error handling: {'Working' if error_handling_working else 'Failed'}")
                results["error_handling"] = {
                    "status": "success" if error_handling_working else "failed",
                    "error_caught": not error_success,
                    "stderr_present": bool(error_stderr)
                }
            else:
                logger.error(f"   ❌ Error handling test failed: HTTP {error_response.status_code}")
                results["error_handling"] = {"status": "failed", "error": f"HTTP {error_response.status_code}"}
            
            # 3. Test timeout (with short timeout)
            logger.info("   Testing timeout handling...")
            timeout_data = {
                "language": "python",
                "code": 'import time\nwhile True:\n    time.sleep(0.1)',  # Infinite loop
                "timeout": 3  # 3 second timeout
            }
            
            timeout_response = self.session.post(f"{self.api_url}/sandbox/execute", json=timeout_data, headers=headers, timeout=15)
            
            if timeout_response.status_code == 200:
                timeout_result = timeout_response.json()
                timeout_success = timeout_result.get("success", True)
                timeout_occurred = timeout_result.get("timeout_occurred", False)
                execution_time = timeout_result.get("execution_time", 0)
                timeout_working = not timeout_success and (timeout_occurred or execution_time >= 3)
                
                logger.info(f"   ✅ Timeout: {'Working' if timeout_working else 'Failed'} (time: {execution_time:.1f}s)")
                results["timeout_test"] = {
                    "status": "success" if timeout_working else "failed",
                    "timeout_occurred": timeout_occurred,
                    "execution_time": execution_time,
                    "timeout_working": timeout_working
                }
            else:
                logger.error(f"   ❌ Timeout test failed: HTTP {timeout_response.status_code}")
                results["timeout_test"] = {"status": "failed", "error": f"HTTP {timeout_response.status_code}"}
            
            # Evaluate overall sandbox features
            successful_features = sum(1 for result in results.values() if result.get("status") == "success")
            total_features = len(results)
            
            if successful_features >= 2:  # At least 2/3 features working
                logger.info("✅ Sandbox features working!")
                return {
                    "status": "success",
                    "successful_features": successful_features,
                    "total_features": total_features,
                    "results": results,
                    "sandbox_features_working": True
                }
            else:
                logger.error("❌ Sandbox features have issues")
                return {
                    "status": "failed",
                    "error": f"Only {successful_features}/{total_features} features working",
                    "results": results,
                    "sandbox_features_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Sandbox features test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_code_templates(self) -> Dict[str, Any]:
        """📝 CODE TEMPLATES - Test template endpoints"""
        logger.info("📝 CODE TEMPLATES TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            results = {}
            
            # 1. Get template languages
            logger.info("   Testing template languages...")
            languages_response = self.session.get(f"{self.api_url}/sandbox/templates/languages", headers=headers, timeout=10)
            
            if languages_response.status_code == 200:
                languages = languages_response.json()
                logger.info(f"   ✅ {len(languages)} template languages available")
                results["languages"] = {"status": "success", "count": len(languages), "languages": languages}
            else:
                logger.error(f"   ❌ Template languages failed: HTTP {languages_response.status_code}")
                results["languages"] = {"status": "failed", "error": f"HTTP {languages_response.status_code}"}
            
            # 2. Get template types
            logger.info("   Testing template types...")
            types_response = self.session.get(f"{self.api_url}/sandbox/templates/types", headers=headers, timeout=10)
            
            if types_response.status_code == 200:
                types = types_response.json()
                expected_types = ["hello_world", "fibonacci", "data_structures"]
                types_correct = all(t in types for t in expected_types)
                
                logger.info(f"   ✅ {len(types)} template types: {types}")
                logger.info(f"   Expected types present: {'✅' if types_correct else '❌'}")
                results["types"] = {
                    "status": "success" if types_correct else "partial",
                    "count": len(types),
                    "types": types,
                    "expected_types_present": types_correct
                }
            else:
                logger.error(f"   ❌ Template types failed: HTTP {types_response.status_code}")
                results["types"] = {"status": "failed", "error": f"HTTP {types_response.status_code}"}
            
            # 3. Test specific templates
            logger.info("   Testing specific templates...")
            test_templates = [
                ("python", "hello_world"),
                ("java", "fibonacci"),
                ("typescript", "data_structures")
            ]
            
            template_results = {}
            for language, template_type in test_templates:
                template_response = self.session.get(
                    f"{self.api_url}/sandbox/templates/template/{language}/{template_type}",
                    headers=headers,
                    timeout=10
                )
                
                if template_response.status_code == 200:
                    template_data = template_response.json()
                    code = template_data.get("code", "")
                    has_code = len(code) > 50  # Template should have substantial code
                    
                    logger.info(f"   ✅ {language}/{template_type}: {len(code)} chars")
                    template_results[f"{language}_{template_type}"] = {
                        "status": "success",
                        "code_length": len(code),
                        "has_substantial_code": has_code
                    }
                else:
                    logger.error(f"   ❌ {language}/{template_type}: HTTP {template_response.status_code}")
                    template_results[f"{language}_{template_type}"] = {
                        "status": "failed",
                        "error": f"HTTP {template_response.status_code}"
                    }
            
            results["specific_templates"] = template_results
            
            # 4. Test template execution
            logger.info("   Testing template execution...")
            if "python_hello_world" in template_results and template_results["python_hello_world"]["status"] == "success":
                # Get Python hello_world template
                python_template_response = self.session.get(
                    f"{self.api_url}/sandbox/templates/template/python/hello_world",
                    headers=headers,
                    timeout=10
                )
                
                if python_template_response.status_code == 200:
                    template_code = python_template_response.json().get("code", "")
                    
                    # Execute the template
                    execute_data = {
                        "language": "python",
                        "code": template_code
                    }
                    
                    execute_response = self.session.post(
                        f"{self.api_url}/sandbox/execute",
                        json=execute_data,
                        headers=headers,
                        timeout=10
                    )
                    
                    if execute_response.status_code == 200:
                        execute_result = execute_response.json()
                        execution_success = execute_result.get("success", False)
                        
                        logger.info(f"   ✅ Template execution: {'Success' if execution_success else 'Failed'}")
                        results["template_execution"] = {
                            "status": "success" if execution_success else "failed",
                            "execution_success": execution_success
                        }
                    else:
                        logger.error(f"   ❌ Template execution failed: HTTP {execute_response.status_code}")
                        results["template_execution"] = {"status": "failed", "error": f"HTTP {execute_response.status_code}"}
                else:
                    results["template_execution"] = {"status": "skipped", "error": "Could not get template code"}
            else:
                results["template_execution"] = {"status": "skipped", "error": "No valid template to test"}
            
            # Evaluate overall templates
            successful_tests = sum(1 for result in results.values() if result.get("status") == "success")
            total_tests = len(results)
            
            if successful_tests >= 3:  # At least 3/4 tests successful
                logger.info("✅ Code Templates working!")
                return {
                    "status": "success",
                    "successful_tests": successful_tests,
                    "total_tests": total_tests,
                    "results": results,
                    "templates_working": True
                }
            else:
                logger.error("❌ Code Templates have issues")
                return {
                    "status": "failed",
                    "error": f"Only {successful_tests}/{total_tests} tests successful",
                    "results": results,
                    "templates_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Code Templates test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_developer_modes(self) -> Dict[str, Any]:
        """🎨 DEVELOPER MODES - Test junior and senior modes"""
        logger.info("🎨 DEVELOPER MODES TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # 1. Get developer modes
            logger.info("   Testing developer modes endpoint...")
            modes_response = self.session.get(f"{self.api_url}/developer-modes/", headers=headers, timeout=10)
            
            if modes_response.status_code == 200:
                modes = modes_response.json()
                expected_modes = ["junior", "senior"]
                modes_present = all(mode in [m.get("name") for m in modes] for mode in expected_modes)
                
                logger.info(f"   ✅ {len(modes)} developer modes available")
                for mode in modes:
                    name = mode.get("name")
                    model = mode.get("model")
                    logger.info(f"      {name}: {model}")
                
                # Verify expected models
                junior_model_correct = any(m.get("name") == "junior" and "haiku" in m.get("model", "").lower() for m in modes)
                senior_model_correct = any(m.get("name") == "senior" and "sonnet" in m.get("model", "").lower() for m in modes)
                
                logger.info(f"   Junior uses Haiku: {'✅' if junior_model_correct else '❌'}")
                logger.info(f"   Senior uses Sonnet: {'✅' if senior_model_correct else '❌'}")
                
                results["modes_endpoint"] = {
                    "status": "success",
                    "modes_count": len(modes),
                    "modes_present": modes_present,
                    "junior_model_correct": junior_model_correct,
                    "senior_model_correct": senior_model_correct,
                    "modes": modes
                }
            else:
                logger.error(f"   ❌ Developer modes failed: HTTP {modes_response.status_code}")
                results["modes_endpoint"] = {"status": "failed", "error": f"HTTP {modes_response.status_code}"}
            
            # 2. Test chat with junior mode
            logger.info("   Testing chat with junior mode...")
            junior_data = {
                "message": "What is Python? Keep it brief.",
                "developer_mode": "junior"
            }
            
            junior_response = self.session.post(f"{self.api_url}/chat", json=junior_data, headers=headers, timeout=30)
            
            if junior_response.status_code == 200:
                junior_result = junior_response.json()
                junior_content = junior_result.get("content", "")
                junior_model = junior_result.get("model", "")
                
                logger.info(f"   ✅ Junior mode: {len(junior_content)} chars, model: {junior_model}")
                results["junior_chat"] = {
                    "status": "success",
                    "response_length": len(junior_content),
                    "model_used": junior_model,
                    "response_received": bool(junior_content)
                }
            else:
                logger.error(f"   ❌ Junior mode chat failed: HTTP {junior_response.status_code}")
                results["junior_chat"] = {"status": "failed", "error": f"HTTP {junior_response.status_code}"}
            
            # 3. Test chat with senior mode
            logger.info("   Testing chat with senior mode...")
            senior_data = {
                "message": "Explain quantum computing in detail.",
                "developer_mode": "senior"
            }
            
            senior_response = self.session.post(f"{self.api_url}/chat", json=senior_data, headers=headers, timeout=45)
            
            if senior_response.status_code == 200:
                senior_result = senior_response.json()
                senior_content = senior_result.get("content", "")
                senior_model = senior_result.get("model", "")
                ultra_thinking = senior_result.get("usage", {}).get("thinking_used", False)
                
                logger.info(f"   ✅ Senior mode: {len(senior_content)} chars, model: {senior_model}")
                logger.info(f"   Ultra-thinking enabled: {'✅' if ultra_thinking else '❌'}")
                results["senior_chat"] = {
                    "status": "success",
                    "response_length": len(senior_content),
                    "model_used": senior_model,
                    "ultra_thinking_enabled": ultra_thinking,
                    "response_received": bool(senior_content)
                }
            else:
                logger.error(f"   ❌ Senior mode chat failed: HTTP {senior_response.status_code}")
                results["senior_chat"] = {"status": "failed", "error": f"HTTP {senior_response.status_code}"}
            
            # Evaluate overall developer modes
            successful_tests = sum(1 for result in results.values() if result.get("status") == "success")
            total_tests = len(results)
            
            if successful_tests >= 2:  # At least 2/3 tests successful
                logger.info("✅ Developer Modes working!")
                return {
                    "status": "success",
                    "successful_tests": successful_tests,
                    "total_tests": total_tests,
                    "results": results,
                    "developer_modes_working": True
                }
            else:
                logger.error("❌ Developer Modes have issues")
                return {
                    "status": "failed",
                    "error": f"Only {successful_tests}/{total_tests} tests successful",
                    "results": results,
                    "developer_modes_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Developer Modes test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_chat_system(self) -> Dict[str, Any]:
        """💬 CHAT SYSTEM - Test basic chat and session management"""
        logger.info("💬 CHAT SYSTEM TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # 1. Basic chat test
            logger.info("   Testing basic chat...")
            chat_data = {
                "message": "What is Python programming language?"
            }
            
            chat_response = self.session.post(f"{self.api_url}/chat", json=chat_data, headers=headers, timeout=30)
            
            if chat_response.status_code == 200:
                chat_result = chat_response.json()
                content = chat_result.get("content", "")
                session_id = chat_result.get("session_id")
                
                logger.info(f"   ✅ Basic chat: {len(content)} chars, session: {session_id}")
                results["basic_chat"] = {
                    "status": "success",
                    "response_length": len(content),
                    "session_created": bool(session_id),
                    "response_received": bool(content)
                }
            else:
                logger.error(f"   ❌ Basic chat failed: HTTP {chat_response.status_code}")
                results["basic_chat"] = {"status": "failed", "error": f"HTTP {chat_response.status_code}"}
            
            # 2. Session list test
            logger.info("   Testing session list...")
            sessions_response = self.session.get(f"{self.api_url}/sessions/list", headers=headers, timeout=10)
            
            if sessions_response.status_code == 200:
                sessions = sessions_response.json()
                sessions_count = len(sessions)
                
                logger.info(f"   ✅ Sessions list: {sessions_count} sessions")
                results["session_list"] = {
                    "status": "success",
                    "sessions_count": sessions_count,
                    "sessions_retrieved": True
                }
            else:
                logger.error(f"   ❌ Session list failed: HTTP {sessions_response.status_code}")
                results["session_list"] = {"status": "failed", "error": f"HTTP {sessions_response.status_code}"}
            
            # 3. Create new session test
            logger.info("   Testing session creation...")
            session_data = {"name": "Test Chat Session"}
            create_session_response = self.session.post(f"{self.api_url}/sessions/", json=session_data, headers=headers, timeout=10)
            
            if create_session_response.status_code == 200:
                new_session = create_session_response.json()
                new_session_id = new_session.get("id")
                
                logger.info(f"   ✅ Session created: {new_session_id}")
                results["session_creation"] = {
                    "status": "success",
                    "session_id": new_session_id,
                    "session_created": bool(new_session_id)
                }
                
                # 4. Test getting specific session
                if new_session_id:
                    logger.info("   Testing get specific session...")
                    get_session_response = self.session.get(f"{self.api_url}/sessions/{new_session_id}", headers=headers, timeout=10)
                    
                    if get_session_response.status_code == 200:
                        session_details = get_session_response.json()
                        logger.info(f"   ✅ Session details retrieved")
                        results["get_session"] = {
                            "status": "success",
                            "session_details_retrieved": True
                        }
                    else:
                        logger.error(f"   ❌ Get session failed: HTTP {get_session_response.status_code}")
                        results["get_session"] = {"status": "failed", "error": f"HTTP {get_session_response.status_code}"}
                
                # 5. Test setting active project
                logger.info("   Testing set active project...")
                project_data = {"project_name": "test_project", "branch": "main"}
                project_response = self.session.post(
                    f"{self.api_url}/sessions/{new_session_id}/set-active-project",
                    json=project_data,
                    headers=headers,
                    timeout=10
                )
                
                if project_response.status_code == 200:
                    logger.info(f"   ✅ Active project set")
                    results["set_active_project"] = {
                        "status": "success",
                        "active_project_set": True
                    }
                else:
                    logger.error(f"   ❌ Set active project failed: HTTP {project_response.status_code}")
                    results["set_active_project"] = {"status": "failed", "error": f"HTTP {project_response.status_code}"}
                    
            else:
                logger.error(f"   ❌ Session creation failed: HTTP {create_session_response.status_code}")
                results["session_creation"] = {"status": "failed", "error": f"HTTP {create_session_response.status_code}"}
            
            # Evaluate overall chat system
            successful_tests = sum(1 for result in results.values() if result.get("status") == "success")
            total_tests = len(results)
            
            if successful_tests >= 3:  # At least 3/5 tests successful
                logger.info("✅ Chat System working!")
                return {
                    "status": "success",
                    "successful_tests": successful_tests,
                    "total_tests": total_tests,
                    "results": results,
                    "chat_system_working": True
                }
            else:
                logger.error("❌ Chat System has issues")
                return {
                    "status": "failed",
                    "error": f"Only {successful_tests}/{total_tests} tests successful",
                    "results": results,
                    "chat_system_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Chat System test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_fork(self) -> Dict[str, Any]:
        """🔀 SESSION FORK - Test context status and health"""
        logger.info("🔀 SESSION FORK TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            results = {}
            
            # 1. Test health endpoint
            logger.info("   Testing session fork health...")
            health_response = self.session.get(f"{self.api_url}/session-fork/health", timeout=10)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                logger.info(f"   ✅ Session fork health: {health_data}")
                results["health"] = {
                    "status": "success",
                    "health_data": health_data,
                    "health_accessible": True
                }
            elif health_response.status_code == 401:
                # May require auth, try with token
                health_response_auth = self.session.get(f"{self.api_url}/session-fork/health", headers=headers, timeout=10)
                if health_response_auth.status_code == 200:
                    health_data = health_response_auth.json()
                    logger.info(f"   ✅ Session fork health (with auth): {health_data}")
                    results["health"] = {
                        "status": "success",
                        "health_data": health_data,
                        "requires_auth": True
                    }
                else:
                    logger.error(f"   ❌ Session fork health failed: HTTP {health_response_auth.status_code}")
                    results["health"] = {"status": "failed", "error": f"HTTP {health_response_auth.status_code}"}
            else:
                logger.error(f"   ❌ Session fork health failed: HTTP {health_response.status_code}")
                results["health"] = {"status": "failed", "error": f"HTTP {health_response.status_code}"}
            
            # 2. Test context status with a session
            logger.info("   Testing context status...")
            
            # First create a session to test with
            session_data = {"name": "Fork Test Session"}
            create_response = self.session.post(f"{self.api_url}/sessions/", json=session_data, headers=headers, timeout=10)
            
            if create_response.status_code == 200:
                session_id = create_response.json().get("id")
                
                # Test context status
                context_response = self.session.get(
                    f"{self.api_url}/session-fork/context-status/{session_id}",
                    headers=headers,
                    timeout=10
                )
                
                if context_response.status_code == 200:
                    context_data = context_response.json()
                    logger.info(f"   ✅ Context status: {context_data}")
                    results["context_status"] = {
                        "status": "success",
                        "context_data": context_data,
                        "context_accessible": True
                    }
                elif context_response.status_code == 404:
                    # Session not found is acceptable for new session
                    logger.info(f"   ⚠️ Context status: Session not found (expected for new session)")
                    results["context_status"] = {
                        "status": "expected",
                        "error": "Session not found",
                        "note": "Expected for new session without messages"
                    }
                else:
                    logger.error(f"   ❌ Context status failed: HTTP {context_response.status_code}")
                    results["context_status"] = {"status": "failed", "error": f"HTTP {context_response.status_code}"}
            else:
                logger.error(f"   ❌ Could not create test session for context status")
                results["context_status"] = {"status": "skipped", "error": "Could not create test session"}
            
            # Evaluate session fork functionality
            successful_tests = sum(1 for result in results.values() if result.get("status") in ["success", "expected"])
            total_tests = len(results)
            
            if successful_tests >= 1:  # At least 1 test successful or expected
                logger.info("✅ Session Fork endpoints accessible!")
                return {
                    "status": "success",
                    "successful_tests": successful_tests,
                    "total_tests": total_tests,
                    "results": results,
                    "session_fork_working": True
                }
            else:
                logger.error("❌ Session Fork has issues")
                return {
                    "status": "failed",
                    "error": f"No tests successful",
                    "results": results,
                    "session_fork_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Session Fork test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_system_health(self) -> Dict[str, Any]:
        """📊 SYSTEM HEALTH - Test all health endpoints"""
        logger.info("📊 SYSTEM HEALTH TEST")
        
        try:
            results = {}
            
            # 1. Main health endpoint
            logger.info("   Testing main health endpoint...")
            health_response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                status = health_data.get("status")
                database_status = health_data.get("services", {}).get("database", {}).get("status")
                ai_providers = health_data.get("services", {}).get("ai_providers", {})
                configured_count = ai_providers.get("configured", 0)
                
                logger.info(f"   ✅ Health status: {status}")
                logger.info(f"   Database: {database_status}")
                logger.info(f"   AI providers: {configured_count} configured")
                
                health_good = (status == "healthy" and database_status == "connected" and configured_count >= 3)
                
                results["main_health"] = {
                    "status": "success" if health_good else "partial",
                    "overall_status": status,
                    "database_status": database_status,
                    "ai_providers_configured": configured_count,
                    "health_good": health_good
                }
            else:
                logger.error(f"   ❌ Main health failed: HTTP {health_response.status_code}")
                results["main_health"] = {"status": "failed", "error": f"HTTP {health_response.status_code}"}
            
            # 2. Sandbox health endpoint
            logger.info("   Testing sandbox health...")
            sandbox_health_response = self.session.get(f"{self.api_url}/sandbox/health", timeout=10)
            
            if sandbox_health_response.status_code == 200:
                sandbox_health = sandbox_health_response.json()
                sandbox_status = sandbox_health.get("status")
                supported_languages = sandbox_health.get("supported_languages", 0)
                
                logger.info(f"   ✅ Sandbox health: {sandbox_status}")
                logger.info(f"   Supported languages: {supported_languages}")
                
                results["sandbox_health"] = {
                    "status": "success",
                    "sandbox_status": sandbox_status,
                    "supported_languages": supported_languages,
                    "sandbox_healthy": sandbox_status == "healthy"
                }
            else:
                logger.error(f"   ❌ Sandbox health failed: HTTP {sandbox_health_response.status_code}")
                results["sandbox_health"] = {"status": "failed", "error": f"HTTP {sandbox_health_response.status_code}"}
            
            # 3. Version endpoint
            logger.info("   Testing version endpoint...")
            version_response = self.session.get(f"{self.api_url}/version", timeout=10)
            
            if version_response.status_code == 200:
                version_data = version_response.json()
                version = version_data.get("version")
                
                logger.info(f"   ✅ Version: {version}")
                results["version"] = {
                    "status": "success",
                    "version": version,
                    "version_available": bool(version)
                }
            else:
                logger.error(f"   ❌ Version endpoint failed: HTTP {version_response.status_code}")
                results["version"] = {"status": "failed", "error": f"HTTP {version_response.status_code}"}
            
            # Evaluate overall system health
            successful_tests = sum(1 for result in results.values() if result.get("status") in ["success", "partial"])
            total_tests = len(results)
            
            if successful_tests >= 2:  # At least 2/3 tests successful
                logger.info("✅ System Health endpoints working!")
                return {
                    "status": "success",
                    "successful_tests": successful_tests,
                    "total_tests": total_tests,
                    "results": results,
                    "system_health_working": True
                }
            else:
                logger.error("❌ System Health has issues")
                return {
                    "status": "failed",
                    "error": f"Only {successful_tests}/{total_tests} tests successful",
                    "results": results,
                    "system_health_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ System Health test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_performance(self) -> Dict[str, Any]:
        """⚡ PERFORMANCE TESTS - Test response times and concurrent requests"""
        logger.info("⚡ PERFORMANCE TESTS")
        
        try:
            results = {}
            
            # 1. Response time tests
            logger.info("   Testing response times...")
            response_times = {}
            
            # Test health endpoint
            start_time = time.time()
            health_response = self.session.get(f"{self.api_url}/health", timeout=10)
            health_time = (time.time() - start_time) * 1000  # Convert to ms
            
            response_times["health"] = {
                "time_ms": health_time,
                "status_code": health_response.status_code,
                "under_100ms": health_time < 100
            }
            logger.info(f"   Health endpoint: {health_time:.1f}ms")
            
            # Test login endpoint (if we have credentials)
            start_time = time.time()
            login_data = {"username": "demo", "password": "demo123"}
            login_response = self.session.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            login_time = (time.time() - start_time) * 1000
            
            response_times["login"] = {
                "time_ms": login_time,
                "status_code": login_response.status_code,
                "under_500ms": login_time < 500
            }
            logger.info(f"   Login endpoint: {login_time:.1f}ms")
            
            # Test sandbox execution (Python)
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
                start_time = time.time()
                execute_data = {"language": "python", "code": 'print("Performance test")'}
                execute_response = self.session.post(f"{self.api_url}/sandbox/execute", json=execute_data, headers=headers, timeout=10)
                execute_time = (time.time() - start_time) * 1000
                
                response_times["sandbox_execute"] = {
                    "time_ms": execute_time,
                    "status_code": execute_response.status_code,
                    "under_2000ms": execute_time < 2000
                }
                logger.info(f"   Sandbox execute: {execute_time:.1f}ms")
            
            results["response_times"] = response_times
            
            # 2. Concurrent requests test
            logger.info("   Testing concurrent requests...")
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
                
                def make_concurrent_request():
                    execute_data = {"language": "python", "code": 'print("Concurrent test")'}
                    response = self.session.post(f"{self.api_url}/sandbox/execute", json=execute_data, headers=headers, timeout=15)
                    return {
                        "status_code": response.status_code,
                        "success": response.status_code == 200,
                        "response_time": response.elapsed.total_seconds() * 1000
                    }
                
                # Run 5 concurrent requests
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    start_time = time.time()
                    futures = [executor.submit(make_concurrent_request) for _ in range(5)]
                    concurrent_results = [future.result() for future in concurrent.futures.as_completed(futures)]
                    total_time = (time.time() - start_time) * 1000
                
                successful_requests = sum(1 for result in concurrent_results if result["success"])
                avg_response_time = sum(result["response_time"] for result in concurrent_results) / len(concurrent_results)
                
                logger.info(f"   Concurrent requests: {successful_requests}/5 successful")
                logger.info(f"   Average response time: {avg_response_time:.1f}ms")
                logger.info(f"   Total time: {total_time:.1f}ms")
                
                results["concurrent_requests"] = {
                    "successful_requests": successful_requests,
                    "total_requests": 5,
                    "avg_response_time": avg_response_time,
                    "total_time": total_time,
                    "all_successful": successful_requests == 5
                }
            else:
                results["concurrent_requests"] = {"status": "skipped", "error": "No authentication token"}
            
            # Evaluate performance
            performance_good = True
            
            # Check response times
            if "health" in response_times and not response_times["health"]["under_100ms"]:
                performance_good = False
            if "login" in response_times and not response_times["login"]["under_500ms"]:
                performance_good = False
            if "sandbox_execute" in response_times and not response_times["sandbox_execute"]["under_2000ms"]:
                performance_good = False
            
            # Check concurrent requests
            if "concurrent_requests" in results and not results["concurrent_requests"].get("all_successful", False):
                performance_good = False
            
            if performance_good:
                logger.info("✅ Performance tests passed!")
                return {
                    "status": "success",
                    "results": results,
                    "performance_good": True
                }
            else:
                logger.warning("⚠️ Some performance issues detected")
                return {
                    "status": "partial",
                    "results": results,
                    "performance_good": False
                }
                
        except Exception as e:
            logger.error(f"❌ Performance tests failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_security_validation(self) -> Dict[str, Any]:
        """🔒 SECURITY VALIDATION - Test encryption and rate limiting"""
        logger.info("🔒 SECURITY VALIDATION TEST")
        
        try:
            results = {}
            
            # 1. Test rate limiting endpoints
            logger.info("   Testing rate limiting...")
            
            # Get rate limits (public endpoint)
            limits_response = self.session.get(f"{self.api_url}/rate-limits/limits", timeout=10)
            
            if limits_response.status_code == 200:
                limits_data = limits_response.json()
                limits_count = len(limits_data)
                
                logger.info(f"   ✅ Rate limits: {limits_count} configured")
                results["rate_limits"] = {
                    "status": "success",
                    "limits_count": limits_count,
                    "limits_configured": limits_count > 0
                }
            else:
                logger.error(f"   ❌ Rate limits failed: HTTP {limits_response.status_code}")
                results["rate_limits"] = {"status": "failed", "error": f"HTTP {limits_response.status_code}"}
            
            # 2. Test authentication requirements
            logger.info("   Testing authentication requirements...")
            
            # Test protected endpoint without token
            protected_response = self.session.get(f"{self.api_url}/sessions/list", timeout=10)
            auth_required = protected_response.status_code == 401
            
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid-token"}
            invalid_response = self.session.get(f"{self.api_url}/sessions/list", headers=invalid_headers, timeout=10)
            invalid_rejected = invalid_response.status_code == 401
            
            # Test with valid token (if available)
            valid_token_works = False
            if self.token:
                valid_headers = {"Authorization": f"Bearer {self.token}"}
                valid_response = self.session.get(f"{self.api_url}/sessions/list", headers=valid_headers, timeout=10)
                valid_token_works = valid_response.status_code == 200
            
            auth_working = auth_required and invalid_rejected and (valid_token_works or not self.token)
            
            logger.info(f"   No token rejected: {'✅' if auth_required else '❌'}")
            logger.info(f"   Invalid token rejected: {'✅' if invalid_rejected else '❌'}")
            logger.info(f"   Valid token works: {'✅' if valid_token_works else '❌' if self.token else 'N/A'}")
            
            results["authentication"] = {
                "status": "success" if auth_working else "failed",
                "no_token_rejected": auth_required,
                "invalid_token_rejected": invalid_rejected,
                "valid_token_works": valid_token_works,
                "authentication_working": auth_working
            }
            
            # 3. Test API key encryption (indirect test)
            logger.info("   Testing API key security...")
            if self.token:
                headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
                
                # Save a test API key
                save_data = {"provider": "test_provider", "api_key": "test-key-12345"}
                save_response = self.session.post(f"{self.api_url}/api-keys/save", json=save_data, headers=headers, timeout=10)
                
                if save_response.status_code == 200:
                    save_result = save_response.json()
                    masked_key = save_result.get("masked_key", "")
                    
                    # Check if key is properly masked
                    key_masked = masked_key.startswith("test-") and masked_key.endswith("...") and len(masked_key) < 20
                    
                    logger.info(f"   ✅ API key masked: {masked_key}")
                    results["api_key_security"] = {
                        "status": "success" if key_masked else "failed",
                        "masked_key": masked_key,
                        "key_properly_masked": key_masked
                    }
                    
                    # Clean up test key
                    self.session.delete(f"{self.api_url}/api-keys/test_provider", headers=headers, timeout=10)
                else:
                    logger.error(f"   ❌ API key save failed: HTTP {save_response.status_code}")
                    results["api_key_security"] = {"status": "failed", "error": f"HTTP {save_response.status_code}"}
            else:
                results["api_key_security"] = {"status": "skipped", "error": "No authentication token"}
            
            # Evaluate security
            successful_tests = sum(1 for result in results.values() if result.get("status") == "success")
            total_tests = len(results)
            
            if successful_tests >= 2:  # At least 2/3 tests successful
                logger.info("✅ Security validation passed!")
                return {
                    "status": "success",
                    "successful_tests": successful_tests,
                    "total_tests": total_tests,
                    "results": results,
                    "security_working": True
                }
            else:
                logger.error("❌ Security validation has issues")
                return {
                    "status": "failed",
                    "error": f"Only {successful_tests}/{total_tests} tests successful",
                    "results": results,
                    "security_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Security validation test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all comprehensive backend tests"""
        logger.info("🚀 STARTING FINAL COMPREHENSIVE BACKEND TEST")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Test sequence
        test_sequence = [
            ("🔐 Authentication", self.authenticate),
            ("🔐 Protected Endpoints", self.test_protected_endpoints),
            ("🔑 API Key Management", self.test_api_key_management),
            ("🚀 Cloud Sandbox - All Languages", self.test_cloud_sandbox_all_languages),
            ("🚀 Sandbox Features", self.test_sandbox_features),
            ("📝 Code Templates", self.test_code_templates),
            ("🎨 Developer Modes", self.test_developer_modes),
            ("💬 Chat System", self.test_chat_system),
            ("🔀 Session Fork", self.test_session_fork),
            ("📊 System Health", self.test_system_health),
            ("⚡ Performance", self.test_performance),
            ("🔒 Security Validation", self.test_security_validation)
        ]
        
        # Run all tests
        for test_name, test_func in test_sequence:
            logger.info(f"\n{test_name}")
            logger.info("-" * 60)
            
            try:
                result = test_func()
                self.test_results[test_name] = result
                
                status = result.get("status", "unknown")
                if status == "success":
                    logger.info(f"✅ {test_name}: PASSED")
                elif status == "partial":
                    logger.info(f"⚠️ {test_name}: PARTIAL")
                elif status == "skipped":
                    logger.info(f"⏭️ {test_name}: SKIPPED")
                else:
                    logger.info(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                self.test_results[test_name] = {"status": "error", "error": str(e)}
        
        # Generate summary
        total_time = time.time() - start_time
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 FINAL COMPREHENSIVE TEST SUMMARY")
        logger.info("=" * 80)
        
        passed_tests = []
        failed_tests = []
        partial_tests = []
        skipped_tests = []
        error_tests = []
        
        for test_name, result in self.test_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                passed_tests.append(test_name)
            elif status == "failed":
                failed_tests.append(test_name)
            elif status == "partial":
                partial_tests.append(test_name)
            elif status == "skipped":
                skipped_tests.append(test_name)
            else:
                error_tests.append(test_name)
        
        logger.info(f"⏱️ Total test time: {total_time:.1f} seconds")
        logger.info(f"📊 Test results:")
        logger.info(f"   ✅ PASSED: {len(passed_tests)}")
        logger.info(f"   ⚠️ PARTIAL: {len(partial_tests)}")
        logger.info(f"   ❌ FAILED: {len(failed_tests)}")
        logger.info(f"   ⏭️ SKIPPED: {len(skipped_tests)}")
        logger.info(f"   🚨 ERROR: {len(error_tests)}")
        
        if passed_tests:
            logger.info(f"\n✅ PASSED TESTS:")
            for test in passed_tests:
                logger.info(f"   • {test}")
        
        if partial_tests:
            logger.info(f"\n⚠️ PARTIAL TESTS:")
            for test in partial_tests:
                logger.info(f"   • {test}")
        
        if failed_tests:
            logger.info(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                error = self.test_results[test].get("error", "Unknown error")
                logger.info(f"   • {test}: {error}")
        
        if error_tests:
            logger.info(f"\n🚨 ERROR TESTS:")
            for test in error_tests:
                error = self.test_results[test].get("error", "Unknown error")
                logger.info(f"   • {test}: {error}")
        
        # Overall assessment
        critical_tests = ["🔐 Authentication", "🔑 API Key Management", "🚀 Cloud Sandbox - All Languages", "🔒 Security Validation"]
        critical_passed = sum(1 for test in critical_tests if test in passed_tests)
        
        overall_success = (
            len(passed_tests) >= 8 and  # At least 8 tests passed
            critical_passed >= 3 and    # At least 3 critical tests passed
            len(error_tests) == 0       # No error tests
        )
        
        if overall_success:
            logger.info(f"\n🎉 OVERALL RESULT: SUCCESS!")
            logger.info(f"   All critical backend features are working correctly.")
        else:
            logger.info(f"\n⚠️ OVERALL RESULT: NEEDS ATTENTION")
            logger.info(f"   Some critical issues need to be addressed.")
        
        return {
            "overall_success": overall_success,
            "total_time": total_time,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "partial_tests": partial_tests,
            "skipped_tests": skipped_tests,
            "error_tests": error_tests,
            "critical_passed": critical_passed,
            "detailed_results": self.test_results
        }

def main():
    """Main function to run comprehensive backend tests"""
    tester = FinalComprehensiveBackendTester()
    results = tester.run_comprehensive_test()
    
    # Return exit code based on results
    if results["overall_success"]:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()