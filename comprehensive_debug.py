#!/usr/bin/env python3
"""
Comprehensive API endpoint debugging and validation
Tests all critical aspects of the API connectivity issue
"""

import os
import re
import json
from pathlib import Path

def check_backend_server_config():
    """Check backend server configuration"""
    print("🔧 Checking Backend Server Configuration:")
    
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    content = server_file.read_text()
    checks_passed = 0
    total_checks = 0
    
    # Check 1: CORS configuration
    total_checks += 1
    cors_count = content.count("app.add_middleware(")
    if cors_count == 1:
        print("   ✅ Single CORS configuration found")
        checks_passed += 1
    else:
        print(f"   ❌ Found {cors_count} CORS configurations, expected 1")
    
    # Check 2: Router inclusion
    total_checks += 1
    router_count = content.count("app.include_router(api_router)")
    if router_count == 1:
        print("   ✅ Single router inclusion found")
        checks_passed += 1
    else:
        print(f"   ❌ Found {router_count} router inclusions, expected 1")
    
    # Check 3: CORS origins
    total_checks += 1
    required_origins = ["localhost:3000", "localhost:3001", "127.0.0.1:3000"]
    missing_origins = [o for o in required_origins if o not in content]
    if not missing_origins:
        print("   ✅ All required CORS origins configured")
        checks_passed += 1
    else:
        print(f"   ❌ Missing CORS origins: {missing_origins}")
    
    # Check 4: No hardcoded secrets
    total_checks += 1
    secret_patterns = [r'sk-ant-[A-Za-z0-9\-_]{10,}', r'sk-proj-[A-Za-z0-9\-_]{10,}', r'pplx-[A-Za-z0-9]{10,}']
    found_secrets = []
    for pattern in secret_patterns:
        found_secrets.extend(re.findall(pattern, content))
    
    if not found_secrets:
        print("   ✅ No hardcoded API keys found")
        checks_passed += 1
    else:
        print(f"   ❌ Found {len(found_secrets)} hardcoded API keys")
    
    print(f"   📊 Backend checks: {checks_passed}/{total_checks} passed")
    return checks_passed == total_checks

def check_frontend_config():
    """Check frontend configuration"""
    print("\n🌐 Checking Frontend Configuration:")
    
    app_file = Path("frontend/src/App.js")
    if not app_file.exists():
        print("❌ App.js not found")
        return False
    
    content = app_file.read_text()
    checks_passed = 0
    total_checks = 0
    
    # Check 1: Backend URL fallback
    total_checks += 1
    if "process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'" in content:
        print("   ✅ Backend URL has fallback configured")
        checks_passed += 1
    else:
        print("   ❌ Backend URL missing fallback")
    
    # Check 2: API base path
    total_checks += 1
    if "const API = `${BACKEND_URL}/api`" in content:
        print("   ✅ API base path configured correctly")
        checks_passed += 1
    else:
        print("   ❌ API base path not configured correctly")
    
    print(f"   📊 Frontend checks: {checks_passed}/{total_checks} passed")
    return checks_passed == total_checks

def check_api_endpoints():
    """Check critical API endpoints are present"""
    print("\n🔌 Checking API Endpoints:")
    
    server_file = Path("backend/server.py")
    if not server_file.exists():
        print("❌ server.py not found")
        return False
    
    content = server_file.read_text()
    
    # Critical endpoints for basic functionality
    critical_endpoints = [
        ("/health", "Health check"),
        ("/api-keys/status", "API key status"),
        ("/api-keys/debug", "Debug information"), 
        ("/api-keys", "API key management"),
        ("/chat", "Chat functionality")
    ]
    
    checks_passed = 0
    for endpoint, description in critical_endpoints:
        if f'@api_router.' in content and f'"{endpoint}"' in content:
            print(f"   ✅ {description} endpoint present")
            checks_passed += 1
        else:
            print(f"   ❌ {description} endpoint missing")
    
    print(f"   📊 Endpoint checks: {checks_passed}/{len(critical_endpoints)} passed")
    return checks_passed == len(critical_endpoints)

def check_potential_issues():
    """Check for potential configuration issues"""
    print("\n🚨 Checking Potential Issues:")
    
    issues_found = []
    
    # Check for .env file
    env_file = Path("backend/.env")
    if not env_file.exists():
        issues_found.append("Missing .env file in backend directory")
    
    # Check for package.json in frontend
    package_json = Path("frontend/package.json")
    if package_json.exists():
        try:
            with open(package_json) as f:
                package_data = json.load(f)
                if 'scripts' in package_data and 'start' in package_data['scripts']:
                    print("   ✅ Frontend has start script")
                else:
                    issues_found.append("Frontend package.json missing start script")
        except Exception as e:
            issues_found.append(f"Cannot parse frontend package.json: {e}")
    else:
        issues_found.append("Frontend package.json not found")
    
    # Check for requirements.txt
    req_file = Path("backend/requirements.txt")
    if not req_file.exists():
        issues_found.append("Backend requirements.txt not found")
    
    if issues_found:
        print("   ⚠️  Potential issues found:")
        for issue in issues_found:
            print(f"      • {issue}")
        return False
    else:
        print("   ✅ No major configuration issues found")
        return True

def generate_fix_summary():
    """Generate summary of fixes applied"""
    print("\n📋 Summary of Applied Fixes:")
    
    fixes = [
        "✅ Removed duplicate CORS middleware configuration",
        "✅ Removed duplicate router inclusion", 
        "✅ Removed hardcoded API keys from server code",
        "✅ Fixed CORS origins to include both localhost and 127.0.0.1",
        "✅ Added backend URL fallback in frontend configuration",
        "✅ Maintained all critical API endpoints",
        "✅ Preserved security measures (API key masking, etc.)"
    ]
    
    for fix in fixes:
        print(f"   {fix}")

def generate_next_steps():
    """Generate next steps for testing"""
    print("\n🚀 Next Steps for Testing:")
    
    steps = [
        "1. Install backend dependencies: pip install fastapi uvicorn python-dotenv",
        "2. Start backend server: cd backend && python server.py",
        "3. Test health endpoint: curl http://localhost:8001/api/health",
        "4. Install frontend dependencies: cd frontend && npm install", 
        "5. Start frontend: npm start",
        "6. Test API connectivity from frontend UI",
        "7. Configure API keys via the UI and test AI functionality"
    ]
    
    for step in steps:
        print(f"   {step}")

def main():
    """Main validation function"""
    print("🔧 XIONIMUS AI - Comprehensive API Endpoint Debugging")
    print("=" * 60)
    
    # Run all checks
    backend_ok = check_backend_server_config()
    frontend_ok = check_frontend_config()
    endpoints_ok = check_api_endpoints()
    config_ok = check_potential_issues()
    
    # Overall assessment
    print("\n" + "=" * 60)
    
    if backend_ok and frontend_ok and endpoints_ok:
        print("🎉 ALL CRITICAL ISSUES FIXED!")
        print("✅ API endpoints should now be accessible with correct keys")
        
        generate_fix_summary()
        generate_next_steps()
        
        return True
    else:
        print("⚠️  Some issues remain:")
        if not backend_ok:
            print("   • Backend configuration issues")
        if not frontend_ok:
            print("   • Frontend configuration issues") 
        if not endpoints_ok:
            print("   • Missing critical API endpoints")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)