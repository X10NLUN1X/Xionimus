#!/usr/bin/env python3
"""
FOCUSED BACKEND TESTING - Current Functionality Verification
Testing specific areas that need retesting based on test_result.md
"""

import requests
import json
import time
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FocusedTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None

    def authenticate(self) -> bool:
        """Authenticate with demo user"""
        logger.info("🔐 Authenticating with demo user (demo/demo123)")
        
        try:
            login_data = {"username": "demo", "password": "demo123"}
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                logger.info("✅ Authentication successful!")
                return True
            else:
                logger.error(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False

    def test_health_endpoints(self) -> Dict[str, Any]:
        """Test health endpoints for API versioning"""
        logger.info("🏥 Testing Health Endpoints (API Versioning)")
        
        results = {}
        endpoints = ["/api/health", "/api/v1/health"]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                logger.info(f"   {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    results[endpoint] = {
                        "status": "success",
                        "data": data,
                        "database_type": data.get("services", {}).get("database", {}).get("type"),
                        "ai_providers": data.get("services", {}).get("ai_providers", {}).get("configured", 0)
                    }
                else:
                    results[endpoint] = {"status": "failed", "status_code": response.status_code}
            except Exception as e:
                results[endpoint] = {"status": "error", "error": str(e)}
        
        return results

    def test_rate_limits_endpoints(self) -> Dict[str, Any]:
        """Test rate limiting endpoints"""
        logger.info("⚡ Testing Rate Limiting Endpoints")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        results = {}
        
        # Test public rate limits endpoint
        try:
            response = self.session.get(f"{self.api_url}/rate-limits/limits", timeout=10)
            logger.info(f"   /api/rate-limits/limits: {response.status_code}")
            results["limits"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code
            }
        except Exception as e:
            results["limits"] = {"status": "error", "error": str(e)}
        
        # Test user quota endpoint (requires auth)
        try:
            response = self.session.get(f"{self.api_url}/rate-limits/quota", headers=headers, timeout=10)
            logger.info(f"   /api/rate-limits/quota: {response.status_code}")
            results["quota"] = {
                "status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code
            }
        except Exception as e:
            results["quota"] = {"status": "error", "error": str(e)}
        
        return results

    def test_developer_modes(self) -> Dict[str, Any]:
        """Test developer modes endpoints"""
        logger.info("🎯 Testing Developer Modes")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        results = {}
        
        # Test developer modes list
        try:
            response = self.session.get(f"{self.api_url}/developer-modes/", headers=headers, timeout=10)
            logger.info(f"   /api/developer-modes/: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results["list"] = {
                    "status": "success",
                    "modes_count": len(data.get("modes", [])),
                    "modes": data.get("modes", [])
                }
            else:
                results["list"] = {"status": "failed", "status_code": response.status_code}
        except Exception as e:
            results["list"] = {"status": "error", "error": str(e)}
        
        return results

    def test_claude_integration(self) -> Dict[str, Any]:
        """Test Claude AI integration with actual API calls"""
        logger.info("🤖 Testing Claude AI Integration")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        results = {}
        
        # Test 1: Simple Claude Sonnet request
        try:
            chat_data = {
                "messages": [{"role": "user", "content": "Say 'Claude Sonnet working' if you can respond"}],
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929"
            }
            
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Claude Sonnet test: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", "")
                results["sonnet"] = {
                    "status": "success",
                    "response_length": len(content),
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "working_response": "working" in content.lower()
                }
            else:
                error_detail = response.json().get("detail", "Unknown") if response.content else f"HTTP {response.status_code}"
                results["sonnet"] = {"status": "failed", "error": error_detail}
                
        except Exception as e:
            results["sonnet"] = {"status": "error", "error": str(e)}
        
        # Test 2: Test with Junior Developer Mode
        try:
            chat_data = {
                "messages": [{"role": "user", "content": "What is Python?"}],
                "developer_mode": "junior"
            }
            
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Junior mode test: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                results["junior_mode"] = {
                    "status": "success",
                    "provider": result.get("provider"),
                    "model": result.get("model"),
                    "ultra_thinking": result.get("usage", {}).get("thinking_used", False)
                }
            else:
                error_detail = response.json().get("detail", "Unknown") if response.content else f"HTTP {response.status_code}"
                results["junior_mode"] = {"status": "failed", "error": error_detail}
                
        except Exception as e:
            results["junior_mode"] = {"status": "error", "error": str(e)}
        
        return results

    def test_session_management(self) -> Dict[str, Any]:
        """Test session management and active project fields"""
        logger.info("📝 Testing Session Management")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        results = {}
        
        # Test 1: Create session and check fields
        try:
            session_data = {"name": "Test Session for Active Project"}
            response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Session creation: {response.status_code}")
            
            if response.status_code == 200:
                session = response.json()
                session_id = session.get("id")
                
                # Check if active_project fields exist
                has_active_project = "active_project" in session
                has_active_project_branch = "active_project_branch" in session
                
                results["session_creation"] = {
                    "status": "success",
                    "session_id": session_id,
                    "has_active_project_field": has_active_project,
                    "has_active_project_branch_field": has_active_project_branch,
                    "session_fields": list(session.keys())
                }
                
                # Test 2: Try to get session details
                detail_response = self.session.get(
                    f"{self.api_url}/sessions/{session_id}",
                    headers=headers,
                    timeout=10
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    results["session_details"] = {
                        "status": "success",
                        "fields": list(detail_data.keys()),
                        "has_active_project": "active_project" in detail_data,
                        "has_active_project_branch": "active_project_branch" in detail_data
                    }
                else:
                    results["session_details"] = {"status": "failed", "status_code": detail_response.status_code}
                    
            else:
                results["session_creation"] = {"status": "failed", "status_code": response.status_code}
                
        except Exception as e:
            results["session_creation"] = {"status": "error", "error": str(e)}
        
        return results

    def test_workspace_endpoints(self) -> Dict[str, Any]:
        """Test workspace endpoints for setting active project"""
        logger.info("🗂️ Testing Workspace Endpoints")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        results = {}
        
        # Test if set-active-project endpoint exists
        endpoints_to_test = [
            "/api/workspace/set-active",
            "/api/workspace/set-active-project",
            "/api/sessions/set-active-project"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                # Try GET first to see if endpoint exists
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers, timeout=10)
                logger.info(f"   {endpoint}: {response.status_code}")
                
                results[endpoint] = {
                    "exists": response.status_code != 404,
                    "status_code": response.status_code
                }
            except Exception as e:
                results[endpoint] = {"status": "error", "error": str(e)}
        
        return results

    def run_focused_tests(self):
        """Run all focused tests"""
        logger.info("🚀 Starting Focused Backend Testing")
        logger.info("=" * 60)
        
        # Authenticate first
        if not self.authenticate():
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return
        
        test_results = {}
        
        # Run focused tests
        test_results["health"] = self.test_health_endpoints()
        test_results["rate_limits"] = self.test_rate_limits_endpoints()
        test_results["developer_modes"] = self.test_developer_modes()
        test_results["claude_integration"] = self.test_claude_integration()
        test_results["session_management"] = self.test_session_management()
        test_results["workspace"] = self.test_workspace_endpoints()
        
        # Summary
        logger.info("\n📊 FOCUSED TEST SUMMARY")
        logger.info("=" * 60)
        
        for test_name, result in test_results.items():
            if isinstance(result, dict):
                if result.get("status") == "success":
                    logger.info(f"✅ {test_name}: SUCCESS")
                elif result.get("status") == "failed":
                    logger.info(f"❌ {test_name}: FAILED")
                elif result.get("status") == "error":
                    logger.info(f"🚨 {test_name}: ERROR")
                else:
                    # Complex result - check sub-results
                    success_count = 0
                    total_count = 0
                    for key, value in result.items():
                        if isinstance(value, dict) and "status" in value:
                            total_count += 1
                            if value["status"] == "success":
                                success_count += 1
                    
                    if total_count > 0:
                        logger.info(f"📊 {test_name}: {success_count}/{total_count} passed")
                    else:
                        logger.info(f"📋 {test_name}: Completed")
        
        return test_results

if __name__ == "__main__":
    tester = FocusedTester()
    tester.run_focused_tests()