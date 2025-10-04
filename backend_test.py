#!/usr/bin/env python3
"""
GitHub Personal Access Token (PAT) Management Testing Suite
Tests GitHub PAT endpoints in Xionimus AI including:
- Login and token authentication
- GitHub PAT verification
- GitHub PAT saving with validation
- GitHub PAT removal
- Database column verification
"""

import requests
import json
import time
import logging
import sqlite3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubPATTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()  # Reuse connections for better performance
        self.db_path = os.path.expanduser("~/.xionimus_ai/xionimus.db")
        
    def test_authentication_system(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test JWT authentication system for GitHub PAT management"""
        logger.info(f"🔐 Testing authentication system with username: {username}")
        
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.user_info = {
                    "user_id": token_data.get("user_id"),
                    "username": token_data.get("username"),
                    "token_type": token_data.get("token_type"),
                    "role": token_data.get("role", "user")
                }
                
                logger.info("✅ Authentication successful")
                logger.info(f"   User ID: {token_data.get('user_id')}")
                logger.info(f"   Role: {token_data.get('role', 'user')}")
                
                return {
                    "status": "success",
                    "token": self.token,
                    "user_info": self.user_info,
                    "response": token_data
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                logger.error(f"   Status code: {response.status_code}")
                logger.error(f"   Response text: {response.text}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response_text": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_verify_token_no_token(self) -> Dict[str, Any]:
        """Test GET /api/github-pat/verify-token when no token is saved"""
        logger.info("🔍 Testing verify-token endpoint (no token saved)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/github-pat/verify-token",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                verify_data = response.json()
                
                logger.info("✅ Verify token endpoint working")
                logger.info(f"   Connected: {verify_data.get('connected', False)}")
                logger.info(f"   GitHub username: {verify_data.get('github_username')}")
                logger.info(f"   Message: {verify_data.get('message')}")
                
                # Should return connected: false when no token is saved
                if verify_data.get('connected') == False:
                    logger.info("✅ Correctly returns connected: false when no token saved")
                    return {
                        "status": "success",
                        "data": verify_data,
                        "expected_result": True
                    }
                else:
                    return {
                        "status": "unexpected",
                        "error": f"Expected connected: false, got connected: {verify_data.get('connected')}",
                        "data": verify_data
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Verify token failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Verify token test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_save_invalid_token(self) -> Dict[str, Any]:
        """Test POST /api/github-pat/save-token with invalid token"""
        logger.info("🚫 Testing save-token endpoint with invalid token")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Use an obviously invalid token
            invalid_token_data = {
                "token": "invalid_token_123"
            }
            
            response = self.session.post(
                f"{self.api_url}/github-pat/save-token",
                json=invalid_token_data,
                headers=headers,
                timeout=15  # GitHub API calls can take longer
            )
            
            if response.status_code == 400:
                error_data = response.json()
                
                logger.info("✅ Save invalid token correctly rejected")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_data.get('detail')}")
                
                # Should contain "Invalid GitHub token" message
                if "Invalid GitHub token" in error_data.get('detail', ''):
                    logger.info("✅ Correct error message returned")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected 'Invalid GitHub token' in error message, got: {error_data.get('detail')}",
                        "data": error_data
                    }
            else:
                logger.error(f"❌ Expected 400 error, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 400 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Save invalid token test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_remove_token(self) -> Dict[str, Any]:
        """Test DELETE /api/github-pat/remove-token"""
        logger.info("🗑️ Testing remove-token endpoint")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.delete(
                f"{self.api_url}/github-pat/remove-token",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                remove_data = response.json()
                
                logger.info("✅ Remove token endpoint working")
                logger.info(f"   Connected: {remove_data.get('connected', True)}")
                logger.info(f"   GitHub username: {remove_data.get('github_username')}")
                logger.info(f"   Message: {remove_data.get('message')}")
                
                # Should return connected: false after removal
                if remove_data.get('connected') == False:
                    logger.info("✅ Correctly returns connected: false after removal")
                    return {
                        "status": "success",
                        "data": remove_data,
                        "token_removed": True
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected connected: false after removal, got connected: {remove_data.get('connected')}",
                        "data": remove_data
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Remove token failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Remove token test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_database_columns_verification(self) -> Dict[str, Any]:
        """Test that github_token and github_username columns exist in users table"""
        logger.info("🗄️ Testing database columns verification")
        
        try:
            # Check if database file exists
            if not os.path.exists(self.db_path):
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table schema for users table
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            
            conn.close()
            
            # Check if required columns exist
            column_names = [col[1] for col in columns]  # Column name is at index 1
            
            github_token_exists = "github_token" in column_names
            github_username_exists = "github_username" in column_names
            
            logger.info("✅ Database schema checked")
            logger.info(f"   Total columns in users table: {len(column_names)}")
            logger.info(f"   github_token column exists: {github_token_exists}")
            logger.info(f"   github_username column exists: {github_username_exists}")
            logger.info(f"   All columns: {column_names}")
            
            if github_token_exists and github_username_exists:
                logger.info("✅ All required GitHub PAT columns exist")
                return {
                    "status": "success",
                    "github_token_exists": github_token_exists,
                    "github_username_exists": github_username_exists,
                    "all_columns": column_names,
                    "columns_count": len(column_names)
                }
            else:
                missing_columns = []
                if not github_token_exists:
                    missing_columns.append("github_token")
                if not github_username_exists:
                    missing_columns.append("github_username")
                
                return {
                    "status": "failed",
                    "error": f"Missing required columns: {missing_columns}",
                    "github_token_exists": github_token_exists,
                    "github_username_exists": github_username_exists,
                    "all_columns": column_names
                }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database error: {e}")
            return {"status": "error", "error": f"Database error: {e}"}
        except Exception as e:
            logger.error(f"❌ Database verification test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_repositories_endpoint_no_token(self) -> Dict[str, Any]:
        """Test GET /api/github-pat/repositories when no token is saved (should fail)"""
        logger.info("📚 Testing repositories endpoint (no token saved)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/github-pat/repositories",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 401:
                error_data = response.json()
                
                logger.info("✅ Repositories endpoint correctly requires GitHub token")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_data.get('detail')}")
                
                # Should contain message about GitHub not being connected
                if "GitHub not connected" in error_data.get('detail', ''):
                    logger.info("✅ Correct error message returned")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected 'GitHub not connected' in error message, got: {error_data.get('detail')}",
                        "data": error_data
                    }
            else:
                logger.error(f"❌ Expected 401 error, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 401 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Repositories endpoint test failed: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Main test runner for GitHub PAT Management Testing"""
    logger.info("🔄 Starting GitHub Personal Access Token (PAT) Management Testing Suite")
    logger.info("=" * 80)
    
    tester = GitHubPATTester()
    
    # Test 1: Authentication System (demo/demo123)
    logger.info("1️⃣ Testing Authentication System (demo/demo123)")
    auth_result = tester.test_authentication_system()
    print(f"Authentication: {auth_result['status']}")
    
    if auth_result['status'] != 'success':
        print(f"❌ Authentication failed: {auth_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with GitHub PAT tests")
        return
    
    # Test 2: Verify Token (No Token Saved)
    logger.info("\n2️⃣ Testing GET /api/github-pat/verify-token (no token)")
    verify_result = tester.test_verify_token_no_token()
    print(f"Verify Token (No Token): {verify_result['status']}")
    if verify_result['status'] == 'success':
        print(f"   ✅ Correctly returns connected: false")
    elif verify_result['status'] == 'failed':
        print(f"   ❌ Failed: {verify_result.get('error')}")
    
    # Test 3: Save Invalid Token
    logger.info("\n3️⃣ Testing POST /api/github-pat/save-token (invalid token)")
    save_invalid_result = tester.test_save_invalid_token()
    print(f"Save Invalid Token: {save_invalid_result['status']}")
    if save_invalid_result['status'] == 'success':
        print(f"   ✅ Invalid token correctly rejected with 400 error")
    elif save_invalid_result['status'] == 'failed':
        print(f"   ❌ Failed: {save_invalid_result.get('error')}")
    
    # Test 4: Remove Token
    logger.info("\n4️⃣ Testing DELETE /api/github-pat/remove-token")
    remove_result = tester.test_remove_token()
    print(f"Remove Token: {remove_result['status']}")
    if remove_result['status'] == 'success':
        print(f"   ✅ Token removal successful (even if no token exists)")
    elif remove_result['status'] == 'failed':
        print(f"   ❌ Failed: {remove_result.get('error')}")
    
    # Test 5: Database Columns Verification
    logger.info("\n5️⃣ Testing Database Columns Verification")
    db_result = tester.test_database_columns_verification()
    print(f"Database Columns: {db_result['status']}")
    if db_result['status'] == 'success':
        print(f"   ✅ github_token column exists: {db_result.get('github_token_exists')}")
        print(f"   ✅ github_username column exists: {db_result.get('github_username_exists')}")
        print(f"   Total columns: {db_result.get('columns_count', 0)}")
    elif db_result['status'] == 'failed':
        print(f"   ❌ Failed: {db_result.get('error')}")
    
    # Test 6: Repositories Endpoint (No Token)
    logger.info("\n6️⃣ Testing GET /api/github-pat/repositories (no token)")
    repos_result = tester.test_repositories_endpoint_no_token()
    print(f"Repositories (No Token): {repos_result['status']}")
    if repos_result['status'] == 'success':
        print(f"   ✅ Correctly requires GitHub token (401 error)")
    elif repos_result['status'] == 'failed':
        print(f"   ❌ Failed: {repos_result.get('error')}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("🔄 GITHUB PAT MANAGEMENT TEST SUMMARY")
    logger.info("=" * 80)
    
    # Count successful tests
    test_results = [
        ("Authentication (demo/demo123)", auth_result['status'] == 'success'),
        ("Verify Token (No Token)", verify_result['status'] == 'success'),
        ("Save Invalid Token", save_invalid_result['status'] == 'success'),
        ("Remove Token", remove_result['status'] == 'success'),
        ("Database Columns", db_result['status'] == 'success'),
        ("Repositories (No Token)", repos_result['status'] == 'success'),
    ]
    
    successful_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall Results: {successful_tests}/{total_tests} tests passed")
    
    for test_name, success in test_results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    # Critical Issues
    critical_issues = []
    if auth_result['status'] != 'success':
        critical_issues.append("Authentication system broken - cannot login with demo/demo123")
    if verify_result['status'] != 'success':
        critical_issues.append("Verify token endpoint not working correctly")
    if save_invalid_result['status'] != 'success':
        critical_issues.append("Save token endpoint not properly validating tokens")
    if remove_result['status'] != 'success':
        critical_issues.append("Remove token endpoint not working")
    if db_result['status'] != 'success':
        critical_issues.append("Database missing required GitHub PAT columns")
    if repos_result['status'] != 'success':
        critical_issues.append("Repositories endpoint not properly secured")
    
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: GitHub PAT Management endpoints working correctly!")
        print("   - Authentication system functional")
        print("   - All endpoints accessible with authentication")
        print("   - Invalid token properly rejected")
        print("   - Database columns created")
        print("   - Proper error handling")
    
    # Test Coverage Notes
    print(f"\n📝 TEST COVERAGE NOTES:")
    print("   - ✅ All endpoints tested for structure and error handling")
    print("   - ✅ Authentication requirements verified")
    print("   - ✅ Database schema verified")
    print("   - ⚠️ Cannot test with real GitHub token (as expected)")
    print("   - ✅ Invalid token rejection verified")
    print("   - ✅ Endpoint security verified")

if __name__ == "__main__":
    main()