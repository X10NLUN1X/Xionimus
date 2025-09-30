#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Xionimus AI - Phase 2 Deep Debugging
Testing all core API endpoints, WebSocket streaming, database operations, and security
"""

import asyncio
import aiohttp
import websockets
import json
import time
import uuid
import sqlite3
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XionimusBackendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.ws_url = base_url.replace("http", "ws")
        self.session = None
        self.test_results = []
        self.test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        
        # Test data
        self.test_user_data = {
            "username": "xionimus_tester",
            "email": "test@xionimus.ai",
            "password": "XionimusTest2024!"
        }
        
        self.test_api_keys = {
            "openai": "sk-test-key-not-real",
            "anthropic": "sk-ant-test-key-not-real", 
            "perplexity": "pplx-test-key-not-real"
        }
        
        self.test_messages = [
            {"role": "user", "content": "Hello, can you help me with a Python function?"},
            {"role": "user", "content": "What is the weather like today?"},
            {"role": "user", "content": "Explain quantum computing in simple terms"},
            {"role": "user", "content": "Write a simple React component"},
            {"role": "user", "content": "How do I optimize database queries?"}
        ]

    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )

    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def log_test_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        logger.info(f"{status} {test_name} ({response_time:.3f}s) - {details}")

    async def test_health_endpoint(self):
        """Test health check endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.api_url}/health") as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                success = (
                    response.status == 200 and
                    data.get("status") == "healthy" and
                    "platform" in data and
                    "services" in data
                )
                
                details = f"Status: {response.status}, Platform: {data.get('platform', 'N/A')}"
                if "services" in data:
                    details += f", Database: {data['services'].get('database', 'N/A')}"
                
                self.log_test_result("Health Check", success, details, response_time)
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Health Check", False, f"Error: {str(e)}", response_time)
            return False

    async def test_chat_providers(self):
        """Test chat providers endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.api_url}/chat/providers") as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                success = (
                    response.status == 200 and
                    "providers" in data and
                    "models" in data
                )
                
                provider_count = len(data.get("providers", {}))
                model_count = len(data.get("models", {}))
                details = f"Status: {response.status}, Providers: {provider_count}, Models: {model_count}"
                
                self.log_test_result("Chat Providers", success, details, response_time)
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Chat Providers", False, f"Error: {str(e)}", response_time)
            return False

    async def test_chat_sessions_crud(self):
        """Test SQLite-based chat sessions CRUD operations"""
        # Test CREATE session
        start_time = time.time()
        try:
            session_data = {
                "name": f"Test Session {datetime.now().strftime('%H:%M:%S')}",
                "workspace_id": None
            }
            
            async with self.session.post(f"{self.api_url}/sessions", json=session_data) as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                create_success = (
                    response.status == 200 and
                    "id" in data and
                    "name" in data
                )
                
                if create_success:
                    session_id = data["id"]
                    self.log_test_result("Session CREATE", True, f"Created session: {session_id}", response_time)
                else:
                    self.log_test_result("Session CREATE", False, f"Status: {response.status}", response_time)
                    return False
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Session CREATE", False, f"Error: {str(e)}", response_time)
            return False

        # Test GET sessions
        start_time = time.time()
        try:
            async with self.session.get(f"{self.api_url}/sessions") as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                get_success = (
                    response.status == 200 and
                    isinstance(data, list)
                )
                
                session_count = len(data) if isinstance(data, list) else 0
                details = f"Status: {response.status}, Sessions found: {session_count}"
                self.log_test_result("Session GET", get_success, details, response_time)
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Session GET", False, f"Error: {str(e)}", response_time)
            return False

        # Test DELETE session
        start_time = time.time()
        try:
            async with self.session.delete(f"{self.api_url}/sessions/{session_id}") as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                delete_success = (
                    response.status == 200 and
                    data.get("status") == "deleted"
                )
                
                details = f"Status: {response.status}, Deleted: {data.get('session_id', 'N/A')}"
                self.log_test_result("Session DELETE", delete_success, details, response_time)
                
                return create_success and get_success and delete_success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Session DELETE", False, f"Error: {str(e)}", response_time)
            return False

    async def test_chat_completion(self):
        """Test chat completion endpoint (expect API key errors)"""
        start_time = time.time()
        try:
            chat_data = {
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "provider": "openai",
                "model": "gpt-5",
                "session_id": self.test_session_id,
                "stream": False,
                "api_keys": self.test_api_keys
            }
            
            async with self.session.post(f"{self.api_url}/chat", json=chat_data) as response:
                response_time = time.time() - start_time
                
                # We expect this to fail with API key error (400 or 500)
                success = response.status in [400, 500]
                
                if response.status == 200:
                    data = await response.json()
                    details = f"Unexpected success - got response: {data.get('content', '')[:50]}..."
                    success = False
                else:
                    try:
                        error_data = await response.json()
                        details = f"Expected error: {response.status} - {error_data.get('detail', 'No detail')}"
                    except:
                        details = f"Expected error: {response.status}"
                
                self.log_test_result("Chat Completion", success, details, response_time)
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Chat Completion", False, f"Error: {str(e)}", response_time)
            return False

    async def test_chat_history(self):
        """Test chat history retrieval"""
        start_time = time.time()
        try:
            # First create a session to get history for
            session_data = {"name": "History Test Session"}
            async with self.session.post(f"{self.api_url}/sessions", json=session_data) as response:
                if response.status != 200:
                    self.log_test_result("Chat History", False, "Failed to create test session", time.time() - start_time)
                    return False
                
                session_data = await response.json()
                session_id = session_data["id"]
            
            # Now test getting history
            async with self.session.get(f"{self.api_url}/sessions/{session_id}/messages") as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                success = (
                    response.status == 200 and
                    isinstance(data, list)
                )
                
                message_count = len(data) if isinstance(data, list) else 0
                details = f"Status: {response.status}, Messages: {message_count}"
                self.log_test_result("Chat History", success, details, response_time)
                
                # Cleanup
                await self.session.delete(f"{self.api_url}/sessions/{session_id}")
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Chat History", False, f"Error: {str(e)}", response_time)
            return False

    async def test_websocket_connection(self):
        """Test WebSocket streaming endpoint"""
        start_time = time.time()
        try:
            ws_url = f"{self.ws_url}/ws/chat/{self.test_session_id}"
            
            async with websockets.connect(ws_url, timeout=10) as websocket:
                response_time = time.time() - start_time
                
                # Send ping message
                ping_message = {"type": "ping"}
                await websocket.send(json.dumps(ping_message))
                
                # Wait for pong
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                success = response_data.get("type") == "pong"
                details = f"Connection established, ping/pong: {success}"
                
                self.log_test_result("WebSocket Connection", success, details, response_time)
                return success
                
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self.log_test_result("WebSocket Connection", False, "Connection timeout", response_time)
            return False
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("WebSocket Connection", False, f"Error: {str(e)}", response_time)
            return False

    async def test_websocket_streaming(self):
        """Test WebSocket message streaming"""
        start_time = time.time()
        try:
            ws_url = f"{self.ws_url}/ws/chat/{self.test_session_id}"
            
            async with websockets.connect(ws_url, timeout=10) as websocket:
                # Send chat message
                chat_message = {
                    "type": "chat",
                    "content": "Hello, this is a test message",
                    "provider": "openai",
                    "model": "gpt-5",
                    "api_keys": self.test_api_keys,
                    "messages": []
                }
                
                await websocket.send(json.dumps(chat_message))
                
                # Wait for start acknowledgment
                start_response = await asyncio.wait_for(websocket.recv(), timeout=5)
                start_data = json.loads(start_response)
                
                # Wait for error (expected due to invalid API keys)
                error_response = await asyncio.wait_for(websocket.recv(), timeout=10)
                error_data = json.loads(error_response)
                
                response_time = time.time() - start_time
                
                success = (
                    start_data.get("type") == "start" and
                    error_data.get("type") == "error"
                )
                
                details = f"Start: {start_data.get('type')}, Error: {error_data.get('type')} (expected)"
                self.log_test_result("WebSocket Streaming", success, details, response_time)
                return success
                
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self.log_test_result("WebSocket Streaming", False, "Streaming timeout", response_time)
            return False
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("WebSocket Streaming", False, f"Error: {str(e)}", response_time)
            return False

    async def test_database_integration(self):
        """Test SQLite database operations"""
        start_time = time.time()
        try:
            # Check if SQLite database exists and is accessible
            db_path = os.path.expanduser("~/.xionimus_ai/xionimus.db")
            if not os.path.exists(db_path):
                # Try alternative paths
                alt_paths = [
                    "/app/xionimus-ai/backend/xionimus_ai.db",
                    "/app/backend/xionimus_ai.db",
                    "/app/xionimus.db"
                ]
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        db_path = alt_path
                        break
                else:
                    self.log_test_result("Database Integration", False, f"SQLite database file not found in expected locations", time.time() - start_time)
                    return False
            
            # Test database connection and basic operations
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            expected_tables = ['sessions', 'messages']
            has_required_tables = all(table in table_names for table in expected_tables)
            
            # Test basic query performance
            query_start = time.time()
            cursor.execute("SELECT COUNT(*) FROM sessions;")
            session_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM messages;")
            message_count = cursor.fetchone()[0]
            query_time = time.time() - query_start
            
            conn.close()
            
            response_time = time.time() - start_time
            success = has_required_tables and query_time < 0.1  # Should be fast
            
            details = f"Tables: {len(table_names)}, Sessions: {session_count}, Messages: {message_count}, Query time: {query_time:.3f}s"
            self.log_test_result("Database Integration", success, details, response_time)
            return success
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Database Integration", False, f"Error: {str(e)}", response_time)
            return False

    async def test_error_handling(self):
        """Test error handling and edge cases"""
        tests_passed = 0
        total_tests = 0
        
        # Test invalid session ID
        total_tests += 1
        start_time = time.time()
        try:
            async with self.session.get(f"{self.api_url}/sessions/invalid-session-id") as response:
                response_time = time.time() - start_time
                success = response.status == 404
                details = f"Invalid session ID returned status: {response.status}"
                self.log_test_result("Error Handling - Invalid Session", success, details, response_time)
                if success:
                    tests_passed += 1
        except Exception as e:
            self.log_test_result("Error Handling - Invalid Session", False, f"Error: {str(e)}", time.time() - start_time)
        
        # Test malformed request
        total_tests += 1
        start_time = time.time()
        try:
            malformed_data = {"invalid": "data", "missing": "required_fields"}
            async with self.session.post(f"{self.api_url}/chat", json=malformed_data) as response:
                response_time = time.time() - start_time
                success = response.status in [400, 422]  # Bad request or validation error
                details = f"Malformed request returned status: {response.status}"
                self.log_test_result("Error Handling - Malformed Request", success, details, response_time)
                if success:
                    tests_passed += 1
        except Exception as e:
            self.log_test_result("Error Handling - Malformed Request", False, f"Error: {str(e)}", time.time() - start_time)
        
        # Test large payload
        total_tests += 1
        start_time = time.time()
        try:
            large_content = "A" * 200000  # 200KB message
            large_data = {
                "messages": [{"role": "user", "content": large_content}],
                "provider": "openai",
                "model": "gpt-5"
            }
            async with self.session.post(f"{self.api_url}/chat", json=large_data) as response:
                response_time = time.time() - start_time
                success = response.status in [400, 413, 422, 500]  # Should handle large payloads gracefully
                details = f"Large payload ({len(large_content)} chars) returned status: {response.status}"
                self.log_test_result("Error Handling - Large Payload", success, details, response_time)
                if success:
                    tests_passed += 1
        except Exception as e:
            self.log_test_result("Error Handling - Large Payload", False, f"Error: {str(e)}", time.time() - start_time)
        
        return tests_passed == total_tests

    async def test_security_validation(self):
        """Test security measures"""
        tests_passed = 0
        total_tests = 0
        
        # Test API key sanitization (no keys should appear in error messages)
        total_tests += 1
        start_time = time.time()
        try:
            test_keys = {
                "openai": "sk-real-looking-key-12345678901234567890",
                "anthropic": "sk-ant-real-looking-key-12345678901234567890"
            }
            
            chat_data = {
                "messages": [{"role": "user", "content": "Test message"}],
                "provider": "openai",
                "model": "gpt-5",
                "api_keys": test_keys
            }
            
            async with self.session.post(f"{self.api_url}/chat", json=chat_data) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                # Check that API keys don't appear in response
                key_exposed = any(key in response_text for key in test_keys.values())
                success = not key_exposed
                
                details = f"API key exposure check: {'EXPOSED' if key_exposed else 'SAFE'}"
                self.log_test_result("Security - API Key Sanitization", success, details, response_time)
                if success:
                    tests_passed += 1
                    
        except Exception as e:
            self.log_test_result("Security - API Key Sanitization", False, f"Error: {str(e)}", time.time() - start_time)
        
        # Test input validation
        total_tests += 1
        start_time = time.time()
        try:
            xss_payload = "<script>alert('xss')</script>"
            injection_data = {
                "messages": [{"role": "user", "content": xss_payload}],
                "provider": "openai'; DROP TABLE sessions; --",
                "model": "gpt-5"
            }
            
            async with self.session.post(f"{self.api_url}/chat", json=injection_data) as response:
                response_time = time.time() - start_time
                success = response.status in [400, 422]  # Should reject malicious input
                details = f"Injection attempt returned status: {response.status}"
                self.log_test_result("Security - Input Validation", success, details, response_time)
                if success:
                    tests_passed += 1
                    
        except Exception as e:
            self.log_test_result("Security - Input Validation", False, f"Error: {str(e)}", time.time() - start_time)
        
        return tests_passed == total_tests

    async def test_performance(self):
        """Test performance under load"""
        start_time = time.time()
        
        # Test concurrent requests
        concurrent_requests = 10
        tasks = []
        
        for i in range(concurrent_requests):
            task = self.session.get(f"{self.api_url}/health")
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            response_time = time.time() - start_time
            
            successful_responses = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            success = successful_responses >= concurrent_requests * 0.8  # 80% success rate
            
            details = f"{successful_responses}/{concurrent_requests} requests successful in {response_time:.3f}s"
            self.log_test_result("Performance - Concurrent Requests", success, details, response_time)
            
            # Close all responses
            for response in responses:
                if hasattr(response, 'close'):
                    response.close()
            
            return success
            
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Performance - Concurrent Requests", False, f"Error: {str(e)}", response_time)
            return False

    async def test_model_configuration(self):
        """Test model configuration and parameter handling"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.api_url}/chat/providers") as response:
                response_time = time.time() - start_time
                data = await response.json()
                
                if response.status != 200:
                    self.log_test_result("Model Configuration", False, f"Status: {response.status}", response_time)
                    return False
                
                models = data.get("models", {})
                expected_models = ["gpt-4o", "gpt-4.1", "o1", "o3", "claude-sonnet-4-5-20250929", "sonar-pro"]
                
                found_models = []
                for provider_models in models.values():
                    if isinstance(provider_models, list):
                        found_models.extend(provider_models)
                
                model_coverage = sum(1 for model in expected_models if any(model in found for found in found_models))
                success = model_coverage >= len(expected_models) * 0.7  # 70% of expected models
                
                details = f"Found {len(found_models)} models, {model_coverage}/{len(expected_models)} expected models"
                self.log_test_result("Model Configuration", success, details, response_time)
                return success
                
        except Exception as e:
            response_time = time.time() - start_time
            self.log_test_result("Model Configuration", False, f"Error: {str(e)}", response_time)
            return False

    async def run_all_tests(self):
        """Run all backend tests"""
        logger.info("🚀 Starting Xionimus AI Backend Comprehensive Testing")
        logger.info(f"Backend URL: {self.base_url}")
        logger.info(f"WebSocket URL: {self.ws_url}")
        
        await self.setup_session()
        
        try:
            # Core API Endpoints Testing
            logger.info("\n📋 CORE API ENDPOINTS TESTING")
            await self.test_health_endpoint()
            await self.test_chat_providers()
            await self.test_chat_sessions_crud()
            await self.test_chat_completion()
            await self.test_chat_history()
            
            # WebSocket Streaming Testing
            logger.info("\n🔌 WEBSOCKET STREAMING TESTING")
            await self.test_websocket_connection()
            await self.test_websocket_streaming()
            
            # Database Integration Testing
            logger.info("\n🗄️ DATABASE INTEGRATION TESTING")
            await self.test_database_integration()
            
            # Error Handling & Edge Cases
            logger.info("\n⚠️ ERROR HANDLING & EDGE CASES")
            await self.test_error_handling()
            
            # Security Validation
            logger.info("\n🔒 SECURITY VALIDATION")
            await self.test_security_validation()
            
            # Performance Testing
            logger.info("\n⚡ PERFORMANCE TESTING")
            await self.test_performance()
            
            # Model Configuration Validation
            logger.info("\n🤖 MODEL CONFIGURATION VALIDATION")
            await self.test_model_configuration()
            
        finally:
            await self.cleanup_session()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("\n" + "="*80)
        logger.info("🎯 XIONIMUS AI BACKEND TESTING SUMMARY")
        logger.info("="*80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  • {result['test']}: {result['details']}")
        
        logger.info("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                logger.info(f"  • {result['test']}: {result['details']}")
        
        # Performance metrics
        avg_response_time = sum(r["response_time"] for r in self.test_results) / len(self.test_results)
        logger.info(f"\n⚡ PERFORMANCE METRICS:")
        logger.info(f"Average Response Time: {avg_response_time:.3f}s")
        
        slowest_test = max(self.test_results, key=lambda x: x["response_time"])
        logger.info(f"Slowest Test: {slowest_test['test']} ({slowest_test['response_time']:.3f}s)")
        
        # Critical issues
        critical_failures = [
            r for r in self.test_results 
            if not r["success"] and any(keyword in r["test"].lower() 
                                      for keyword in ["health", "database", "security"])
        ]
        
        if critical_failures:
            logger.info(f"\n🚨 CRITICAL ISSUES FOUND: {len(critical_failures)}")
            for failure in critical_failures:
                logger.info(f"  • {failure['test']}: {failure['details']}")
        
        logger.info("="*80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "critical_issues": len(critical_failures),
            "test_results": self.test_results
        }

async def main():
    """Main test execution"""
    tester = XionimusBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())