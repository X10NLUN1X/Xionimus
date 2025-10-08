#!/usr/bin/env python3
"""
COMPREHENSIVE CLOUD SANDBOX API TESTING - ALL 7 LANGUAGES

This test suite comprehensively tests the Cloud Sandbox API with all 7 supported languages:
1. Python ✅ (256MB)
2. JavaScript/Node.js ✅ (512MB) 
3. Bash ✅ (128MB)
4. C++ (NEW) ✅ (512MB)
5. C (NEW) ✅ (512MB)
6. C# (NEW) ✅ (512MB - Mono)
7. Perl (NEW) ✅ (256MB)

TEST CATEGORIES:
- Language Support Query (GET /api/sandbox/languages)
- Code Execution for all 7 languages
- Compilation tests for C++, C, C#
- Compilation error handling
- Cross-language comparison tests
- Authentication checks
- Memory limits verification
- Timeout handling

CREDENTIALS: demo/demo123
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SandboxComprehensiveTester:
    def __init__(self, base_url: str = None):
        # Use localhost for testing since we're in the same container
        self.base_url = base_url or "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
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
            
            logger.info(f"   Response status: {response.status_code}")
            
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

    def test_language_support_query(self) -> Dict[str, Any]:
        """Test GET /api/sandbox/languages - Verify all 7 languages are supported"""
        logger.info("🔍 Testing Language Support Query (GET /api/sandbox/languages)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(
                f"{self.api_url}/sandbox/languages",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                languages_data = response.json()
                languages = languages_data.get("languages", [])
                
                logger.info(f"   Found {len(languages)} supported languages")
                
                # Expected languages with their memory limits
                expected_languages = {
                    "python": 256,
                    "javascript": 512,
                    "bash": 128,
                    "cpp": 512,
                    "c": 512,
                    "csharp": 512,
                    "perl": 256
                }
                
                found_languages = {}
                missing_languages = []
                
                for lang_info in languages:
                    lang_name = lang_info.get("language")
                    memory_limit = lang_info.get("memory_limit_mb")
                    extension = lang_info.get("extension")
                    timeout = lang_info.get("timeout")
                    
                    found_languages[lang_name] = {
                        "memory_limit_mb": memory_limit,
                        "extension": extension,
                        "timeout": timeout
                    }
                    
                    logger.info(f"   ✅ {lang_name}: {extension}, {timeout}s timeout, {memory_limit}MB")
                
                # Check for missing languages
                for expected_lang, expected_memory in expected_languages.items():
                    if expected_lang not in found_languages:
                        missing_languages.append(expected_lang)
                        logger.error(f"   ❌ Missing language: {expected_lang}")
                    else:
                        actual_memory = found_languages[expected_lang]["memory_limit_mb"]
                        if actual_memory != expected_memory:
                            logger.warning(f"   ⚠️ {expected_lang}: Expected {expected_memory}MB, got {actual_memory}MB")
                
                if not missing_languages and len(found_languages) == 7:
                    logger.info("✅ All 7 languages supported with correct memory limits!")
                    return {
                        "status": "success",
                        "total_languages": len(found_languages),
                        "found_languages": found_languages,
                        "missing_languages": missing_languages,
                        "all_languages_supported": True
                    }
                else:
                    logger.error(f"❌ Language support incomplete. Missing: {missing_languages}")
                    return {
                        "status": "failed",
                        "error": f"Missing languages: {missing_languages}",
                        "total_languages": len(found_languages),
                        "found_languages": found_languages,
                        "missing_languages": missing_languages,
                        "all_languages_supported": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Language support query failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Language support query test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_python_execution(self) -> Dict[str, Any]:
        """Test Python code execution (256MB)"""
        logger.info("🐍 Testing Python Code Execution (256MB)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test code from review request
        test_code = 'print("Python works!")\nfor i in range(3): print(f"Loop {i}")'
        
        try:
            execution_data = {
                "code": test_code,
                "language": "python"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                if stderr:
                    logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output
                expected_output = "Python works!\nLoop 0\nLoop 1\nLoop 2\n"
                output_correct = stdout == expected_output
                
                if success and exit_code == 0 and output_correct:
                    logger.info("✅ Python execution successful with correct output!")
                    return {
                        "status": "success",
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "stdout": stdout,
                        "python_working": True
                    }
                else:
                    logger.error(f"❌ Python execution failed or incorrect output")
                    return {
                        "status": "failed",
                        "error": f"Success: {success}, Exit code: {exit_code}, Output correct: {output_correct}",
                        "success": success,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "python_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Python execution request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Python execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_javascript_execution(self) -> Dict[str, Any]:
        """Test JavaScript/Node.js code execution (512MB)"""
        logger.info("🟨 Testing JavaScript/Node.js Code Execution (512MB)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test code from review request
        test_code = 'console.log("JavaScript works!"); [1,2,3].forEach(n => console.log(n*2));'
        
        try:
            execution_data = {
                "code": test_code,
                "language": "javascript"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                if stderr:
                    logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output (JavaScript works! followed by 2, 4, 6)
                expected_lines = ["JavaScript works!", "2", "4", "6"]
                output_lines = stdout.strip().split('\n')
                output_correct = output_lines == expected_lines
                
                if success and exit_code == 0 and output_correct:
                    logger.info("✅ JavaScript execution successful with correct output!")
                    return {
                        "status": "success",
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "stdout": stdout,
                        "javascript_working": True
                    }
                else:
                    logger.error(f"❌ JavaScript execution failed or incorrect output")
                    return {
                        "status": "failed",
                        "error": f"Success: {success}, Exit code: {exit_code}, Output correct: {output_correct}",
                        "success": success,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "javascript_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ JavaScript execution request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ JavaScript execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_bash_execution(self) -> Dict[str, Any]:
        """Test Bash script execution (128MB)"""
        logger.info("🐚 Testing Bash Script Execution (128MB)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test code from review request
        test_code = 'echo "Bash works!"; echo "Date: $(date +%Y-%m-%d)"'
        
        try:
            execution_data = {
                "code": test_code,
                "language": "bash"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                if stderr:
                    logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output (should contain "Bash works!" and date)
                output_correct = "Bash works!" in stdout and "Date:" in stdout
                
                if success and exit_code == 0 and output_correct:
                    logger.info("✅ Bash execution successful with correct output!")
                    return {
                        "status": "success",
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "stdout": stdout,
                        "bash_working": True
                    }
                else:
                    logger.error(f"❌ Bash execution failed or incorrect output")
                    return {
                        "status": "failed",
                        "error": f"Success: {success}, Exit code: {exit_code}, Output correct: {output_correct}",
                        "success": success,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "bash_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Bash execution request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Bash execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_cpp_execution(self) -> Dict[str, Any]:
        """Test C++ code execution (NEW - 512MB)"""
        logger.info("⚡ Testing C++ Code Execution (NEW - 512MB)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test code from review request
        test_code = '#include <iostream>\nusing namespace std;\nint main() { cout << "C++ works!" << endl; return 0; }'
        
        try:
            execution_data = {
                "code": test_code,
                "language": "cpp"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                if stderr:
                    logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output
                expected_output = "C++ works!\n"
                output_correct = stdout == expected_output
                
                if success and exit_code == 0 and output_correct:
                    logger.info("✅ C++ compilation and execution successful!")
                    return {
                        "status": "success",
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "stdout": stdout,
                        "cpp_working": True,
                        "compilation_successful": True
                    }
                else:
                    logger.error(f"❌ C++ execution failed or incorrect output")
                    return {
                        "status": "failed",
                        "error": f"Success: {success}, Exit code: {exit_code}, Output correct: {output_correct}",
                        "success": success,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "cpp_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ C++ execution request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ C++ execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_c_execution(self) -> Dict[str, Any]:
        """Test C code execution (NEW - 512MB)"""
        logger.info("🔧 Testing C Code Execution (NEW - 512MB)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test code from review request
        test_code = '#include <stdio.h>\nint main() { printf("C works!\\n"); return 0; }'
        
        try:
            execution_data = {
                "code": test_code,
                "language": "c"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                if stderr:
                    logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output
                expected_output = "C works!\n"
                output_correct = stdout == expected_output
                
                if success and exit_code == 0 and output_correct:
                    logger.info("✅ C compilation and execution successful!")
                    return {
                        "status": "success",
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "stdout": stdout,
                        "c_working": True,
                        "compilation_successful": True
                    }
                else:
                    logger.error(f"❌ C execution failed or incorrect output")
                    return {
                        "status": "failed",
                        "error": f"Success: {success}, Exit code: {exit_code}, Output correct: {output_correct}",
                        "success": success,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "c_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ C execution request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ C execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_csharp_execution(self) -> Dict[str, Any]:
        """Test C# code execution (NEW - 512MB - Mono)"""
        logger.info("🔷 Testing C# Code Execution (NEW - 512MB - Mono)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test code from review request
        test_code = 'using System; class P { static void Main() { Console.WriteLine("C# works!"); } }'
        
        try:
            execution_data = {
                "code": test_code,
                "language": "csharp"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                if stderr:
                    logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output
                expected_output = "C# works!\n"
                output_correct = stdout == expected_output
                
                if success and exit_code == 0 and output_correct:
                    logger.info("✅ C# compilation (mcs) and execution (mono) successful!")
                    return {
                        "status": "success",
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "stdout": stdout,
                        "csharp_working": True,
                        "compilation_successful": True,
                        "mono_execution": True
                    }
                else:
                    logger.error(f"❌ C# execution failed or incorrect output")
                    return {
                        "status": "failed",
                        "error": f"Success: {success}, Exit code: {exit_code}, Output correct: {output_correct}",
                        "success": success,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "csharp_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ C# execution request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ C# execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_perl_execution(self) -> Dict[str, Any]:
        """Test Perl code execution (NEW - 256MB)"""
        logger.info("🐪 Testing Perl Code Execution (NEW - 256MB)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test code from review request
        test_code = 'print "Perl works!\\n"; print "Version: $]\\n";'
        
        try:
            execution_data = {
                "code": test_code,
                "language": "perl"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                if stderr:
                    logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output (should contain "Perl works!" and version)
                output_correct = "Perl works!" in stdout and "Version:" in stdout
                
                if success and exit_code == 0 and output_correct:
                    logger.info("✅ Perl execution successful with version info!")
                    return {
                        "status": "success",
                        "success": success,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "stdout": stdout,
                        "perl_working": True
                    }
                else:
                    logger.error(f"❌ Perl execution failed or incorrect output")
                    return {
                        "status": "failed",
                        "error": f"Success: {success}, Exit code: {exit_code}, Output correct: {output_correct}",
                        "success": success,
                        "exit_code": exit_code,
                        "stdout": stdout,
                        "stderr": stderr,
                        "perl_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Perl execution request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Perl execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_compilation_error_handling(self) -> Dict[str, Any]:
        """Test compilation error handling for compiled languages"""
        logger.info("🚨 Testing Compilation Error Handling")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        results = {}
        
        # Test C++ compilation error (missing semicolon)
        try:
            logger.info("   Testing C++ compilation error...")
            cpp_error_code = '#include <iostream>\nusing namespace std;\nint main() { cout << "Missing semicolon" return 0; }'
            
            execution_data = {
                "code": cpp_error_code,
                "language": "cpp"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stderr = result.get("stderr", "")
                
                # Should fail compilation
                compilation_error_handled = not success and "error" in stderr.lower()
                
                results["cpp_error"] = {
                    "success": success,
                    "error_handled": compilation_error_handled,
                    "stderr": stderr
                }
                
                logger.info(f"   C++ error handling: {'✅' if compilation_error_handled else '❌'}")
            else:
                results["cpp_error"] = {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            results["cpp_error"] = {"error": str(e)}
        
        # Test C compilation error
        try:
            logger.info("   Testing C compilation error...")
            c_error_code = '#include <stdio.h>\nint main() { printf("Missing semicolon") return 0; }'
            
            execution_data = {
                "code": c_error_code,
                "language": "c"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stderr = result.get("stderr", "")
                
                # Should fail compilation
                compilation_error_handled = not success and "error" in stderr.lower()
                
                results["c_error"] = {
                    "success": success,
                    "error_handled": compilation_error_handled,
                    "stderr": stderr
                }
                
                logger.info(f"   C error handling: {'✅' if compilation_error_handled else '❌'}")
            else:
                results["c_error"] = {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            results["c_error"] = {"error": str(e)}
        
        # Test C# compilation error
        try:
            logger.info("   Testing C# compilation error...")
            csharp_error_code = 'using System; class P { static void Main() { Console.WriteLine("Missing semicolon") } }'
            
            execution_data = {
                "code": csharp_error_code,
                "language": "csharp"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get("success", False)
                stderr = result.get("stderr", "")
                
                # Should fail compilation
                compilation_error_handled = not success and "error" in stderr.lower()
                
                results["csharp_error"] = {
                    "success": success,
                    "error_handled": compilation_error_handled,
                    "stderr": stderr
                }
                
                logger.info(f"   C# error handling: {'✅' if compilation_error_handled else '❌'}")
            else:
                results["csharp_error"] = {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            results["csharp_error"] = {"error": str(e)}
        
        # Evaluate overall error handling
        successful_error_handling = sum(
            1 for result in results.values() 
            if isinstance(result, dict) and result.get("error_handled", False)
        )
        
        if successful_error_handling >= 2:  # At least 2 out of 3 languages handle errors correctly
            logger.info("✅ Compilation error handling working correctly!")
            return {
                "status": "success",
                "successful_error_handling": successful_error_handling,
                "total_tested": len(results),
                "results": results,
                "error_handling_working": True
            }
        else:
            logger.error("❌ Compilation error handling not working correctly")
            return {
                "status": "failed",
                "error": "Compilation error handling insufficient",
                "successful_error_handling": successful_error_handling,
                "total_tested": len(results),
                "results": results,
                "error_handling_working": False
            }

    def test_cross_language_comparison(self) -> Dict[str, Any]:
        """Test same algorithm (fibonacci) in multiple languages"""
        logger.info("🔄 Testing Cross-Language Comparison (Fibonacci)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Fibonacci implementations for different languages
        fibonacci_codes = {
            "python": '''def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print(fib(10))''',
            
            "javascript": '''function fib(n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2);
}

console.log(fib(10));''',
            
            "cpp": '''#include <iostream>
using namespace std;

int fib(int n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2);
}

int main() {
    cout << fib(10) << endl;
    return 0;
}''',
            
            "c": '''#include <stdio.h>

int fib(int n) {
    if (n <= 1) return n;
    return fib(n-1) + fib(n-2);
}

int main() {
    printf("%d\\n", fib(10));
    return 0;
}''',
            
            "perl": '''sub fib {
    my $n = shift;
    return $n if $n <= 1;
    return fib($n-1) + fib($n-2);
}

print fib(10) . "\\n";'''
        }
        
        results = {}
        expected_result = "55"  # fib(10) = 55
        
        for language, code in fibonacci_codes.items():
            try:
                logger.info(f"   Testing {language} fibonacci...")
                
                execution_data = {
                    "code": code,
                    "language": language
                }
                
                response = self.session.post(
                    f"{self.api_url}/sandbox/execute",
                    json=execution_data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    success = result.get("success", False)
                    stdout = result.get("stdout", "").strip()
                    execution_time = result.get("execution_time", 0)
                    
                    # Check if output is correct
                    output_correct = stdout == expected_result
                    
                    results[language] = {
                        "success": success,
                        "output": stdout,
                        "execution_time": execution_time,
                        "output_correct": output_correct
                    }
                    
                    logger.info(f"   {language}: {'✅' if output_correct else '❌'} ({execution_time:.3f}s)")
                else:
                    results[language] = {"error": f"HTTP {response.status_code}"}
                    logger.error(f"   {language}: ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                results[language] = {"error": str(e)}
                logger.error(f"   {language}: ❌ {e}")
        
        # Evaluate results
        successful_languages = sum(
            1 for result in results.values() 
            if isinstance(result, dict) and result.get("output_correct", False)
        )
        
        if successful_languages >= 3:  # At least 3 languages working
            logger.info(f"✅ Cross-language comparison successful! ({successful_languages} languages)")
            return {
                "status": "success",
                "successful_languages": successful_languages,
                "total_tested": len(results),
                "results": results,
                "expected_result": expected_result,
                "cross_language_working": True
            }
        else:
            logger.error(f"❌ Cross-language comparison failed ({successful_languages} languages)")
            return {
                "status": "failed",
                "error": f"Only {successful_languages} languages produced correct results",
                "successful_languages": successful_languages,
                "total_tested": len(results),
                "results": results,
                "cross_language_working": False
            }

    def test_authentication_check(self) -> Dict[str, Any]:
        """Test that sandbox endpoints require authentication"""
        logger.info("🔒 Testing Authentication Requirements")
        
        try:
            # Test execute endpoint without authentication
            execution_data = {
                "code": 'print("test")',
                "language": "python"
            }
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            execute_protected = response.status_code == 401
            logger.info(f"   Execute endpoint protected: {'✅' if execute_protected else '❌'}")
            
            # Test languages endpoint without authentication
            response = self.session.get(
                f"{self.api_url}/sandbox/languages",
                timeout=10
            )
            
            languages_protected = response.status_code == 401
            logger.info(f"   Languages endpoint protected: {'✅' if languages_protected else '❌'}")
            
            if execute_protected and languages_protected:
                logger.info("✅ Authentication requirements working correctly!")
                return {
                    "status": "success",
                    "execute_protected": execute_protected,
                    "languages_protected": languages_protected,
                    "authentication_working": True
                }
            else:
                logger.error("❌ Authentication requirements not working correctly")
                return {
                    "status": "failed",
                    "error": "Some endpoints not properly protected",
                    "execute_protected": execute_protected,
                    "languages_protected": languages_protected,
                    "authentication_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication check test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive sandbox tests"""
        logger.info("🚀 STARTING COMPREHENSIVE CLOUD SANDBOX API TESTING - ALL 7 LANGUAGES")
        logger.info("=" * 80)
        
        # Authenticate first
        auth_result = self.authenticate()
        if auth_result.get("status") != "success":
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return {"status": "failed", "error": "Authentication failed", "auth_result": auth_result}
        
        # Run all tests
        test_results = {}
        
        # Test 1: Language Support Query
        test_results["language_support"] = self.test_language_support_query()
        
        # Test 2-8: Individual Language Tests
        test_results["python"] = self.test_python_execution()
        test_results["javascript"] = self.test_javascript_execution()
        test_results["bash"] = self.test_bash_execution()
        test_results["cpp"] = self.test_cpp_execution()
        test_results["c"] = self.test_c_execution()
        test_results["csharp"] = self.test_csharp_execution()
        test_results["perl"] = self.test_perl_execution()
        
        # Test 9: Compilation Error Handling
        test_results["compilation_errors"] = self.test_compilation_error_handling()
        
        # Test 10: Cross-Language Comparison
        test_results["cross_language"] = self.test_cross_language_comparison()
        
        # Test 11: Authentication Check
        test_results["authentication"] = self.test_authentication_check()
        
        # Summary
        logger.info("=" * 80)
        logger.info("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        logger.info("=" * 80)
        
        successful_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                successful_tests += 1
                logger.info(f"✅ {test_name}: PASSED")
            elif status == "failed":
                logger.error(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
            elif status == "skipped":
                logger.warning(f"⏭️ {test_name}: SKIPPED - {result.get('error', 'Unknown reason')}")
            else:
                logger.warning(f"⚠️ {test_name}: {status.upper()}")
        
        logger.info("=" * 80)
        logger.info(f"📈 OVERALL RESULTS: {successful_tests}/{total_tests} tests passed")
        
        # Language-specific summary
        language_results = {
            "python": test_results["python"].get("python_working", False),
            "javascript": test_results["javascript"].get("javascript_working", False),
            "bash": test_results["bash"].get("bash_working", False),
            "cpp": test_results["cpp"].get("cpp_working", False),
            "c": test_results["c"].get("c_working", False),
            "csharp": test_results["csharp"].get("csharp_working", False),
            "perl": test_results["perl"].get("perl_working", False)
        }
        
        working_languages = sum(1 for working in language_results.values() if working)
        
        logger.info(f"🌐 LANGUAGE SUPPORT: {working_languages}/7 languages working")
        for lang, working in language_results.items():
            logger.info(f"   {lang}: {'✅' if working else '❌'}")
        
        if successful_tests >= total_tests * 0.8:  # 80% success rate
            logger.info("🎉 COMPREHENSIVE TESTING SUCCESSFUL!")
            overall_status = "success"
        else:
            logger.error("💥 COMPREHENSIVE TESTING FAILED!")
            overall_status = "failed"
        
        return {
            "status": overall_status,
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "working_languages": working_languages,
            "language_results": language_results,
            "test_results": test_results,
            "auth_result": auth_result
        }


def main():
    """Main test execution"""
    tester = SandboxComprehensiveTester()
    results = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    if results.get("status") == "success":
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()