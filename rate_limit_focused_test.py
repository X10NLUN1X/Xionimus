#!/usr/bin/env python3
"""
Focused Rate Limiting Test
Tests specific rate limiting functionality
"""

import requests
import time
import json

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api"

def test_login_rate_limit():
    """Test login rate limiting (5 requests/minute)"""
    print("🚦 Testing Login Rate Limiting (5 requests/minute)")
    
    for i in range(7):
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": "invalid", "password": "invalid"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print(f"✅ Rate limit triggered on request {i+1}")
            print(f"   Retry-After: {response.headers.get('Retry-After', 'Not set')}")
            print(f"   Response: {response.json()}")
            return True
        
        time.sleep(0.1)
    
    print("❌ Rate limit not triggered after 7 attempts")
    return False

def test_chat_rate_limit():
    """Test chat rate limiting with authentication"""
    print("\n🚦 Testing Chat Rate Limiting (30 requests/minute)")
    
    # First login to get token
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "demo", "password": "demo123"},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Make rapid chat requests
    for i in range(35):
        response = requests.post(
            f"{API_URL}/chat/",
            json={
                "messages": [{"role": "user", "content": f"Test {i+1}"}],
                "provider": "openai",
                "model": "gpt-4"
            },
            headers=headers
        )
        
        print(f"Chat request {i+1}: Status {response.status_code}")
        
        if response.status_code == 429:
            print(f"✅ Chat rate limit triggered on request {i+1}")
            print(f"   Retry-After: {response.headers.get('Retry-After', 'Not set')}")
            print(f"   Response: {response.json()}")
            return True
        
        time.sleep(0.05)
    
    print("❌ Chat rate limit not triggered after 35 attempts")
    return False

def test_quota_tracking():
    """Test user quota tracking"""
    print("\n📊 Testing User Quota Tracking")
    
    # Login to get token
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "demo", "password": "demo123"},
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get quota status
    response = requests.get(f"{API_URL}/rate-limits/quota", headers=headers)
    
    if response.status_code == 200:
        quota_data = response.json()
        print("✅ Quota tracking working")
        print(f"   User role: {quota_data.get('user_role')}")
        print(f"   Requests: {quota_data.get('requests', {}).get('used')}/{quota_data.get('requests', {}).get('limit')}")
        print(f"   AI calls: {quota_data.get('ai_calls', {}).get('used')}/{quota_data.get('ai_calls', {}).get('limit')}")
        return True
    else:
        print(f"❌ Quota endpoint failed: {response.status_code}")
        return False

def test_management_api():
    """Test rate limiting management API"""
    print("\n⚙️ Testing Rate Limiting Management API")
    
    # Test limits endpoint (public)
    response = requests.get(f"{API_URL}/rate-limits/limits")
    if response.status_code == 200:
        limits_data = response.json()
        print(f"✅ Limits endpoint working ({len(limits_data.get('rate_limits', []))} limits configured)")
    else:
        print(f"❌ Limits endpoint failed: {response.status_code}")
        return False
    
    # Test health endpoint (public)
    response = requests.get(f"{API_URL}/rate-limits/health")
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ Health endpoint working (status: {health_data.get('status')})")
    else:
        print(f"❌ Health endpoint failed: {response.status_code}")
        return False
    
    return True

def main():
    print("🚀 Focused Rate Limiting Tests")
    print("=" * 50)
    
    # Wait for any previous rate limits to reset
    print("⏳ Waiting 10 seconds for rate limits to reset...")
    time.sleep(10)
    
    results = []
    
    # Test 1: Login Rate Limiting
    results.append(("Login Rate Limiting", test_login_rate_limit()))
    
    # Wait for rate limit to reset
    print("\n⏳ Waiting 65 seconds for login rate limit to reset...")
    time.sleep(65)
    
    # Test 2: Chat Rate Limiting
    results.append(("Chat Rate Limiting", test_chat_rate_limit()))
    
    # Test 3: Quota Tracking
    results.append(("Quota Tracking", test_quota_tracking()))
    
    # Test 4: Management API
    results.append(("Management API", test_management_api()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FOCUSED TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"Overall: {passed}/{total} tests passed\n")
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")

if __name__ == "__main__":
    main()