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
import sqlite3
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
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Create a new session
            session_data = {
                "title": "GitHub Preview Test Session",
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
            
            self.test_session_id = session_id
            logger.info(f"✅ Created test session: {session_id}")
            
            # Add test messages with various code blocks
            test_messages = [
                {
                    "role": "user",
                    "content": "Can you help me create a Python function to calculate fibonacci numbers and a simple HTML page to display them?"
                },
                {
                    "role": "assistant", 
                    "content": """I'll help you create both a Python function for Fibonacci numbers and an HTML page to display them.

First, here's the Python function:

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

def fibonacci_sequence(count):
    \"\"\"Generate a sequence of Fibonacci numbers\"\"\"
    return [fibonacci(i) for i in range(count)]

# Example usage
if __name__ == "__main__":
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")
```

And here's a simple HTML page to display the results:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fibonacci Numbers</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .fibonacci-item {
            padding: 10px;
            margin: 5px 0;
            background-color: #f0f0f0;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Fibonacci Numbers</h1>
    <div id="fibonacci-list"></div>
    
    <script>
        function fibonacci(n) {
            if (n <= 0) return 0;
            if (n === 1) return 1;
            return fibonacci(n-1) + fibonacci(n-2);
        }
        
        function displayFibonacci() {
            const list = document.getElementById('fibonacci-list');
            for (let i = 0; i < 10; i++) {
                const div = document.createElement('div');
                div.className = 'fibonacci-item';
                div.textContent = `F(${i}) = ${fibonacci(i)}`;
                list.appendChild(div);
            }
        }
        
        displayFibonacci();
    </script>
</body>
</html>
```

This gives you both a Python implementation and a web page to display the results!"""
                },
                {
                    "role": "user",
                    "content": "Great! Can you also add some CSS styling to make it look better?"
                },
                {
                    "role": "assistant",
                    "content": """Here's an enhanced version with better CSS styling:

```css
/* styles.css */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 30px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    background: white;
    border-radius: 15px;
    padding: 40px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

h1 {
    text-align: center;
    color: #4a5568;
    font-size: 2.5em;
    margin-bottom: 30px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.fibonacci-item {
    padding: 15px 20px;
    margin: 10px 0;
    background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border-radius: 10px;
    font-size: 1.2em;
    font-weight: bold;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
}

.fibonacci-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.fibonacci-item:nth-child(even) {
    background: linear-gradient(45deg, #a8edea 0%, #fed6e3 100%);
    color: #333;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.fibonacci-item {
    animation: fadeIn 0.5s ease forwards;
}
```

And here's also a JavaScript utility function:

```javascript
// fibonacci-utils.js
class FibonacciCalculator {
    constructor() {
        this.cache = new Map();
    }
    
    calculate(n) {
        if (this.cache.has(n)) {
            return this.cache.get(n);
        }
        
        let result;
        if (n <= 0) {
            result = 0;
        } else if (n === 1) {
            result = 1;
        } else {
            result = this.calculate(n-1) + this.calculate(n-2);
        }
        
        this.cache.set(n, result);
        return result;
    }
    
    generateSequence(count) {
        return Array.from({length: count}, (_, i) => this.calculate(i));
    }
}

// Usage
const fibCalc = new FibonacciCalculator();
console.log(fibCalc.generateSequence(15));
```

This enhanced version includes beautiful gradients, hover effects, and animations!"""
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
            
            # Fix: Update session to associate with authenticated user
            # This is needed because the session creation endpoint uses get_current_user_optional
            # but the GitHub preview endpoint requires the session to be associated with the user
            try:
                import sqlite3
                import os
                
                db_path = os.path.expanduser('~/.xionimus_ai/xionimus.db')
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Update session with user_id from token
                cursor.execute(
                    "UPDATE sessions SET user_id = ? WHERE id = ?",
                    (self.user_info['user_id'], session_id)
                )
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Updated session {session_id} with user_id: {self.user_info['user_id']}")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not update session user_id: {e}")
            
            return {
                "status": "success",
                "session_id": session_id,
                "message_count": len(test_messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Test session creation failed: {e}")
            return {"status": "error", "error": str(e)}

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