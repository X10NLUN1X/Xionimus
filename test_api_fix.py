#!/usr/bin/env python3
"""
Simple test script to validate API endpoint fixes
Tests basic connectivity and CORS functionality
"""

import requests
import json
import time
from typing import Dict, Any

# Backend URL
BACKEND_URL = "http://localhost:8001"

def test_basic_connectivity():
    """Test basic server connectivity"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is responding")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {str(e)}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {str(e)}")
        return False

def test_cors_headers():
    """Test CORS headers"""
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{BACKEND_URL}/api/health", headers=headers, timeout=5)
        
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-methods': response.headers.get('access-control-allow-methods'),
            'access-control-allow-headers': response.headers.get('access-control-allow-headers'),
        }
        
        if cors_headers['access-control-allow-origin']:
            print("✅ CORS headers are configured")
            print(f"   Allowed Origin: {cors_headers['access-control-allow-origin']}")
            print(f"   Allowed Methods: {cors_headers['access-control-allow-methods']}")
            return True
        else:
            print("❌ CORS headers not found")
            return False
    except Exception as e:
        print(f"❌ CORS test error: {str(e)}")
        return False

def test_api_keys_status():
    """Test API keys status endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/api-keys/status", timeout=5)
        if response.status_code == 200:
            print("✅ API keys status endpoint is working")
            status_data = response.json()
            print(f"   Services: {list(status_data.get('services', {}).keys())}")
            return True
        else:
            print(f"❌ API keys status returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API keys status error: {str(e)}")
        return False

def test_debug_endpoint():
    """Test debug endpoint for comprehensive analysis"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/api-keys/debug", timeout=10)
        if response.status_code == 200:
            print("✅ Debug endpoint is working")
            debug_data = response.json()
            print(f"   Environment services: {len(debug_data.get('environment_analysis', {}).get('services', {}))}")
            print(f"   System health: {debug_data.get('system_health', {}).get('all_systems_operational', 'unknown')}")
            return True
        else:
            print(f"❌ Debug endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Debug endpoint error: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("🔧 XIONIMUS AI - API Endpoint Connectivity Test")
    print("=" * 50)
    
    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("Health Endpoint", test_health_endpoint), 
        ("CORS Configuration", test_cors_headers),
        ("API Keys Status", test_api_keys_status),
        ("Debug Endpoint", test_debug_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        if test_func():
            passed += 1
        time.sleep(0.5)  # Brief delay between tests
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🚀 All API endpoint tests PASSED - System is functional!")
        return True
    else:
        print(f"⚠️  {total - passed} tests FAILED - API endpoints need attention")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)