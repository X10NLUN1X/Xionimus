#!/usr/bin/env python3
"""
GitHub Import Functionality Testing Suite (WITHOUT Authentication)
Tests the GitHub import functionality without authentication as requested:
- Test public repo import WITHOUT auth (POST /api/github/import)
- Test invalid URL handling
- Test non-existent repo handling  
- Verify import status endpoint WITHOUT auth (GET /api/github/import/status)
"""

import requests
import json
import time
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubImportTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()  # Reuse connections for better performance

    def test_public_repo_import_without_auth(self) -> Dict[str, Any]:
        """Test POST /api/github/import with public repo WITHOUT authentication"""
        logger.info("🔓 Testing public repo import WITHOUT authentication")
        
        try:
            # Test with octocat/Hello-World as specified in the review request
            import_data = {
                "repo_url": "https://github.com/octocat/Hello-World",
                "branch": "master"
            }
            
            # NO Authorization header - this is the key test
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=30  # Git clone can take time
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                import_result = response.json()
                
                logger.info("✅ Public repo import WITHOUT auth successful!")
                logger.info(f"   Repository: {import_result.get('repository', {}).get('owner')}/{import_result.get('repository', {}).get('name')}")
                logger.info(f"   Branch: {import_result.get('repository', {}).get('branch')}")
                logger.info(f"   Total files: {import_result.get('import_details', {}).get('total_files', 0)}")
                logger.info(f"   Target directory: {import_result.get('import_details', {}).get('target_directory')}")
                
                return {
                    "status": "success",
                    "data": import_result,
                    "repository": import_result.get('repository', {}),
                    "import_details": import_result.get('import_details', {}),
                    "no_auth_required": True
                }
            elif response.status_code == 401:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ CRITICAL: Still requires authentication! {error_detail}")
                return {
                    "status": "failed",
                    "error": f"Import still requires authentication: {error_detail}",
                    "status_code": response.status_code,
                    "critical_issue": "Authentication still required for public repos"
                }
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                if "already exists" in error_detail:
                    logger.info("⚠️ Directory already exists - this is expected behavior")
                    return {
                        "status": "success",
                        "message": "Directory already exists (expected behavior)",
                        "no_auth_required": True
                    }
                else:
                    logger.error(f"❌ Bad request: {error_detail}")
                    return {
                        "status": "failed",
                        "error": error_detail,
                        "status_code": response.status_code
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Import failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Public repo import test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_invalid_url_import(self) -> Dict[str, Any]:
        """Test POST /api/github/import with invalid URL"""
        logger.info("🚫 Testing import with invalid URL")
        
        try:
            import_data = {
                "repo_url": "https://invalid-url.com/repo",
                "branch": "main"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=15
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code in [400, 404]:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                
                logger.info("✅ Invalid URL correctly rejected")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_detail}")
                
                # Should contain message about invalid URL
                if "Invalid GitHub URL" in error_detail or "github.com" in error_detail:
                    logger.info("✅ Correct error message for invalid URL")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True,
                        "error_message": error_detail
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected GitHub URL validation error, got: {error_detail}",
                        "data": error_data
                    }
            else:
                logger.error(f"❌ Expected 400/404 error, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 400/404 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Invalid URL test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_nonexistent_repo_import(self) -> Dict[str, Any]:
        """Test POST /api/github/import with non-existent repository"""
        logger.info("🔍 Testing import with non-existent repository")
        
        try:
            import_data = {
                "repo_url": "https://github.com/nonexistent/nonexistent-repo-12345",
                "branch": "main"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=30  # Git operations can take time
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 404:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                
                logger.info("✅ Non-existent repo correctly rejected")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_detail}")
                
                # Should contain message about repository not found
                if "not found" in error_detail.lower() or "not accessible" in error_detail.lower():
                    logger.info("✅ Correct error message for non-existent repo")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True,
                        "error_message": error_detail
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected 'not found' in error message, got: {error_detail}",
                        "data": error_data
                    }
            elif response.status_code == 400:
                # Could also be 400 with appropriate error message
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                
                if "not found" in error_detail.lower() or "clone failed" in error_detail.lower():
                    logger.info("✅ Non-existent repo correctly rejected (400 with appropriate message)")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True,
                        "error_message": error_detail
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected repository error message, got: {error_detail}",
                        "data": error_data
                    }
            else:
                logger.error(f"❌ Expected 404/400 error, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 404/400 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Non-existent repo test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_import_status_endpoint_without_auth(self) -> Dict[str, Any]:
        """Test GET /api/github/import/status WITHOUT authentication"""
        logger.info("📊 Testing import status endpoint WITHOUT authentication")
        
        try:
            # NO Authorization header
            headers = {"Content-Type": "application/json"}
            
            response = self.session.get(
                f"{self.api_url}/github/import/status",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                
                logger.info("✅ Import status endpoint accessible WITHOUT auth")
                logger.info(f"   Status: {status_data.get('status')}")
                logger.info(f"   Feature: {status_data.get('feature')}")
                logger.info(f"   Workspace root: {status_data.get('workspace_root')}")
                logger.info(f"   Existing projects: {len(status_data.get('existing_projects', []))}")
                
                return {
                    "status": "success",
                    "data": status_data,
                    "no_auth_required": True,
                    "workspace_info": {
                        "root": status_data.get('workspace_root'),
                        "projects_count": len(status_data.get('existing_projects', []))
                    }
                }
            elif response.status_code == 401:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ CRITICAL: Status endpoint still requires authentication! {error_detail}")
                return {
                    "status": "failed",
                    "error": f"Status endpoint still requires authentication: {error_detail}",
                    "status_code": response.status_code,
                    "critical_issue": "Authentication still required for status endpoint"
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Status endpoint failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Import status test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_system_dependencies(self) -> Dict[str, Any]:
        """Check if required system dependencies are available"""
        logger.info("🔧 Checking system dependencies for GitHub import")
        
        try:
            import subprocess
            import os
            from pathlib import Path
            
            # Check if git is available
            try:
                result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
                git_available = result.returncode == 0
                git_version = result.stdout.strip() if git_available else "Not available"
            except:
                git_available = False
                git_version = "Not available"
            
            # Check workspace directory
            workspace_root = Path("/app/xionimus-ai")
            workspace_exists = workspace_root.exists()
            workspace_writable = False
            
            if workspace_exists:
                try:
                    test_file = workspace_root / ".test_write"
                    test_file.write_text("test")
                    test_file.unlink()
                    workspace_writable = True
                except:
                    workspace_writable = False
            else:
                try:
                    workspace_root.mkdir(parents=True, exist_ok=True)
                    workspace_exists = True
                    workspace_writable = True
                except:
                    pass
            
            logger.info(f"✅ System dependencies check completed")
            logger.info(f"   Git available: {git_available} ({git_version})")
            logger.info(f"   Workspace exists: {workspace_exists}")
            logger.info(f"   Workspace writable: {workspace_writable}")
            
            all_dependencies_ok = git_available and workspace_exists and workspace_writable
            
            return {
                "status": "success" if all_dependencies_ok else "partial",
                "git_available": git_available,
                "git_version": git_version,
                "workspace_exists": workspace_exists,
                "workspace_writable": workspace_writable,
                "workspace_path": str(workspace_root),
                "all_dependencies_ok": all_dependencies_ok
            }
            
        except Exception as e:
            logger.error(f"❌ System dependencies check failed: {e}")
            return {"status": "error", "error": str(e)}


def main():
    """Main test runner for GitHub Import Testing WITHOUT Authentication"""
    logger.info("🔄 Starting GitHub Import Functionality Testing Suite (WITHOUT Authentication)")
    logger.info("=" * 80)
    
    tester = GitHubImportTester()
    
    # Test 1: System Dependencies Check
    logger.info("1️⃣ Checking System Dependencies")
    deps_result = tester.check_system_dependencies()
    print(f"System Dependencies: {deps_result['status']}")
    
    if deps_result['status'] == 'error':
        print(f"❌ System dependencies check failed: {deps_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with GitHub import tests")
        return
    elif deps_result['status'] == 'partial':
        print(f"⚠️ Some dependencies missing but continuing tests")
        if not deps_result.get('git_available'):
            print("   ❌ Git not available - import tests will fail")
        if not deps_result.get('workspace_writable'):
            print("   ❌ Workspace not writable - import tests will fail")

    # Test 2: Public Repo Import WITHOUT Auth (MAIN TEST)
    logger.info("\n2️⃣ Testing Public Repo Import WITHOUT Authentication (MAIN TEST)")
    public_import_result = tester.test_public_repo_import_without_auth()
    print(f"Public Repo Import (No Auth): {public_import_result['status']}")
    
    if public_import_result['status'] == 'success':
        if public_import_result.get('no_auth_required'):
            print(f"   ✅ SUCCESS: No authentication required!")
            if 'repository' in public_import_result:
                repo = public_import_result['repository']
                print(f"   ✅ Repository: {repo.get('owner')}/{repo.get('name')}")
                print(f"   ✅ Branch: {repo.get('branch')}")
            if 'import_details' in public_import_result:
                details = public_import_result['import_details']
                print(f"   ✅ Files imported: {details.get('total_files', 0)}")
        else:
            print(f"   ✅ Import successful: {public_import_result.get('message', 'Success')}")
    elif public_import_result['status'] == 'failed':
        print(f"   ❌ FAILED: {public_import_result.get('error')}")
        if public_import_result.get('critical_issue'):
            print(f"   🔴 CRITICAL: {public_import_result['critical_issue']}")
    
    # Test 3: Invalid URL Test
    logger.info("\n3️⃣ Testing Invalid URL Handling")
    invalid_url_result = tester.test_invalid_url_import()
    print(f"Invalid URL Test: {invalid_url_result['status']}")
    
    if invalid_url_result['status'] == 'success':
        print(f"   ✅ Invalid URL correctly rejected")
        print(f"   ✅ Error message: {invalid_url_result.get('error_message', 'N/A')}")
    elif invalid_url_result['status'] == 'failed':
        print(f"   ❌ Failed: {invalid_url_result.get('error')}")
    
    # Test 4: Non-Existent Repo Test
    logger.info("\n4️⃣ Testing Non-Existent Repository Handling")
    nonexistent_repo_result = tester.test_nonexistent_repo_import()
    print(f"Non-Existent Repo Test: {nonexistent_repo_result['status']}")
    
    if nonexistent_repo_result['status'] == 'success':
        print(f"   ✅ Non-existent repo correctly rejected")
        print(f"   ✅ Error message: {nonexistent_repo_result.get('error_message', 'N/A')}")
    elif nonexistent_repo_result['status'] == 'failed':
        print(f"   ❌ Failed: {nonexistent_repo_result.get('error')}")
    
    # Test 5: Import Status Endpoint WITHOUT Auth
    logger.info("\n5️⃣ Testing Import Status Endpoint WITHOUT Authentication")
    status_result = tester.test_import_status_endpoint_without_auth()
    print(f"Import Status (No Auth): {status_result['status']}")
    
    if status_result['status'] == 'success':
        print(f"   ✅ Status endpoint accessible without auth")
        if 'workspace_info' in status_result:
            workspace = status_result['workspace_info']
            print(f"   ✅ Workspace: {workspace.get('root')}")
            print(f"   ✅ Projects: {workspace.get('projects_count', 0)}")
    elif status_result['status'] == 'failed':
        print(f"   ❌ FAILED: {status_result.get('error')}")
        if status_result.get('critical_issue'):
            print(f"   🔴 CRITICAL: {status_result['critical_issue']}")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("🔄 GITHUB IMPORT WITHOUT AUTHENTICATION TEST SUMMARY")
    logger.info("=" * 80)
    
    # Count successful tests
    test_results = [
        ("System Dependencies Check", deps_result['status'] in ['success', 'partial']),
        ("Public Repo Import (No Auth)", public_import_result['status'] == 'success'),
        ("Invalid URL Handling", invalid_url_result['status'] == 'success'),
        ("Non-Existent Repo Handling", nonexistent_repo_result['status'] == 'success'),
        ("Import Status (No Auth)", status_result['status'] == 'success'),
    ]
    
    successful_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall Results: {successful_tests}/{total_tests} tests passed")
    
    for test_name, success in test_results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    # Critical Issues Analysis
    critical_issues = []
    
    if deps_result['status'] == 'error':
        critical_issues.append("System dependencies check failed - cannot proceed with import tests")
    elif deps_result['status'] == 'partial':
        if not deps_result.get('git_available'):
            critical_issues.append("Git not available - GitHub import will not work")
        if not deps_result.get('workspace_writable'):
            critical_issues.append("Workspace not writable - GitHub import will fail")
    
    if public_import_result['status'] == 'failed':
        if public_import_result.get('critical_issue'):
            critical_issues.append(f"❌ MAIN ISSUE: {public_import_result['critical_issue']}")
        else:
            critical_issues.append(f"❌ Public repo import failed: {public_import_result.get('error', 'Unknown error')}")
    
    if invalid_url_result['status'] == 'failed':
        critical_issues.append(f"Invalid URL handling failed: {invalid_url_result.get('error', 'Unknown error')}")
    
    if nonexistent_repo_result['status'] == 'failed':
        critical_issues.append(f"Non-existent repo handling failed: {nonexistent_repo_result.get('error', 'Unknown error')}")
    
    if status_result['status'] == 'failed':
        if status_result.get('critical_issue'):
            critical_issues.append(f"❌ Status endpoint issue: {status_result['critical_issue']}")
        else:
            critical_issues.append(f"Import status endpoint failed: {status_result.get('error', 'Unknown error')}")
    
    # Main Analysis
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: GitHub Import WITHOUT Authentication working correctly!")
        print("   - Public repositories can be imported without authentication")
        print("   - Invalid URLs are properly rejected with clear error messages")
        print("   - Non-existent repositories are properly handled")
        print("   - Import status endpoint accessible without authentication")
        print("   - System dependencies (Git, workspace) are available")
    
    # Detailed Results
    if public_import_result['status'] == 'success' and 'repository' in public_import_result:
        repo = public_import_result['repository']
        details = public_import_result.get('import_details', {})
        print(f"\n📋 PUBLIC REPO IMPORT RESULTS:")
        print(f"   - Repository: {repo.get('owner')}/{repo.get('name')}")
        print(f"   - Branch: {repo.get('branch')}")
        print(f"   - Files imported: {details.get('total_files', 0)}")
        print(f"   - Target directory: {details.get('target_directory', 'N/A')}")
    
    if status_result['status'] == 'success' and 'workspace_info' in status_result:
        workspace = status_result['workspace_info']
        print(f"\n📄 WORKSPACE STATUS:")
        print(f"   - Workspace root: {workspace.get('root')}")
        print(f"   - Existing projects: {workspace.get('projects_count', 0)}")
    
    # Diagnostic Information
    print(f"\n📝 DIAGNOSTIC INFORMATION:")
    print(f"   - Backend URL: {tester.base_url}")
    print(f"   - API URL: {tester.api_url}")
    print(f"   - Git available: {'✅ Yes' if deps_result.get('git_available') else '❌ No'}")
    print(f"   - Workspace writable: {'✅ Yes' if deps_result.get('workspace_writable') else '❌ No'}")
    print(f"   - Public import working: {'✅ Yes' if public_import_result['status'] == 'success' else '❌ No'}")
    print(f"   - No auth required: {'✅ Confirmed' if public_import_result.get('no_auth_required') else '❌ Still required'}")
    
    return {
        'total_tests': total_tests,
        'successful_tests': successful_tests,
        'critical_issues': critical_issues,
        'public_import_working': public_import_result['status'] == 'success',
        'no_auth_required': public_import_result.get('no_auth_required', False),
        'all_endpoints_accessible': status_result['status'] == 'success'
    }


if __name__ == "__main__":
    main()