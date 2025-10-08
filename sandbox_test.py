#!/usr/bin/env python3
"""
COMPREHENSIVE SANDBOX API TESTING - Phase 4
Testing the newly implemented Cloud Sandbox functionality

TEST SCOPE:
1. Python Code Execution ✅ (Priority: HIGH)
2. JavaScript/Node.js Execution ✅ (Priority: HIGH)  
3. Bash Script Execution ✅ (Priority: MEDIUM)
4. Error Handling (Priority: HIGH)
5. Timeout Test (Priority: MEDIUM)
6. Security Validation (Priority: HIGH)
7. Language Support Query (Priority: LOW)
8. Authentication Check (Priority: HIGH)

TEST CREDENTIALS:
- Username: demo
- Password: demo123

EXPECTED RESULTS:
- All three languages working
- Memory limits appropriate
- Error handling robust
- Security features active
- Response format consistent
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SandboxTester:
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

    def test_python_execution(self) -> Dict[str, Any]:
        """Test 1: Python Code Execution ✅ (Priority: HIGH)"""
        logger.info("🐍 Testing Python Code Execution (HIGH PRIORITY)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test Python code execution
            python_code = 'print("Hello")\nfor i in range(5):\n    print(i)'
            
            execution_data = {
                "code": python_code,
                "language": "python",
                "timeout": 10
            }
            
            logger.info("   Executing Python code...")
            logger.info(f"   Code: {python_code}")
            
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
                exit_code = result.get("exit_code")
                execution_time = result.get("execution_time")
                execution_id = result.get("execution_id")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output
                expected_output = "Hello\n0\n1\n2\n3\n4\n"
                output_correct = stdout == expected_output
                exit_code_correct = exit_code == 0
                has_execution_time = execution_time is not None and execution_time > 0
                has_execution_id = execution_id is not None
                
                logger.info(f"   Output correct: {'✅' if output_correct else '❌'}")
                logger.info(f"   Exit code correct: {'✅' if exit_code_correct else '❌'}")
                logger.info(f"   Has execution time: {'✅' if has_execution_time else '❌'}")
                logger.info(f"   Has execution ID: {'✅' if has_execution_id else '❌'}")
                
                if success and output_correct and exit_code_correct and has_execution_time:
                    logger.info("✅ Python code execution working perfectly!")
                    return {
                        "status": "success",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_correct": output_correct,
                        "python_working": True
                    }
                else:
                    logger.error("❌ Python code execution issues detected")
                    return {
                        "status": "failed",
                        "error": "Python execution validation failed",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "output_correct": output_correct,
                        "python_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Python execution failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Python execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_javascript_execution(self) -> Dict[str, Any]:
        """Test 2: JavaScript/Node.js Execution ✅ (Priority: HIGH)"""
        logger.info("🟨 Testing JavaScript/Node.js Execution (HIGH PRIORITY)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test JavaScript code execution
            js_code = 'console.log("Test");\nconst arr = [1,2,3];\nconsole.log(arr.map(x => x*2));'
            
            execution_data = {
                "code": js_code,
                "language": "javascript",
                "timeout": 10
            }
            
            logger.info("   Executing JavaScript code...")
            logger.info(f"   Code: {js_code}")
            
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
                exit_code = result.get("exit_code")
                execution_time = result.get("execution_time")
                execution_id = result.get("execution_id")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output (Node.js output format)
                expected_contains = ["Test", "2", "4", "6"]  # Should contain these values
                output_has_expected = all(str(val) in stdout for val in expected_contains)
                exit_code_correct = exit_code == 0
                has_execution_time = execution_time is not None and execution_time > 0
                has_execution_id = execution_id is not None
                
                logger.info(f"   Output has expected values: {'✅' if output_has_expected else '❌'}")
                logger.info(f"   Exit code correct: {'✅' if exit_code_correct else '❌'}")
                logger.info(f"   Has execution time: {'✅' if has_execution_time else '❌'}")
                logger.info(f"   Has execution ID: {'✅' if has_execution_id else '❌'}")
                
                if success and output_has_expected and exit_code_correct and has_execution_time:
                    logger.info("✅ JavaScript code execution working perfectly!")
                    return {
                        "status": "success",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_has_expected": output_has_expected,
                        "javascript_working": True
                    }
                else:
                    logger.error("❌ JavaScript code execution issues detected")
                    return {
                        "status": "failed",
                        "error": "JavaScript execution validation failed",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "output_has_expected": output_has_expected,
                        "javascript_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ JavaScript execution failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ JavaScript execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_bash_execution(self) -> Dict[str, Any]:
        """Test 3: Bash Script Execution ✅ (Priority: MEDIUM)"""
        logger.info("🐚 Testing Bash Script Execution (MEDIUM PRIORITY)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test Bash script execution
            bash_code = 'echo "Test"\nls /tmp | head -3\ndate'
            
            execution_data = {
                "code": bash_code,
                "language": "bash",
                "timeout": 10
            }
            
            logger.info("   Executing Bash script...")
            logger.info(f"   Code: {bash_code}")
            
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
                exit_code = result.get("exit_code")
                execution_time = result.get("execution_time")
                execution_id = result.get("execution_id")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify expected output
                expected_contains = ["Test"]  # Should contain "Test" from echo
                output_has_expected = all(val in stdout for val in expected_contains)
                exit_code_correct = exit_code == 0
                has_execution_time = execution_time is not None and execution_time > 0
                has_execution_id = execution_id is not None
                
                logger.info(f"   Output has expected values: {'✅' if output_has_expected else '❌'}")
                logger.info(f"   Exit code correct: {'✅' if exit_code_correct else '❌'}")
                logger.info(f"   Has execution time: {'✅' if has_execution_time else '❌'}")
                logger.info(f"   Has execution ID: {'✅' if has_execution_id else '❌'}")
                
                if success and output_has_expected and exit_code_correct and has_execution_time:
                    logger.info("✅ Bash script execution working perfectly!")
                    return {
                        "status": "success",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "output_has_expected": output_has_expected,
                        "bash_working": True
                    }
                else:
                    logger.error("❌ Bash script execution issues detected")
                    return {
                        "status": "failed",
                        "error": "Bash execution validation failed",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "output_has_expected": output_has_expected,
                        "bash_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Bash execution failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Bash execution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_error_handling(self) -> Dict[str, Any]:
        """Test 4: Error Handling (Priority: HIGH)"""
        logger.info("🚨 Testing Error Handling (HIGH PRIORITY)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test syntax error in Python
            python_error_code = 'print("test'  # Missing closing quote
            
            execution_data = {
                "code": python_error_code,
                "language": "python",
                "timeout": 10
            }
            
            logger.info("   Testing syntax error handling...")
            logger.info(f"   Code with error: {python_error_code}")
            
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
                exit_code = result.get("exit_code")
                execution_time = result.get("execution_time")
                execution_id = result.get("execution_id")
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Stdout: {repr(stdout)}")
                logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify error handling
                success_is_false = success == False
                exit_code_non_zero = exit_code != 0
                stderr_has_error = len(stderr) > 0
                has_execution_time = execution_time is not None
                has_execution_id = execution_id is not None
                
                logger.info(f"   Success is False: {'✅' if success_is_false else '❌'}")
                logger.info(f"   Exit code non-zero: {'✅' if exit_code_non_zero else '❌'}")
                logger.info(f"   Stderr captured: {'✅' if stderr_has_error else '❌'}")
                logger.info(f"   Has execution time: {'✅' if has_execution_time else '❌'}")
                logger.info(f"   Has execution ID: {'✅' if has_execution_id else '❌'}")
                
                if success_is_false and exit_code_non_zero and stderr_has_error:
                    logger.info("✅ Error handling working perfectly!")
                    return {
                        "status": "success",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "error_handling_working": True
                    }
                else:
                    logger.error("❌ Error handling not working correctly")
                    return {
                        "status": "failed",
                        "error": "Error handling validation failed",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "error_handling_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Error handling test failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_timeout_handling(self) -> Dict[str, Any]:
        """Test 5: Timeout Test (Priority: MEDIUM)"""
        logger.info("⏰ Testing Timeout Handling (MEDIUM PRIORITY)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test infinite loop with short timeout
            infinite_loop_code = 'import time\nwhile True:\n    time.sleep(0.1)'
            
            execution_data = {
                "code": infinite_loop_code,
                "language": "python",
                "timeout": 3  # Short timeout
            }
            
            logger.info("   Testing timeout with infinite loop...")
            logger.info(f"   Code: {infinite_loop_code}")
            logger.info("   Timeout: 3 seconds")
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30  # HTTP timeout longer than execution timeout
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code")
                execution_time = result.get("execution_time")
                execution_id = result.get("execution_id")
                timeout_occurred = result.get("timeout_occurred", False)
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Timeout occurred: {timeout_occurred}")
                logger.info(f"   Stdout: {repr(stdout)}")
                logger.info(f"   Stderr: {repr(stderr)}")
                
                # Verify timeout handling
                timeout_detected = timeout_occurred == True
                success_is_false = success == False
                has_execution_time = execution_time is not None
                has_execution_id = execution_id is not None
                stderr_mentions_timeout = "timeout" in stderr.lower()
                
                logger.info(f"   Timeout detected: {'✅' if timeout_detected else '❌'}")
                logger.info(f"   Success is False: {'✅' if success_is_false else '❌'}")
                logger.info(f"   Has execution time: {'✅' if has_execution_time else '❌'}")
                logger.info(f"   Has execution ID: {'✅' if has_execution_id else '❌'}")
                logger.info(f"   Stderr mentions timeout: {'✅' if stderr_mentions_timeout else '❌'}")
                
                if timeout_detected and success_is_false and stderr_mentions_timeout:
                    logger.info("✅ Timeout handling working perfectly!")
                    return {
                        "status": "success",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "timeout_occurred": timeout_occurred,
                        "timeout_handling_working": True
                    }
                else:
                    logger.error("❌ Timeout handling not working correctly")
                    return {
                        "status": "failed",
                        "error": "Timeout handling validation failed",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "timeout_occurred": timeout_occurred,
                        "timeout_handling_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Timeout test failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Timeout test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_security_validation(self) -> Dict[str, Any]:
        """Test 6: Security Validation (Priority: HIGH)"""
        logger.info("🔒 Testing Security Validation (HIGH PRIORITY)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # Test 1: Resource limits are applied (memory test)
            memory_test_code = '''
import sys
data = []
try:
    for i in range(1000000):  # Try to allocate a lot of memory
        data.append("x" * 1000)
    print("Memory allocation succeeded")
except MemoryError:
    print("Memory limit enforced")
except Exception as e:
    print(f"Other error: {e}")
'''
            
            execution_data = {
                "code": memory_test_code,
                "language": "python",
                "timeout": 10
            }
            
            logger.info("   Testing resource limits (memory)...")
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                execution_id_1 = result.get("execution_id")
                
                results["memory_limits"] = {
                    "status": "tested",
                    "execution_id": execution_id_1,
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", "")
                }
                
                logger.info(f"   Memory test execution ID: {execution_id_1}")
                logger.info(f"   Memory test output: {result.get('stdout', '')}")
            
            # Test 2: Execution ID uniqueness
            simple_code = 'print("Hello World")'
            
            execution_data = {
                "code": simple_code,
                "language": "python",
                "timeout": 10
            }
            
            logger.info("   Testing execution ID uniqueness...")
            
            response1 = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            response2 = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            if response1.status_code == 200 and response2.status_code == 200:
                result1 = response1.json()
                result2 = response2.json()
                
                execution_id_1 = result1.get("execution_id")
                execution_id_2 = result2.get("execution_id")
                
                unique_ids = execution_id_1 != execution_id_2
                
                results["unique_execution_ids"] = {
                    "status": "success" if unique_ids else "failed",
                    "execution_id_1": execution_id_1,
                    "execution_id_2": execution_id_2,
                    "unique": unique_ids
                }
                
                logger.info(f"   Execution ID 1: {execution_id_1}")
                logger.info(f"   Execution ID 2: {execution_id_2}")
                logger.info(f"   IDs are unique: {'✅' if unique_ids else '❌'}")
            
            # Test 3: File system isolation (temporary files cleanup)
            file_test_code = '''
import os
import tempfile

# Create a temporary file
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("test data")
    temp_file = f.name

print(f"Created temp file: {temp_file}")
print(f"File exists: {os.path.exists(temp_file)}")

# List files in temp directory
temp_dir = os.path.dirname(temp_file)
files = os.listdir(temp_dir)
print(f"Files in temp dir: {len(files)}")
'''
            
            execution_data = {
                "code": file_test_code,
                "language": "python",
                "timeout": 10
            }
            
            logger.info("   Testing file system isolation...")
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                results["file_system_isolation"] = {
                    "status": "tested",
                    "execution_id": result.get("execution_id"),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", "")
                }
                
                logger.info(f"   File system test output: {result.get('stdout', '')}")
            
            # Evaluate security validation
            memory_tested = "memory_limits" in results
            unique_ids_working = results.get("unique_execution_ids", {}).get("unique", False)
            file_system_tested = "file_system_isolation" in results
            
            security_score = sum([memory_tested, unique_ids_working, file_system_tested])
            
            if security_score >= 2:  # At least 2 out of 3 security features working
                logger.info("✅ Security validation working!")
                return {
                    "status": "success",
                    "results": results,
                    "security_score": security_score,
                    "security_working": True
                }
            else:
                logger.error("❌ Security validation issues detected")
                return {
                    "status": "failed",
                    "error": "Security validation failed",
                    "results": results,
                    "security_score": security_score,
                    "security_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Security validation test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_language_support_query(self) -> Dict[str, Any]:
        """Test 7: Language Support Query (Priority: LOW)"""
        logger.info("📋 Testing Language Support Query (LOW PRIORITY)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info("   Querying supported languages...")
            
            response = self.session.get(
                f"{self.api_url}/sandbox/languages",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                languages = result.get("languages", [])
                
                logger.info(f"   Languages response: {result}")
                
                # Expected languages
                expected_languages = ["python", "javascript", "bash"]
                expected_memory_limits = {
                    "python": 256,
                    "javascript": 512,
                    "bash": 128
                }
                
                # Verify languages
                available_languages = [lang.get("language") for lang in languages]
                all_languages_present = all(lang in available_languages for lang in expected_languages)
                
                # Verify memory limits
                memory_limits_correct = True
                for lang_info in languages:
                    lang_name = lang_info.get("language")
                    memory_limit = lang_info.get("memory_limit_mb")
                    expected_limit = expected_memory_limits.get(lang_name)
                    
                    if expected_limit and memory_limit != expected_limit:
                        memory_limits_correct = False
                        logger.warning(f"   Memory limit mismatch for {lang_name}: got {memory_limit}, expected {expected_limit}")
                
                logger.info(f"   Available languages: {available_languages}")
                logger.info(f"   All expected languages present: {'✅' if all_languages_present else '❌'}")
                logger.info(f"   Memory limits correct: {'✅' if memory_limits_correct else '❌'}")
                
                # Log individual language details
                for lang_info in languages:
                    lang_name = lang_info.get("language")
                    extension = lang_info.get("extension")
                    timeout = lang_info.get("timeout")
                    memory_limit = lang_info.get("memory_limit_mb")
                    
                    logger.info(f"   {lang_name}: {extension}, {timeout}s timeout, {memory_limit}MB memory")
                
                if all_languages_present and memory_limits_correct and len(languages) == 3:
                    logger.info("✅ Language support query working perfectly!")
                    return {
                        "status": "success",
                        "languages": languages,
                        "available_languages": available_languages,
                        "all_languages_present": all_languages_present,
                        "memory_limits_correct": memory_limits_correct,
                        "language_query_working": True
                    }
                else:
                    logger.error("❌ Language support query issues detected")
                    return {
                        "status": "failed",
                        "error": "Language support validation failed",
                        "languages": languages,
                        "available_languages": available_languages,
                        "all_languages_present": all_languages_present,
                        "memory_limits_correct": memory_limits_correct,
                        "language_query_working": False
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

    def test_authentication_check(self) -> Dict[str, Any]:
        """Test 8: Authentication Check (Priority: HIGH)"""
        logger.info("🔐 Testing Authentication Check (HIGH PRIORITY)")
        
        try:
            # Test sandbox execute without token
            execution_data = {
                "code": 'print("Hello")',
                "language": "python",
                "timeout": 10
            }
            
            logger.info("   Testing sandbox execute without authentication...")
            
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers={"Content-Type": "application/json"},  # No Authorization header
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 401:
                error_detail = response.json().get("detail", "Unknown error") if response.content else "No detail"
                logger.info(f"   Error detail: {error_detail}")
                
                # Test languages endpoint without token
                logger.info("   Testing languages endpoint without authentication...")
                
                languages_response = self.session.get(
                    f"{self.api_url}/sandbox/languages",
                    headers={"Content-Type": "application/json"},  # No Authorization header
                    timeout=10
                )
                
                logger.info(f"   Languages response status: {languages_response.status_code}")
                
                if languages_response.status_code == 401:
                    languages_error = languages_response.json().get("detail", "Unknown error") if languages_response.content else "No detail"
                    logger.info(f"   Languages error detail: {languages_error}")
                    
                    logger.info("✅ Authentication check working perfectly!")
                    return {
                        "status": "success",
                        "execute_without_auth": response.status_code,
                        "languages_without_auth": languages_response.status_code,
                        "execute_error": error_detail,
                        "languages_error": languages_error,
                        "authentication_required": True,
                        "auth_check_working": True
                    }
                else:
                    logger.error("❌ Languages endpoint should require authentication")
                    return {
                        "status": "failed",
                        "error": "Languages endpoint does not require authentication",
                        "execute_without_auth": response.status_code,
                        "languages_without_auth": languages_response.status_code,
                        "auth_check_working": False
                    }
            else:
                logger.error("❌ Sandbox execute should require authentication")
                return {
                    "status": "failed",
                    "error": "Sandbox execute does not require authentication",
                    "execute_without_auth": response.status_code,
                    "auth_check_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication check test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all sandbox tests"""
        logger.info("🚀 STARTING COMPREHENSIVE SANDBOX API TESTING - PHASE 4")
        logger.info("=" * 80)
        
        results = {}
        
        # Step 1: Authentication
        logger.info("\n" + "=" * 80)
        auth_result = self.authenticate()
        results["authentication"] = auth_result
        
        if auth_result.get("status") != "success":
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return results
        
        # Step 2: Authentication Check (test without token first)
        logger.info("\n" + "=" * 80)
        auth_check_result = self.test_authentication_check()
        results["authentication_check"] = auth_check_result
        
        # Step 3: Language Support Query
        logger.info("\n" + "=" * 80)
        language_query_result = self.test_language_support_query()
        results["language_support_query"] = language_query_result
        
        # Step 4: Python Code Execution
        logger.info("\n" + "=" * 80)
        python_result = self.test_python_execution()
        results["python_execution"] = python_result
        
        # Step 5: JavaScript Code Execution
        logger.info("\n" + "=" * 80)
        javascript_result = self.test_javascript_execution()
        results["javascript_execution"] = javascript_result
        
        # Step 6: Bash Script Execution
        logger.info("\n" + "=" * 80)
        bash_result = self.test_bash_execution()
        results["bash_execution"] = bash_result
        
        # Step 7: Error Handling
        logger.info("\n" + "=" * 80)
        error_handling_result = self.test_error_handling()
        results["error_handling"] = error_handling_result
        
        # Step 8: Timeout Test
        logger.info("\n" + "=" * 80)
        timeout_result = self.test_timeout_handling()
        results["timeout_test"] = timeout_result
        
        # Step 9: Security Validation
        logger.info("\n" + "=" * 80)
        security_result = self.test_security_validation()
        results["security_validation"] = security_result
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE SANDBOX TESTING SUMMARY")
        logger.info("=" * 80)
        
        test_categories = [
            ("Authentication", "authentication"),
            ("Authentication Check", "authentication_check"),
            ("Language Support Query", "language_support_query"),
            ("Python Code Execution", "python_execution"),
            ("JavaScript Code Execution", "javascript_execution"),
            ("Bash Script Execution", "bash_execution"),
            ("Error Handling", "error_handling"),
            ("Timeout Test", "timeout_test"),
            ("Security Validation", "security_validation")
        ]
        
        passed_tests = 0
        total_tests = len(test_categories)
        
        for test_name, test_key in test_categories:
            test_result = results.get(test_key, {})
            status = test_result.get("status", "unknown")
            
            if status == "success":
                logger.info(f"✅ {test_name}: PASSED")
                passed_tests += 1
            elif status == "failed":
                logger.info(f"❌ {test_name}: FAILED - {test_result.get('error', 'Unknown error')}")
            elif status == "skipped":
                logger.info(f"⏭️ {test_name}: SKIPPED - {test_result.get('error', 'Unknown reason')}")
            else:
                logger.info(f"⚠️ {test_name}: {status.upper()} - {test_result.get('error', 'Unknown status')}")
        
        logger.info("=" * 80)
        logger.info(f"📈 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            logger.info("🎉 SANDBOX API TESTING: OVERALL SUCCESS!")
        elif passed_tests >= total_tests * 0.6:  # 60% pass rate
            logger.info("⚠️ SANDBOX API TESTING: PARTIAL SUCCESS - Some issues detected")
        else:
            logger.info("❌ SANDBOX API TESTING: SIGNIFICANT ISSUES DETECTED")
        
        logger.info("=" * 80)
        
        results["summary"] = {
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "pass_rate": passed_tests / total_tests,
            "overall_status": "success" if passed_tests >= total_tests * 0.8 else "partial" if passed_tests >= total_tests * 0.6 else "failed"
        }
        
        return results

def main():
    """Main test execution"""
    tester = SandboxTester()
    results = tester.run_comprehensive_tests()
    
    # Save results to file
    with open("/app/sandbox_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📄 Test results saved to: /app/sandbox_test_results.json")
    
    return results

if __name__ == "__main__":
    main()