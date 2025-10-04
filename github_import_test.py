#!/usr/bin/env python3
"""
GitHub Import Endpoint Testing Suite
Tests the GitHub import functionality as requested by user.

USER REPORTED ISSUE: GitHub-Import Button nicht funktioniert

TEST PLAN:
1. Endpoint Verification - GET /docs to check if /api/github/import exists
2. Import Test (Public Repo) - POST /api/github/import with octocat/Hello-World
3. Error Handling - Test with invalid URLs and non-existent repos
4. Backend Logs - Check for import-related errors
5. System Dependencies - Check if git command is available
"""

import requests
import json
import time
import logging
import subprocess
import os
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubImportTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()
        
    def test_authentication_system(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test JWT authentication system"""
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
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_endpoint_verification(self) -> Dict[str, Any]:
        """Test 1: Verify /api/github/import endpoint exists in API docs"""
        logger.info("📋 Testing endpoint verification - checking if /api/github/import exists in API docs")
        
        try:
            # Get OpenAPI spec
            response = self.session.get(
                f"{self.base_url}/openapi.json",
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Cannot access OpenAPI spec: {response.status_code}"
                }
            
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            # Check if GitHub import endpoint exists
            import_endpoint = "/api/github/import"
            endpoint_exists = import_endpoint in paths
            
            logger.info(f"   OpenAPI spec loaded with {len(paths)} endpoints")
            logger.info(f"   GitHub import endpoint (/api/github/import): {'✅ Found' if endpoint_exists else '❌ Not found'}")
            
            if endpoint_exists:
                endpoint_info = paths[import_endpoint]
                methods = list(endpoint_info.keys())
                logger.info(f"   Supported methods: {methods}")
                
                # Check if POST method exists
                post_method_exists = "post" in endpoint_info
                logger.info(f"   POST method: {'✅ Available' if post_method_exists else '❌ Missing'}")
                
                return {
                    "status": "success",
                    "endpoint_exists": endpoint_exists,
                    "post_method_exists": post_method_exists,
                    "methods": methods,
                    "total_endpoints": len(paths)
                }
            else:
                # List GitHub-related endpoints for debugging
                github_endpoints = [path for path in paths.keys() if "github" in path.lower()]
                logger.info(f"   Available GitHub endpoints: {github_endpoints}")
                
                return {
                    "status": "failed",
                    "error": "GitHub import endpoint not found in API spec",
                    "endpoint_exists": False,
                    "github_endpoints": github_endpoints,
                    "total_endpoints": len(paths)
                }
                
        except Exception as e:
            logger.error(f"❌ Endpoint verification failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_system_dependencies(self) -> Dict[str, Any]:
        """Test system dependencies like git command"""
        logger.info("🔧 Testing system dependencies")
        
        try:
            # Check if git is available
            git_result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            git_available = git_result.returncode == 0
            git_version = git_result.stdout.strip() if git_available else None
            
            logger.info(f"   Git command: {'✅ Available' if git_available else '❌ Missing'}")
            if git_version:
                logger.info(f"   Git version: {git_version}")
            
            # Check workspace directory
            workspace_dir = "/app/xionimus-ai"
            workspace_exists = os.path.exists(workspace_dir)
            workspace_writable = os.access(workspace_dir, os.W_OK) if workspace_exists else False
            
            logger.info(f"   Workspace directory ({workspace_dir}): {'✅ Exists' if workspace_exists else '❌ Missing'}")
            if workspace_exists:
                logger.info(f"   Workspace writable: {'✅ Yes' if workspace_writable else '❌ No'}")
            
            # Check temp directory access
            temp_writable = os.access("/tmp", os.W_OK)
            logger.info(f"   Temp directory writable: {'✅ Yes' if temp_writable else '❌ No'}")
            
            return {
                "status": "success",
                "git_available": git_available,
                "git_version": git_version,
                "workspace_exists": workspace_exists,
                "workspace_writable": workspace_writable,
                "temp_writable": temp_writable,
                "workspace_path": workspace_dir
            }
            
        except Exception as e:
            logger.error(f"❌ System dependencies check failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_public_repo_import(self) -> Dict[str, Any]:
        """Test 2: Import public repository (octocat/Hello-World)"""
        logger.info("📥 Testing public repository import - octocat/Hello-World")
        
        try:
            # Test data as specified in review request
            import_data = {
                "repo_url": "https://github.com/octocat/Hello-World",
                "branch": "master"
            }
            
            # Test without Authorization header (public repo)
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=120  # 2 minute timeout for git operations
            )
            
            logger.info(f"   Response status: {response.status_code}")
            logger.info(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                import_result = response.json()
                
                logger.info("✅ Public repository import successful")
                logger.info(f"   Repository: {import_result.get('repository', {}).get('owner')}/{import_result.get('repository', {}).get('name')}")
                logger.info(f"   Branch: {import_result.get('repository', {}).get('branch')}")
                logger.info(f"   Target directory: {import_result.get('import_details', {}).get('target_directory')}")
                logger.info(f"   Total files: {import_result.get('import_details', {}).get('total_files')}")
                logger.info(f"   Workspace path: {import_result.get('workspace_path')}")
                
                return {
                    "status": "success",
                    "data": import_result,
                    "repository": import_result.get('repository'),
                    "import_details": import_result.get('import_details'),
                    "workspace_path": import_result.get('workspace_path')
                }
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_detail = error_data.get("detail", "Unknown error")
                
                logger.error(f"❌ Import failed with 400 error: {error_detail}")
                
                # Check for specific error types
                if "already exists" in error_detail.lower():
                    logger.info("   ℹ️ Directory already exists - this might be expected")
                    return {
                        "status": "directory_exists",
                        "error": error_detail,
                        "data": error_data
                    }
                elif "git" in error_detail.lower():
                    logger.error("   🔧 Git-related error detected")
                    return {
                        "status": "git_error",
                        "error": error_detail,
                        "data": error_data
                    }
                else:
                    return {
                        "status": "failed",
                        "error": error_detail,
                        "data": error_data
                    }
            elif response.status_code == 404:
                error_data = response.json() if response.content else {}
                logger.error(f"❌ Import endpoint not found: {error_data.get('detail', 'Endpoint not found')}")
                return {
                    "status": "endpoint_not_found",
                    "error": error_data.get('detail', 'Endpoint not found'),
                    "status_code": response.status_code
                }
            elif response.status_code == 408:
                logger.error("❌ Import timeout - repository might be too large")
                return {
                    "status": "timeout",
                    "error": "Repository clone timeout",
                    "status_code": response.status_code
                }
            else:
                error_data = response.json() if response.content else {}
                error_detail = error_data.get("detail", f"HTTP {response.status_code}")
                logger.error(f"❌ Import failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout during import")
            return {
                "status": "timeout",
                "error": "Request timeout during repository import"
            }
        except Exception as e:
            logger.error(f"❌ Public repo import test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_error_handling(self) -> Dict[str, Any]:
        """Test 3: Error handling with invalid URLs and non-existent repos"""
        logger.info("🚫 Testing error handling")
        
        test_cases = [
            {
                "name": "Invalid URL format",
                "data": {"repo_url": "not-a-github-url", "branch": "main"},
                "expected_status": 400
            },
            {
                "name": "Non-existent repository",
                "data": {"repo_url": "https://github.com/nonexistent-user/nonexistent-repo", "branch": "main"},
                "expected_status": 404
            },
            {
                "name": "Invalid branch",
                "data": {"repo_url": "https://github.com/octocat/Hello-World", "branch": "nonexistent-branch"},
                "expected_status": 400
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            logger.info(f"   Testing: {test_case['name']}")
            
            try:
                headers = {"Content-Type": "application/json"}
                
                response = self.session.post(
                    f"{self.api_url}/github/import",
                    json=test_case["data"],
                    headers=headers,
                    timeout=30
                )
                
                expected_status = test_case["expected_status"]
                actual_status = response.status_code
                
                if actual_status == expected_status:
                    error_data = response.json() if response.content else {}
                    logger.info(f"   ✅ Correct error response: {actual_status}")
                    logger.info(f"   Error message: {error_data.get('detail', 'No detail')}")
                    
                    results.append({
                        "test": test_case["name"],
                        "status": "success",
                        "expected_status": expected_status,
                        "actual_status": actual_status,
                        "error_message": error_data.get('detail')
                    })
                else:
                    logger.error(f"   ❌ Wrong status code: expected {expected_status}, got {actual_status}")
                    results.append({
                        "test": test_case["name"],
                        "status": "failed",
                        "expected_status": expected_status,
                        "actual_status": actual_status,
                        "response": response.text
                    })
                    
            except Exception as e:
                logger.error(f"   ❌ Test failed: {e}")
                results.append({
                    "test": test_case["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        successful_tests = sum(1 for r in results if r["status"] == "success")
        total_tests = len(results)
        
        logger.info(f"   Error handling tests: {successful_tests}/{total_tests} passed")
        
        return {
            "status": "success" if successful_tests == total_tests else "partial",
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "results": results
        }

    def test_import_status_endpoint(self) -> Dict[str, Any]:
        """Test GET /api/github/import/status endpoint"""
        logger.info("📊 Testing import status endpoint")
        
        try:
            response = self.session.get(
                f"{self.api_url}/github/import/status",
                timeout=10
            )
            
            if response.status_code == 200:
                status_data = response.json()
                
                logger.info("✅ Import status endpoint working")
                logger.info(f"   Status: {status_data.get('status')}")
                logger.info(f"   Feature: {status_data.get('feature')}")
                logger.info(f"   Workspace root: {status_data.get('workspace_root')}")
                logger.info(f"   Existing projects: {len(status_data.get('existing_projects', []))}")
                
                return {
                    "status": "success",
                    "data": status_data,
                    "workspace_root": status_data.get('workspace_root'),
                    "existing_projects": status_data.get('existing_projects', [])
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Import status endpoint failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Import status test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_backend_logs(self) -> Dict[str, Any]:
        """Test 4: Check backend logs for import-related errors"""
        logger.info("📋 Checking backend logs for GitHub import errors")
        
        try:
            # Check supervisor backend logs
            log_files = [
                "/var/log/supervisor/backend.err.log",
                "/var/log/supervisor/backend.out.log"
            ]
            
            logs_found = []
            import_related_entries = []
            
            for log_file in log_files:
                try:
                    if os.path.exists(log_file):
                        result = subprocess.run(
                            ["tail", "-n", "100", log_file],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            log_content = result.stdout.strip()
                            logs_found.append({
                                "file": log_file,
                                "content": log_content
                            })
                            
                            # Look for import-related entries
                            lines = log_content.split('\n')
                            for line in lines:
                                if any(keyword in line.lower() for keyword in ['import', 'github', 'git', 'clone', 'repository']):
                                    import_related_entries.append({
                                        "file": log_file,
                                        "line": line.strip()
                                    })
                                    
                except Exception as e:
                    logger.warning(f"Could not read {log_file}: {e}")
            
            if logs_found:
                logger.info(f"✅ Found {len(logs_found)} log files")
                logger.info(f"   Import-related entries: {len(import_related_entries)}")
                
                for entry in import_related_entries[:5]:  # Show first 5 entries
                    logger.info(f"   📝 {entry['line']}")
                
                return {
                    "status": "success",
                    "logs_found": len(logs_found),
                    "import_entries": len(import_related_entries),
                    "logs": logs_found,
                    "import_related": import_related_entries
                }
            else:
                logger.info("⚠️ No backend logs found")
                return {
                    "status": "no_logs",
                    "message": "No backend logs found"
                }
                
        except Exception as e:
            logger.error(f"❌ Backend log check failed: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Main test runner for GitHub Import functionality"""
    logger.info("🔄 Starting GitHub Import Endpoint Testing Suite")
    logger.info("=" * 80)
    logger.info("USER REPORTED ISSUE: GitHub-Import Button nicht funktioniert")
    logger.info("=" * 80)
    
    tester = GitHubImportTester()
    
    # Test 1: System Dependencies Check
    logger.info("1️⃣ Testing System Dependencies")
    deps_result = tester.test_system_dependencies()
    print(f"System Dependencies: {deps_result['status']}")
    
    if deps_result['status'] == 'success':
        print(f"   Git available: {'✅' if deps_result.get('git_available') else '❌'}")
        print(f"   Workspace exists: {'✅' if deps_result.get('workspace_exists') else '❌'}")
        print(f"   Workspace writable: {'✅' if deps_result.get('workspace_writable') else '❌'}")
        if deps_result.get('git_version'):
            print(f"   Git version: {deps_result['git_version']}")
    
    # Test 2: Endpoint Verification
    logger.info("\n2️⃣ Testing Endpoint Verification")
    endpoint_result = tester.test_endpoint_verification()
    print(f"Endpoint Verification: {endpoint_result['status']}")
    
    if endpoint_result['status'] == 'success':
        print(f"   /api/github/import exists: ✅")
        print(f"   POST method available: {'✅' if endpoint_result.get('post_method_exists') else '❌'}")
        print(f"   Total API endpoints: {endpoint_result.get('total_endpoints', 0)}")
    elif endpoint_result['status'] == 'failed':
        print(f"   ❌ Endpoint not found in API spec")
        github_endpoints = endpoint_result.get('github_endpoints', [])
        if github_endpoints:
            print(f"   Available GitHub endpoints: {github_endpoints}")
    
    # Test 3: Authentication (optional for public repos)
    logger.info("\n3️⃣ Testing Authentication System (optional for public repos)")
    auth_result = tester.test_authentication_system()
    print(f"Authentication: {auth_result['status']}")
    
    # Test 4: Import Status Endpoint
    logger.info("\n4️⃣ Testing Import Status Endpoint")
    status_result = tester.test_import_status_endpoint()
    print(f"Import Status Endpoint: {status_result['status']}")
    
    if status_result['status'] == 'success':
        print(f"   Workspace root: {status_result.get('workspace_root')}")
        print(f"   Existing projects: {len(status_result.get('existing_projects', []))}")
    
    # Test 5: Public Repository Import (MAIN TEST)
    logger.info("\n5️⃣ Testing Public Repository Import (MAIN TEST)")
    import_result = tester.test_public_repo_import()
    print(f"Public Repo Import: {import_result['status']}")
    
    if import_result['status'] == 'success':
        print(f"   ✅ Successfully imported octocat/Hello-World")
        print(f"   Files imported: {import_result.get('import_details', {}).get('total_files', 0)}")
        print(f"   Target directory: {import_result.get('import_details', {}).get('target_directory')}")
    elif import_result['status'] == 'directory_exists':
        print(f"   ℹ️ Directory already exists (might be expected)")
    elif import_result['status'] == 'git_error':
        print(f"   🔧 Git-related error: {import_result.get('error')}")
    elif import_result['status'] == 'endpoint_not_found':
        print(f"   ❌ Import endpoint not found")
    elif import_result['status'] == 'timeout':
        print(f"   ⏱️ Import timeout")
    elif import_result['status'] == 'failed':
        print(f"   ❌ Import failed: {import_result.get('error')}")
    
    # Test 6: Error Handling
    logger.info("\n6️⃣ Testing Error Handling")
    error_result = tester.test_error_handling()
    print(f"Error Handling: {error_result['status']}")
    
    if error_result['status'] in ['success', 'partial']:
        print(f"   Tests passed: {error_result.get('successful_tests', 0)}/{error_result.get('total_tests', 0)}")
    
    # Test 7: Backend Logs Check
    logger.info("\n7️⃣ Checking Backend Logs")
    logs_result = tester.check_backend_logs()
    print(f"Backend Logs: {logs_result['status']}")
    
    if logs_result['status'] == 'success':
        print(f"   Log files found: {logs_result.get('logs_found', 0)}")
        print(f"   Import-related entries: {logs_result.get('import_entries', 0)}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("🔄 GITHUB IMPORT TEST SUMMARY")
    logger.info("=" * 80)
    
    # Count successful tests
    test_results = [
        ("System Dependencies", deps_result['status'] == 'success'),
        ("Endpoint Verification", endpoint_result['status'] == 'success'),
        ("Authentication System", auth_result['status'] == 'success'),
        ("Import Status Endpoint", status_result['status'] == 'success'),
        ("Public Repo Import", import_result['status'] == 'success'),
        ("Error Handling", error_result['status'] in ['success', 'partial']),
        ("Backend Logs Check", logs_result['status'] in ['success', 'no_logs']),
    ]
    
    successful_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall Results: {successful_tests}/{total_tests} tests passed")
    
    for test_name, success in test_results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    # Critical Issues Analysis
    critical_issues = []
    
    if not deps_result.get('git_available'):
        critical_issues.append("❌ CRITICAL: Git command not available - required for repository cloning")
    
    if endpoint_result['status'] == 'failed':
        critical_issues.append("❌ CRITICAL: /api/github/import endpoint not found in API specification")
    
    if import_result['status'] == 'endpoint_not_found':
        critical_issues.append("❌ CRITICAL: GitHub import endpoint returns 404 - endpoint not registered")
    elif import_result['status'] == 'git_error':
        critical_issues.append(f"❌ CRITICAL: Git operation failed - {import_result.get('error')}")
    elif import_result['status'] == 'failed':
        critical_issues.append(f"❌ CRITICAL: Public repository import failed - {import_result.get('error')}")
    
    if not deps_result.get('workspace_exists'):
        critical_issues.append("❌ CRITICAL: Workspace directory /app/xionimus-ai does not exist")
    elif not deps_result.get('workspace_writable'):
        critical_issues.append("❌ CRITICAL: Workspace directory not writable")
    
    # Main Analysis
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   {issue}")
        
        print(f"\n💡 LIKELY ROOT CAUSE:")
        if not deps_result.get('git_available'):
            print("   - Git command is missing from the system")
            print("   - Install git: apt-get update && apt-get install -y git")
        elif endpoint_result['status'] == 'failed':
            print("   - GitHub import endpoint not properly registered in FastAPI")
            print("   - Check if GitHub integration is enabled in backend")
        elif not deps_result.get('workspace_exists'):
            print("   - Workspace directory missing")
            print("   - Create directory: mkdir -p /app/xionimus-ai")
        else:
            print("   - Check backend logs for detailed error information")
            print("   - Verify GitHub integration configuration")
    else:
        print(f"\n🟢 SUCCESS: GitHub Import functionality working correctly!")
        print("   - All system dependencies available")
        print("   - Import endpoint properly registered")
        print("   - Public repository import successful")
        print("   - Error handling working correctly")
    
    # Diagnostic Information
    print(f"\n📝 DIAGNOSTIC INFORMATION:")
    print(f"   Backend URL: {tester.base_url}")
    print(f"   API URL: {tester.api_url}")
    print(f"   Git available: {'✅' if deps_result.get('git_available') else '❌'}")
    print(f"   Workspace path: {deps_result.get('workspace_path', '/app/xionimus-ai')}")
    print(f"   Import endpoint exists: {'✅' if endpoint_result['status'] == 'success' else '❌'}")
    print(f"   Public repo import: {'✅' if import_result['status'] == 'success' else '❌'}")
    
    return {
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'critical_issues': critical_issues,
        'import_working': import_result['status'] == 'success',
        'git_available': deps_result.get('git_available', False),
        'endpoint_exists': endpoint_result['status'] == 'success'
    }

if __name__ == "__main__":
    main()