#!/usr/bin/env python3
"""
Quick Regression Test - Core Backend Functionality

Tests the most critical backend features to ensure no regressions.
"""

import requests
import time
import json

BACKEND_URL = "http://localhost:8001"
TEST_CREDENTIALS = {"username": "demo", "password": "demo123"}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def test_core_functionality():
    """Test core backend functionality"""
    print(f"{Colors.CYAN}{Colors.BOLD}🔍 QUICK REGRESSION TEST - CORE FUNCTIONALITY{Colors.END}")
    
    results = {"passed": 0, "total": 0, "details": []}
    
    # Test 1: Authentication
    results["total"] += 1
    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=TEST_CREDENTIALS, timeout=5)
        if response.status_code == 200 and response.json().get("access_token"):
            auth_token = response.json().get("access_token")
            results["passed"] += 1
            results["details"].append("✅ Authentication: Working")
        else:
            results["details"].append(f"❌ Authentication: Failed ({response.status_code})")
            return results
    except Exception as e:
        results["details"].append(f"❌ Authentication: Error ({e})")
        return results
    
    # Test 2: Health Check
    results["total"] += 1
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            results["passed"] += 1
            results["details"].append("✅ Health Check: Working")
        else:
            results["details"].append(f"❌ Health Check: Failed ({response.status_code})")
    except Exception as e:
        results["details"].append(f"❌ Health Check: Error ({e})")
    
    # Test 3: Metrics Performance (the main fix)
    results["total"] += 1
    try:
        start_time = time.time()
        response = requests.get(f"{BACKEND_URL}/api/metrics", timeout=5)
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        if response.status_code == 200 and response_time_ms < 200:
            results["passed"] += 1
            results["details"].append(f"✅ Metrics Performance: {response_time_ms:.1f}ms (<200ms target)")
        else:
            results["details"].append(f"❌ Metrics Performance: {response_time_ms:.1f}ms (too slow)")
    except Exception as e:
        results["details"].append(f"❌ Metrics Performance: Error ({e})")
    
    # Test 4: Session Management
    results["total"] += 1
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(f"{BACKEND_URL}/api/sessions/", 
                               json={"title": "Regression Test"}, headers=headers, timeout=5)
        if response.status_code == 200:
            results["passed"] += 1
            results["details"].append("✅ Session Management: Working")
        else:
            results["details"].append(f"❌ Session Management: Failed ({response.status_code})")
    except Exception as e:
        results["details"].append(f"❌ Session Management: Error ({e})")
    
    # Test 5: Cloud Sandbox
    results["total"] += 1
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        code_data = {"language": "python", "code": "print('Hello World')"}
        response = requests.post(f"{BACKEND_URL}/api/sandbox/execute", 
                               json=code_data, headers=headers, timeout=10)
        if response.status_code == 200 and response.json().get("success"):
            results["passed"] += 1
            results["details"].append("✅ Cloud Sandbox: Working")
        else:
            results["details"].append(f"❌ Cloud Sandbox: Failed ({response.status_code})")
    except Exception as e:
        results["details"].append(f"❌ Cloud Sandbox: Error ({e})")
    
    # Test 6: Rate Limiting
    results["total"] += 1
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BACKEND_URL}/api/rate-limits/quota", headers=headers, timeout=5)
        if response.status_code == 200:
            results["passed"] += 1
            results["details"].append("✅ Rate Limiting: Working")
        else:
            results["details"].append(f"❌ Rate Limiting: Failed ({response.status_code})")
    except Exception as e:
        results["details"].append(f"❌ Rate Limiting: Error ({e})")
    
    # Test 7: Database Operations
    results["total"] += 1
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BACKEND_URL}/api/sessions/list", headers=headers, timeout=5)
        if response.status_code == 200:
            results["passed"] += 1
            results["details"].append(f"✅ Database Operations: Working ({len(response.json())} sessions)")
        else:
            results["details"].append(f"❌ Database Operations: Failed ({response.status_code})")
    except Exception as e:
        results["details"].append(f"❌ Database Operations: Error ({e})")
    
    return results

def main():
    """Main test execution"""
    results = test_core_functionality()
    
    print(f"\n{Colors.BOLD}RESULTS:{Colors.END}")
    for detail in results["details"]:
        print(f"  {detail}")
    
    success_rate = (results["passed"] / results["total"]) * 100
    print(f"\n{Colors.BOLD}SUMMARY: {results['passed']}/{results['total']} tests passed ({success_rate:.1f}%){Colors.END}")
    
    if results["passed"] == results["total"]:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL CORE FUNCTIONALITY WORKING!{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ SOME CORE FUNCTIONALITY ISSUES{Colors.END}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)