#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM TEST - ALL FEATURES
Based on review request for complete testing of all implemented features

TEST CREDENTIALS:
- Username: demo
- Password: demo123

FOCUS AREAS:
1. 🔐 API KEY MANAGEMENT (NEW - PRIORITY HIGH)
2. 🎯 CLOUD SANDBOX - ALL 12 LANGUAGES  
3. 📝 CODE TEMPLATES
4. 🎨 DEVELOPER MODES
5. 💬 CHAT SYSTEM
6. 🔒 AUTHENTICATION
7. 📊 SYSTEM HEALTH
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveSystemTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        
    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with demo/demo123 credentials"""
        logger.info("🔐 Authenticating with demo user (demo/demo123)")
        
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
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                logger.info("✅ Authentication successful!")
                logger.info(f"   User ID: {self.user_info['user_id']}")
                logger.info(f"   Username: {self.user_info['username']}")
                
                return {"status": "success", "token": self.token, "user_info": self.user_info}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {"status": "failed", "error": error_detail}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.token:
            return {"Content-Type": "application/json"}
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def test_api_key_management(self) -> Dict[str, Any]:
        """🔐 1. API KEY MANAGEMENT (NEW - PRIORITY HIGH)"""
        logger.info("🔐 Testing API Key Management System")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = self.get_auth_headers()
        results = {}
        
        try:
            # Test 1: Save API Keys
            logger.info("   Testing Save API Keys...")
            
            # Save Anthropic Key
            anthropic_data = {
                "provider": "anthropic",
                "api_key": "sk-ant-test-key-12345"
            }
            
            response = self.session.post(
                f"{self.api_url}/api-keys/save",
                json=anthropic_data,
                headers=headers,
                timeout=10
            )
            
            results["save_anthropic"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                masked_key = data.get("masked_key", "")
                results["save_anthropic"]["masked_key"] = masked_key
                logger.info(f"   ✅ Anthropic key saved, masked: {masked_key}")
            else:
                logger.error(f"   ❌ Anthropic key save failed: {response.status_code}")
            
            # Save OpenAI Key
            openai_data = {
                "provider": "openai", 
                "api_key": "sk-proj-test-key-67890"
            }
            
            response = self.session.post(
                f"{self.api_url}/api-keys/save",
                json=openai_data,
                headers=headers,
                timeout=10
            )
            
            results["save_openai"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                masked_key = data.get("masked_key", "")
                results["save_openai"]["masked_key"] = masked_key
                logger.info(f"   ✅ OpenAI key saved, masked: {masked_key}")
            else:
                logger.error(f"   ❌ OpenAI key save failed: {response.status_code}")
            
            # Save Perplexity Key
            perplexity_data = {
                "provider": "perplexity",
                "api_key": "pplx-test-key-abcdef"
            }
            
            response = self.session.post(
                f"{self.api_url}/api-keys/save",
                json=perplexity_data,
                headers=headers,
                timeout=10
            )
            
            results["save_perplexity"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                data = response.json()
                masked_key = data.get("masked_key", "")
                results["save_perplexity"]["masked_key"] = masked_key
                logger.info(f"   ✅ Perplexity key saved, masked: {masked_key}")
            else:
                logger.error(f"   ❌ Perplexity key save failed: {response.status_code}")
            
            # Test 2: List API Keys
            logger.info("   Testing List API Keys...")
            
            response = self.session.get(
                f"{self.api_url}/api-keys/list",
                headers=headers,
                timeout=10
            )
            
            results["list_keys"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                response_data = response.json()
                keys_data = response_data.get("api_keys", [])
                results["list_keys"]["keys"] = keys_data
                logger.info(f"   ✅ Listed {len(keys_data)} API keys")
                for key_info in keys_data:
                    logger.info(f"      {key_info.get('provider')}: {key_info.get('masked_key')}")
            else:
                logger.error(f"   ❌ List keys failed: {response.status_code}")
            
            # Test 3: Status Check
            logger.info("   Testing Status Check...")
            
            response = self.session.get(
                f"{self.api_url}/api-keys/status",
                headers=headers,
                timeout=10
            )
            
            results["status_check"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                status_data = response.json()
                results["status_check"]["status"] = status_data
                configured_count = status_data.get("configured_providers", 0)
                logger.info(f"   ✅ Status check: {configured_count} providers configured")
            else:
                logger.error(f"   ❌ Status check failed: {response.status_code}")
            
            # Test 4: Update Key (save existing)
            logger.info("   Testing Update Key...")
            
            update_data = {
                "provider": "openai",
                "api_key": "sk-proj-updated-key-99999"
            }
            
            response = self.session.post(
                f"{self.api_url}/api-keys/save",
                json=update_data,
                headers=headers,
                timeout=10
            )
            
            results["update_key"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                logger.info("   ✅ OpenAI key updated successfully")
            else:
                logger.error(f"   ❌ Key update failed: {response.status_code}")
            
            # Test 5: Delete Key
            logger.info("   Testing Delete Key...")
            
            response = self.session.delete(
                f"{self.api_url}/api-keys/openai",
                headers=headers,
                timeout=10
            )
            
            results["delete_key"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                logger.info("   ✅ OpenAI key deleted successfully")
            else:
                logger.error(f"   ❌ Key deletion failed: {response.status_code}")
            
            # Test 6: Connection Test
            logger.info("   Testing Connection Test...")
            
            for provider in ["anthropic", "perplexity"]:  # Skip openai since we deleted it
                response = self.session.post(
                    f"{self.api_url}/api-keys/test-connection",
                    json={"provider": provider},
                    headers=headers,
                    timeout=15
                )
                
                results[f"test_connection_{provider}"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    test_result = response.json()
                    success = test_result.get("success", False)
                    logger.info(f"   {'✅' if success else '⚠️'} {provider} connection test: {success}")
                else:
                    logger.error(f"   ❌ {provider} connection test failed: {response.status_code}")
            
            # Calculate overall success
            successful_tests = sum(1 for result in results.values() if result.get("success", False))
            total_tests = len(results)
            
            logger.info(f"🔐 API Key Management: {successful_tests}/{total_tests} tests passed")
            
            return {
                "status": "success" if successful_tests >= total_tests * 0.8 else "partial",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ API Key Management test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_cloud_sandbox_all_languages(self) -> Dict[str, Any]:
        """🎯 2. CLOUD SANDBOX - ALL 12 LANGUAGES"""
        logger.info("🎯 Testing Cloud Sandbox - ALL 12 LANGUAGES")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = self.get_auth_headers()
        results = {}
        
        # Define all 12 languages with test code
        languages = {
            "python": {
                "code": "print('Hello World')\nfor i in range(3):\n    print(f'Fibonacci: {i}')",
                "expected_output": "Hello World"
            },
            "javascript": {
                "code": "console.log('Hello World');\nconst arr = [1,2,3];\nconsole.log(arr.map(x => x*2));",
                "expected_output": "Hello World"
            },
            "typescript": {
                "code": "interface Person { name: string; }\nconst person: Person = { name: 'Test' };\nconsole.log('Hello World', person.name);",
                "expected_output": "Hello World"
            },
            "bash": {
                "code": "echo 'Hello World'\necho 'Array operations'\nfor i in 1 2 3; do echo $i; done",
                "expected_output": "Hello World"
            },
            "php": {
                "code": "<?php\necho 'Hello World\\n';\nfor($i = 0; $i < 3; $i++) {\n    echo 'Loop: ' . $i . '\\n';\n}",
                "expected_output": "Hello World"
            },
            "ruby": {
                "code": "puts 'Hello World'\n[1,2,3].each { |x| puts \"Number: #{x}\" }",
                "expected_output": "Hello World"
            },
            "perl": {
                "code": "print \"Hello World\\n\";\nmy @arr = (1,2,3);\nforeach my $num (@arr) { print \"Number: $num\\n\"; }",
                "expected_output": "Hello World"
            },
            "cpp": {
                "code": "#include <iostream>\n#include <vector>\nusing namespace std;\nint main() {\n    cout << \"Hello World\" << endl;\n    vector<int> v = {1,2,3};\n    for(int x : v) cout << x << \" \";\n    return 0;\n}",
                "expected_output": "Hello World"
            },
            "c": {
                "code": "#include <stdio.h>\nint main() {\n    printf(\"Hello World\\n\");\n    int arr[] = {1,2,3};\n    for(int i=0; i<3; i++) printf(\"%d \", arr[i]);\n    return 0;\n}",
                "expected_output": "Hello World"
            },
            "csharp": {
                "code": "using System;\nusing System.Linq;\nclass Program {\n    static void Main() {\n        Console.WriteLine(\"Hello World\");\n        int[] arr = {1,2,3};\n        Console.WriteLine(string.Join(\", \", arr.Select(x => x*2)));\n    }\n}",
                "expected_output": "Hello World"
            },
            "java": {
                "code": "import java.util.*;\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello World\");\n        List<Integer> list = Arrays.asList(1,2,3);\n        list.forEach(System.out::println);\n    }\n}",
                "expected_output": "Hello World"
            },
            "go": {
                "code": "package main\nimport \"fmt\"\nfunc main() {\n    fmt.Println(\"Hello World\")\n    arr := []int{1,2,3}\n    for _, v := range arr {\n        fmt.Printf(\"%d \", v)\n    }\n}",
                "expected_output": "Hello World"
            }
        }
        
        try:
            # First, get supported languages
            logger.info("   Getting supported languages...")
            
            response = self.session.get(
                f"{self.api_url}/sandbox/languages",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {"status": "failed", "error": f"Languages endpoint failed: {response.status_code}"}
            
            response_data = response.json()
            supported_languages = response_data.get("languages", [])
            logger.info(f"   Supported languages: {len(supported_languages)}")
            
            # Test each language
            for lang_name, lang_config in languages.items():
                logger.info(f"   Testing {lang_name}...")
                
                execute_data = {
                    "language": lang_name,
                    "code": lang_config["code"]
                }
                
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
                    stderr = result.get("stderr", "")
                    exit_code = result.get("exit_code", -1)
                    execution_time = result.get("execution_time", 0)
                    
                    # Check if expected output is present
                    output_correct = lang_config["expected_output"] in stdout
                    
                    results[lang_name] = {
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "output_correct": output_correct,
                        "stdout_length": len(stdout),
                        "stderr_length": len(stderr),
                        "status": "success" if success and exit_code == 0 and output_correct else "failed"
                    }
                    
                    status_icon = "✅" if success and exit_code == 0 and output_correct else "❌"
                    logger.info(f"      {status_icon} {lang_name}: success={success}, exit_code={exit_code}, time={execution_time:.3f}s")
                    
                    if not output_correct:
                        logger.warning(f"         Expected '{lang_config['expected_output']}' in output")
                        
                else:
                    results[lang_name] = {
                        "status": "failed",
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    }
                    logger.error(f"      ❌ {lang_name}: HTTP {response.status_code}")
            
            # Calculate success rate
            successful_languages = sum(1 for result in results.values() if result.get("status") == "success")
            total_languages = len(results)
            
            logger.info(f"🎯 Cloud Sandbox: {successful_languages}/{total_languages} languages working")
            
            return {
                "status": "success" if successful_languages >= 10 else "partial",  # At least 10/12 languages
                "successful_languages": successful_languages,
                "total_languages": total_languages,
                "results": results,
                "supported_languages": supported_languages
            }
            
        except Exception as e:
            logger.error(f"❌ Cloud Sandbox test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_code_templates(self) -> Dict[str, Any]:
        """📝 3. CODE TEMPLATES"""
        logger.info("📝 Testing Code Templates")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = self.get_auth_headers()
        results = {}
        
        try:
            # Test 1: Get template languages
            logger.info("   Testing template languages...")
            
            response = self.session.get(
                f"{self.api_url}/sandbox/templates/languages",
                headers=headers,
                timeout=10
            )
            
            results["languages"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                languages = response.json()
                results["languages"]["count"] = len(languages)
                logger.info(f"   ✅ Template languages: {len(languages)}")
            else:
                logger.error(f"   ❌ Template languages failed: {response.status_code}")
                return {"status": "failed", "error": "Template languages endpoint failed"}
            
            # Test 2: Get template types
            logger.info("   Testing template types...")
            
            response = self.session.get(
                f"{self.api_url}/sandbox/templates/types",
                headers=headers,
                timeout=10
            )
            
            results["types"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                types = response.json()
                results["types"]["types"] = types
                logger.info(f"   ✅ Template types: {types}")
            else:
                logger.error(f"   ❌ Template types failed: {response.status_code}")
            
            # Test 3: Get specific templates
            logger.info("   Testing specific templates...")
            
            test_templates = [
                ("python", "hello_world"),
                ("java", "fibonacci"),
                ("typescript", "data_structures"),
                ("cpp", "hello_world"),
                ("javascript", "fibonacci")
            ]
            
            for language, template_type in test_templates:
                response = self.session.get(
                    f"{self.api_url}/sandbox/templates/template/{language}/{template_type}",
                    headers=headers,
                    timeout=10
                )
                
                template_key = f"{language}_{template_type}"
                results[template_key] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    template_data = response.json()
                    code = template_data.get("code", "")
                    results[template_key]["code_length"] = len(code)
                    logger.info(f"   ✅ {language}/{template_type}: {len(code)} chars")
                else:
                    logger.error(f"   ❌ {language}/{template_type}: HTTP {response.status_code}")
            
            # Calculate success rate
            successful_tests = sum(1 for result in results.values() if result.get("success", False))
            total_tests = len(results)
            
            logger.info(f"📝 Code Templates: {successful_tests}/{total_tests} tests passed")
            
            return {
                "status": "success" if successful_tests >= total_tests * 0.8 else "partial",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Code Templates test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_developer_modes(self) -> Dict[str, Any]:
        """🎨 4. DEVELOPER MODES"""
        logger.info("🎨 Testing Developer Modes")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = self.get_auth_headers()
        results = {}
        
        try:
            # Test 1: Junior Developer Mode
            logger.info("   Testing Junior Developer Mode...")
            
            junior_data = {
                "message": "Explain what Python is",
                "developer_mode": "junior"
            }
            
            response = self.session.post(
                f"{self.api_url}/chat",
                json=junior_data,
                headers=headers,
                timeout=30
            )
            
            results["junior_mode"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                result = response.json()
                model = result.get("model", "")
                results["junior_mode"]["model"] = model
                results["junior_mode"]["is_haiku"] = "haiku" in model.lower()
                logger.info(f"   ✅ Junior mode: {model}")
            else:
                logger.error(f"   ❌ Junior mode failed: {response.status_code}")
            
            # Test 2: Senior Developer Mode
            logger.info("   Testing Senior Developer Mode...")
            
            senior_data = {
                "message": "Explain advanced Python concepts",
                "developer_mode": "senior"
            }
            
            response = self.session.post(
                f"{self.api_url}/chat",
                json=senior_data,
                headers=headers,
                timeout=30
            )
            
            results["senior_mode"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                result = response.json()
                model = result.get("model", "")
                ultra_thinking = result.get("usage", {}).get("thinking_used", False)
                results["senior_mode"]["model"] = model
                results["senior_mode"]["is_sonnet"] = "sonnet" in model.lower()
                results["senior_mode"]["ultra_thinking"] = ultra_thinking
                logger.info(f"   ✅ Senior mode: {model}, ultra-thinking: {ultra_thinking}")
            else:
                logger.error(f"   ❌ Senior mode failed: {response.status_code}")
            
            # Calculate success rate
            successful_tests = sum(1 for result in results.values() if result.get("success", False))
            total_tests = len(results)
            
            logger.info(f"🎨 Developer Modes: {successful_tests}/{total_tests} tests passed")
            
            return {
                "status": "success" if successful_tests == total_tests else "partial",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Developer Modes test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_chat_system(self) -> Dict[str, Any]:
        """💬 5. CHAT SYSTEM"""
        logger.info("💬 Testing Chat System")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = self.get_auth_headers()
        results = {}
        
        try:
            # Test 1: Basic Chat
            logger.info("   Testing basic chat...")
            
            chat_data = {
                "message": "Hello, this is a test message"
            }
            
            response = self.session.post(
                f"{self.api_url}/chat",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            results["basic_chat"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "")
                session_id = result.get("session_id", "")
                results["basic_chat"]["has_content"] = bool(content)
                results["basic_chat"]["has_session"] = bool(session_id)
                logger.info(f"   ✅ Basic chat: {len(content)} chars, session: {session_id[:8]}...")
            else:
                logger.error(f"   ❌ Basic chat failed: {response.status_code}")
            
            # Test 2: Session Management
            logger.info("   Testing session management...")
            
            # Create session
            session_data = {"name": "Test Chat Session"}
            response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            results["session_create"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                session = response.json()
                session_id = session.get("id")
                results["session_create"]["session_id"] = session_id
                logger.info(f"   ✅ Session created: {session_id}")
                
                # List sessions
                response = self.session.get(
                    f"{self.api_url}/sessions/list",
                    headers=headers,
                    timeout=10
                )
                
                results["session_list"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    sessions = response.json()
                    results["session_list"]["count"] = len(sessions)
                    logger.info(f"   ✅ Sessions listed: {len(sessions)}")
                else:
                    logger.error(f"   ❌ Session list failed: {response.status_code}")
            else:
                logger.error(f"   ❌ Session create failed: {response.status_code}")
            
            # Calculate success rate
            successful_tests = sum(1 for result in results.values() if result.get("success", False))
            total_tests = len(results)
            
            logger.info(f"💬 Chat System: {successful_tests}/{total_tests} tests passed")
            
            return {
                "status": "success" if successful_tests >= total_tests * 0.8 else "partial",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Chat System test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_authentication(self) -> Dict[str, Any]:
        """🔒 6. AUTHENTICATION"""
        logger.info("🔒 Testing Authentication")
        
        results = {}
        
        try:
            # Test 1: Valid Login
            logger.info("   Testing valid login...")
            
            auth_result = self.authenticate()
            results["valid_login"] = {
                "success": auth_result.get("status") == "success",
                "token_received": bool(auth_result.get("token")),
                "user_info": auth_result.get("user_info")
            }
            
            if results["valid_login"]["success"]:
                logger.info("   ✅ Valid login successful")
            else:
                logger.error("   ❌ Valid login failed")
            
            # Test 2: Invalid Login
            logger.info("   Testing invalid login...")
            
            invalid_data = {
                "username": "invalid",
                "password": "wrong"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=invalid_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            results["invalid_login"] = {
                "status_code": response.status_code,
                "correctly_rejected": response.status_code == 401
            }
            
            if response.status_code == 401:
                logger.info("   ✅ Invalid login correctly rejected")
            else:
                logger.error(f"   ❌ Invalid login not rejected: {response.status_code}")
            
            # Test 3: Protected Endpoint Access
            logger.info("   Testing protected endpoint access...")
            
            if self.token:
                headers = self.get_auth_headers()
                response = self.session.get(
                    f"{self.api_url}/sessions/list",
                    headers=headers,
                    timeout=10
                )
                
                results["protected_access"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    logger.info("   ✅ Protected endpoint accessible with token")
                else:
                    logger.error(f"   ❌ Protected endpoint failed: {response.status_code}")
            else:
                results["protected_access"] = {"success": False, "error": "No token"}
            
            # Test 4: Protected Endpoint Without Token
            logger.info("   Testing protected endpoint without token...")
            
            response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            results["no_token_access"] = {
                "status_code": response.status_code,
                "correctly_blocked": response.status_code == 401
            }
            
            if response.status_code == 401:
                logger.info("   ✅ Protected endpoint correctly blocked without token")
            else:
                logger.error(f"   ❌ Protected endpoint not blocked: {response.status_code}")
            
            # Calculate success rate
            successful_tests = sum(1 for result in results.values() if result.get("success", False) or result.get("correctly_rejected", False) or result.get("correctly_blocked", False))
            total_tests = len(results)
            
            logger.info(f"🔒 Authentication: {successful_tests}/{total_tests} tests passed")
            
            return {
                "status": "success" if successful_tests == total_tests else "partial",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_system_health(self) -> Dict[str, Any]:
        """📊 7. SYSTEM HEALTH"""
        logger.info("📊 Testing System Health")
        
        results = {}
        
        try:
            # Test 1: Health Endpoint
            logger.info("   Testing health endpoint...")
            
            response = self.session.get(
                f"{self.api_url}/health",
                timeout=10
            )
            
            results["health_endpoint"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                health_data = response.json()
                results["health_endpoint"]["data"] = health_data
                status = health_data.get("status", "unknown")
                logger.info(f"   ✅ Health endpoint: {status}")
            else:
                logger.error(f"   ❌ Health endpoint failed: {response.status_code}")
            
            # Test 2: Sandbox Health
            logger.info("   Testing sandbox health...")
            
            if self.token:
                headers = self.get_auth_headers()
                response = self.session.get(
                    f"{self.api_url}/sandbox/health",
                    headers=headers,
                    timeout=10
                )
                
                results["sandbox_health"] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    sandbox_data = response.json()
                    results["sandbox_health"]["data"] = sandbox_data
                    logger.info("   ✅ Sandbox health check passed")
                else:
                    logger.error(f"   ❌ Sandbox health failed: {response.status_code}")
            else:
                results["sandbox_health"] = {"success": False, "error": "No token"}
            
            # Test 3: Version Endpoint
            logger.info("   Testing version endpoint...")
            
            response = self.session.get(
                f"{self.api_url}/version",
                timeout=10
            )
            
            results["version_endpoint"] = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                version_data = response.json()
                results["version_endpoint"]["data"] = version_data
                version = version_data.get("version", "unknown")
                logger.info(f"   ✅ Version endpoint: {version}")
            else:
                logger.error(f"   ❌ Version endpoint failed: {response.status_code}")
            
            # Calculate success rate
            successful_tests = sum(1 for result in results.values() if result.get("success", False))
            total_tests = len(results)
            
            logger.info(f"📊 System Health: {successful_tests}/{total_tests} tests passed")
            
            return {
                "status": "success" if successful_tests >= total_tests * 0.8 else "partial",
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ System Health test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive System Test - ALL FEATURES")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Authenticate first
        auth_result = self.authenticate()
        if auth_result.get("status") != "success":
            return {
                "status": "failed",
                "error": "Authentication failed",
                "auth_result": auth_result
            }
        
        # Run all tests
        test_results = {}
        
        test_functions = [
            ("API Key Management", self.test_api_key_management),
            ("Cloud Sandbox", self.test_cloud_sandbox_all_languages),
            ("Code Templates", self.test_code_templates),
            ("Developer Modes", self.test_developer_modes),
            ("Chat System", self.test_chat_system),
            ("Authentication", self.test_authentication),
            ("System Health", self.test_system_health)
        ]
        
        for test_name, test_func in test_functions:
            logger.info(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                test_results[test_name] = result
                
                status = result.get("status", "unknown")
                if status == "success":
                    logger.info(f"✅ {test_name}: PASSED")
                elif status == "partial":
                    logger.info(f"⚠️ {test_name}: PARTIAL")
                else:
                    logger.info(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                test_results[test_name] = {"status": "error", "error": str(e)}
        
        # Calculate overall results
        total_time = time.time() - start_time
        
        successful_categories = sum(1 for result in test_results.values() if result.get("status") == "success")
        partial_categories = sum(1 for result in test_results.values() if result.get("status") == "partial")
        failed_categories = sum(1 for result in test_results.values() if result.get("status") in ["failed", "error"])
        total_categories = len(test_results)
        
        logger.info("\n" + "="*60)
        logger.info("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ Successful: {successful_categories}/{total_categories}")
        logger.info(f"⚠️ Partial: {partial_categories}/{total_categories}")
        logger.info(f"❌ Failed: {failed_categories}/{total_categories}")
        logger.info(f"⏱️ Total time: {total_time:.2f}s")
        
        # Detailed results
        for test_name, result in test_results.items():
            status = result.get("status", "unknown")
            icon = "✅" if status == "success" else "⚠️" if status == "partial" else "❌"
            
            if "successful_tests" in result and "total_tests" in result:
                logger.info(f"{icon} {test_name}: {result['successful_tests']}/{result['total_tests']} tests passed")
            else:
                logger.info(f"{icon} {test_name}: {status}")
        
        overall_status = "success" if successful_categories >= total_categories * 0.8 else "partial"
        
        return {
            "status": overall_status,
            "total_time": total_time,
            "successful_categories": successful_categories,
            "partial_categories": partial_categories,
            "failed_categories": failed_categories,
            "total_categories": total_categories,
            "test_results": test_results,
            "summary": f"{successful_categories}/{total_categories} categories passed"
        }

def main():
    """Main test execution"""
    tester = ComprehensiveSystemTester()
    result = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if result.get("status") == "success":
        exit(0)
    elif result.get("status") == "partial":
        exit(1)
    else:
        exit(2)

if __name__ == "__main__":
    main()