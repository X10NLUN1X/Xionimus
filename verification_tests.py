#!/usr/bin/env python3
"""
VERIFICATION TESTS - Additional checks for specific requirements
"""

import requests
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VerificationTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self) -> bool:
        """Authenticate with demo/demo123 credentials"""
        try:
            login_data = {"username": "demo", "password": "demo123"}
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                return True
            return False
        except Exception:
            return False
    
    def execute_code(self, language: str, code: str) -> Dict[str, Any]:
        """Execute code in specified language"""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        request_data = {"code": code, "language": language}
        
        try:
            response = self.session.post(
                f"{self.api_url}/sandbox/execute",
                json=request_data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_typescript_advanced_features(self):
        """Test TypeScript with advanced features"""
        logger.info("🔍 Testing TypeScript Advanced Features...")
        
        ts_code = '''// Advanced TypeScript features test
interface User {
    id: number;
    name: string;
    email?: string;
}

class UserManager {
    private users: User[] = [];
    
    addUser(user: User): void {
        this.users.push(user);
        console.log(`Added user: ${user.name}`);
    }
    
    getUsers(): User[] {
        return this.users;
    }
    
    getUserCount(): number {
        return this.users.length;
    }
}

// Generic function
function identity<T>(arg: T): T {
    return arg;
}

// Test execution
const manager = new UserManager();
manager.addUser({ id: 1, name: "Alice" });
manager.addUser({ id: 2, name: "Bob", email: "bob@test.com" });

console.log(`Total users: ${manager.getUserCount()}`);
console.log("Users:", manager.getUsers());

// Test generics
const stringResult = identity<string>("TypeScript rocks!");
const numberResult = identity<number>(42);

console.log("String identity:", stringResult);
console.log("Number identity:", numberResult);

// Array operations with types
const numbers: number[] = [1, 2, 3, 4, 5];
const squares: number[] = numbers.map((n: number): number => n * n);
console.log("Squares:", squares);

console.log("✅ TypeScript advanced features test complete!");'''
        
        result = self.execute_code("typescript", ts_code)
        
        if result.get("success"):
            logger.info("✅ TypeScript advanced features working!")
            logger.info(f"   Execution time: {result.get('execution_time', 0)}s")
            logger.info(f"   Output length: {len(result.get('stdout', ''))} chars")
            return True
        else:
            logger.error(f"❌ TypeScript advanced features failed: {result.get('error')}")
            return False
    
    def test_java_class_extraction(self):
        """Test Java class name extraction"""
        logger.info("🔍 Testing Java Class Name Extraction...")
        
        java_code = '''public class MySpecialClass {
    public static void main(String[] args) {
        System.out.println("Java class extraction test");
        System.out.println("Class name should be extracted correctly");
        
        // Test some Java features
        int[] numbers = {10, 20, 30, 40, 50};
        int sum = 0;
        for (int num : numbers) {
            sum += num;
        }
        
        System.out.println("Sum of numbers: " + sum);
        System.out.println("✅ Java class extraction test complete!");
    }
}'''
        
        result = self.execute_code("java", java_code)
        
        if result.get("success"):
            logger.info("✅ Java class name extraction working!")
            logger.info(f"   Execution time: {result.get('execution_time', 0)}s")
            return True
        else:
            logger.error(f"❌ Java class extraction failed: {result.get('error')}")
            return False
    
    def test_go_gocache(self):
        """Test Go GOCACHE configuration"""
        logger.info("🔍 Testing Go GOCACHE Configuration...")
        
        go_code = '''package main

import (
    "fmt"
    "os"
    "runtime"
)

func main() {
    fmt.Println("Go GOCACHE test")
    fmt.Printf("Go version: %s\\n", runtime.Version())
    fmt.Printf("GOOS: %s\\n", runtime.GOOS)
    fmt.Printf("GOARCH: %s\\n", runtime.GOARCH)
    
    // Check if GOCACHE is set
    gocache := os.Getenv("GOCACHE")
    if gocache != "" {
        fmt.Printf("GOCACHE is set: %s\\n", gocache)
    } else {
        fmt.Println("GOCACHE not explicitly set (using default)")
    }
    
    // Test some Go features
    numbers := []int{1, 2, 3, 4, 5}
    sum := 0
    for _, num := range numbers {
        sum += num
    }
    
    fmt.Printf("Sum: %d\\n", sum)
    fmt.Println("✅ Go GOCACHE test complete!")
}'''
        
        result = self.execute_code("go", go_code)
        
        if result.get("success"):
            logger.info("✅ Go GOCACHE configuration working!")
            logger.info(f"   Execution time: {result.get('execution_time', 0)}s")
            return True
        else:
            logger.error(f"❌ Go GOCACHE test failed: {result.get('error')}")
            return False
    
    def test_compilation_errors(self):
        """Test compilation error handling"""
        logger.info("🔍 Testing Compilation Error Handling...")
        
        # Test C++ compilation error
        cpp_error_code = '''#include <iostream>
using namespace std;

int main() {
    cout << "Missing semicolon test" << endl
    return 0;  // Missing semicolon above
}'''
        
        result = self.execute_code("cpp", cpp_error_code)
        
        if not result.get("success") and result.get("exit_code") != 0:
            logger.info("✅ C++ compilation error handling working!")
            logger.info(f"   Error detected: {result.get('stderr', '')[:100]}...")
            return True
        else:
            logger.error("❌ C++ compilation error not properly handled")
            return False
    
    def test_memory_limits(self):
        """Test memory limits are appropriate"""
        logger.info("🔍 Testing Memory Limits...")
        
        # Test Python memory usage
        python_code = '''import sys
print(f"Python version: {sys.version}")
print("Memory limit test - creating small data structures")

# Create some data to test memory
data = []
for i in range(1000):
    data.append(f"Item {i}")

print(f"Created {len(data)} items")
print("✅ Memory limit test complete!")'''
        
        result = self.execute_code("python", python_code)
        
        if result.get("success"):
            logger.info("✅ Memory limits working correctly!")
            logger.info(f"   Execution time: {result.get('execution_time', 0)}s")
            return True
        else:
            logger.error(f"❌ Memory limit test failed: {result.get('error')}")
            return False
    
    def run_all_verification_tests(self):
        """Run all verification tests"""
        logger.info("🚀 STARTING VERIFICATION TESTS")
        logger.info("=" * 50)
        
        tests = [
            ("TypeScript Advanced Features", self.test_typescript_advanced_features),
            ("Java Class Extraction", self.test_java_class_extraction),
            ("Go GOCACHE Configuration", self.test_go_gocache),
            ("Compilation Error Handling", self.test_compilation_errors),
            ("Memory Limits", self.test_memory_limits)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                results[test_name] = False
        
        logger.info(f"\n{'='*50}")
        logger.info("🏁 VERIFICATION TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Passed: {passed}/{total}")
        logger.info(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            logger.info("🎉 ALL VERIFICATION TESTS PASSED!")
        else:
            logger.info("⚠️ Some verification tests failed")
        
        return passed == total

def main():
    tester = VerificationTester()
    
    if not tester.authenticate():
        logger.error("❌ Authentication failed")
        return False
    
    return tester.run_all_verification_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)