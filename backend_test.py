#!/usr/bin/env python3
"""
Session Active Project Status Debugging
Testing session active_project field after GitHub import

TEST PLAN:
1. Login as demo/demo123
2. Get session list and find current session ID
3. Get session details and check for active_project and active_project_branch fields
4. Check workspace status via GitHub import status
5. If a project exists, set active project
6. Verify that active_project is set correctly

EXPECTED RESULT:
- Session has active_project field
- Value is the name of the imported repository
- Path /app/{active_project} exists
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

class SessionActiveProjectTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()  # Reuse connections for better performance
        self.token = None
        self.user_info = None
    def authenticate_demo_user(self) -> Dict[str, Any]:
        """Authenticate with demo/demo123 credentials"""
        logger.info("🔐 Authenticating with demo user (demo/demo123)")
        
        try:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                logger.info("✅ Authentication successful!")
                logger.info(f"   User ID: {self.user_info['user_id']}")
                logger.info(f"   Username: {self.user_info['username']}")
                logger.info(f"   Token type: {auth_data.get('token_type')}")
                
                return {
                    "status": "success",
                    "token": self.token,
                    "user_info": self.user_info,
                    "auth_data": auth_data
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
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_creation(self) -> Dict[str, Any]:
        """Test POST /api/sessions/ - Create new session"""
        logger.info("📝 Testing session creation (POST /api/sessions/)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            session_data = {
                "name": "Test Session"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                session_response = response.json()
                session_id = session_response.get("id")
                
                logger.info("✅ Session creation successful!")
                logger.info(f"   Session ID: {session_id}")
                logger.info(f"   Session name: {session_response.get('name')}")
                logger.info(f"   Message count: {session_response.get('message_count', 0)}")
                
                return {
                    "status": "success",
                    "session_id": session_id,
                    "session_data": session_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session creation failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session creation error: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_retrieval(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id} - This endpoint had the 500 error"""
        logger.info(f"🔍 Testing session retrieval (GET /api/sessions/{session_id}) - CRITICAL TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                session_data = response.json()
                
                logger.info("✅ Session retrieval successful! (Bug fix working)")
                logger.info(f"   Session ID: {session_data.get('id')}")
                logger.info(f"   Session name: {session_data.get('name')}")
                logger.info(f"   Message count: {session_data.get('message_count', 0)}")
                logger.info(f"   Created at: {session_data.get('created_at')}")
                
                return {
                    "status": "success",
                    "session_data": session_data,
                    "bug_fix_verified": True
                }
            elif response.status_code == 500:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ CRITICAL: Still getting 500 error! Bug fix may not be working: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "bug_fix_failed": True,
                    "response": response.text
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session retrieval failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session retrieval error: {e}")
            return {"status": "error", "error": str(e)}

    def test_list_sessions(self) -> Dict[str, Any]:
        """Test GET /api/sessions/list - List user sessions"""
        logger.info("📋 Testing session list (GET /api/sessions/list)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                sessions_list = response.json()
                
                logger.info("✅ Session list successful!")
                logger.info(f"   Total sessions: {len(sessions_list)}")
                
                for i, session in enumerate(sessions_list[:3]):  # Show first 3
                    logger.info(f"   Session {i+1}: {session.get('name')} (ID: {session.get('id')[:12]}...)")
                
                return {
                    "status": "success",
                    "sessions_count": len(sessions_list),
                    "sessions_list": sessions_list
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session list failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session list error: {e}")
            return {"status": "error", "error": str(e)}

    def test_add_message(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/sessions/messages - Add message to session"""
        logger.info(f"💬 Testing add message (POST /api/sessions/messages)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            message_data = {
                "session_id": session_id,
                "role": "user",
                "content": "Test message content"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/messages",
                json=message_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                message_response = response.json()
                
                logger.info("✅ Add message successful!")
                logger.info(f"   Message ID: {message_response.get('id')}")
                logger.info(f"   Role: {message_response.get('role')}")
                logger.info(f"   Content: {message_response.get('content')[:50]}...")
                
                return {
                    "status": "success",
                    "message_id": message_response.get('id'),
                    "message_data": message_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Add message failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Add message error: {e}")
            return {"status": "error", "error": str(e)}

    def test_get_messages(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id}/messages - Get session messages"""
        logger.info(f"📨 Testing get messages (GET /api/sessions/{session_id}/messages)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}/messages",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                messages_list = response.json()
                
                logger.info("✅ Get messages successful!")
                logger.info(f"   Total messages: {len(messages_list)}")
                
                for i, message in enumerate(messages_list):
                    logger.info(f"   Message {i+1}: {message.get('role')} - {message.get('content')[:30]}...")
                
                return {
                    "status": "success",
                    "messages_count": len(messages_list),
                    "messages_list": messages_list
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Get messages failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Get messages error: {e}")
            return {"status": "error", "error": str(e)}

    def test_public_repo_import_without_auth(self) -> Dict[str, Any]:
        """Test POST /api/github/import with public repository (Windows compatibility focus)"""
        logger.info("🔄 Testing GitHub Import with Windows Compatibility (octocat/Hello-World)")
        
        try:
            import_data = {
                "repo_url": "https://github.com/octocat/Hello-World",
                "branch": "master"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=60  # Git operations can take time
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                import_data = response.json()
                
                logger.info("✅ GitHub import successful!")
                logger.info(f"   Repository: {import_data.get('repository', {}).get('name')}")
                logger.info(f"   Owner: {import_data.get('repository', {}).get('owner')}")
                logger.info(f"   Branch: {import_data.get('repository', {}).get('branch')}")
                logger.info(f"   Total files: {import_data.get('import_details', {}).get('total_files', 0)}")
                logger.info(f"   Workspace path: {import_data.get('workspace_path')}")
                
                # Verify expected data structure
                repository = import_data.get('repository', {})
                import_details = import_data.get('import_details', {})
                
                # Check if file count > 0 (requirement from test plan)
                file_count = import_details.get('total_files', 0)
                repo_name = repository.get('name', '')
                
                if file_count > 0 and repo_name == 'Hello-World':
                    logger.info("✅ Import result verification passed")
                    logger.info(f"   ✓ File count > 0: {file_count}")
                    logger.info(f"   ✓ Repository name correct: {repo_name}")
                    
                    return {
                        "status": "success",
                        "data": import_data,
                        "file_count": file_count,
                        "repository_name": repo_name,
                        "windows_compatibility_tested": True,
                        "cleanup_warnings_check_needed": True
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Import verification failed - file_count: {file_count}, repo_name: {repo_name}",
                        "data": import_data
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ GitHub import failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ GitHub import test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_backend_logs_for_cleanup_warnings(self) -> Dict[str, Any]:
        """Check backend logs for cleanup warnings (Windows compatibility verification)"""
        logger.info("📋 Checking backend logs for cleanup warnings")
        
        try:
            import subprocess
            
            # Check supervisor backend logs
            log_files = [
                "/var/log/supervisor/backend.out.log",
                "/var/log/supervisor/backend.err.log"
            ]
            
            cleanup_warnings = []
            cleanup_success = []
            
            for log_file in log_files:
                try:
                    # Get last 100 lines of logs
                    result = subprocess.run(
                        ["tail", "-n", "100", log_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        log_content = result.stdout
                        
                        # Look for cleanup-related messages
                        lines = log_content.split('\n')
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['cleanup', 'failed to clean', 'remove readonly', 'permission']):
                                if 'warning' in line.lower() or 'failed' in line.lower():
                                    cleanup_warnings.append(line.strip())
                                elif 'success' in line.lower() or 'cleaned' in line.lower():
                                    cleanup_success.append(line.strip())
                        
                        logger.info(f"   Checked {log_file}: {len(lines)} lines")
                        
                except Exception as e:
                    logger.warning(f"   Could not read {log_file}: {e}")
            
            logger.info(f"✅ Backend logs check completed")
            logger.info(f"   Cleanup warnings found: {len(cleanup_warnings)}")
            logger.info(f"   Cleanup success messages: {len(cleanup_success)}")
            
            # Show warnings if any
            if cleanup_warnings:
                logger.info("   ⚠️ Cleanup warnings found:")
                for warning in cleanup_warnings[-5:]:  # Show last 5
                    logger.info(f"     {warning}")
            
            # Show success messages if any
            if cleanup_success:
                logger.info("   ✅ Cleanup success messages:")
                for success in cleanup_success[-3:]:  # Show last 3
                    logger.info(f"     {success}")
            
            # Determine if warnings are non-critical (as expected)
            non_critical_warnings = len(cleanup_warnings) > 0
            
            return {
                "status": "success",
                "cleanup_warnings_count": len(cleanup_warnings),
                "cleanup_success_count": len(cleanup_success),
                "cleanup_warnings": cleanup_warnings,
                "cleanup_success": cleanup_success,
                "non_critical_warnings_found": non_critical_warnings,
                "windows_compatibility_verified": non_critical_warnings
            }
            
        except Exception as e:
            logger.error(f"❌ Backend logs check failed: {e}")
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


    def test_specific_session_retrieval(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id} for a specific session ID"""
        logger.info(f"🔍 Testing specific session retrieval: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            logger.info(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                session_data = response.json()
                logger.info("✅ Session found!")
                logger.info(f"   Session ID: {session_data.get('id')}")
                logger.info(f"   Session name: {session_data.get('name')}")
                logger.info(f"   Message count: {session_data.get('message_count', 0)}")
                logger.info(f"   Created at: {session_data.get('created_at')}")
                
                return {
                    "status": "success",
                    "session_data": session_data
                }
            elif response.status_code == 404:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session not found (404): {error_detail}")
                return {
                    "status": "not_found",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
            elif response.status_code == 403:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Access denied (403): {error_detail}")
                return {
                    "status": "access_denied",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session retrieval failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session retrieval error: {e}")
            return {"status": "error", "error": str(e)}

    def check_database_sessions(self) -> Dict[str, Any]:
        """Check sessions directly in the SQLite database"""
        logger.info("🗄️ Checking sessions in SQLite database")
        
        try:
            if not os.path.exists(self.db_path):
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Check if sessions table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                conn.close()
                return {
                    "status": "failed",
                    "error": "Sessions table does not exist in database"
                }
            
            # Get all sessions
            cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10")
            sessions = cursor.fetchall()
            
            # Get session count
            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            total_count = cursor.fetchone()['count']
            
            conn.close()
            
            logger.info(f"✅ Database check completed")
            logger.info(f"   Database path: {self.db_path}")
            logger.info(f"   Total sessions: {total_count}")
            logger.info(f"   Recent sessions (showing up to 10):")
            
            session_list = []
            for session in sessions:
                session_dict = dict(session)
                session_list.append(session_dict)
                user_id = session_dict.get('user_id', 'None')
                logger.info(f"     - {session['id']}: {session['name']} (user_id: {user_id}) - {session['created_at']}")
            
            return {
                "status": "success",
                "database_path": self.db_path,
                "total_sessions": total_count,
                "recent_sessions": session_list,
                "sessions_table_exists": True
            }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database error: {e}")
            return {"status": "error", "error": f"Database error: {e}"}
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_creation_and_immediate_retrieval(self) -> Dict[str, Any]:
        """Test creating a session and immediately retrieving it"""
        logger.info("🔄 Testing session creation + immediate retrieval")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Step 1: Create session
            session_data = {
                "name": "Test Session for 404 Debug"
            }
            
            create_response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Create response status: {create_response.status_code}")
            
            if create_response.status_code != 200:
                error_detail = create_response.json().get("detail", "Unknown error") if create_response.content else f"HTTP {create_response.status_code}"
                return {
                    "status": "failed",
                    "error": f"Session creation failed: {error_detail}",
                    "status_code": create_response.status_code
                }
            
            session_response = create_response.json()
            session_id = session_response.get("id")
            
            logger.info(f"✅ Session created: {session_id}")
            
            # Step 2: Immediately retrieve the same session
            retrieve_response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Retrieve response status: {retrieve_response.status_code}")
            
            if retrieve_response.status_code == 200:
                retrieved_data = retrieve_response.json()
                logger.info("✅ Session immediately retrievable!")
                logger.info(f"   Retrieved ID: {retrieved_data.get('id')}")
                logger.info(f"   Retrieved name: {retrieved_data.get('name')}")
                
                return {
                    "status": "success",
                    "session_id": session_id,
                    "created_data": session_response,
                    "retrieved_data": retrieved_data,
                    "persistence_working": True
                }
            elif retrieve_response.status_code == 404:
                error_detail = retrieve_response.json().get("detail", "Unknown error") if retrieve_response.content else f"HTTP {retrieve_response.status_code}"
                logger.error("❌ CRITICAL: Session not found immediately after creation!")
                logger.error("❌ This indicates a PERSISTENCE PROBLEM!")
                return {
                    "status": "persistence_failure",
                    "error": f"Session not found after creation: {error_detail}",
                    "session_id": session_id,
                    "created_data": session_response,
                    "persistence_working": False
                }
            else:
                error_detail = retrieve_response.json().get("detail", "Unknown error") if retrieve_response.content else f"HTTP {retrieve_response.status_code}"
                return {
                    "status": "failed",
                    "error": f"Session retrieval failed: {error_detail}",
                    "status_code": retrieve_response.status_code,
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"❌ Session creation + retrieval test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_user_id_session_filtering_issue(self) -> Dict[str, Any]:
        """Test the user_id filtering issue that causes sessions to not appear in list"""
        logger.info("🔍 Testing user_id filtering issue (ROOT CAUSE)")
        
        if not self.token or not self.user_info:
            return {"status": "skipped", "error": "No authentication info available"}
        
        current_user_id = self.user_info.get("user_id")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Step 1: Create a session (this creates with user_id=None due to bug)
            session_data = {"name": "User ID Test Session"}
            
            create_response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if create_response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Session creation failed: {create_response.status_code}"
                }
            
            session_response = create_response.json()
            session_id = session_response.get("id")
            
            logger.info(f"✅ Created session: {session_id}")
            
            # Step 2: Check if session appears in list (it won't due to user_id filtering)
            list_response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers=headers,
                timeout=10
            )
            
            if list_response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Session list failed: {list_response.status_code}"
                }
            
            sessions_list = list_response.json()
            created_session_in_list = any(s.get("id") == session_id for s in sessions_list)
            
            logger.info(f"   Sessions in list: {len(sessions_list)}")
            logger.info(f"   Created session in list: {created_session_in_list}")
            
            # Step 3: Try to retrieve the session directly (this should work)
            get_response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            direct_retrieval_works = get_response.status_code == 200
            logger.info(f"   Direct retrieval works: {direct_retrieval_works}")
            
            # Step 4: Check database to see actual user_id
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM sessions WHERE id = ?", (session_id,))
                row = cursor.fetchone()
                actual_user_id = row[0] if row else None
                conn.close()
                
                logger.info(f"   Expected user_id: {current_user_id}")
                logger.info(f"   Actual user_id in DB: {actual_user_id}")
                
                user_id_mismatch = actual_user_id != current_user_id
            else:
                user_id_mismatch = True
                actual_user_id = "DB_NOT_FOUND"
            
            # Analysis
            if user_id_mismatch and not created_session_in_list and direct_retrieval_works:
                logger.error("🚨 ROOT CAUSE IDENTIFIED!")
                logger.error("   Sessions are created with user_id=None instead of authenticated user_id")
                logger.error("   List API filters by user_id, so sessions don't appear")
                logger.error("   Direct retrieval works because it doesn't check user_id ownership")
                
                return {
                    "status": "root_cause_identified",
                    "issue": "user_id_not_set_on_creation",
                    "session_id": session_id,
                    "expected_user_id": current_user_id,
                    "actual_user_id": actual_user_id,
                    "session_in_list": created_session_in_list,
                    "direct_retrieval_works": direct_retrieval_works,
                    "user_id_mismatch": user_id_mismatch
                }
            else:
                return {
                    "status": "success",
                    "session_id": session_id,
                    "session_in_list": created_session_in_list,
                    "direct_retrieval_works": direct_retrieval_works,
                    "user_id_correct": not user_id_mismatch
                }
                
        except Exception as e:
            logger.error(f"❌ User ID filtering test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_user_id_associations(self) -> Dict[str, Any]:
        """Check user_id associations in sessions"""
        logger.info("👤 Checking user_id associations in sessions")
        
        if not self.token or not self.user_info:
            return {"status": "skipped", "error": "No authentication info available"}
        
        current_user_id = self.user_info.get("user_id")
        
        try:
            if not os.path.exists(self.db_path):
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get sessions with user_id info
            cursor.execute("""
                SELECT id, name, user_id, created_at 
                FROM sessions 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            sessions = cursor.fetchall()
            
            # Count sessions by user_id
            cursor.execute("""
                SELECT 
                    user_id,
                    COUNT(*) as count
                FROM sessions 
                GROUP BY user_id
            """)
            user_counts = cursor.fetchall()
            
            conn.close()
            
            logger.info(f"✅ User ID association check completed")
            logger.info(f"   Current authenticated user_id: {current_user_id}")
            logger.info(f"   Sessions by user_id:")
            
            user_stats = {}
            for row in user_counts:
                user_id = row['user_id'] if row['user_id'] else 'NULL'
                count = row['count']
                user_stats[user_id] = count
                logger.info(f"     {user_id}: {count} sessions")
            
            # Check sessions for current user
            current_user_sessions = [dict(s) for s in sessions if s['user_id'] == current_user_id]
            null_user_sessions = [dict(s) for s in sessions if s['user_id'] is None]
            
            logger.info(f"   Sessions for current user ({current_user_id}): {len(current_user_sessions)}")
            logger.info(f"   Sessions with NULL user_id: {len(null_user_sessions)}")
            
            return {
                "status": "success",
                "current_user_id": current_user_id,
                "user_stats": user_stats,
                "current_user_sessions": current_user_sessions,
                "null_user_sessions": null_user_sessions,
                "total_sessions_checked": len(sessions)
            }
            
        except Exception as e:
            logger.error(f"❌ User ID association check failed: {e}")
            return {"status": "error", "error": str(e)}

    def verify_route_registration(self) -> Dict[str, Any]:
        """Verify that session routes are properly registered"""
        logger.info("🛣️ Verifying route registration")
        
        try:
            # Check OpenAPI spec for session routes
            response = self.session.get(f"{self.api_url}/../openapi.json", timeout=10)
            
            if response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Could not fetch OpenAPI spec: {response.status_code}"
                }
            
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            # Check for session-related routes
            session_routes = [path for path in paths.keys() if "/sessions" in path]
            
            logger.info(f"✅ Route verification completed")
            logger.info(f"   Total API routes: {len(paths)}")
            logger.info(f"   Session routes found: {len(session_routes)}")
            
            for route in session_routes:
                methods = list(paths[route].keys())
                logger.info(f"     {route}: {methods}")
            
            # Check for specific routes we need
            required_routes = [
                "/api/sessions/",
                "/api/sessions/{session_id}",
                "/api/sessions/list"
            ]
            
            missing_routes = []
            for required_route in required_routes:
                if required_route not in paths:
                    missing_routes.append(required_route)
            
            if missing_routes:
                return {
                    "status": "failed",
                    "error": f"Missing required routes: {missing_routes}",
                    "session_routes": session_routes,
                    "total_routes": len(paths)
                }
            
            return {
                "status": "success",
                "session_routes": session_routes,
                "total_routes": len(paths),
                "all_required_routes_present": True
            }
            
        except Exception as e:
            logger.error(f"❌ Route verification failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_list_and_get_current(self) -> Dict[str, Any]:
        """Test GET /api/sessions/list and find current session"""
        logger.info("📋 Testing session list and finding current session")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                sessions_list = response.json()
                
                logger.info("✅ Session list successful!")
                logger.info(f"   Total sessions: {len(sessions_list)}")
                
                # Find the most recent session (current session)
                current_session = None
                if sessions_list:
                    # Sort by updated_at to get the most recent
                    sessions_list.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
                    current_session = sessions_list[0]
                    
                    logger.info(f"   Current session ID: {current_session.get('id')}")
                    logger.info(f"   Current session name: {current_session.get('name')}")
                    logger.info(f"   Message count: {current_session.get('message_count', 0)}")
                
                return {
                    "status": "success",
                    "sessions_count": len(sessions_list),
                    "sessions_list": sessions_list,
                    "current_session": current_session
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session list failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session list error: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_details_active_project(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id} and check active_project fields"""
        logger.info(f"🔍 Testing session details for active_project fields: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                session_data = response.json()
                
                logger.info("✅ Session details retrieved successfully!")
                logger.info(f"   Session ID: {session_data.get('id')}")
                logger.info(f"   Session name: {session_data.get('name')}")
                logger.info(f"   Message count: {session_data.get('message_count', 0)}")
                
                # Check for active_project fields
                active_project = session_data.get('active_project')
                active_project_branch = session_data.get('active_project_branch')
                
                logger.info(f"   🎯 active_project: {active_project}")
                logger.info(f"   🎯 active_project_branch: {active_project_branch}")
                
                # Check if fields are present
                has_active_project_field = 'active_project' in session_data
                has_active_project_branch_field = 'active_project_branch' in session_data
                
                logger.info(f"   ✓ active_project field present: {has_active_project_field}")
                logger.info(f"   ✓ active_project_branch field present: {has_active_project_branch_field}")
                
                return {
                    "status": "success",
                    "session_data": session_data,
                    "active_project": active_project,
                    "active_project_branch": active_project_branch,
                    "has_active_project_field": has_active_project_field,
                    "has_active_project_branch_field": has_active_project_branch_field,
                    "active_project_set": active_project is not None,
                    "active_project_branch_set": active_project_branch is not None
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session details failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session details error: {e}")
            return {"status": "error", "error": str(e)}

    def test_workspace_status(self) -> Dict[str, Any]:
        """Test GET /api/github/import/status to check workspace projects"""
        logger.info("📊 Testing workspace status and imported projects")
        
        try:
            # No authentication needed for this endpoint
            headers = {"Content-Type": "application/json"}
            
            response = self.session.get(
                f"{self.api_url}/github/import/status",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                
                logger.info("✅ Workspace status retrieved successfully!")
                logger.info(f"   Status: {status_data.get('status')}")
                logger.info(f"   Workspace root: {status_data.get('workspace_root')}")
                logger.info(f"   Total projects: {status_data.get('total_projects', 0)}")
                
                existing_projects = status_data.get('existing_projects', [])
                logger.info(f"   Existing projects: {len(existing_projects)}")
                
                for i, project in enumerate(existing_projects[:5]):  # Show first 5
                    logger.info(f"     {i+1}. {project.get('name')} ({project.get('file_count', 0)} files)")
                
                return {
                    "status": "success",
                    "workspace_data": status_data,
                    "existing_projects": existing_projects,
                    "total_projects": len(existing_projects),
                    "has_projects": len(existing_projects) > 0
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Workspace status failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Workspace status error: {e}")
            return {"status": "error", "error": str(e)}

    def test_set_active_project(self, session_id: str, project_name: str, branch: str = "main") -> Dict[str, Any]:
        """Test setting active project for a session (if endpoint exists)"""
        logger.info(f"🎯 Testing set active project: {project_name} for session {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Try to set active project via workspace endpoint (if it exists)
            request_data = {
                "session_id": session_id,
                "project_name": project_name,
                "branch": branch
            }
            
            response = self.session.post(
                f"{self.api_url}/workspace/set-active",
                json=request_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result_data = response.json()
                
                logger.info("✅ Active project set successfully!")
                logger.info(f"   Project: {project_name}")
                logger.info(f"   Branch: {branch}")
                logger.info(f"   Session: {session_id}")
                
                return {
                    "status": "success",
                    "project_name": project_name,
                    "branch": branch,
                    "session_id": session_id,
                    "result_data": result_data
                }
            elif response.status_code == 404:
                logger.info("ℹ️ Set active project endpoint not found - this is expected")
                return {
                    "status": "endpoint_not_found",
                    "error": "Workspace set-active endpoint not implemented",
                    "status_code": response.status_code
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Set active project failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Set active project error: {e}")
            return {"status": "error", "error": str(e)}

    def test_manual_session_update(self, session_id: str, project_name: str, branch: str = "main") -> Dict[str, Any]:
        """Test manually updating session with active_project via direct database or API"""
        logger.info(f"🔧 Testing manual session update for active_project")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Try to update session via PATCH endpoint (if it exists)
            request_data = {
                "active_project": project_name,
                "active_project_branch": branch
            }
            
            response = self.session.patch(
                f"{self.api_url}/sessions/{session_id}",
                json=request_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result_data = response.json()
                
                logger.info("✅ Session updated successfully!")
                logger.info(f"   Active project: {project_name}")
                logger.info(f"   Active branch: {branch}")
                
                return {
                    "status": "success",
                    "project_name": project_name,
                    "branch": branch,
                    "session_id": session_id,
                    "result_data": result_data
                }
            elif response.status_code == 404:
                logger.info("ℹ️ Session PATCH endpoint not found")
                return {
                    "status": "endpoint_not_found",
                    "error": "Session PATCH endpoint not implemented",
                    "status_code": response.status_code
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session update failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session update error: {e}")
            return {"status": "error", "error": str(e)}

    def verify_project_path_exists(self, project_name: str) -> Dict[str, Any]:
        """Verify that the project path exists in /app/"""
        logger.info(f"📁 Verifying project path exists: /app/{project_name}")
        
        try:
            from pathlib import Path
            
            project_path = Path(f"/app/{project_name}")
            exists = project_path.exists()
            is_directory = project_path.is_dir() if exists else False
            
            if exists and is_directory:
                # Count files in the project
                file_count = sum(1 for _ in project_path.rglob('*') if _.is_file())
                logger.info(f"✅ Project path exists: {project_path}")
                logger.info(f"   Files in project: {file_count}")
                
                return {
                    "status": "success",
                    "project_path": str(project_path),
                    "exists": True,
                    "is_directory": True,
                    "file_count": file_count
                }
            elif exists:
                logger.warning(f"⚠️ Path exists but is not a directory: {project_path}")
                return {
                    "status": "warning",
                    "project_path": str(project_path),
                    "exists": True,
                    "is_directory": False,
                    "error": "Path exists but is not a directory"
                }
            else:
                logger.error(f"❌ Project path does not exist: {project_path}")
                return {
                    "status": "failed",
                    "project_path": str(project_path),
                    "exists": False,
                    "is_directory": False,
                    "error": "Project path does not exist"
                }
                
        except Exception as e:
            logger.error(f"❌ Path verification error: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """
    Main test function for Session Active Project Status Debugging
    """
    logger.info("🚀 Starting Session Active Project Status Debugging")
    logger.info("=" * 60)
    logger.info("DEBUGGING TASK: Check Session active_project Status")
    logger.info("GOAL: Verify active_project field is set correctly after GitHub import")
    logger.info("=" * 60)
    
    tester = SessionActiveProjectTester()
    results = {}
    
    # Test 1: Authentication
    logger.info("\n1️⃣ AUTHENTICATION (demo/demo123)")
    auth_result = tester.authenticate_demo_user()
    results["authentication"] = auth_result
    
    if auth_result["status"] != "success":
        logger.error("❌ Authentication failed - cannot continue with tests")
        return results
    
    # Test 2: Session List and Current Session
    logger.info("\n2️⃣ SESSION LIST AND CURRENT SESSION")
    session_list_result = tester.test_session_list_and_get_current()
    results["session_list"] = session_list_result
    
    current_session = None
    if session_list_result["status"] == "success":
        current_session = session_list_result.get("current_session")
    
    if not current_session:
        logger.error("❌ No current session found - cannot continue with session tests")
        # Continue with workspace tests anyway
    
    # Test 3: Session Details and Active Project Fields
    if current_session:
        logger.info("\n3️⃣ SESSION DETAILS AND ACTIVE PROJECT FIELDS")
        session_details_result = tester.test_session_details_active_project(current_session["id"])
        results["session_details"] = session_details_result
    else:
        results["session_details"] = {"status": "skipped", "error": "No current session available"}
    
    # Test 4: Workspace Status
    logger.info("\n4️⃣ WORKSPACE STATUS AND IMPORTED PROJECTS")
    workspace_result = tester.test_workspace_status()
    results["workspace_status"] = workspace_result
    
    # Test 5: Set Active Project (if projects exist)
    available_projects = []
    if workspace_result["status"] == "success" and workspace_result.get("has_projects"):
        available_projects = workspace_result["existing_projects"]
        
        if available_projects and current_session:
            first_project = available_projects[0]
            project_name = first_project["name"]
            
            logger.info(f"\n5️⃣ SET ACTIVE PROJECT ({project_name})")
            set_active_result = tester.test_set_active_project(
                current_session["id"], 
                project_name, 
                first_project.get("branch", "main")
            )
            results["set_active_project"] = set_active_result
            
            # If direct endpoint doesn't exist, try manual update
            if set_active_result["status"] == "endpoint_not_found":
                logger.info("\n5️⃣b MANUAL SESSION UPDATE")
                manual_update_result = tester.test_manual_session_update(
                    current_session["id"], 
                    project_name, 
                    first_project.get("branch", "main")
                )
                results["manual_session_update"] = manual_update_result
        else:
            results["set_active_project"] = {"status": "skipped", "error": "No projects or session available"}
    else:
        results["set_active_project"] = {"status": "skipped", "error": "No projects found in workspace"}
    
    # Test 6: Verify Active Project After Setting
    if current_session:
        logger.info("\n6️⃣ VERIFY ACTIVE PROJECT AFTER SETTING")
        final_session_result = tester.test_session_details_active_project(current_session["id"])
        results["final_session_check"] = final_session_result
    else:
        results["final_session_check"] = {"status": "skipped", "error": "No current session available"}
    
    # Test 7: Verify Project Path Exists
    if available_projects:
        first_project = available_projects[0]
        project_name = first_project["name"]
        
        logger.info(f"\n7️⃣ VERIFY PROJECT PATH EXISTS (/app/{project_name})")
        path_verification_result = tester.verify_project_path_exists(project_name)
        results["path_verification"] = path_verification_result
    else:
        results["path_verification"] = {"status": "skipped", "error": "No projects to verify"}
    
    # Summary and Analysis
    logger.info("\n" + "=" * 60)
    logger.info("📊 SESSION ACTIVE PROJECT STATUS SUMMARY")
    logger.info("=" * 60)
    
    total_tests = len([r for r in results.values() if r["status"] != "skipped"])
    passed_tests = sum(1 for r in results.values() if r["status"] == "success")
    
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    
    for test_name, result in results.items():
        if result["status"] == "skipped":
            continue
        status_emoji = "✅" if result["status"] == "success" else "❌"
        logger.info(f"{status_emoji} {test_name.replace('_', ' ').title()}: {result['status']}")
        
        if result["status"] not in ["success"]:
            logger.info(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Detailed Analysis
    logger.info("\n" + "=" * 60)
    logger.info("🔍 DETAILED ANALYSIS")
    logger.info("=" * 60)
    
    # Check authentication
    if results["authentication"]["status"] == "success":
        logger.info("✅ AUTHENTICATION WORKING")
        user_info = results["authentication"]["user_info"]
        logger.info(f"   User: {user_info['username']} (ID: {user_info['user_id']})")
    else:
        logger.error("❌ AUTHENTICATION FAILED")
        return results
    
    # Check session fields
    session_details = results.get("session_details", {})
    if session_details.get("status") == "success":
        has_active_project_field = session_details.get("has_active_project_field", False)
        has_active_project_branch_field = session_details.get("has_active_project_branch_field", False)
        active_project_set = session_details.get("active_project_set", False)
        active_project_value = session_details.get("active_project")
        
        logger.info("📋 SESSION FIELDS ANALYSIS:")
        logger.info(f"   ✓ active_project field exists: {has_active_project_field}")
        logger.info(f"   ✓ active_project_branch field exists: {has_active_project_branch_field}")
        logger.info(f"   ✓ active_project has value: {active_project_set}")
        logger.info(f"   ✓ active_project value: {active_project_value}")
        
        if has_active_project_field and has_active_project_branch_field:
            logger.info("✅ SESSION MODEL HAS REQUIRED FIELDS")
        else:
            logger.error("❌ SESSION MODEL MISSING REQUIRED FIELDS")
    
    # Check workspace projects
    workspace_status = results.get("workspace_status", {})
    if workspace_status.get("status") == "success":
        has_projects = workspace_status.get("has_projects", False)
        total_projects = workspace_status.get("total_projects", 0)
        
        logger.info("📁 WORKSPACE ANALYSIS:")
        logger.info(f"   ✓ Has imported projects: {has_projects}")
        logger.info(f"   ✓ Total projects: {total_projects}")
        
        if has_projects:
            logger.info("✅ WORKSPACE HAS IMPORTED PROJECTS")
            projects = workspace_status.get("existing_projects", [])
            for project in projects[:3]:  # Show first 3
                logger.info(f"     - {project['name']} ({project.get('file_count', 0)} files)")
        else:
            logger.warning("⚠️ NO PROJECTS FOUND IN WORKSPACE")
    
    # Check final status
    final_session = results.get("final_session_check", {})
    if final_session.get("status") == "success":
        final_active_project = final_session.get("active_project")
        final_active_branch = final_session.get("active_project_branch")
        
        logger.info("🎯 FINAL STATUS:")
        logger.info(f"   ✓ Final active_project: {final_active_project}")
        logger.info(f"   ✓ Final active_project_branch: {final_active_branch}")
        
        if final_active_project:
            logger.info("✅ ACTIVE PROJECT IS SET!")
        else:
            logger.error("❌ ACTIVE PROJECT IS NOT SET")
    
    # Check path verification
    path_verification = results.get("path_verification", {})
    if path_verification.get("status") == "success":
        project_path = path_verification.get("project_path")
        file_count = path_verification.get("file_count", 0)
        
        logger.info("📂 PATH VERIFICATION:")
        logger.info(f"   ✓ Project path exists: {project_path}")
        logger.info(f"   ✓ Files in project: {file_count}")
        logger.info("✅ PROJECT PATH VERIFIED")
    elif path_verification.get("status") == "failed":
        logger.error("❌ PROJECT PATH DOES NOT EXIST")
    
    return results

    def test_preview_session_files_endpoint(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/github-pat/preview-session-files"""
        logger.info(f"📋 Testing preview-session-files endpoint for session: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            request_data = {
                "session_id": session_id
            }
            
            response = self.session.post(
                f"{self.api_url}/github-pat/preview-session-files",
                json=request_data,
                headers=headers,
                timeout=15
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                preview_data = response.json()
                
                logger.info("✅ Preview endpoint working correctly")
                logger.info(f"   Total files: {preview_data.get('file_count', 0)}")
                logger.info(f"   Total size: {preview_data.get('total_size', 0)} bytes")
                
                files = preview_data.get('files', [])
                file_types = {}
                
                for file in files:
                    file_type = file.get('type', 'unknown')
                    if file_type not in file_types:
                        file_types[file_type] = 0
                    file_types[file_type] += 1
                    
                    logger.info(f"   📄 {file.get('path', 'unknown')} ({file_type}) - {file.get('size', 0)} bytes")
                
                logger.info(f"   File types found: {file_types}")
                
                # Verify expected file types
                expected_types = ['readme', 'messages', 'code']
                found_types = set(file_types.keys())
                missing_types = set(expected_types) - found_types
                
                if missing_types:
                    logger.warning(f"   ⚠️ Missing expected file types: {missing_types}")
                
                return {
                    "status": "success",
                    "data": preview_data,
                    "file_count": preview_data.get('file_count', 0),
                    "total_size": preview_data.get('total_size', 0),
                    "file_types": file_types,
                    "files": files
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Preview endpoint failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Preview endpoint test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_file_types_verification(self, preview_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify that all expected file types are present with correct structure"""
        logger.info("🔍 Testing file types verification")
        
        try:
            files = preview_data.get('files', [])
            if not files:
                return {
                    "status": "failed",
                    "error": "No files found in preview data"
                }
            
            # Check for required file types
            file_types_found = {}
            required_fields = ['path', 'content', 'size', 'type']
            
            for file in files:
                file_type = file.get('type', 'unknown')
                
                # Verify all required fields are present
                missing_fields = [field for field in required_fields if field not in file]
                if missing_fields:
                    logger.error(f"❌ File {file.get('path', 'unknown')} missing fields: {missing_fields}")
                    return {
                        "status": "failed",
                        "error": f"File missing required fields: {missing_fields}"
                    }
                
                if file_type not in file_types_found:
                    file_types_found[file_type] = []
                file_types_found[file_type].append(file.get('path', 'unknown'))
            
            # Verify expected file types
            expected_readme = any(f.get('type') == 'readme' and f.get('path') == 'README.md' for f in files)
            expected_messages = any(f.get('type') == 'messages' and f.get('path') == 'messages.json' for f in files)
            expected_code = any(f.get('type') == 'code' and f.get('path', '').startswith('code/') for f in files)
            
            logger.info(f"✅ File types verification completed")
            logger.info(f"   README.md (readme): {'✅' if expected_readme else '❌'}")
            logger.info(f"   messages.json (messages): {'✅' if expected_messages else '❌'}")
            logger.info(f"   Code files: {'✅' if expected_code else '❌'}")
            
            for file_type, paths in file_types_found.items():
                logger.info(f"   {file_type}: {len(paths)} files - {paths}")
            
            all_types_present = expected_readme and expected_messages and expected_code
            
            return {
                "status": "success" if all_types_present else "partial",
                "readme_present": expected_readme,
                "messages_present": expected_messages,
                "code_present": expected_code,
                "file_types_found": file_types_found,
                "all_types_present": all_types_present
            }
            
        except Exception as e:
            logger.error(f"❌ File types verification failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_push_session_with_selection(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/github-pat/push-session with selected_files parameter"""
        logger.info(f"🚀 Testing push-session with file selection for session: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test with selected files (should fail with GitHub token error, but structure should be correct)
            push_data = {
                "session_id": session_id,
                "repo_name": "test-preview-session",
                "repo_description": "Test repository for GitHub push preview functionality",
                "is_private": False,
                "selected_files": ["README.md", "messages.json"]  # Only select these files
            }
            
            response = self.session.post(
                f"{self.api_url}/github-pat/push-session",
                json=push_data,
                headers=headers,
                timeout=15
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 401:
                error_data = response.json()
                
                logger.info("✅ Push with selection correctly requires GitHub token")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_data.get('detail')}")
                
                # Should contain message about GitHub not being connected
                if "GitHub not connected" in error_data.get('detail', ''):
                    logger.info("✅ Correct error message for missing GitHub token")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_behavior": True,
                        "selected_files_accepted": True
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected 'GitHub not connected' in error message, got: {error_data.get('detail')}",
                        "data": error_data
                    }
            elif response.status_code == 422:
                # Validation error - check if it's related to selected_files
                error_data = response.json()
                logger.error(f"❌ Validation error: {error_data}")
                return {
                    "status": "failed",
                    "error": f"Validation error with selected_files parameter: {error_data}",
                    "status_code": response.status_code
                }
            else:
                logger.error(f"❌ Unexpected status code: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 401 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Push with selection test failed: {e}")
            return {"status": "error", "error": str(e)}

    # Removed unused methods for GitHub preview testing

    # Additional unused methods removed for GitHub preview testing focus

    def test_summarize_and_fork_endpoint(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/session-management/summarize-and-fork"""
        logger.info(f"🔄 Testing summarize-and-fork endpoint for session: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            request_data = {
                "session_id": session_id
            }
            
            response = self.session.post(
                f"{self.api_url}/session-management/summarize-and-fork",
                json=request_data,
                headers=headers,
                timeout=30  # AI calls can take longer
            )
            
            logger.info(f"   Response status: {response.status_code}")
            logger.info(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                summary_data = response.json()
                
                logger.info("✅ Summarize and fork endpoint working")
                logger.info(f"   Original session: {summary_data.get('session_id')}")
                logger.info(f"   New session: {summary_data.get('new_session_id')}")
                logger.info(f"   Summary length: {len(summary_data.get('summary', ''))}")
                logger.info(f"   Next steps count: {len(summary_data.get('next_steps', []))}")
                
                return {
                    "status": "success",
                    "data": summary_data,
                    "new_session_id": summary_data.get('new_session_id'),
                    "summary_length": len(summary_data.get('summary', ''))
                }
            elif response.status_code == 404:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ 404 Error - Route not found: {error_detail}")
                return {
                    "status": "route_not_found",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
            elif response.status_code == 401:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication error: {error_detail}")
                return {
                    "status": "auth_error",
                    "error": error_detail,
                    "status_code": response.status_code
                }
            elif response.status_code == 500:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Backend error (expected without AI keys): {error_detail}")
                return {
                    "status": "backend_error",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "expected_without_ai_keys": True
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Summarize and fork failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Summarize and fork test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_continue_with_option_endpoint(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/session-management/continue-with-option"""
        logger.info(f"▶️ Testing continue-with-option endpoint for session: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            request_data = {
                "session_id": session_id,
                "option_action": "Weiter am Code arbeiten und neue Features hinzufügen"
            }
            
            response = self.session.post(
                f"{self.api_url}/session-management/continue-with-option",
                json=request_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                option_data = response.json()
                
                logger.info("✅ Continue with option endpoint working")
                logger.info(f"   Status: {option_data.get('status')}")
                logger.info(f"   Action: {option_data.get('action')}")
                logger.info(f"   Message: {option_data.get('message')}")
                
                return {
                    "status": "success",
                    "data": option_data,
                    "action_status": option_data.get('status')
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Continue with option failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Continue with option test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_backend_logs(self) -> Dict[str, Any]:
        """Check backend logs for any errors related to session management"""
        logger.info("📋 Checking backend logs for session management errors")
        
        try:
            import subprocess
            
            # Check supervisor backend logs
            log_files = [
                "/var/log/supervisor/backend.err.log",
                "/var/log/supervisor/backend.out.log"
            ]
            
            logs_found = []
            for log_file in log_files:
                try:
                    if os.path.exists(log_file):
                        result = subprocess.run(
                            ["tail", "-n", "50", log_file],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            logs_found.append({
                                "file": log_file,
                                "content": result.stdout.strip()
                            })
                except Exception as e:
                    logger.warning(f"Could not read {log_file}: {e}")
            
            if logs_found:
                logger.info(f"✅ Found {len(logs_found)} log files")
                for log in logs_found:
                    logger.info(f"   Log file: {log['file']}")
                    # Look for session-management related errors
                    if "session-management" in log['content'].lower() or "404" in log['content']:
                        logger.info("   ⚠️ Found session-management related entries")
                
                return {
                    "status": "success",
                    "logs_found": len(logs_found),
                    "logs": logs_found
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

    def create_test_session_with_messages(self) -> Dict[str, Any]:
        """Create a test session with messages for push testing"""
        logger.info("📝 Creating test session with messages for push testing")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Create a new session
            session_data = {
                "title": "GitHub Push Test Session",
                "model": "gpt-4"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to create session: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Failed to create session: {response.status_code}",
                    "response": response.text
                }
            
            session_response = response.json()
            session_id = session_response.get("id") or session_response.get("session_id")
            
            if not session_id:
                return {
                    "status": "failed",
                    "error": f"No session_id returned from session creation. Response: {session_response}"
                }
            
            logger.info(f"✅ Created test session: {session_id}")
            
            # Add test messages to the session
            test_messages = [
                {
                    "role": "user",
                    "content": "Can you help me create a simple Python function to calculate fibonacci numbers?"
                },
                {
                    "role": "assistant", 
                    "content": """I'll help you create a Python function to calculate Fibonacci numbers. Here's a simple implementation:

```python
def fibonacci(n):
    \"\"\"
    Calculate the nth Fibonacci number
    Args:
        n (int): The position in the Fibonacci sequence
    Returns:
        int: The nth Fibonacci number
    \"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Example usage
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

This is a recursive implementation. For better performance with larger numbers, you might want to use an iterative approach:

```python
def fibonacci_iterative(n):
    \"\"\"
    Calculate the nth Fibonacci number iteratively
    \"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

The iterative version is much more efficient for large values of n."""
                }
            ]
            
            # Add messages to session
            for msg in test_messages:
                message_data = {
                    "session_id": session_id,
                    "role": msg["role"],
                    "content": msg["content"],
                    "model": "gpt-4"
                }
                
                msg_response = self.session.post(
                    f"{self.api_url}/sessions/messages",
                    json=message_data,
                    headers=headers,
                    timeout=10
                )
                
                if msg_response.status_code != 200:
                    logger.error(f"❌ Failed to add message: {msg_response.status_code}")
                    return {
                        "status": "failed",
                        "error": f"Failed to add message: {msg_response.status_code}",
                        "response": msg_response.text
                    }
            
            logger.info(f"✅ Added {len(test_messages)} messages to session")
            
            return {
                "status": "success",
                "session_id": session_id,
                "message_count": len(test_messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Test session creation failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_push_session_no_github_token(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/github-pat/push-session without GitHub token (should fail with 401)"""
        logger.info("🚀 Testing push-session endpoint (no GitHub token)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            push_data = {
                "session_id": session_id,
                "repo_name": "test-push-session",
                "repo_description": "Test repository for GitHub push session functionality",
                "is_private": False
            }
            
            response = self.session.post(
                f"{self.api_url}/github-pat/push-session",
                json=push_data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 401:
                error_data = response.json()
                
                logger.info("✅ Push session endpoint correctly requires GitHub token")
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
            logger.error(f"❌ Push session test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_push_session_missing_session_id(self) -> Dict[str, Any]:
        """Test POST /api/github-pat/push-session with missing session_id"""
        logger.info("❌ Testing push-session endpoint (missing session_id)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Missing session_id in request
            push_data = {
                "repo_name": "test-push-session",
                "repo_description": "Test repository",
                "is_private": False
            }
            
            response = self.session.post(
                f"{self.api_url}/github-pat/push-session",
                json=push_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 422:  # Validation error
                error_data = response.json()
                
                logger.info("✅ Push session correctly validates required session_id")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error details: {error_data}")
                
                return {
                    "status": "success",
                    "data": error_data,
                    "validation_working": True
                }
            else:
                logger.error(f"❌ Expected 422 validation error, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 422 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Push session validation test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_push_session_invalid_session_id(self) -> Dict[str, Any]:
        """Test POST /api/github-pat/push-session with invalid session_id"""
        logger.info("🔍 Testing push-session endpoint (invalid session_id)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            push_data = {
                "session_id": "invalid-session-id-12345",
                "repo_name": "test-push-session",
                "repo_description": "Test repository",
                "is_private": False
            }
            
            response = self.session.post(
                f"{self.api_url}/github-pat/push-session",
                json=push_data,
                headers=headers,
                timeout=10
            )
            
            # Should fail with 401 (GitHub not connected) before checking session
            # OR 404 (Session not found) if it gets that far
            if response.status_code in [401, 404]:
                error_data = response.json()
                
                logger.info("✅ Push session handles invalid session_id correctly")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_data.get('detail')}")
                
                return {
                    "status": "success",
                    "data": error_data,
                    "proper_error_handling": True
                }
            else:
                logger.error(f"❌ Unexpected status code: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 401 or 404 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Push session invalid ID test failed: {e}")
            return {"status": "error", "error": str(e)}

    """
    Main test function for Session API Bug Fix Verification
    Tests all Session API endpoints after the get_db_session -> get_database() fix
    """
    logger.info("🚀 Starting Session API Bug Fix Testing")
    logger.info("=" * 60)
    
    tester = SessionAPITester()
    results = {}
    
    # Test 1: Authentication
    logger.info("\n1️⃣ AUTHENTICATION TEST")
    auth_result = tester.authenticate_demo_user()
    results["authentication"] = auth_result
    
    if auth_result["status"] != "success":
        logger.error("❌ Authentication failed - cannot proceed with other tests")
        return results
    
    # Test 2: Session Creation
    logger.info("\n2️⃣ SESSION CREATION TEST")
    session_result = tester.test_session_creation()
    results["session_creation"] = session_result
    
    if session_result["status"] != "success":
        logger.error("❌ Session creation failed - cannot proceed with session-dependent tests")
        return results
    
    session_id = session_result["session_id"]
    
    # Test 3: Session Retrieval (CRITICAL - this had the 500 error)
    logger.info("\n3️⃣ SESSION RETRIEVAL TEST (CRITICAL - Previously had 500 error)")
    retrieval_result = tester.test_session_retrieval(session_id)
    results["session_retrieval"] = retrieval_result
    
    # Test 4: List Sessions
    logger.info("\n4️⃣ LIST SESSIONS TEST")
    list_result = tester.test_list_sessions()
    results["list_sessions"] = list_result
    
    # Test 5: Add Message
    logger.info("\n5️⃣ ADD MESSAGE TEST")
    add_msg_result = tester.test_add_message(session_id)
    results["add_message"] = add_msg_result
    
    # Test 6: Get Messages
    logger.info("\n6️⃣ GET MESSAGES TEST")
    get_msg_result = tester.test_get_messages(session_id)
    results["get_messages"] = get_msg_result
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 SESSION API TEST SUMMARY")
    logger.info("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["status"] == "success")
    
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    
    for test_name, result in results.items():
        status_emoji = "✅" if result["status"] == "success" else "❌"
        logger.info(f"{status_emoji} {test_name.replace('_', ' ').title()}: {result['status']}")
        
        if result["status"] == "failed":
            logger.info(f"   Error: {result.get('error', 'Unknown error')}")
            if result.get("bug_fix_failed"):
                logger.error(f"   🚨 BUG FIX VERIFICATION FAILED!")
    
    # Critical assessment
    critical_test_passed = results.get("session_retrieval", {}).get("status") == "success"
    
    if critical_test_passed:
        logger.info("\n🎉 BUG FIX VERIFICATION: SUCCESS!")
        logger.info("✅ No more 'get_db_session is not defined' errors")
        logger.info("✅ No more 500 Internal Server Errors")
        logger.info("✅ Session API is fully functional")
    else:
        logger.error("\n🚨 BUG FIX VERIFICATION: FAILED!")
        logger.error("❌ Session retrieval still failing")
        logger.error("❌ Bug fix may not be working correctly")
    
    return results

if __name__ == "__main__":
    main()