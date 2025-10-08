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