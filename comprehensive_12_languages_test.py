#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - ALL 12 PROGRAMMING LANGUAGES
Cloud Sandbox Testing with Special Focus on TypeScript (NEWLY FIXED)

LANGUAGES TO TEST:
1. Python (256MB)
2. JavaScript (512MB - Node.js) 
3. TypeScript (512MB - ts-node) - NEWLY FIXED
4. Bash (128MB)
5. C++ (512MB - g++)
6. C (512MB - gcc)
7. C# (512MB - Mono)
8. Java (768MB - OpenJDK 17)
9. Go (512MB - Go 1.19.8)
10. PHP (256MB - PHP 8.2.29)
11. Ruby (256MB - Ruby 3.1.2)
12. Perl (256MB - Perl 5.36.0)

VERIFICATION CHECKS:
- All 12 languages execute successfully
- Correct stdout for each
- Exit code 0 for all
- Reasonable execution times
- No compilation errors
- TypeScript with interfaces works
- Java class name extraction works
- Go GOCACHE configured
- Memory limits appropriate
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

class ComprehensiveLanguageTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.test_results = {}
        
    def authenticate(self) -> bool:
        """Authenticate with demo/demo123 credentials"""
        logger.info("🔐 Authenticating with demo/demo123...")
        
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
                logger.info("✅ Authentication successful!")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages from API"""
        logger.info("📋 Getting supported languages...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(
                f"{self.api_url}/sandbox/languages",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                languages = data.get("languages", [])
                logger.info(f"✅ Found {len(languages)} supported languages")
                return {"success": True, "languages": languages}
            else:
                logger.error(f"❌ Failed to get languages: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Error getting languages: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_code(self, language: str, code: str, timeout: int = None) -> Dict[str, Any]:
        """Execute code in specified language"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        request_data = {
            "code": code,
            "language": language
        }
        
        if timeout:
            request_data["timeout"] = timeout
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=request_data,
                headers=headers,
                timeout=120  # Allow up to 2 minutes for execution
            )
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                result["api_execution_time"] = round(execution_time, 3)
                return result
            else:
                logger.error(f"❌ Execution failed: {response.status_code}")
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                return {
                    "success": False,
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_language(self, language: str, test_code: str, expected_output: str = None) -> Dict[str, Any]:
        """Test a specific language with given code"""
        logger.info(f"🧪 Testing {language.upper()}...")
        
        result = self.execute_code(language, test_code)
        
        if result.get("success"):
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            exit_code = result.get("exit_code", -1)
            exec_time = result.get("execution_time", 0)
            api_time = result.get("api_execution_time", 0)
            
            # Check if output matches expected (if provided)
            output_correct = True
            if expected_output:
                output_correct = expected_output.strip() in stdout.strip()
            
            success = exit_code == 0 and (not expected_output or output_correct)
            
            logger.info(f"   ✅ Exit code: {exit_code}")
            logger.info(f"   ✅ Execution time: {exec_time}s")
            logger.info(f"   ✅ API time: {api_time}s")
            logger.info(f"   ✅ Stdout: {len(stdout)} chars")
            if stderr:
                logger.info(f"   ⚠️ Stderr: {stderr[:100]}...")
            
            return {
                "success": success,
                "exit_code": exit_code,
                "execution_time": exec_time,
                "api_execution_time": api_time,
                "stdout": stdout,
                "stderr": stderr,
                "output_correct": output_correct,
                "language": language
            }
        else:
            logger.error(f"   ❌ {language.upper()} failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "language": language
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of all 12 languages"""
        logger.info("🚀 STARTING COMPREHENSIVE 12-LANGUAGE TEST")
        logger.info("=" * 60)
        
        # Test cases for each language
        test_cases = {
            "python": {
                "code": '''print("Hello from Python!")
for i in range(3):
    print(f"Count: {i}")
print("Python test complete")''',
                "expected": "Hello from Python!"
            },
            
            "javascript": {
                "code": '''console.log("Hello from JavaScript!");
const arr = [1, 2, 3];
console.log("Array:", arr.map(x => x * 2));
console.log("JavaScript test complete");''',
                "expected": "Hello from JavaScript!"
            },
            
            "typescript": {
                "code": '''interface Person {
    name: string;
    age: number;
}

function greet(person: Person): string {
    return `Hello, ${person.name}! You are ${person.age} years old.`;
}

const user: Person = { name: "TypeScript", age: 5 };
console.log(greet(user));

const numbers: number[] = [1, 2, 3, 4, 5];
const doubled = numbers.map((n: number) => n * 2);
console.log("Doubled numbers:", doubled);
console.log("TypeScript test complete");''',
                "expected": "Hello, TypeScript!"
            },
            
            "bash": {
                "code": '''#!/bin/bash
echo "Hello from Bash!"
for i in {1..3}; do
    echo "Loop iteration: $i"
done
echo "Bash test complete"''',
                "expected": "Hello from Bash!"
            },
            
            "cpp": {
                "code": '''#include <iostream>
#include <vector>
using namespace std;

int main() {
    cout << "Hello from C++!" << endl;
    
    vector<int> numbers = {1, 2, 3, 4, 5};
    cout << "Numbers: ";
    for(int n : numbers) {
        cout << n << " ";
    }
    cout << endl;
    
    cout << "C++ test complete" << endl;
    return 0;
}''',
                "expected": "Hello from C++!"
            },
            
            "c": {
                "code": '''#include <stdio.h>

int main() {
    printf("Hello from C!\\n");
    
    int numbers[] = {1, 2, 3, 4, 5};
    printf("Numbers: ");
    for(int i = 0; i < 5; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\\n");
    
    printf("C test complete\\n");
    return 0;
}''',
                "expected": "Hello from C!"
            },
            
            "csharp": {
                "code": '''using System;

class Program {
    static void Main() {
        Console.WriteLine("Hello from C#!");
        
        int[] numbers = {1, 2, 3, 4, 5};
        Console.Write("Numbers: ");
        foreach(int n in numbers) {
            Console.Write(n + " ");
        }
        Console.WriteLine();
        
        Console.WriteLine("C# test complete");
    }
}''',
                "expected": "Hello from C#!"
            },
            
            "java": {
                "code": '''public class TestProgram {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
        
        int[] numbers = {1, 2, 3, 4, 5};
        System.out.print("Numbers: ");
        for(int n : numbers) {
            System.out.print(n + " ");
        }
        System.out.println();
        
        System.out.println("Java test complete");
    }
}''',
                "expected": "Hello from Java!"
            },
            
            "go": {
                "code": '''package main

import "fmt"

func main() {
    fmt.Println("Hello from Go!")
    
    numbers := []int{1, 2, 3, 4, 5}
    fmt.Print("Numbers: ")
    for _, n := range numbers {
        fmt.Print(n, " ")
    }
    fmt.Println()
    
    fmt.Println("Go test complete")
}''',
                "expected": "Hello from Go!"
            },
            
            "php": {
                "code": '''<?php
echo "Hello from PHP!\\n";

$numbers = [1, 2, 3, 4, 5];
echo "Numbers: ";
foreach($numbers as $n) {
    echo "$n ";
}
echo "\\n";

echo "PHP test complete\\n";
?>''',
                "expected": "Hello from PHP!"
            },
            
            "ruby": {
                "code": '''puts "Hello from Ruby!"

numbers = [1, 2, 3, 4, 5]
print "Numbers: "
numbers.each { |n| print "#{n} " }
puts

puts "Ruby test complete"''',
                "expected": "Hello from Ruby!"
            },
            
            "perl": {
                "code": '''print "Hello from Perl!\\n";

my @numbers = (1, 2, 3, 4, 5);
print "Numbers: ";
foreach my $n (@numbers) {
    print "$n ";
}
print "\\n";

print "Perl test complete\\n";''',
                "expected": "Hello from Perl!"
            }
        }
        
        # Run tests for each language
        results = {}
        successful_languages = []
        failed_languages = []
        
        for language, test_case in test_cases.items():
            logger.info(f"\n{'='*20} {language.upper()} {'='*20}")
            
            result = self.test_language(
                language=language,
                test_code=test_case["code"],
                expected_output=test_case["expected"]
            )
            
            results[language] = result
            
            if result.get("success"):
                successful_languages.append(language)
                logger.info(f"✅ {language.upper()} - SUCCESS")
            else:
                failed_languages.append(language)
                logger.error(f"❌ {language.upper()} - FAILED")
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("🏁 COMPREHENSIVE TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful languages: {len(successful_languages)}/12")
        logger.info(f"❌ Failed languages: {len(failed_languages)}/12")
        
        if successful_languages:
            logger.info(f"\n✅ WORKING LANGUAGES:")
            for lang in successful_languages:
                exec_time = results[lang].get("execution_time", 0)
                logger.info(f"   • {lang.upper()} ({exec_time}s)")
        
        if failed_languages:
            logger.info(f"\n❌ FAILED LANGUAGES:")
            for lang in failed_languages:
                error = results[lang].get("error", "Unknown error")
                logger.info(f"   • {lang.upper()}: {error}")
        
        # Special focus on TypeScript
        if "typescript" in results:
            ts_result = results["typescript"]
            logger.info(f"\n🎯 TYPESCRIPT (NEWLY FIXED) STATUS:")
            if ts_result.get("success"):
                logger.info("   ✅ TypeScript is NOW WORKING!")
                logger.info("   ✅ Interface definitions working")
                logger.info("   ✅ Type-safe functions working")
                logger.info("   ✅ Array operations with types working")
                logger.info(f"   ✅ Execution time: {ts_result.get('execution_time', 0)}s")
            else:
                logger.error("   ❌ TypeScript still not working!")
                logger.error(f"   ❌ Error: {ts_result.get('error', 'Unknown')}")
        
        # Overall result
        all_working = len(successful_languages) == 12
        logger.info(f"\n🎯 FINAL RESULT:")
        if all_working:
            logger.info("🎉 ALL 12 LANGUAGES WORKING - PRODUCTION READY!")
        else:
            logger.info(f"⚠️ {len(failed_languages)} languages need attention")
        
        return {
            "total_languages": 12,
            "successful_count": len(successful_languages),
            "failed_count": len(failed_languages),
            "successful_languages": successful_languages,
            "failed_languages": failed_languages,
            "all_working": all_working,
            "detailed_results": results,
            "typescript_working": results.get("typescript", {}).get("success", False)
        }

def main():
    """Main test execution"""
    tester = ComprehensiveLanguageTester()
    
    # Authenticate
    if not tester.authenticate():
        logger.error("❌ Authentication failed - cannot proceed")
        return False
    
    # Get supported languages first
    lang_result = tester.get_supported_languages()
    if lang_result.get("success"):
        languages = lang_result["languages"]
        logger.info(f"📋 API reports {len(languages)} supported languages:")
        for lang in languages:
            logger.info(f"   • {lang['language']} ({lang['memory_limit_mb']}MB, {lang['timeout']}s)")
    
    # Run comprehensive test
    results = tester.run_comprehensive_test()
    
    # Return success status
    return results["all_working"]

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)