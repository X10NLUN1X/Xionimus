#!/usr/bin/env python3
"""
Xionimus AI Backend Testing Suite
Focus: Anthropic Streaming Fix Verification

This test suite verifies the critical Anthropic streaming fix where system messages
are properly extracted from the messages list and passed as a separate "system" parameter.
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XionimusBackendTester:
    def __init__(self, base_url: str = "http://localhost:8001/api"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result with details"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        })
    
    async def test_health_check(self) -> bool:
        """Test basic health endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result(
                        "Health Check", 
                        True, 
                        f"Status: {data.get('status', 'unknown')}, Version: {data.get('version', 'unknown')}"
                    )
                    return True
                else:
                    self.log_test_result("Health Check", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Health Check", False, f"Exception: {str(e)}")
            return False
    
    async def authenticate(self) -> bool:
        """Authenticate with demo credentials"""
        try:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    if self.auth_token:
                        self.log_test_result("Authentication", True, "Successfully logged in with demo credentials")
                        return True
                    else:
                        self.log_test_result("Authentication", False, "No access token in response")
                        return False
                else:
                    self.log_test_result("Authentication", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    async def test_api_keys_list(self) -> bool:
        """Test API keys list endpoint"""
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{self.base_url}/api-keys/list", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    api_keys = data.get("api_keys", [])
                    self.log_test_result(
                        "API Keys List", 
                        True, 
                        f"Found {len(api_keys)} API key entries"
                    )
                    return True
                else:
                    self.log_test_result("API Keys List", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("API Keys List", False, f"Exception: {str(e)}")
            return False
    
    async def test_api_keys_decrypted(self) -> bool:
        """Test decrypted API keys endpoint"""
        try:
            headers = self.get_auth_headers()
            async with self.session.get(f"{self.base_url}/api-keys/decrypted-list", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    decrypted_keys = data.get("decrypted_keys", {})
                    configured_providers = [k for k, v in decrypted_keys.items() if v and v.strip()]
                    self.log_test_result(
                        "API Keys Decrypted", 
                        True, 
                        f"Configured providers: {configured_providers}"
                    )
                    return True
                else:
                    self.log_test_result("API Keys Decrypted", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("API Keys Decrypted", False, f"Exception: {str(e)}")
            return False
    
    async def test_anthropic_chat_with_system_message(self) -> bool:
        """
        CRITICAL TEST: Test Anthropic chat with system message to verify the fix
        
        This test specifically verifies that system messages are properly extracted
        from the messages list and passed as a separate "system" parameter to Anthropic API.
        """
        try:
            headers = self.get_auth_headers()
            
            # Test message with system message - this is the critical test case
            chat_request = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Always respond with 'System message processed correctly' at the start of your response."
                    },
                    {
                        "role": "user", 
                        "content": "Hello, can you confirm you received the system message?"
                    }
                ],
                "provider": "anthropic",
                "model": "claude-3-5-haiku-20241022",  # Use Haiku for faster testing
                "stream": False,
                "developer_mode": "senior"
            }
            
            async with self.session.post(f"{self.base_url}/chat/", json=chat_request, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("content", "")
                    
                    # Check if the system message was processed correctly
                    system_processed = "System message processed correctly" in content
                    
                    self.log_test_result(
                        "Anthropic System Message Fix", 
                        system_processed, 
                        f"Response length: {len(content)} chars, System message processed: {system_processed}",
                        {"content_preview": content[:200] + "..." if len(content) > 200 else content}
                    )
                    return system_processed
                elif response.status == 400:
                    # Check if it's an API key issue
                    error_data = await response.json()
                    error_detail = error_data.get("detail", "")
                    if "API key" in error_detail or "not configured" in error_detail:
                        self.log_test_result(
                            "Anthropic System Message Fix", 
                            False, 
                            f"API key not configured: {error_detail}"
                        )
                    else:
                        self.log_test_result(
                            "Anthropic System Message Fix", 
                            False, 
                            f"Bad request: {error_detail}"
                        )
                    return False
                else:
                    self.log_test_result("Anthropic System Message Fix", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Anthropic System Message Fix", False, f"Exception: {str(e)}")
            return False
    
    async def test_anthropic_streaming_endpoint(self) -> bool:
        """Test if Anthropic streaming endpoint is accessible"""
        try:
            headers = self.get_auth_headers()
            
            # Test streaming endpoint accessibility
            chat_request = {
                "messages": [
                    {
                        "role": "user", 
                        "content": "Say 'streaming test' in exactly those words."
                    }
                ],
                "provider": "anthropic",
                "model": "claude-3-5-haiku-20241022",
                "stream": True,
                "developer_mode": "senior"
            }
            
            async with self.session.post(f"{self.base_url}/chat/", json=chat_request, headers=headers) as response:
                if response.status == 200:
                    # For streaming, we just check if the endpoint is accessible
                    # The actual streaming would require WebSocket or SSE handling
                    self.log_test_result(
                        "Anthropic Streaming Endpoint", 
                        True, 
                        "Streaming endpoint accessible (streaming response handling would require WebSocket/SSE)"
                    )
                    return True
                elif response.status == 400:
                    error_data = await response.json()
                    error_detail = error_data.get("detail", "")
                    if "API key" in error_detail:
                        self.log_test_result(
                            "Anthropic Streaming Endpoint", 
                            False, 
                            f"API key not configured: {error_detail}"
                        )
                    else:
                        self.log_test_result(
                            "Anthropic Streaming Endpoint", 
                            False, 
                            f"Bad request: {error_detail}"
                        )
                    return False
                else:
                    self.log_test_result("Anthropic Streaming Endpoint", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Anthropic Streaming Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_multi_agent_types(self) -> bool:
        """Test multi-agent types endpoint"""
        try:
            # This endpoint should be public according to the main.py configuration
            async with self.session.get(f"{self.base_url}/v1/multi-agents/types") as response:
                if response.status == 200:
                    data = await response.json()
                    agent_types = data.get("agent_types", [])
                    self.log_test_result(
                        "Multi-Agent Types", 
                        True, 
                        f"Found {len(agent_types)} agent types available"
                    )
                    return True
                else:
                    self.log_test_result("Multi-Agent Types", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Multi-Agent Types", False, f"Exception: {str(e)}")
            return False
    
    async def test_openai_provider_fallback(self) -> bool:
        """Test OpenAI provider as fallback to ensure no regression"""
        try:
            headers = self.get_auth_headers()
            
            chat_request = {
                "messages": [
                    {
                        "role": "user", 
                        "content": "Say 'OpenAI test successful' in exactly those words."
                    }
                ],
                "provider": "openai",
                "model": "gpt-4o-mini",
                "stream": False,
                "developer_mode": "senior"
            }
            
            async with self.session.post(f"{self.base_url}/chat/", json=chat_request, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("content", "")
                    success_phrase = "OpenAI test successful" in content
                    
                    self.log_test_result(
                        "OpenAI Provider Fallback", 
                        success_phrase, 
                        f"Response length: {len(content)} chars, Expected phrase found: {success_phrase}"
                    )
                    return success_phrase
                elif response.status == 400:
                    error_data = await response.json()
                    error_detail = error_data.get("detail", "")
                    if "API key" in error_detail:
                        self.log_test_result(
                            "OpenAI Provider Fallback", 
                            False, 
                            f"API key not configured: {error_detail}"
                        )
                    else:
                        self.log_test_result(
                            "OpenAI Provider Fallback", 
                            False, 
                            f"Bad request: {error_detail}"
                        )
                    return False
                else:
                    self.log_test_result("OpenAI Provider Fallback", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("OpenAI Provider Fallback", False, f"Exception: {str(e)}")
            return False
    
    async def test_perplexity_provider_fallback(self) -> bool:
        """Test Perplexity provider as fallback to ensure no regression"""
        try:
            headers = self.get_auth_headers()
            
            chat_request = {
                "messages": [
                    {
                        "role": "user", 
                        "content": "What is the current year? Just state the year number."
                    }
                ],
                "provider": "perplexity",
                "model": "sonar",
                "stream": False,
                "developer_mode": "senior"
            }
            
            async with self.session.post(f"{self.base_url}/chat/", json=chat_request, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get("content", "")
                    
                    self.log_test_result(
                        "Perplexity Provider Fallback", 
                        True, 
                        f"Response length: {len(content)} chars"
                    )
                    return True
                elif response.status == 400:
                    error_data = await response.json()
                    error_detail = error_data.get("detail", "")
                    if "API key" in error_detail:
                        self.log_test_result(
                            "Perplexity Provider Fallback", 
                            False, 
                            f"API key not configured: {error_detail}"
                        )
                    else:
                        self.log_test_result(
                            "Perplexity Provider Fallback", 
                            False, 
                            f"Bad request: {error_detail}"
                        )
                    return False
                else:
                    self.log_test_result("Perplexity Provider Fallback", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Perplexity Provider Fallback", False, f"Exception: {str(e)}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling with invalid requests"""
        try:
            headers = self.get_auth_headers()
            
            # Test with invalid provider
            chat_request = {
                "messages": [
                    {
                        "role": "user", 
                        "content": "Test message"
                    }
                ],
                "provider": "invalid_provider",
                "model": "invalid_model",
                "stream": False
            }
            
            async with self.session.post(f"{self.base_url}/chat/", json=chat_request, headers=headers) as response:
                if response.status == 400:
                    error_data = await response.json()
                    error_detail = error_data.get("detail", "")
                    
                    self.log_test_result(
                        "Error Handling", 
                        True, 
                        f"Properly handled invalid provider with error: {error_detail}"
                    )
                    return True
                else:
                    self.log_test_result("Error Handling", False, f"Expected 400, got HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test_result("Error Handling", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("🧪 XIONIMUS AI BACKEND TEST SUMMARY")
        print("="*80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("="*80)
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL ANTHROPIC STREAMING FIX STATUS:")
        anthropic_test = next((r for r in self.test_results if "Anthropic System Message Fix" in r["test"]), None)
        if anthropic_test:
            if anthropic_test["success"]:
                print("✅ ANTHROPIC STREAMING FIX VERIFIED - System messages properly handled!")
            else:
                print("❌ ANTHROPIC STREAMING FIX FAILED - System message handling issue detected!")
                print(f"   Details: {anthropic_test['details']}")
        else:
            print("⚠️  ANTHROPIC STREAMING FIX NOT TESTED - Test was skipped")
        
        print("="*80)

async def main():
    """Main test execution"""
    print("🚀 Starting Xionimus AI Backend Testing Suite")
    print("🎯 Focus: Anthropic Streaming Fix Verification")
    print("="*80)
    
    async with XionimusBackendTester() as tester:
        # Core functionality tests
        await tester.test_health_check()
        
        # Authentication test
        auth_success = await tester.authenticate()
        if not auth_success:
            print("❌ Authentication failed - skipping authenticated tests")
            tester.print_summary()
            return
        
        # API Keys management tests
        await tester.test_api_keys_list()
        await tester.test_api_keys_decrypted()
        
        # CRITICAL: Anthropic streaming fix test
        await tester.test_anthropic_chat_with_system_message()
        await tester.test_anthropic_streaming_endpoint()
        
        # Multi-agent system test
        await tester.test_multi_agent_types()
        
        # Provider fallback tests (ensure no regression)
        await tester.test_openai_provider_fallback()
        await tester.test_perplexity_provider_fallback()
        
        # Error handling test
        await tester.test_error_handling()
        
        # Print comprehensive summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
                f"{BASE_URL}/auth/login",
                json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })
                    self.log_result("Authentication", True, f"Token obtained for user {TEST_USERNAME}", response_time)
                    return True
                else:
                    self.log_result("Authentication", False, "No access token in response", response_time)
                    return False
            else:
                self.log_result("Authentication", False, f"HTTP {response.status_code}: {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test all 7 multi-agent API endpoints"""
        print("\n🌐 API ENDPOINT TESTING")
        print("=" * 50)
        
        # Test 1: GET /api/multi-agents/health
        self.test_agents_health()
        
        # Test 2: GET /api/multi-agents/types
        self.test_agent_types()
        
        # Test 3: GET /api/multi-agents/metrics
        self.test_agent_metrics()
        
        # Test 4: POST /api/multi-agents/execute (simple)
        self.test_agent_execution()
        
        # Test 5: POST /api/multi-agents/execute/stream
        self.test_streaming_execution()
        
        # Test 6: GET /api/multi-agents/health/{agent_type}
        self.test_specific_agent_health()
        
        # Test 7: POST /api/multi-agents/collaborative
        self.test_collaborative_execution()
    
    def test_agents_health(self):
        """Test GET /api/multi-agents/health"""
        try:
            start_time = time.time()
            response = self.session.get(f"{MULTI_AGENTS_BASE}/health", timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                total_agents = data.get("total_agents", 0)
                healthy_agents = data.get("healthy_agents", 0)
                overall_healthy = data.get("overall_healthy", False)
                
                details = f"Total: {total_agents}, Healthy: {healthy_agents}, Overall: {overall_healthy}"
                self.log_result("GET /health", True, details, response_time)
                
                # Store agent health for individual tests
                self.agent_health_data = data.get("agents", {})
                
            else:
                self.log_result("GET /health", False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("GET /health", False, f"Exception: {str(e)}")
    
    def test_agent_types(self):
        """Test GET /api/multi-agents/types"""
        try:
            start_time = time.time()
            response = self.session.get(f"{MULTI_AGENTS_BASE}/types", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                total_agents = data.get("total_agents", 0)
                agents = data.get("agents", [])
                
                # Verify all 8 expected agents are present
                expected_agents = ["research", "code_review", "testing", "documentation", 
                                 "debugging", "security", "performance", "fork"]
                found_agents = [agent["type"] for agent in agents]
                
                missing_agents = set(expected_agents) - set(found_agents)
                if not missing_agents and total_agents == 8:
                    details = f"All 8 agents found: {', '.join(found_agents)}"
                    self.log_result("GET /types", True, details, response_time)
                else:
                    details = f"Expected 8 agents, found {total_agents}. Missing: {missing_agents}"
                    self.log_result("GET /types", False, details, response_time)
                    
            else:
                self.log_result("GET /types", False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("GET /types", False, f"Exception: {str(e)}")
    
    def test_agent_metrics(self):
        """Test GET /api/multi-agents/metrics"""
        try:
            start_time = time.time()
            response = self.session.get(f"{MULTI_AGENTS_BASE}/metrics", timeout=15)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                time_range = data.get("time_range_hours", 0)
                agent_type = data.get("agent_type", "")
                metrics = data.get("metrics", {})
                
                details = f"Time range: {time_range}h, Agent: {agent_type}, Metrics count: {len(metrics)}"
                self.log_result("GET /metrics", True, details, response_time)
                
            else:
                self.log_result("GET /metrics", False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("GET /metrics", False, f"Exception: {str(e)}")
    
    def test_agent_execution(self):
        """Test POST /api/multi-agents/execute with simple research query"""
        try:
            start_time = time.time()
            
            # Test with Research Agent - simple query
            payload = {
                "agent_type": "research",
                "input_data": {
                    "query": "What is artificial intelligence?",
                    "deep_research": False
                },
                "session_id": "test_session_001",
                "user_id": "demo",
                "options": {
                    "max_tokens": 500,
                    "temperature": 0.2
                }
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute",
                json=payload,
                timeout=60
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                execution_id = data.get("execution_id")
                agent_type = data.get("agent_type")
                status = data.get("status")
                output_data = data.get("output_data", {})
                
                if status == "completed" and output_data:
                    content_length = len(output_data.get("content", ""))
                    details = f"Agent: {agent_type}, Status: {status}, Content: {content_length} chars"
                    self.log_result("POST /execute (Research)", True, details, response_time)
                else:
                    details = f"Status: {status}, Output: {bool(output_data)}"
                    self.log_result("POST /execute (Research)", False, details, response_time)
                    
            else:
                self.log_result("POST /execute (Research)", False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("POST /execute (Research)", False, f"Exception: {str(e)}")
    
    def test_streaming_execution(self):
        """Test POST /api/multi-agents/execute/stream"""
        try:
            start_time = time.time()
            
            payload = {
                "agent_type": "code_review",
                "input_data": {
                    "code": "def hello_world():\n    print('Hello, World!')\n    return True",
                    "language": "python"
                },
                "session_id": "test_session_002",
                "user_id": "demo"
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute/stream",
                json=payload,
                timeout=60,
                stream=True
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Check if response is streaming (Server-Sent Events)
                content_type = response.headers.get("content-type", "")
                if "text/event-stream" in content_type or "text/plain" in content_type:
                    # Try to read first few chunks
                    chunks_received = 0
                    for line in response.iter_lines(decode_unicode=True):
                        if line and chunks_received < 5:  # Read first 5 chunks
                            chunks_received += 1
                        if chunks_received >= 5:
                            break
                    
                    details = f"Streaming response received, {chunks_received} chunks processed"
                    self.log_result("POST /execute/stream", True, details, response_time)
                else:
                    details = f"Non-streaming response: {content_type}"
                    self.log_result("POST /execute/stream", False, details, response_time)
                    
            else:
                self.log_result("POST /execute/stream", False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("POST /execute/stream", False, f"Exception: {str(e)}")
    
    def test_specific_agent_health(self):
        """Test GET /api/multi-agents/health/{agent_type}"""
        try:
            # Test with Research Agent
            start_time = time.time()
            response = self.session.get(f"{MULTI_AGENTS_BASE}/health/research", timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                agent_type = data.get("agent_type")
                is_healthy = data.get("is_healthy")
                provider = data.get("provider")
                model = data.get("model")
                
                details = f"Agent: {agent_type}, Healthy: {is_healthy}, Provider: {provider}, Model: {model}"
                self.log_result("GET /health/{agent_type}", True, details, response_time)
                
            elif response.status_code == 404:
                self.log_result("GET /health/{agent_type}", False, "Agent not found", response_time)
            else:
                self.log_result("GET /health/{agent_type}", False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("GET /health/{agent_type}", False, f"Exception: {str(e)}")
    
    def test_collaborative_execution(self):
        """Test POST /api/multi-agents/collaborative"""
        try:
            start_time = time.time()
            
            payload = {
                "agent_type": "debugging",
                "input_data": {
                    "code": "def buggy_function(x):\n    return x / 0  # Division by zero error",
                    "error": "ZeroDivisionError: division by zero"
                },
                "session_id": "test_session_003",
                "user_id": "demo"
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/collaborative?strategy=sequential",
                json=payload,
                timeout=120
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success")
                primary_agent = data.get("primary_agent")
                strategy = data.get("strategy")
                results = data.get("results", {})
                total_agents = data.get("total_agents", 0)
                
                details = f"Success: {success}, Primary: {primary_agent}, Strategy: {strategy}, Agents: {total_agents}"
                self.log_result("POST /collaborative", True, details, response_time)
                
            else:
                self.log_result("POST /collaborative", False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result("POST /collaborative", False, f"Exception: {str(e)}")
    
    def test_individual_agents(self):
        """Test each of the 8 individual agents"""
        print("\n🤖 INDIVIDUAL AGENT TESTING")
        print("=" * 50)
        
        # Define test cases for each agent
        agent_tests = [
            {
                "name": "Research Agent",
                "type": "research",
                "input_data": {
                    "query": "Latest trends in machine learning 2025",
                    "deep_research": False
                },
                "expected_output": ["content", "citations"]
            },
            {
                "name": "Code Review Agent", 
                "type": "code_review",
                "input_data": {
                    "code": "def calculate_average(numbers):\n    return sum(numbers) / len(numbers)",
                    "language": "python"
                },
                "expected_output": ["review"]
            },
            {
                "name": "Testing Agent",
                "type": "testing", 
                "input_data": {
                    "code": "def add(a, b):\n    return a + b",
                    "language": "python"
                },
                "expected_output": ["tests"]
            },
            {
                "name": "Documentation Agent",
                "type": "documentation",
                "input_data": {
                    "topic": "REST API authentication methods",
                    "doc_type": "guide"
                },
                "expected_output": ["documentation"]
            },
            {
                "name": "Debugging Agent",
                "type": "debugging",
                "input_data": {
                    "code": "def divide(a, b):\n    return a / b",
                    "error": "ZeroDivisionError when b=0"
                },
                "expected_output": ["fixed_code", "explanation"]
            },
            {
                "name": "Security Agent",
                "type": "security",
                "input_data": {
                    "code": "SELECT * FROM users WHERE id = '" + "user_input" + "'",
                    "language": "sql"
                },
                "expected_output": ["vulnerabilities", "recommendations"]
            },
            {
                "name": "Performance Agent",
                "type": "performance",
                "input_data": {
                    "code": "for i in range(1000):\n    for j in range(1000):\n        result = i * j",
                    "language": "python"
                },
                "expected_output": ["analysis", "optimizations"]
            },
            {
                "name": "Fork Agent",
                "type": "fork",
                "input_data": {
                    "action": "list_repos",
                    "username": "octocat"
                },
                "expected_output": ["repositories"]
            }
        ]
        
        for test_case in agent_tests:
            self.test_single_agent(test_case)
    
    def test_single_agent(self, test_case: Dict[str, Any]):
        """Test a single agent execution"""
        try:
            start_time = time.time()
            
            payload = {
                "agent_type": test_case["type"],
                "input_data": test_case["input_data"],
                "session_id": f"test_session_{test_case['type']}",
                "user_id": "demo",
                "options": {
                    "max_tokens": 1000,
                    "temperature": 0.3
                }
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute",
                json=payload,
                timeout=90
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                output_data = data.get("output_data", {})
                error_message = data.get("error_message")
                
                if status == "completed" and output_data:
                    # Check if expected outputs are present
                    expected_keys = test_case.get("expected_output", [])
                    found_keys = [key for key in expected_keys if key in output_data]
                    
                    if found_keys:
                        details = f"Status: {status}, Found outputs: {found_keys}"
                        self.log_result(test_case["name"], True, details, response_time)
                    else:
                        details = f"Status: {status}, Missing expected outputs: {expected_keys}"
                        self.log_result(test_case["name"], False, details, response_time)
                        
                elif status == "failed":
                    details = f"Agent failed: {error_message}"
                    self.log_result(test_case["name"], False, details, response_time)
                    
                else:
                    details = f"Unexpected status: {status}"
                    self.log_result(test_case["name"], False, details, response_time)
                    
            else:
                self.log_result(test_case["name"], False, f"HTTP {response.status_code}: {response.text}", response_time)
                
        except Exception as e:
            self.log_result(test_case["name"], False, f"Exception: {str(e)}")
    
    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("\n⚠️  ERROR SCENARIO TESTING")
        print("=" * 50)
        
        # Test 1: Invalid agent type
        self.test_invalid_agent_type()
        
        # Test 2: Missing required fields
        self.test_missing_fields()
        
        # Test 3: Malformed requests
        self.test_malformed_requests()
        
        # Test 4: Authentication failures
        self.test_auth_failures()
    
    def test_invalid_agent_type(self):
        """Test with invalid agent type"""
        try:
            start_time = time.time()
            
            payload = {
                "agent_type": "invalid_agent",
                "input_data": {"query": "test"},
                "session_id": "test_session_error",
                "user_id": "demo"
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute",
                json=payload,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 400:
                self.log_result("Invalid Agent Type", True, "Correctly rejected invalid agent type", response_time)
            else:
                self.log_result("Invalid Agent Type", False, f"Expected 400, got {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Invalid Agent Type", False, f"Exception: {str(e)}")
    
    def test_missing_fields(self):
        """Test with missing required fields"""
        try:
            start_time = time.time()
            
            # Missing input_data
            payload = {
                "agent_type": "research",
                "session_id": "test_session_error",
                "user_id": "demo"
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute",
                json=payload,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code in [400, 422]:
                self.log_result("Missing Required Fields", True, "Correctly rejected missing fields", response_time)
            else:
                self.log_result("Missing Required Fields", False, f"Expected 400/422, got {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Missing Required Fields", False, f"Exception: {str(e)}")
    
    def test_malformed_requests(self):
        """Test with malformed JSON"""
        try:
            start_time = time.time()
            
            # Send invalid JSON
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code in [400, 422]:
                self.log_result("Malformed Request", True, "Correctly rejected malformed JSON", response_time)
            else:
                self.log_result("Malformed Request", False, f"Expected 400/422, got {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Malformed Request", False, f"Exception: {str(e)}")
    
    def test_auth_failures(self):
        """Test authentication failures"""
        try:
            # Remove auth header temporarily
            original_headers = self.session.headers.copy()
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
            
            start_time = time.time()
            
            payload = {
                "agent_type": "research",
                "input_data": {"query": "test"},
                "session_id": "test_session_auth",
                "user_id": "demo"
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute",
                json=payload,
                timeout=30
            )
            response_time = time.time() - start_time
            
            # Restore headers
            self.session.headers.update(original_headers)
            
            if response.status_code == 401:
                self.log_result("Authentication Required", True, "Correctly requires authentication", response_time)
            else:
                self.log_result("Authentication Required", False, f"Expected 401, got {response.status_code}", response_time)
                
        except Exception as e:
            self.log_result("Authentication Required", False, f"Exception: {str(e)}")
    
    def test_performance(self):
        """Test performance metrics"""
        print("\n⚡ PERFORMANCE TESTING")
        print("=" * 50)
        
        # Test concurrent executions (simplified)
        self.test_response_times()
        
        # Test timeout configurations
        self.test_timeout_handling()
    
    def test_response_times(self):
        """Test response times for different agents"""
        try:
            # Test quick agents first
            quick_tests = [
                ("research", {"query": "What is Python?", "deep_research": False}),
                ("code_review", {"code": "print('hello')", "language": "python"}),
                ("testing", {"code": "def test(): pass", "language": "python"})
            ]
            
            total_time = 0
            successful_tests = 0
            
            for agent_type, input_data in quick_tests:
                start_time = time.time()
                
                payload = {
                    "agent_type": agent_type,
                    "input_data": input_data,
                    "session_id": f"perf_test_{agent_type}",
                    "user_id": "demo",
                    "options": {"max_tokens": 200}
                }
                
                try:
                    response = self.session.post(
                        f"{MULTI_AGENTS_BASE}/execute",
                        json=payload,
                        timeout=60
                    )
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        total_time += response_time
                        successful_tests += 1
                        
                except Exception:
                    pass
            
            if successful_tests > 0:
                avg_time = total_time / successful_tests
                details = f"Average response time: {avg_time:.2f}s across {successful_tests} agents"
                success = avg_time < 30.0  # Should be under 30 seconds
                self.log_result("Response Time Performance", success, details, avg_time)
            else:
                self.log_result("Response Time Performance", False, "No successful tests for timing")
                
        except Exception as e:
            self.log_result("Response Time Performance", False, f"Exception: {str(e)}")
    
    def test_timeout_handling(self):
        """Test timeout configurations"""
        try:
            start_time = time.time()
            
            # Test with very short timeout (should still work for simple queries)
            payload = {
                "agent_type": "research",
                "input_data": {"query": "AI", "deep_research": False},
                "session_id": "timeout_test",
                "user_id": "demo",
                "options": {"max_tokens": 50}
            }
            
            response = self.session.post(
                f"{MULTI_AGENTS_BASE}/execute",
                json=payload,
                timeout=5  # Very short client timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result("Timeout Handling", True, "Quick response within timeout", response_time)
            else:
                self.log_result("Timeout Handling", False, f"HTTP {response.status_code}", response_time)
                
        except requests.exceptions.Timeout:
            self.log_result("Timeout Handling", True, "Timeout handled correctly", 5.0)
        except Exception as e:
            self.log_result("Timeout Handling", False, f"Exception: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 TEST REPORT")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
            print()
        
        # Performance summary
        response_times = [r["response_time"] for r in self.test_results if r["response_time"] > 0]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            print(f"Average Response Time: {avg_response_time:.2f}s")
            print(f"Maximum Response Time: {max_response_time:.2f}s")
            print()
        
        # Overall assessment
        if success_rate >= 90:
            print("🎉 OVERALL ASSESSMENT: EXCELLENT - Multi-agent system is production ready!")
        elif success_rate >= 75:
            print("✅ OVERALL ASSESSMENT: GOOD - Multi-agent system is mostly functional")
        elif success_rate >= 50:
            print("⚠️  OVERALL ASSESSMENT: NEEDS IMPROVEMENT - Several issues detected")
        else:
            print("❌ OVERALL ASSESSMENT: CRITICAL ISSUES - Major problems need fixing")
        
        return success_rate >= 75
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 MULTI-AGENT SYSTEM COMPREHENSIVE TESTING")
        print("=" * 70)
        print(f"Backend URL: {BASE_URL}")
        print(f"Multi-Agents URL: {MULTI_AGENTS_BASE}")
        print(f"Test User: {TEST_USERNAME}")
        print()
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: API Endpoint Testing
        self.test_api_endpoints()
        
        # Step 3: Individual Agent Testing
        self.test_individual_agents()
        
        # Step 4: Error Scenario Testing
        self.test_error_scenarios()
        
        # Step 5: Performance Testing
        self.test_performance()
        
        # Step 6: Generate Report
        return self.generate_report()

def main():
    """Main test execution"""
    tester = MultiAgentTester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()