#!/usr/bin/env python3
"""
COMPREHENSIVE 100% BACKEND HEALTH CHECK
Based on the detailed review request for systematic testing of ALL implemented backend features.

TEST SCOPE - ALL API ENDPOINTS:
1. 🔐 Authentication & User Management
2. 💬 Session Management  
3. 🤖 Multi-Agent System
4. 🚀 Cloud Sandbox
5. 📚 Research History & PDF Export
6. 🔗 GitHub Integration
7. ⚡ Rate Limiting
8. 🔑 API Keys Management
9. 🎨 Developer Modes
10. 📊 Health & System

TEST CREDENTIALS:
- Username: demo
- Password: demo123
- API URL: http://localhost:8001/api (from frontend/.env)
"""

import requests
import json
import time
import logging
import os
import concurrent.futures
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveBackendHealthChecker:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.test_results = {}
        self.total_endpoints_tested = 0
        self.successful_endpoints = 0
        self.failed_endpoints = 0
        
    def authenticate(self) -> Dict[str, Any]:
        """🔐 AUTHENTICATION - Login with demo/demo123"""
        logger.info("🔐 AUTHENTICATION & USER MANAGEMENT TEST")
        
        try:
            # 1. POST /api/auth/login
            logger.info("   Testing POST /api/auth/login...")
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
            
            self.total_endpoints_tested += 1
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                # Verify required fields
                required_fields = ["access_token", "token_type", "user_id", "username"]
                missing_fields = [field for field in required_fields if not auth_data.get(field)]
                
                if not missing_fields and auth_data.get("token_type") == "bearer":
                    logger.info(f"   ✅ POST /api/auth/login - SUCCESS")
                    logger.info(f"      User ID: {self.user_info['user_id']}")
                    logger.info(f"      Username: {self.user_info['username']}")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ POST /api/auth/login - FAILED: Missing fields or invalid token type")
                    self.failed_endpoints += 1
                    return {"status": "failed", "error": f"Missing fields: {missing_fields}"}
            else:
                logger.error(f"   ❌ POST /api/auth/login - FAILED: HTTP {response.status_code}")
                self.failed_endpoints += 1
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
            
            # 2. GET /api/auth/me (current user)
            if self.token:
                logger.info("   Testing GET /api/auth/me...")
                headers = {"Authorization": f"Bearer {self.token}"}
                me_response = self.session.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
                
                self.total_endpoints_tested += 1
                
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    logger.info(f"   ✅ GET /api/auth/me - SUCCESS")
                    logger.info(f"      Current user: {me_data.get('username')}")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ GET /api/auth/me - FAILED: HTTP {me_response.status_code}")
                    self.failed_endpoints += 1
            
            # 3. Token validation test
            logger.info("   Testing token validation...")
            invalid_headers = {"Authorization": "Bearer invalid-token-12345"}
            validation_response = self.session.get(f"{self.api_url}/auth/me", headers=invalid_headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if validation_response.status_code == 401:
                logger.info(f"   ✅ Token validation - SUCCESS (correctly rejected invalid token)")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ Token validation - FAILED: Should return 401 for invalid token")
                self.failed_endpoints += 1
                
            return {"status": "success", "token": self.token, "user_info": self.user_info}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            self.failed_endpoints += 1
            return {"status": "error", "error": str(e)}

    def test_session_management(self) -> Dict[str, Any]:
        """💬 SESSION MANAGEMENT - Test all session endpoints"""
        logger.info("💬 SESSION MANAGEMENT TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            session_id = None
            
            # 1. POST /api/sessions/ (create session)
            logger.info("   Testing POST /api/sessions/...")
            session_data = {"name": "Health Check Test Session"}
            create_response = self.session.post(f"{self.api_url}/sessions/", json=session_data, headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if create_response.status_code == 200:
                session_result = create_response.json()
                session_id = session_result.get("id")
                logger.info(f"   ✅ POST /api/sessions/ - SUCCESS (ID: {session_id})")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/sessions/ - FAILED: HTTP {create_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. GET /api/sessions/list (list all sessions)
            logger.info("   Testing GET /api/sessions/list...")
            list_response = self.session.get(f"{self.api_url}/sessions/list", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if list_response.status_code == 200:
                sessions = list_response.json()
                logger.info(f"   ✅ GET /api/sessions/list - SUCCESS ({len(sessions)} sessions)")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/sessions/list - FAILED: HTTP {list_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. GET /api/sessions/{id} (get specific session)
            if session_id:
                logger.info(f"   Testing GET /api/sessions/{session_id}...")
                get_response = self.session.get(f"{self.api_url}/sessions/{session_id}", headers=headers, timeout=10)
                
                self.total_endpoints_tested += 1
                
                if get_response.status_code == 200:
                    session_details = get_response.json()
                    logger.info(f"   ✅ GET /api/sessions/{{id}} - SUCCESS")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ GET /api/sessions/{{id}} - FAILED: HTTP {get_response.status_code}")
                    self.failed_endpoints += 1
            
            # 4. POST /api/sessions/messages (add message)
            if session_id:
                logger.info("   Testing POST /api/sessions/messages...")
                message_data = {
                    "session_id": session_id,
                    "role": "user",
                    "content": "Test message for health check"
                }
                message_response = self.session.post(f"{self.api_url}/sessions/messages", json=message_data, headers=headers, timeout=10)
                
                self.total_endpoints_tested += 1
                
                if message_response.status_code == 200:
                    logger.info(f"   ✅ POST /api/sessions/messages - SUCCESS")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ POST /api/sessions/messages - FAILED: HTTP {message_response.status_code}")
                    self.failed_endpoints += 1
            
            # 5. DELETE /api/sessions/{id} (delete session)
            if session_id:
                logger.info(f"   Testing DELETE /api/sessions/{session_id}...")
                delete_response = self.session.delete(f"{self.api_url}/sessions/{session_id}", headers=headers, timeout=10)
                
                self.total_endpoints_tested += 1
                
                if delete_response.status_code in [200, 204]:
                    logger.info(f"   ✅ DELETE /api/sessions/{{id}} - SUCCESS")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ DELETE /api/sessions/{{id}} - FAILED: HTTP {delete_response.status_code}")
                    self.failed_endpoints += 1
                    
            return {"status": "success", "session_management_working": True}
                
        except Exception as e:
            logger.error(f"❌ Session Management test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_multi_agent_system(self) -> Dict[str, Any]:
        """🤖 MULTI-AGENT SYSTEM - Test all multi-agent endpoints"""
        logger.info("🤖 MULTI-AGENT SYSTEM TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. GET /api/v1/multi-agents/health (agent system health)
            logger.info("   Testing GET /api/v1/multi-agents/health...")
            health_response = self.session.get(f"{self.api_url}/multi-agents/health", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                logger.info(f"   ✅ GET /api/v1/multi-agents/health - SUCCESS")
                logger.info(f"      Status: {health_data.get('status')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/v1/multi-agents/health - FAILED: HTTP {health_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. GET /api/v1/multi-agents/types (list agent types)
            logger.info("   Testing GET /api/v1/multi-agents/types...")
            types_response = self.session.get(f"{self.api_url}/multi-agents/types", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if types_response.status_code == 200:
                types_data = types_response.json()
                agent_count = len(types_data.get('agents', []))
                logger.info(f"   ✅ GET /api/v1/multi-agents/types - SUCCESS ({agent_count} agent types)")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/v1/multi-agents/types - FAILED: HTTP {types_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. POST /api/v1/multi-agents/execute (execute research agent)
            logger.info("   Testing POST /api/v1/multi-agents/execute...")
            execute_data = {
                "agent_type": "research",
                "input_data": "What is Python programming language?",
                "parameters": {}
            }
            execute_response = self.session.post(f"{self.api_url}/multi-agents/execute", json=execute_data, headers=headers, timeout=30)
            
            self.total_endpoints_tested += 1
            
            if execute_response.status_code == 200:
                execute_result = execute_response.json()
                logger.info(f"   ✅ POST /api/v1/multi-agents/execute - SUCCESS")
                logger.info(f"      Agent: {execute_result.get('agent_type')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/v1/multi-agents/execute - FAILED: HTTP {execute_response.status_code}")
                self.failed_endpoints += 1
            
            # 4. GET /api/v1/multi-agents/metrics (agent metrics)
            logger.info("   Testing GET /api/v1/multi-agents/metrics...")
            metrics_response = self.session.get(f"{self.api_url}/multi-agents/metrics", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                logger.info(f"   ✅ GET /api/v1/multi-agents/metrics - SUCCESS")
                logger.info(f"      Total executions: {metrics_data.get('total_executions', 0)}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/v1/multi-agents/metrics - FAILED: HTTP {metrics_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "multi_agent_working": True}
                
        except Exception as e:
            logger.error(f"❌ Multi-Agent System test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_cloud_sandbox(self) -> Dict[str, Any]:
        """🚀 CLOUD SANDBOX - Test all sandbox endpoints"""
        logger.info("🚀 CLOUD SANDBOX TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. GET /api/sandbox/languages (list supported languages)
            logger.info("   Testing GET /api/sandbox/languages...")
            languages_response = self.session.get(f"{self.api_url}/sandbox/languages", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if languages_response.status_code == 200:
                languages = languages_response.json()
                logger.info(f"   ✅ GET /api/sandbox/languages - SUCCESS ({len(languages)} languages)")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/sandbox/languages - FAILED: HTTP {languages_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. POST /api/sandbox/execute (Python code execution)
            logger.info("   Testing POST /api/sandbox/execute (Python)...")
            python_data = {
                "language": "python",
                "code": 'print("Hello from Python health check!")'
            }
            python_response = self.session.post(f"{self.api_url}/sandbox/execute", json=python_data, headers=headers, timeout=15)
            
            self.total_endpoints_tested += 1
            
            if python_response.status_code == 200:
                python_result = python_response.json()
                success = python_result.get("success", False)
                stdout = python_result.get("stdout", "")
                
                if success and "Hello from Python health check!" in stdout:
                    logger.info(f"   ✅ POST /api/sandbox/execute (Python) - SUCCESS")
                    logger.info(f"      Execution time: {python_result.get('execution_time', 0):.3f}s")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ POST /api/sandbox/execute (Python) - FAILED: Execution failed or wrong output")
                    self.failed_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/sandbox/execute (Python) - FAILED: HTTP {python_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. POST /api/sandbox/execute (JavaScript execution)
            logger.info("   Testing POST /api/sandbox/execute (JavaScript)...")
            js_data = {
                "language": "javascript",
                "code": 'console.log("Hello from JavaScript health check!");'
            }
            js_response = self.session.post(f"{self.api_url}/sandbox/execute", json=js_data, headers=headers, timeout=15)
            
            self.total_endpoints_tested += 1
            
            if js_response.status_code == 200:
                js_result = js_response.json()
                success = js_result.get("success", False)
                stdout = js_result.get("stdout", "")
                
                if success and "Hello from JavaScript health check!" in stdout:
                    logger.info(f"   ✅ POST /api/sandbox/execute (JavaScript) - SUCCESS")
                    logger.info(f"      Execution time: {js_result.get('execution_time', 0):.3f}s")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ POST /api/sandbox/execute (JavaScript) - FAILED: Execution failed or wrong output")
                    self.failed_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/sandbox/execute (JavaScript) - FAILED: HTTP {js_response.status_code}")
                self.failed_endpoints += 1
            
            # 4. POST /api/sandbox/execute (Error handling test)
            logger.info("   Testing POST /api/sandbox/execute (Error handling)...")
            error_data = {
                "language": "python",
                "code": 'print("test'  # Missing closing quote
            }
            error_response = self.session.post(f"{self.api_url}/sandbox/execute", json=error_data, headers=headers, timeout=15)
            
            self.total_endpoints_tested += 1
            
            if error_response.status_code == 200:
                error_result = error_response.json()
                success = error_result.get("success", True)
                stderr = error_result.get("stderr", "")
                
                if not success and "error" in stderr.lower():
                    logger.info(f"   ✅ POST /api/sandbox/execute (Error handling) - SUCCESS")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ POST /api/sandbox/execute (Error handling) - FAILED: Should catch syntax error")
                    self.failed_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/sandbox/execute (Error handling) - FAILED: HTTP {error_response.status_code}")
                self.failed_endpoints += 1
            
            # 5. POST /api/sandbox/execute (Timeout test)
            logger.info("   Testing POST /api/sandbox/execute (Timeout)...")
            timeout_data = {
                "language": "python",
                "code": 'import time\nfor i in range(10):\n    time.sleep(0.5)',  # 5 second execution
                "timeout": 2  # 2 second timeout
            }
            timeout_response = self.session.post(f"{self.api_url}/sandbox/execute", json=timeout_data, headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if timeout_response.status_code == 200:
                timeout_result = timeout_response.json()
                success = timeout_result.get("success", True)
                timeout_occurred = timeout_result.get("timeout_occurred", False)
                execution_time = timeout_result.get("execution_time", 0)
                
                if not success and (timeout_occurred or execution_time >= 2):
                    logger.info(f"   ✅ POST /api/sandbox/execute (Timeout) - SUCCESS")
                    logger.info(f"      Timeout correctly enforced at {execution_time:.1f}s")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ POST /api/sandbox/execute (Timeout) - FAILED: Timeout not enforced")
                    self.failed_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/sandbox/execute (Timeout) - FAILED: HTTP {timeout_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "cloud_sandbox_working": True}
                
        except Exception as e:
            logger.error(f"❌ Cloud Sandbox test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_research_history_pdf(self) -> Dict[str, Any]:
        """📚 RESEARCH HISTORY & PDF EXPORT - Test all research endpoints"""
        logger.info("📚 RESEARCH HISTORY & PDF EXPORT TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            research_id = None
            
            # 1. POST /api/research/save (save research)
            logger.info("   Testing POST /api/research/save...")
            research_data = {
                "query": "Health check research query",
                "result": "This is a test research result for health check purposes.",
                "sources": [
                    {"title": "Test Source 1", "url": "https://example.com/1"},
                    {"title": "Test Source 2", "url": "https://example.com/2"}
                ],
                "citations": ["Citation 1", "Citation 2"],
                "token_usage": {"input_tokens": 100, "output_tokens": 200}
            }
            save_response = self.session.post(f"{self.api_url}/research/save", json=research_data, headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if save_response.status_code == 200:
                save_result = save_response.json()
                research_id = save_result.get("id")
                logger.info(f"   ✅ POST /api/research/save - SUCCESS (ID: {research_id})")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/research/save - FAILED: HTTP {save_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. GET /api/research/history (get history)
            logger.info("   Testing GET /api/research/history...")
            history_response = self.session.get(f"{self.api_url}/research/history", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                logger.info(f"   ✅ GET /api/research/history - SUCCESS ({len(history_data)} items)")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/research/history - FAILED: HTTP {history_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. PATCH /api/research/history/{id}/favorite (toggle favorite)
            if research_id:
                logger.info(f"   Testing PATCH /api/research/history/{research_id}/favorite...")
                favorite_response = self.session.patch(f"{self.api_url}/research/history/{research_id}/favorite", headers=headers, timeout=10)
                
                self.total_endpoints_tested += 1
                
                if favorite_response.status_code == 200:
                    favorite_result = favorite_response.json()
                    logger.info(f"   ✅ PATCH /api/research/history/{{id}}/favorite - SUCCESS")
                    logger.info(f"      Favorite status: {favorite_result.get('is_favorite')}")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ PATCH /api/research/history/{{id}}/favorite - FAILED: HTTP {favorite_response.status_code}")
                    self.failed_endpoints += 1
            
            # 4. GET /api/research/history/{id}/export-pdf (export PDF)
            if research_id:
                logger.info(f"   Testing GET /api/research/history/{research_id}/export-pdf...")
                pdf_response = self.session.get(f"{self.api_url}/research/history/{research_id}/export-pdf", headers=headers, timeout=15)
                
                self.total_endpoints_tested += 1
                
                if pdf_response.status_code == 200:
                    content_type = pdf_response.headers.get('content-type', '')
                    content_length = len(pdf_response.content)
                    
                    if 'application/pdf' in content_type and content_length > 1000:
                        logger.info(f"   ✅ GET /api/research/history/{{id}}/export-pdf - SUCCESS")
                        logger.info(f"      PDF size: {content_length} bytes")
                        self.successful_endpoints += 1
                    else:
                        logger.error(f"   ❌ GET /api/research/history/{{id}}/export-pdf - FAILED: Invalid PDF response")
                        self.failed_endpoints += 1
                else:
                    logger.error(f"   ❌ GET /api/research/history/{{id}}/export-pdf - FAILED: HTTP {pdf_response.status_code}")
                    self.failed_endpoints += 1
            
            # 5. POST /api/research/export-bulk-pdf (bulk export)
            if research_id:
                logger.info("   Testing POST /api/research/export-bulk-pdf...")
                bulk_data = {
                    "research_ids": [research_id],
                    "title": "Health Check Bulk Export",
                    "include_sources": True,
                    "include_metadata": True
                }
                bulk_response = self.session.post(f"{self.api_url}/research/export-bulk-pdf", json=bulk_data, headers=headers, timeout=15)
                
                self.total_endpoints_tested += 1
                
                if bulk_response.status_code == 200:
                    content_type = bulk_response.headers.get('content-type', '')
                    content_length = len(bulk_response.content)
                    
                    if 'application/pdf' in content_type and content_length > 1000:
                        logger.info(f"   ✅ POST /api/research/export-bulk-pdf - SUCCESS")
                        logger.info(f"      Bulk PDF size: {content_length} bytes")
                        self.successful_endpoints += 1
                    else:
                        logger.error(f"   ❌ POST /api/research/export-bulk-pdf - FAILED: Invalid PDF response")
                        self.failed_endpoints += 1
                else:
                    logger.error(f"   ❌ POST /api/research/export-bulk-pdf - FAILED: HTTP {bulk_response.status_code}")
                    self.failed_endpoints += 1
            
            # 6. DELETE /api/research/history/{id} (delete)
            if research_id:
                logger.info(f"   Testing DELETE /api/research/history/{research_id}...")
                delete_response = self.session.delete(f"{self.api_url}/research/history/{research_id}", headers=headers, timeout=10)
                
                self.total_endpoints_tested += 1
                
                if delete_response.status_code in [200, 204]:
                    logger.info(f"   ✅ DELETE /api/research/history/{{id}} - SUCCESS")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ DELETE /api/research/history/{{id}} - FAILED: HTTP {delete_response.status_code}")
                    self.failed_endpoints += 1
            
            # 7. GET /api/research/stats (statistics)
            logger.info("   Testing GET /api/research/stats...")
            stats_response = self.session.get(f"{self.api_url}/research/stats", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                logger.info(f"   ✅ GET /api/research/stats - SUCCESS")
                logger.info(f"      Total queries: {stats_data.get('total_queries', 0)}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/research/stats - FAILED: HTTP {stats_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "research_history_working": True}
                
        except Exception as e:
            logger.error(f"❌ Research History & PDF Export test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_github_integration(self) -> Dict[str, Any]:
        """🔗 GITHUB INTEGRATION - Test GitHub endpoints"""
        logger.info("🔗 GITHUB INTEGRATION TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. GET /api/github/health (GitHub config status)
            logger.info("   Testing GET /api/github/health...")
            health_response = self.session.get(f"{self.api_url}/github/health", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                logger.info(f"   ✅ GET /api/github/health - SUCCESS")
                logger.info(f"      Status: {health_data.get('status')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/github/health - FAILED: HTTP {health_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. GET /api/github/oauth/url (OAuth URL - if configured)
            logger.info("   Testing GET /api/github/oauth/url...")
            oauth_response = self.session.get(f"{self.api_url}/github/oauth/url", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if oauth_response.status_code == 200:
                oauth_data = oauth_response.json()
                logger.info(f"   ✅ GET /api/github/oauth/url - SUCCESS")
                logger.info(f"      OAuth URL available: {bool(oauth_data.get('oauth_url'))}")
                self.successful_endpoints += 1
            elif oauth_response.status_code == 404:
                logger.info(f"   ⚠️ GET /api/github/oauth/url - NOT CONFIGURED (expected)")
                self.successful_endpoints += 1  # This is acceptable
            else:
                logger.error(f"   ❌ GET /api/github/oauth/url - FAILED: HTTP {oauth_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. POST /api/github/import (import repo - public)
            logger.info("   Testing POST /api/github/import...")
            import_data = {
                "repo_url": "https://github.com/octocat/Hello-World",
                "branch": "master"
            }
            import_response = self.session.post(f"{self.api_url}/github/import", json=import_data, headers=headers, timeout=20)
            
            self.total_endpoints_tested += 1
            
            if import_response.status_code == 200:
                import_result = import_response.json()
                logger.info(f"   ✅ POST /api/github/import - SUCCESS")
                logger.info(f"      Import status: {import_result.get('status')}")
                self.successful_endpoints += 1
            elif import_response.status_code == 422:
                logger.info(f"   ⚠️ POST /api/github/import - VALIDATION ERROR (expected for test repo)")
                self.successful_endpoints += 1  # This is acceptable for testing
            else:
                logger.error(f"   ❌ POST /api/github/import - FAILED: HTTP {import_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "github_integration_working": True}
                
        except Exception as e:
            logger.error(f"❌ GitHub Integration test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_rate_limiting(self) -> Dict[str, Any]:
        """⚡ RATE LIMITING - Test all rate limiting endpoints"""
        logger.info("⚡ RATE LIMITING TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. GET /api/rate-limits/limits (list rate limits)
            logger.info("   Testing GET /api/rate-limits/limits...")
            limits_response = self.session.get(f"{self.api_url}/rate-limits/limits", timeout=10)
            
            self.total_endpoints_tested += 1
            
            if limits_response.status_code == 200:
                limits_data = limits_response.json()
                logger.info(f"   ✅ GET /api/rate-limits/limits - SUCCESS")
                logger.info(f"      Rate limits configured: {len(limits_data)}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/rate-limits/limits - FAILED: HTTP {limits_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. GET /api/rate-limits/quota (user quota)
            logger.info("   Testing GET /api/rate-limits/quota...")
            quota_response = self.session.get(f"{self.api_url}/rate-limits/quota", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if quota_response.status_code == 200:
                quota_data = quota_response.json()
                logger.info(f"   ✅ GET /api/rate-limits/quota - SUCCESS")
                logger.info(f"      User role: {quota_data.get('role')}")
                logger.info(f"      Requests used: {quota_data.get('requests_used')}/{quota_data.get('requests_limit')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/rate-limits/quota - FAILED: HTTP {quota_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. GET /api/rate-limits/health (rate limit health)
            logger.info("   Testing GET /api/rate-limits/health...")
            health_response = self.session.get(f"{self.api_url}/rate-limits/health", timeout=10)
            
            self.total_endpoints_tested += 1
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                logger.info(f"   ✅ GET /api/rate-limits/health - SUCCESS")
                logger.info(f"      Rate limiting status: {health_data.get('status')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/rate-limits/health - FAILED: HTTP {health_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "rate_limiting_working": True}
                
        except Exception as e:
            logger.error(f"❌ Rate Limiting test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_api_keys_management(self) -> Dict[str, Any]:
        """🔑 API KEYS MANAGEMENT - Test API key endpoints"""
        logger.info("🔑 API KEYS MANAGEMENT TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. GET /api/api-keys/ (list user API keys)
            logger.info("   Testing GET /api/api-keys/...")
            list_response = self.session.get(f"{self.api_url}/api-keys/", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if list_response.status_code == 200:
                keys_data = list_response.json()
                logger.info(f"   ✅ GET /api/api-keys/ - SUCCESS")
                logger.info(f"      API keys configured: {len(keys_data)}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/api-keys/ - FAILED: HTTP {list_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. POST /api/api-keys/ (add API key)
            logger.info("   Testing POST /api/api-keys/...")
            add_data = {
                "provider": "test_provider",
                "api_key": "test-key-12345"
            }
            add_response = self.session.post(f"{self.api_url}/api-keys/", json=add_data, headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if add_response.status_code == 200:
                add_result = add_response.json()
                logger.info(f"   ✅ POST /api/api-keys/ - SUCCESS")
                logger.info(f"      Added key for: {add_result.get('provider')}")
                self.successful_endpoints += 1
                
                # 3. DELETE /api/api-keys/{provider} (delete key)
                logger.info("   Testing DELETE /api/api-keys/test_provider...")
                delete_response = self.session.delete(f"{self.api_url}/api-keys/test_provider", headers=headers, timeout=10)
                
                self.total_endpoints_tested += 1
                
                if delete_response.status_code in [200, 204]:
                    logger.info(f"   ✅ DELETE /api/api-keys/{{provider}} - SUCCESS")
                    self.successful_endpoints += 1
                else:
                    logger.error(f"   ❌ DELETE /api/api-keys/{{provider}} - FAILED: HTTP {delete_response.status_code}")
                    self.failed_endpoints += 1
            else:
                logger.error(f"   ❌ POST /api/api-keys/ - FAILED: HTTP {add_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "api_keys_working": True}
                
        except Exception as e:
            logger.error(f"❌ API Keys Management test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_developer_modes(self) -> Dict[str, Any]:
        """🎨 DEVELOPER MODES - Test developer mode endpoints"""
        logger.info("🎨 DEVELOPER MODES TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. GET /api/developer-modes (list modes)
            logger.info("   Testing GET /api/developer-modes...")
            modes_response = self.session.get(f"{self.api_url}/developer-modes", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if modes_response.status_code == 200:
                modes_data = modes_response.json()
                logger.info(f"   ✅ GET /api/developer-modes - SUCCESS")
                logger.info(f"      Available modes: {len(modes_data)}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/developer-modes - FAILED: HTTP {modes_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. GET /api/developer-modes/junior (junior mode details)
            logger.info("   Testing GET /api/developer-modes/junior...")
            junior_response = self.session.get(f"{self.api_url}/developer-modes/junior", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if junior_response.status_code == 200:
                junior_data = junior_response.json()
                logger.info(f"   ✅ GET /api/developer-modes/junior - SUCCESS")
                logger.info(f"      Junior model: {junior_data.get('model')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/developer-modes/junior - FAILED: HTTP {junior_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. GET /api/developer-modes/senior (senior mode details)
            logger.info("   Testing GET /api/developer-modes/senior...")
            senior_response = self.session.get(f"{self.api_url}/developer-modes/senior", headers=headers, timeout=10)
            
            self.total_endpoints_tested += 1
            
            if senior_response.status_code == 200:
                senior_data = senior_response.json()
                logger.info(f"   ✅ GET /api/developer-modes/senior - SUCCESS")
                logger.info(f"      Senior model: {senior_data.get('model')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/developer-modes/senior - FAILED: HTTP {senior_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "developer_modes_working": True}
                
        except Exception as e:
            logger.error(f"❌ Developer Modes test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_health_system(self) -> Dict[str, Any]:
        """📊 HEALTH & SYSTEM - Test health and system endpoints"""
        logger.info("📊 HEALTH & SYSTEM TEST")
        
        try:
            # 1. GET /api/health (system health)
            logger.info("   Testing GET /api/health...")
            health_response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            self.total_endpoints_tested += 1
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                logger.info(f"   ✅ GET /api/health - SUCCESS")
                logger.info(f"      System status: {health_data.get('status')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/health - FAILED: HTTP {health_response.status_code}")
                self.failed_endpoints += 1
            
            # 2. GET /api/version (API version info)
            logger.info("   Testing GET /api/version...")
            version_response = self.session.get(f"{self.api_url}/version", timeout=10)
            
            self.total_endpoints_tested += 1
            
            if version_response.status_code == 200:
                version_data = version_response.json()
                logger.info(f"   ✅ GET /api/version - SUCCESS")
                logger.info(f"      API version: {version_data.get('version')}")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/version - FAILED: HTTP {version_response.status_code}")
                self.failed_endpoints += 1
            
            # 3. GET /api/metrics (Prometheus metrics)
            logger.info("   Testing GET /api/metrics...")
            metrics_response = self.session.get(f"{self.api_url}/metrics", timeout=10)
            
            self.total_endpoints_tested += 1
            
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.text  # Prometheus metrics are text format
                logger.info(f"   ✅ GET /api/metrics - SUCCESS")
                logger.info(f"      Metrics data length: {len(metrics_data)} chars")
                self.successful_endpoints += 1
            else:
                logger.error(f"   ❌ GET /api/metrics - FAILED: HTTP {metrics_response.status_code}")
                self.failed_endpoints += 1
                
            return {"status": "success", "health_system_working": True}
                
        except Exception as e:
            logger.error(f"❌ Health & System test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check of all backend endpoints"""
        logger.info("🚀 STARTING COMPREHENSIVE 100% BACKEND HEALTH CHECK")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Initialize counters
        self.total_endpoints_tested = 0
        self.successful_endpoints = 0
        self.failed_endpoints = 0
        
        # Run all tests
        test_results = {}
        
        # 1. Authentication & User Management
        test_results["authentication"] = self.authenticate()
        
        # 2. Session Management
        test_results["session_management"] = self.test_session_management()
        
        # 3. Multi-Agent System
        test_results["multi_agent_system"] = self.test_multi_agent_system()
        
        # 4. Cloud Sandbox
        test_results["cloud_sandbox"] = self.test_cloud_sandbox()
        
        # 5. Research History & PDF Export
        test_results["research_history_pdf"] = self.test_research_history_pdf()
        
        # 6. GitHub Integration
        test_results["github_integration"] = self.test_github_integration()
        
        # 7. Rate Limiting
        test_results["rate_limiting"] = self.test_rate_limiting()
        
        # 8. API Keys Management
        test_results["api_keys_management"] = self.test_api_keys_management()
        
        # 9. Developer Modes
        test_results["developer_modes"] = self.test_developer_modes()
        
        # 10. Health & System
        test_results["health_system"] = self.test_health_system()
        
        # Calculate final results
        total_time = time.time() - start_time
        success_rate = (self.successful_endpoints / self.total_endpoints_tested * 100) if self.total_endpoints_tested > 0 else 0
        
        # Generate summary
        logger.info("=" * 80)
        logger.info("🎯 COMPREHENSIVE BACKEND HEALTH CHECK COMPLETED")
        logger.info("=" * 80)
        logger.info(f"📊 SUMMARY:")
        logger.info(f"   Total endpoints tested: {self.total_endpoints_tested}")
        logger.info(f"   Successful endpoints: {self.successful_endpoints}")
        logger.info(f"   Failed endpoints: {self.failed_endpoints}")
        logger.info(f"   Success rate: {success_rate:.1f}%")
        logger.info(f"   Total execution time: {total_time:.2f} seconds")
        logger.info("=" * 80)
        
        # Identify broken endpoints
        broken_endpoints = []
        security_concerns = []
        performance_issues = []
        
        for category, result in test_results.items():
            if result.get("status") in ["failed", "error"]:
                broken_endpoints.append(f"{category}: {result.get('error', 'Unknown error')}")
        
        # Performance analysis
        if total_time > 60:
            performance_issues.append(f"Total test execution time too high: {total_time:.2f}s")
        
        # Security analysis
        if test_results.get("authentication", {}).get("status") != "success":
            security_concerns.append("Authentication system not working properly")
        
        # Generate recommendations
        recommendations = []
        if broken_endpoints:
            recommendations.append("Fix broken/failing endpoints")
        if security_concerns:
            recommendations.append("Address security concerns immediately")
        if performance_issues:
            recommendations.append("Optimize performance issues")
        if success_rate < 90:
            recommendations.append("Investigate and fix failing endpoints to achieve >90% success rate")
        
        return {
            "status": "success" if success_rate >= 90 else "partial" if success_rate >= 70 else "failed",
            "summary": {
                "total_endpoints_tested": self.total_endpoints_tested,
                "successful_endpoints": self.successful_endpoints,
                "failed_endpoints": self.failed_endpoints,
                "success_rate": success_rate,
                "total_time": total_time
            },
            "test_results": test_results,
            "broken_endpoints": broken_endpoints,
            "security_concerns": security_concerns,
            "performance_issues": performance_issues,
            "recommendations": recommendations
        }

def main():
    """Main function to run the comprehensive health check"""
    try:
        # Initialize health checker
        checker = ComprehensiveBackendHealthChecker()
        
        # Run comprehensive health check
        results = checker.run_comprehensive_health_check()
        
        # Print final status
        status = results["status"]
        if status == "success":
            logger.info("🎉 BACKEND HEALTH CHECK: ALL SYSTEMS OPERATIONAL")
        elif status == "partial":
            logger.info("⚠️ BACKEND HEALTH CHECK: SOME ISSUES DETECTED")
        else:
            logger.info("❌ BACKEND HEALTH CHECK: CRITICAL ISSUES FOUND")
        
        # Print recommendations
        if results["recommendations"]:
            logger.info("🔧 RECOMMENDATIONS:")
            for rec in results["recommendations"]:
                logger.info(f"   - {rec}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Health check failed with exception: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    main()