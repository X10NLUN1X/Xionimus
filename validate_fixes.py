#!/usr/bin/env python3
"""
Validate API endpoint fixes without running the server
Tests the fixes we made to server.py
"""

import os
import re
from pathlib import Path

def check_duplicate_cors():
    """Check if duplicate CORS configurations were removed"""
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    content = server_file.read_text()
    cors_count = content.count("app.add_middleware(")
    
    if cors_count == 1:
        print("✅ Duplicate CORS configuration removed")
        return True
    else:
        print(f"❌ Found {cors_count} CORS configurations, should be 1")
        return False

def check_duplicate_router():
    """Check if duplicate router inclusion was removed"""
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    content = server_file.read_text()
    router_count = content.count("app.include_router(api_router)")
    
    if router_count == 1:
        print("✅ Duplicate router inclusion removed")
        return True
    else:
        print(f"❌ Found {router_count} router inclusions, should be 1")
        return False

def check_hardcoded_keys_removed():
    """Check if hardcoded API keys were removed"""
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    content = server_file.read_text()
    
    # Look for patterns that might indicate hardcoded keys
    key_patterns = [
        r'sk-ant-api03-[A-Za-z0-9\-_]+',  # Anthropic key pattern
        r'sk-proj-[A-Za-z0-9\-_]+',       # OpenAI key pattern  
        r'pplx-[A-Za-z0-9]+',             # Perplexity key pattern
    ]
    
    found_keys = []
    for pattern in key_patterns:
        matches = re.findall(pattern, content)
        found_keys.extend(matches)
    
    if not found_keys:
        print("✅ No hardcoded API keys found")
        return True
    else:
        print(f"❌ Found {len(found_keys)} hardcoded API keys")
        return False

def check_cors_origins():
    """Check if CORS origins are properly configured"""
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    content = server_file.read_text()
    
    # Check for localhost origins
    required_origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    missing_origins = []
    for origin in required_origins:
        if origin not in content:
            missing_origins.append(origin)
    
    if not missing_origins:
        print("✅ All required CORS origins are configured")
        return True
    else:
        print(f"❌ Missing CORS origins: {missing_origins}")
        return False

def check_api_endpoints():
    """Check if all expected API endpoints are present"""
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    content = server_file.read_text()
    
    # Essential endpoints that should exist (more flexible patterns)
    essential_endpoints = [
        ("/health", "@api_router.get(\"/health\")"),
        ("/api-keys/status", "@api_router.get(\"/api-keys/status\")"),
        ("POST /api-keys", "@api_router.post(\"/api-keys\")"),
        ("/api-keys/debug", "@api_router.get(\"/api-keys/debug\")"),
        ("POST /chat", "@api_router.post(\"/chat")  # More flexible match
    ]
    
    missing_endpoints = []
    for name, pattern in essential_endpoints:
        if pattern not in content:
            missing_endpoints.append(name)
    
    if not missing_endpoints:
        print("✅ All essential API endpoints are present")
        return True
    else:
        print(f"❌ Missing API endpoints: {missing_endpoints}")
        return False

def check_syntax():
    """Check Python syntax of server.py"""
    import ast
    
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    try:
        with open(server_file, 'r') as f:
            ast.parse(f.read())
        print("✅ server.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in server.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")
        return False

def main():
    """Main validation function"""
    print("🔧 XIONIMUS AI - API Endpoint Fix Validation")
    print("=" * 50)
    
    tests = [
        ("Duplicate CORS Configuration", check_duplicate_cors),
        ("Duplicate Router Inclusion", check_duplicate_router),
        ("Hardcoded API Keys Removed", check_hardcoded_keys_removed),
        ("CORS Origins Configuration", check_cors_origins),
        ("API Endpoints Present", check_api_endpoints),
        ("Python Syntax", check_syntax),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🚀 All fixes validated successfully!")
        print("✅ API endpoint issues should be resolved")
        return True
    else:
        print(f"⚠️  {total - passed} checks FAILED - Additional fixes needed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)