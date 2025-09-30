#!/usr/bin/env python3
"""
Backend Startup Test
Tests that all modules load correctly
"""
import sys
import traceback

def test_imports():
    """Test all critical imports"""
    tests = []
    
    # Test 1: Config
    try:
        from app.core.config import settings
        tests.append(("Config", True, None))
    except Exception as e:
        tests.append(("Config", False, str(e)))
    
    # Test 2: Database
    try:
        from app.core.database import init_database
        tests.append(("Database", True, None))
    except Exception as e:
        tests.append(("Database", False, str(e)))
    
    # Test 3: Auth
    try:
        from app.core.auth import get_current_user
        tests.append(("Auth", True, None))
    except Exception as e:
        tests.append(("Auth", False, str(e)))
    
    # Test 4: Rate Limiting
    try:
        from app.core.rate_limit import limiter
        tests.append(("Rate Limit", True, None))
    except Exception as e:
        tests.append(("Rate Limit", False, str(e)))
    
    # Test 5: File Validator
    try:
        from app.core.file_validator import validate_upload
        tests.append(("File Validator", True, None))
    except Exception as e:
        tests.append(("File Validator", False, str(e)))
    
    # Test 6: Errors
    try:
        from app.core.errors import XionimusException
        tests.append(("Errors", True, None))
    except Exception as e:
        tests.append(("Errors", False, str(e)))
    
    # Test 7: API Routes
    try:
        from app.api import chat, auth, sessions
        tests.append(("API Routes", True, None))
    except Exception as e:
        tests.append(("API Routes", False, str(e)))
    
    return tests

def main():
    print("\n" + "="*60)
    print("Backend Startup Test")
    print("="*60 + "\n")
    
    results = test_imports()
    
    passed = 0
    failed = 0
    
    for name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} | {name:20}", end="")
        if error:
            print(f" | {error[:40]}")
            failed += 1
        else:
            print()
            passed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed > 0:
        print("❌ Some tests failed. Check errors above.")
        return 1
    else:
        print("✅ All imports successful! Backend ready to start.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
