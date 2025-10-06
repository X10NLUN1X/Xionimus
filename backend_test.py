#!/usr/bin/env python3
"""
HARDENING FEATURES RETEST - Focus on Previously Failed Features

RETEST FOCUS:
1. M2: API Versioning - Test /api/v1/health and /api/version endpoints (should be public now)
2. L4: Prometheus Metrics - Test /api/metrics and /api/v1/metrics endpoints (should be public now)  
3. L1: CORS Configuration - Verify CORS headers in API responses
4. H4: Test Coverage - Run test_jwt_auth.py and test_rate_limiting.py

SUCCESS CRITERIA:
- /api/v1/health returns 200 without auth ✅
- /api/metrics returns Prometheus metrics without auth ✅
- CORS headers present in responses ✅
- More tests passing ✅
"""

import requests
import json
import time
import logging
import sqlite3
import os
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardeningRetester:
    def __init__(self, base_url: str = None):
        # Use localhost for testing since we're in the same container
        self.base_url = base_url or "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.db_path = os.path.expanduser("~/.xionimus_ai/xionimus.db")
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
                
                return {"status": "success", "token": self.token, "user_info": self.user_info}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {"status": "failed", "error": error_detail}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def test_dependency_resolution(self) -> Dict[str, Any]:
        """Test H1: Dependency Resolution - Backend starts without conflicts"""
        logger.info("🔧 Testing Dependency Resolution (H1)")
        
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

    def test_api_versioning_public_endpoints(self) -> Dict[str, Any]:
        """Test M2: API Versioning - Public endpoints should work without auth"""
        logger.info("🔄 Testing API Versioning (M2) - Public endpoints without auth")
        
        results = {}
        
        # Test endpoints that should be public
        public_endpoints = [
            "/api/v1/health",
            "/api/health", 
            "/api/version",
            "/api/v1/version"
        ]
        
        for endpoint in public_endpoints:
            try:
                logger.info(f"   Testing {endpoint}")
                
                # NO Authorization header - should work for public endpoints
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                logger.info(f"   Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ {endpoint} accessible without auth")
                    
                    # Check for version info in response
                    if "version" in data or "status" in data:
                        logger.info(f"   Response contains expected fields: {list(data.keys())}")
                        results[endpoint] = {
                            "status": "success",
                            "public_access": True,
                            "response_data": data
                        }
                    else:
                        results[endpoint] = {
                            "status": "partial",
                            "public_access": True,
                            "error": "Response missing expected fields",
                            "response_data": data
                        }
                elif response.status_code == 401:
                    logger.error(f"❌ {endpoint} still requires authentication!")
                    results[endpoint] = {
                        "status": "failed",
                        "public_access": False,
                        "error": "Endpoint still requires authentication",
                        "status_code": response.status_code
                    }
                else:
                    error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                    logger.error(f"❌ {endpoint} failed: {error_detail}")
                    results[endpoint] = {
                        "status": "failed",
                        "error": error_detail,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} test failed: {e}")
                results[endpoint] = {"status": "error", "error": str(e)}
        
        # Summary
        successful_endpoints = [ep for ep, result in results.items() if result["status"] == "success"]
        failed_endpoints = [ep for ep, result in results.items() if result["status"] == "failed"]
        
        logger.info(f"✅ API Versioning Test Summary:")
        logger.info(f"   Successful public endpoints: {len(successful_endpoints)}")
        logger.info(f"   Failed endpoints: {len(failed_endpoints)}")
        
        return {
            "status": "success" if len(failed_endpoints) == 0 else "partial",
            "successful_endpoints": successful_endpoints,
            "failed_endpoints": failed_endpoints,
            "results": results,
            "total_tested": len(public_endpoints)
        }

    def test_prometheus_metrics_public_access(self) -> Dict[str, Any]:
        """Test L4: Prometheus Metrics - Should be accessible without auth"""
        logger.info("📊 Testing Prometheus Metrics (L4) - Public access without auth")
        
        results = {}
        
        # Test metrics endpoints that should be public
        metrics_endpoints = [
            "/api/metrics",
            "/api/v1/metrics"
        ]
        
        for endpoint in metrics_endpoints:
            try:
                logger.info(f"   Testing {endpoint}")
                
                # NO Authorization header - should work for public endpoints
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers={"Accept": "text/plain"},  # Prometheus format
                    timeout=10
                )
                
                logger.info(f"   Response status: {response.status_code}")
                logger.info(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
                
                if response.status_code == 200:
                    content = response.text
                    logger.info(f"✅ {endpoint} accessible without auth")
                    logger.info(f"   Response length: {len(content)} characters")
                    
                    # Check if it's Prometheus format
                    is_prometheus_format = (
                        "# HELP" in content or 
                        "# TYPE" in content or
                        "_total" in content or
                        "_count" in content
                    )
                    
                    if is_prometheus_format:
                        logger.info("✅ Response is in Prometheus format")
                        
                        # Count metrics
                        help_lines = content.count("# HELP")
                        type_lines = content.count("# TYPE")
                        
                        logger.info(f"   Metrics found: {help_lines} HELP lines, {type_lines} TYPE lines")
                        
                        results[endpoint] = {
                            "status": "success",
                            "public_access": True,
                            "prometheus_format": True,
                            "metrics_count": help_lines,
                            "content_length": len(content)
                        }
                    else:
                        logger.warning("⚠️ Response not in expected Prometheus format")
                        results[endpoint] = {
                            "status": "partial",
                            "public_access": True,
                            "prometheus_format": False,
                            "error": "Not in Prometheus format",
                            "content_preview": content[:200]
                        }
                elif response.status_code == 401:
                    logger.error(f"❌ {endpoint} still requires authentication!")
                    results[endpoint] = {
                        "status": "failed",
                        "public_access": False,
                        "error": "Endpoint still requires authentication",
                        "status_code": response.status_code
                    }
                else:
                    error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                    logger.error(f"❌ {endpoint} failed: {error_detail}")
                    results[endpoint] = {
                        "status": "failed",
                        "error": error_detail,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} test failed: {e}")
                results[endpoint] = {"status": "error", "error": str(e)}
        
        # Summary
        successful_endpoints = [ep for ep, result in results.items() if result["status"] == "success"]
        failed_endpoints = [ep for ep, result in results.items() if result["status"] == "failed"]
        
        logger.info(f"✅ Prometheus Metrics Test Summary:")
        logger.info(f"   Successful public endpoints: {len(successful_endpoints)}")
        logger.info(f"   Failed endpoints: {len(failed_endpoints)}")
        
        return {
            "status": "success" if len(failed_endpoints) == 0 else "partial",
            "successful_endpoints": successful_endpoints,
            "failed_endpoints": failed_endpoints,
            "results": results,
            "total_tested": len(metrics_endpoints)
        }

    def test_cors_configuration(self) -> Dict[str, Any]:
        """Test L1: CORS Configuration - Check CORS headers in responses"""
        logger.info("🌐 Testing CORS Configuration (L1) - Verify CORS headers")
        
        results = {}
        
        # Test various endpoints for CORS headers
        test_endpoints = [
            "/api/health",
            "/api/v1/health",
            "/api/metrics",
            "/api/version"
        ]
        
        # Test different HTTP methods and origins
        test_scenarios = [
            {"method": "GET", "origin": "http://localhost:3000"},
            {"method": "GET", "origin": "https://app.xionimus.ai"},
            {"method": "OPTIONS", "origin": "http://localhost:3000"}  # Preflight request
        ]
        
        for endpoint in test_endpoints:
            results[endpoint] = {}
            
            for scenario in test_scenarios:
                scenario_key = f"{scenario['method']}_{scenario['origin']}"
                
                try:
                    logger.info(f"   Testing {endpoint} with {scenario['method']} from {scenario['origin']}")
                    
                    headers = {
                        "Origin": scenario["origin"],
                        "Content-Type": "application/json"
                    }
                    
                    if scenario["method"] == "OPTIONS":
                        # Preflight request
                        headers.update({
                            "Access-Control-Request-Method": "GET",
                            "Access-Control-Request-Headers": "Content-Type,Authorization"
                        })
                    
                    response = self.session.request(
                        scenario["method"],
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=10
                    )
                    
                    logger.info(f"   Response status: {response.status_code}")
                    
                    # Check CORS headers
                    cors_headers = {
                        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                        "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                        "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
                    }
                    
                    # Log found CORS headers
                    found_headers = {k: v for k, v in cors_headers.items() if v is not None}
                    logger.info(f"   CORS headers found: {found_headers}")
                    
                    # Check if essential CORS headers are present
                    has_allow_origin = cors_headers["Access-Control-Allow-Origin"] is not None
                    
                    if has_allow_origin:
                        logger.info(f"✅ CORS headers present for {scenario_key}")
                        results[endpoint][scenario_key] = {
                            "status": "success",
                            "cors_headers": cors_headers,
                            "has_cors": True
                        }
                    else:
                        logger.warning(f"⚠️ Missing CORS headers for {scenario_key}")
                        results[endpoint][scenario_key] = {
                            "status": "partial",
                            "cors_headers": cors_headers,
                            "has_cors": False,
                            "error": "Missing Access-Control-Allow-Origin header"
                        }
                        
                except Exception as e:
                    logger.error(f"❌ CORS test failed for {endpoint} {scenario_key}: {e}")
                    results[endpoint][scenario_key] = {"status": "error", "error": str(e)}
        
        # Summary
        total_tests = len(test_endpoints) * len(test_scenarios)
        successful_tests = sum(
            1 for endpoint_results in results.values() 
            for scenario_result in endpoint_results.values() 
            if scenario_result["status"] == "success"
        )
        
        logger.info(f"✅ CORS Configuration Test Summary:")
        logger.info(f"   Successful CORS tests: {successful_tests}/{total_tests}")
        
        return {
            "status": "success" if successful_tests > 0 else "failed",
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "results": results,
            "cors_working": successful_tests > 0
        }

    def run_test_coverage_scripts(self) -> Dict[str, Any]:
        """Test H4: Test Coverage - Run test_jwt_auth.py and test_rate_limiting.py"""
        logger.info("🧪 Testing Test Coverage (H4) - Running test scripts")
        
        results = {}
        
        # Test scripts to run
        test_scripts = [
            "/app/test_jwt_auth.py",
            "/app/test_rate_limiting.py"
        ]
        
        for script_path in test_scripts:
            script_name = os.path.basename(script_path)
            logger.info(f"   Running {script_name}")
            
            try:
                # Check if script exists
                if not os.path.exists(script_path):
                    logger.warning(f"⚠️ {script_name} not found at {script_path}")
                    results[script_name] = {
                        "status": "not_found",
                        "error": f"Script not found at {script_path}"
                    }
                    continue
                
                # Run the script
                result = subprocess.run(
                    ["python3", script_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd="/app"
                )
                
                logger.info(f"   Exit code: {result.returncode}")
                
                if result.returncode == 0:
                    logger.info(f"✅ {script_name} passed")
                    results[script_name] = {
                        "status": "success",
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                else:
                    logger.error(f"❌ {script_name} failed with exit code {result.returncode}")
                    logger.error(f"   STDOUT: {result.stdout}")
                    logger.error(f"   STDERR: {result.stderr}")
                    results[script_name] = {
                        "status": "failed",
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ {script_name} timed out after 60 seconds")
                results[script_name] = {
                    "status": "timeout",
                    "error": "Script execution timed out"
                }
            except Exception as e:
                logger.error(f"❌ {script_name} execution failed: {e}")
                results[script_name] = {"status": "error", "error": str(e)}
        
        # Summary
        successful_scripts = [name for name, result in results.items() if result["status"] == "success"]
        failed_scripts = [name for name, result in results.items() if result["status"] in ["failed", "error", "timeout"]]
        
        logger.info(f"✅ Test Coverage Summary:")
        logger.info(f"   Successful scripts: {len(successful_scripts)}")
        logger.info(f"   Failed scripts: {len(failed_scripts)}")
        
        return {
            "status": "success" if len(failed_scripts) == 0 else "partial",
            "successful_scripts": successful_scripts,
            "failed_scripts": failed_scripts,
            "results": results,
            "total_tested": len(test_scripts)
        }

def main():
    """
    Main test function for Hardening Features Retest
    """
    logger.info("🚀 Starting Hardening Features Retest")
    logger.info("=" * 60)
    logger.info("RETEST FOCUS: Previously Failed Hardening Features")
    logger.info("1. M2: API Versioning - Public endpoints")
    logger.info("2. L4: Prometheus Metrics - Public access")
    logger.info("3. L1: CORS Configuration - Headers verification")
    logger.info("4. H4: Test Coverage - Run test scripts")
    logger.info("=" * 60)
    
    tester = HardeningRetester()
    results = {}
    
    # Test 1: API Versioning (M2) - Public endpoints should work without auth
    logger.info("\n1️⃣ API VERSIONING (M2) - Public Endpoints")
    api_versioning_result = tester.test_api_versioning_public_endpoints()
    results["api_versioning"] = api_versioning_result
    
    # Test 2: Prometheus Metrics (L4) - Should be accessible without auth
    logger.info("\n2️⃣ PROMETHEUS METRICS (L4) - Public Access")
    metrics_result = tester.test_prometheus_metrics_public_access()
    results["prometheus_metrics"] = metrics_result
    
    # Test 3: CORS Configuration (L1) - Check CORS headers
    logger.info("\n3️⃣ CORS CONFIGURATION (L1) - Headers Verification")
    cors_result = tester.test_cors_configuration()
    results["cors_configuration"] = cors_result
    
    # Test 4: Test Coverage (H4) - Run test scripts
    logger.info("\n4️⃣ TEST COVERAGE (H4) - Run Test Scripts")
    test_coverage_result = tester.run_test_coverage_scripts()
    results["test_coverage"] = test_coverage_result
    
    # Optional: Authentication test for comparison
    logger.info("\n5️⃣ AUTHENTICATION TEST (for comparison)")
    auth_result = tester.authenticate_demo_user()
    results["authentication"] = auth_result
    
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

if __name__ == "__main__":
    main()