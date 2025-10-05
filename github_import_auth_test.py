#!/usr/bin/env python3
"""
GitHub Import Endpoint Testing with Authentication
Tests the GitHub import functionality with proper authentication.
"""

import requests
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubImportAuthTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.session = requests.Session()
        
    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with demo user"""
        logger.info("🔐 Authenticating with demo user")
        
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
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                logger.info("✅ Authentication successful")
                return {"status": "success", "token": self.token}
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return {"status": "failed", "error": response.text}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def test_github_import_with_auth(self) -> Dict[str, Any]:
        """Test GitHub import with authentication"""
        logger.info("📥 Testing GitHub import with authentication")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        try:
            import_data = {
                "repo_url": "https://github.com/octocat/Hello-World",
                "branch": "master"
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=120
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ GitHub import successful with authentication")
                logger.info(f"   Repository: {result.get('repository', {}).get('owner')}/{result.get('repository', {}).get('name')}")
                logger.info(f"   Files imported: {result.get('import_details', {}).get('total_files', 0)}")
                return {"status": "success", "data": result}
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
                
        except Exception as e:
            logger.error(f"❌ Import test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_import_status(self) -> Dict[str, Any]:
        """Test import status endpoint"""
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
                logger.info(f"   Workspace: {status_data.get('workspace_root')}")
                return {"status": "success", "data": status_data}
            else:
                logger.error(f"❌ Status endpoint failed: {response.status_code}")
                return {"status": "failed", "status_code": response.status_code}
                
        except Exception as e:
            logger.error(f"❌ Status test failed: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Main test runner"""
    logger.info("🔄 GitHub Import Authentication Test")
    logger.info("=" * 50)
    
    tester = GitHubImportAuthTester()
    
    # Step 1: Authenticate
    auth_result = tester.authenticate()
    print(f"Authentication: {auth_result['status']}")
    
    if auth_result['status'] != 'success':
        print("❌ Cannot proceed without authentication")
        return
    
    # Step 2: Test import status
    status_result = tester.test_import_status()
    print(f"Import Status: {status_result['status']}")
    
    # Step 3: Test GitHub import with auth
    import_result = tester.test_github_import_with_auth()
    print(f"GitHub Import: {import_result['status']}")
    
    if import_result['status'] == 'success':
        print("✅ GitHub import working with authentication")
    else:
        print(f"❌ GitHub import failed: {import_result.get('error')}")
    
    return import_result

if __name__ == "__main__":
    main()