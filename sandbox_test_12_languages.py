#!/usr/bin/env python3
"""
CLOUD SANDBOX - COMPLETE RE-TEST ALL 12 LANGUAGES

Nach Installation aller fehlenden Runtimes, bitte alle 12 Sprachen erneut testen:

**Test Credentials:**
- Username: demo
- Password: demo123

**ALLE 12 SPRACHEN TESTEN:**

**Interpreted Languages (7):**
1. **Python** - print("Hello from Python")
2. **JavaScript** - console.log("Hello from JavaScript")
3. **TypeScript** (NEU installiert) - console.log("Hello from TypeScript")
4. **Bash** - echo "Hello from Bash"
5. **PHP** (NEU installiert) - echo "Hello from PHP"
6. **Ruby** (NEU installiert) - puts "Hello from Ruby"
7. **Perl** - print "Hello from Perl"

**Compiled Languages (5):**
8. **C++** - iostream, cout
9. **C** - stdio, printf
10. **C#** (NEU installiert) - Console.WriteLine
11. **Java** (NEU installiert) - System.out.println
12. **Go** (NEU installiert) - fmt.Println

**FÜR JEDE SPRACHE TESTEN:**
- POST /api/sandbox/execute
- Verify: success = true
- Verify: stdout enthält "Hello from ..."
- Verify: exit_code = 0
- Verify: execution_time < 2s
- Verify: Compilation successful (für compiled languages)

**ERWARTETES ERGEBNIS:**
- 12/12 Sprachen sollten ALLE funktionieren ✅
- Keine Runtime-Fehler
- Alle Compilations erfolgreich
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SandboxLanguageTester:
    def __init__(self, base_url: str = None):
        # Use localhost for testing since we're in the same container
        self.base_url = base_url or "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        
        # Define all 12 languages with their test code
        self.languages = {
            # Interpreted Languages (7)
            "python": {
                "code": 'print("Hello from Python")',
                "expected_output": "Hello from Python",
                "type": "interpreted",
                "new": False
            },
            "javascript": {
                "code": 'console.log("Hello from JavaScript");',
                "expected_output": "Hello from JavaScript",
                "type": "interpreted", 
                "new": False
            },
            "typescript": {
                "code": 'console.log("Hello from TypeScript");',
                "expected_output": "Hello from TypeScript",
                "type": "interpreted",
                "new": True  # NEU installiert
            },
            "bash": {
                "code": 'echo "Hello from Bash"',
                "expected_output": "Hello from Bash",
                "type": "interpreted",
                "new": False
            },
            "php": {
                "code": '<?php echo "Hello from PHP"; ?>',
                "expected_output": "Hello from PHP",
                "type": "interpreted",
                "new": True  # NEU installiert
            },
            "ruby": {
                "code": 'puts "Hello from Ruby"',
                "expected_output": "Hello from Ruby",
                "type": "interpreted",
                "new": True  # NEU installiert
            },
            "perl": {
                "code": 'print "Hello from Perl\\n";',
                "expected_output": "Hello from Perl",
                "type": "interpreted",
                "new": False
            },
            
            # Compiled Languages (5)
            "cpp": {
                "code": '#include <iostream>\nusing namespace std;\nint main() {\n    cout << "Hello from C++" << endl;\n    return 0;\n}',
                "expected_output": "Hello from C++",
                "type": "compiled",
                "new": False
            },
            "c": {
                "code": '#include <stdio.h>\nint main() {\n    printf("Hello from C\\n");\n    return 0;\n}',
                "expected_output": "Hello from C",
                "type": "compiled",
                "new": False
            },
            "csharp": {
                "code": 'using System;\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello from C#");\n    }\n}',
                "expected_output": "Hello from C#",
                "type": "compiled",
                "new": True  # NEU installiert
            },
            "java": {
                "code": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java");\n    }\n}',
                "expected_output": "Hello from Java",
                "type": "compiled",
                "new": True  # NEU installiert
            },
            "go": {
                "code": 'package main\nimport "fmt"\nfunc main() {\n    fmt.Println("Hello from Go")\n}',
                "expected_output": "Hello from Go",
                "type": "compiled",
                "new": True  # NEU installiert
            }
        }

    def authenticate_demo_user(self) -> Dict[str, Any]:
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

    def test_language_support_endpoint(self) -> Dict[str, Any]:
        """Test GET /api/sandbox/languages endpoint"""
        logger.info("📋 Testing Language Support Endpoint")
        
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
                supported_languages = languages_data.get("languages", [])
                
                logger.info(f"   Supported languages count: {len(supported_languages)}")
                
                # Extract language names
                language_names = []
                for lang in supported_languages:
                    if isinstance(lang, dict):
                        lang_name = lang.get("language", lang.get("name", "unknown"))
                        language_names.append(lang_name)
                        logger.info(f"   - {lang_name}: {lang.get('extension', 'N/A')} (timeout: {lang.get('timeout', 'N/A')}s, memory: {lang.get('memory_limit_mb', 'N/A')}MB)")
                
                return {
                    "status": "success",
                    "supported_languages": language_names,
                    "total_count": len(supported_languages),
                    "languages_data": supported_languages
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Languages endpoint failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Language support endpoint test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_single_language(self, language: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single programming language"""
        logger.info(f"🧪 Testing {language.upper()} {'(NEW)' if config['new'] else ''}")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Prepare execution request
            execution_data = {
                "code": config["code"],
                "language": language,
                "timeout": 30  # 30 seconds timeout
            }
            
            logger.info(f"   Code: {config['code'][:50]}{'...' if len(config['code']) > 50 else ''}")
            logger.info(f"   Expected output: {config['expected_output']}")
            
            # Execute code
            start_time = time.time()
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=execution_data,
                headers=headers,
                timeout=45  # Allow extra time for compilation
            )
            end_time = time.time()
            
            logger.info(f"   Response status: {response.status_code}")
            logger.info(f"   Request time: {end_time - start_time:.3f}s")
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract response fields
                success = result.get("success", False)
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exit_code = result.get("exit_code", -1)
                execution_time = result.get("execution_time", 0)
                execution_id = result.get("execution_id", "")
                timeout_occurred = result.get("timeout_occurred", False)
                
                logger.info(f"   Success: {success}")
                logger.info(f"   Exit code: {exit_code}")
                logger.info(f"   Execution time: {execution_time}s")
                logger.info(f"   Execution ID: {execution_id}")
                logger.info(f"   Timeout occurred: {timeout_occurred}")
                logger.info(f"   Stdout: {stdout.strip()}")
                if stderr:
                    logger.info(f"   Stderr: {stderr.strip()}")
                
                # Verify results
                checks = {
                    "success_true": success == True,
                    "exit_code_zero": exit_code == 0,
                    "execution_time_reasonable": execution_time < 2.0,
                    "expected_output_present": config["expected_output"] in stdout,
                    "execution_id_present": bool(execution_id),
                    "no_timeout": not timeout_occurred
                }
                
                # Log check results
                for check_name, check_result in checks.items():
                    logger.info(f"   ✅ {check_name}: {check_result}")
                
                # Overall success
                all_checks_passed = all(checks.values())
                
                if all_checks_passed:
                    logger.info(f"✅ {language.upper()} WORKING PERFECTLY!")
                    return {
                        "status": "success",
                        "language": language,
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "execution_id": execution_id,
                        "timeout_occurred": timeout_occurred,
                        "checks": checks,
                        "all_checks_passed": True,
                        "type": config["type"],
                        "new": config["new"]
                    }
                else:
                    failed_checks = [name for name, result in checks.items() if not result]
                    logger.error(f"❌ {language.upper()} FAILED - Failed checks: {failed_checks}")
                    return {
                        "status": "failed",
                        "language": language,
                        "error": f"Failed checks: {failed_checks}",
                        "success": success,
                        "stdout": stdout,
                        "stderr": stderr,
                        "exit_code": exit_code,
                        "execution_time": execution_time,
                        "checks": checks,
                        "all_checks_passed": False,
                        "failed_checks": failed_checks,
                        "type": config["type"],
                        "new": config["new"]
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ {language.upper()} EXECUTION FAILED: {error_detail}")
                return {
                    "status": "failed",
                    "language": language,
                    "error": error_detail,
                    "status_code": response.status_code,
                    "type": config["type"],
                    "new": config["new"]
                }
                
        except Exception as e:
            logger.error(f"❌ {language.upper()} test failed: {e}")
            return {
                "status": "error",
                "language": language,
                "error": str(e),
                "type": config["type"],
                "new": config["new"]
            }

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of all 12 languages"""
        logger.info("🚀 STARTING COMPREHENSIVE 12-LANGUAGE SANDBOX TEST")
        logger.info("=" * 80)
        
        # Step 1: Authenticate
        auth_result = self.authenticate_demo_user()
        if auth_result["status"] != "success":
            return {
                "status": "failed",
                "error": "Authentication failed",
                "auth_result": auth_result
            }
        
        # Step 2: Test language support endpoint
        logger.info("\n" + "=" * 80)
        languages_result = self.test_language_support_endpoint()
        
        # Step 3: Test all 12 languages
        logger.info("\n" + "=" * 80)
        logger.info("TESTING ALL 12 LANGUAGES")
        logger.info("=" * 80)
        
        results = {}
        successful_languages = []
        failed_languages = []
        new_languages = []
        
        for language, config in self.languages.items():
            logger.info(f"\n{'-' * 40}")
            result = self.test_single_language(language, config)
            results[language] = result
            
            if result["status"] == "success":
                successful_languages.append(language)
                if config["new"]:
                    new_languages.append(language)
            else:
                failed_languages.append(language)
        
        # Step 4: Generate comprehensive summary
        logger.info("\n" + "=" * 80)
        logger.info("COMPREHENSIVE TEST RESULTS SUMMARY")
        logger.info("=" * 80)
        
        total_languages = len(self.languages)
        successful_count = len(successful_languages)
        failed_count = len(failed_languages)
        new_working_count = len(new_languages)
        
        logger.info(f"📊 OVERALL RESULTS: {successful_count}/{total_languages} languages working")
        logger.info(f"✅ Successful: {successful_count}")
        logger.info(f"❌ Failed: {failed_count}")
        logger.info(f"🆕 New languages working: {new_working_count}/5")
        
        # Categorize results
        interpreted_results = {}
        compiled_results = {}
        
        for language, result in results.items():
            if self.languages[language]["type"] == "interpreted":
                interpreted_results[language] = result
            else:
                compiled_results[language] = result
        
        # Log interpreted languages
        logger.info(f"\n📝 INTERPRETED LANGUAGES ({len(interpreted_results)}):")
        for language, result in interpreted_results.items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            new_icon = " (NEW)" if self.languages[language]["new"] else ""
            logger.info(f"   {status_icon} {language.upper()}{new_icon}")
        
        # Log compiled languages
        logger.info(f"\n🔨 COMPILED LANGUAGES ({len(compiled_results)}):")
        for language, result in compiled_results.items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            new_icon = " (NEW)" if self.languages[language]["new"] else ""
            logger.info(f"   {status_icon} {language.upper()}{new_icon}")
        
        # Log failed languages with details
        if failed_languages:
            logger.info(f"\n❌ FAILED LANGUAGES ({len(failed_languages)}):")
            for language in failed_languages:
                result = results[language]
                error = result.get("error", "Unknown error")
                logger.error(f"   - {language.upper()}: {error}")
        
        # Final verdict
        if successful_count == total_languages:
            logger.info(f"\n🎉 PERFECT SCORE! ALL {total_languages}/12 LANGUAGES WORKING!")
            final_status = "perfect"
        elif successful_count >= 10:
            logger.info(f"\n🎯 EXCELLENT! {successful_count}/12 languages working")
            final_status = "excellent"
        elif successful_count >= 8:
            logger.info(f"\n👍 GOOD! {successful_count}/12 languages working")
            final_status = "good"
        else:
            logger.error(f"\n⚠️ NEEDS WORK! Only {successful_count}/12 languages working")
            final_status = "needs_work"
        
        return {
            "status": final_status,
            "total_languages": total_languages,
            "successful_count": successful_count,
            "failed_count": failed_count,
            "successful_languages": successful_languages,
            "failed_languages": failed_languages,
            "new_languages_working": new_languages,
            "new_working_count": new_working_count,
            "interpreted_results": interpreted_results,
            "compiled_results": compiled_results,
            "detailed_results": results,
            "languages_endpoint_result": languages_result,
            "auth_result": auth_result
        }

def main():
    """Main test execution"""
    print("🚀 CLOUD SANDBOX - COMPLETE RE-TEST ALL 12 LANGUAGES")
    print("=" * 80)
    print("Testing all 12 programming languages after runtime installation")
    print("Credentials: demo/demo123")
    print("=" * 80)
    
    tester = SandboxLanguageTester()
    result = tester.run_comprehensive_test()
    
    # Final summary for easy reading
    print("\n" + "=" * 80)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 80)
    
    if result["status"] == "perfect":
        print("🎉 PERFECT! ALL 12/12 LANGUAGES WORKING!")
    elif result["status"] == "excellent":
        print(f"🎯 EXCELLENT! {result['successful_count']}/12 LANGUAGES WORKING")
    elif result["status"] == "good":
        print(f"👍 GOOD! {result['successful_count']}/12 LANGUAGES WORKING")
    else:
        print(f"⚠️ NEEDS WORK! {result['successful_count']}/12 LANGUAGES WORKING")
    
    print(f"✅ Working: {', '.join(result['successful_languages'])}")
    if result['failed_languages']:
        print(f"❌ Failed: {', '.join(result['failed_languages'])}")
    
    print(f"🆕 New languages working: {result['new_working_count']}/5")
    print("=" * 80)
    
    return result

if __name__ == "__main__":
    main()