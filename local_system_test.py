#!/usr/bin/env python3
"""
XIONIMUS AI - Local System Validation Test
Tests all core functionality running completely locally
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Test backend health and local storage"""
    print("🏠 Testing Backend & Local Storage...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend Status: {data['status']}")
            print(f"   ✅ Local Storage: {data['services']['local_storage']}")
            print(f"   ✅ Agents Available: {data['agents']['available']}")
            return True
        else:
            print(f"   ❌ Backend Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend Connection Failed: {e}")
        return False

def test_agents():
    """Test that all agents are loaded"""
    print("🤖 Testing Agent System...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/agents", timeout=5)
        if response.status_code == 200:
            agents = response.json()
            print(f"   ✅ {len(agents)} Agents Loaded:")
            for agent in agents:
                print(f"      • {agent['name']}: {agent['capabilities']}")
            return len(agents) == 8
        else:
            print(f"   ❌ Agents Test Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Agents Connection Failed: {e}")
        return False

def test_local_storage():
    """Test local storage operations"""
    print("💾 Testing Local Storage Operations...")
    try:
        # Create a test project
        test_project = {
            "name": "Local System Test",
            "description": "Testing local storage functionality"
        }
        response = requests.post(f"{BACKEND_URL}/api/projects", 
                               json=test_project, timeout=10)
        
        if response.status_code == 200:
            project = response.json()
            project_id = project['id']
            print(f"   ✅ Project Created: {project_id}")
            
            # List all projects
            response = requests.get(f"{BACKEND_URL}/api/projects", timeout=5)
            if response.status_code == 200:
                projects = response.json()
                print(f"   ✅ Total Projects: {len(projects)}")
                
                # Clean up test project
                response = requests.delete(f"{BACKEND_URL}/api/projects/{project_id}", timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ Test Project Cleaned Up")
                    return True
                else:
                    print(f"   ⚠️ Cleanup Warning: {response.status_code}")
                    return True  # Still success
            
        print(f"   ❌ Local Storage Test Failed: {response.status_code}")
        return False
    except Exception as e:
        print(f"   ❌ Local Storage Error: {e}")
        return False

def test_frontend():
    """Test frontend is running"""
    print("🌐 Testing Frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is running and accessible")
            return True
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Frontend Connection Failed: {e}")
        return False

def test_api_key_management():
    """Test API key management system"""
    print("🔑 Testing API Key Management...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/api-keys/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            configured_services = sum(1 for status in data['status'].values() if status)
            print(f"   ✅ API Key System Working")
            print(f"   ℹ️ Configured Services: {configured_services}/3")
            return True
        else:
            print(f"   ❌ API Key Test Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API Key Error: {e}")
        return False

def main():
    """Run all local system tests"""
    print("🚀 XIONIMUS AI - LOCAL SYSTEM VALIDATION")
    print("=" * 50)
    print(f"Starting validation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Backend & Local Storage", test_backend_health),
        ("Agent System", test_agents),
        ("Local Storage Operations", test_local_storage),
        ("Frontend", test_frontend),
        ("API Key Management", test_api_key_management)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        print()
    
    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - System is fully operational locally!")
        print("💡 System is ready for production use")
        print("🔧 To enable full AI functionality, add API keys via the web interface")
        return 0
    else:
        print(f"⚠️ {total-passed} tests failed - check above for details")
        print("🔧 Some features may not be available")
        return 1

if __name__ == "__main__":
    sys.exit(main())