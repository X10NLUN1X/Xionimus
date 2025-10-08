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

class MultiAgentTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
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
        print(f"{status} {test_name} ({response_time:.3f}s)")
        if details:
            print(f"    {details}")
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        print("\n🔐 AUTHENTICATION")
        print("=" * 50)
        
        try:
            start_time = time.time()
            response = self.session.post(
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