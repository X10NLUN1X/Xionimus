#!/usr/bin/env python3
"""
Comprehensive Backend Testing - GitHub OAuth & Chat Functionality
Focus: GitHub OAuth endpoints, API Keys management, and Chat functionality with reasoning models
"""

import asyncio
import httpx
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Test Configuration
BACKEND_URL = "http://localhost:8001"
TEST_USER = "demo"
TEST_PASSWORD = "demo123"

class GitHubOAuthChatTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_result(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    📋 {details}")
        if error:
            print(f"    ❌ Error: {error}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    async def authenticate(self) -> bool:
        """Authenticate with demo credentials"""
        try:
            response = await self.client.post(
                f"{BACKEND_URL}/api/auth/login",
                json={"username": TEST_USER, "password": TEST_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.log_result("Authentication", True, f"Logged in as {TEST_USER}")
                return True
            else:
                self.log_result("Authentication", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, error=str(e))
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
    
    async def test_github_oauth_authorize_url(self) -> bool:
        """Test GitHub OAuth authorization URL generation"""
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/api/github/oauth/authorize-url",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if "authorization_url" in data and "state" in data:
                    auth_url = data["authorization_url"]
                    if "github.com/login/oauth/authorize" in auth_url:
                        self.log_result("GitHub OAuth - Authorize URL", True, 
                                      f"Generated URL with state: {data['state'][:8]}...")
                        return True
                    else:
                        self.log_result("GitHub OAuth - Authorize URL", False, 
                                      error="Invalid authorization URL format")
                        return False
                else:
                    self.log_result("GitHub OAuth - Authorize URL", False, 
                                  error="Missing authorization_url or state in response")
                    return False
            else:
                self.log_result("GitHub OAuth - Authorize URL", False, 
                              error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GitHub OAuth - Authorize URL", False, error=str(e))
            return False
    
    async def test_github_oauth_status(self) -> bool:
        """Test GitHub OAuth connection status"""
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/api/github/oauth/status",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if "connected" in data and "message" in data:
                    connected = data["connected"]
                    message = data["message"]
                    self.log_result("GitHub OAuth - Status Check", True, 
                                  f"Connected: {connected}, Message: {message}")
                    return True
                else:
                    self.log_result("GitHub OAuth - Status Check", False, 
                                  error="Missing connected or message in response")
                    return False
            else:
                self.log_result("GitHub OAuth - Status Check", False, 
                              error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("GitHub OAuth - Status Check", False, error=str(e))
            return False
    
    async def test_api_keys_list(self) -> Dict[str, bool]:
        """Test API keys listing and return which providers are configured"""
        try:
            response = await self.client.get(
                f"{BACKEND_URL}/api/api-keys/list",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                api_keys = data.get("api_keys", [])
                
                # Check which providers are configured
                configured_providers = {}
                for key in api_keys:
                    provider = key.get("provider")
                    is_active = key.get("is_active", False)
                    masked_key = key.get("masked_key", "")
                    
                    # Consider key configured if it's active and not requiring re-entry
                    configured_providers[provider] = is_active and not masked_key.startswith("[Key requires")
                
                provider_status = []
                for provider in ["anthropic", "openai", "perplexity", "github"]:
                    status = "✅" if configured_providers.get(provider, False) else "❌"
                    provider_status.append(f"{provider}: {status}")
                
                self.log_result("API Keys - List", True, 
                              f"Found {len(api_keys)} keys. Status: {', '.join(provider_status)}")
                return configured_providers
            else:
                self.log_result("API Keys - List", False, 
                              error=f"HTTP {response.status_code}: {response.text}")
                return {}
                
        except Exception as e:
            self.log_result("API Keys - List", False, error=str(e))
            return {}
    
    async def test_api_key_connection(self, provider: str) -> bool:
        """Test connection to specific API provider"""
        try:
            response = await self.client.post(
                f"{BACKEND_URL}/api/api-keys/test-connection",
                headers=self.get_auth_headers(),
                json={"provider": provider}
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                message = data.get("message", "")
                
                self.log_result(f"API Connection - {provider.title()}", success, 
                              f"Connection test: {message}")
                return success
            elif response.status_code == 404:
                self.log_result(f"API Connection - {provider.title()}", False, 
                              error="API key not configured")
                return False
            else:
                self.log_result(f"API Connection - {provider.title()}", False, 
                              error=f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result(f"API Connection - {provider.title()}", False, error=str(e))
            return False
    
    async def test_chat_functionality(self, provider: str, model: str, test_message: str = "Hello, please respond with 'Test successful'") -> bool:
        """Test chat functionality with specific provider and model"""
        try:
            # Create a test session first
            session_response = await self.client.post(
                f"{BACKEND_URL}/api/sessions/",
                headers=self.get_auth_headers(),
                json={"name": f"Test Chat - {provider} {model}"}
            )
            
            if session_response.status_code != 200:
                self.log_result(f"Chat Test - {provider} {model}", False, 
                              error=f"Failed to create session: {session_response.status_code}")
                return False
            
            session_data = session_response.json()
            session_id = session_data.get("id")
            
            # Test chat via HTTP API (not WebSocket for simplicity)
            
            # Use the correct chat endpoint
            chat_payload = {
                "messages": [{"role": "user", "content": test_message}],
                "provider": provider,
                "model": model,
                "session_id": session_id,
                "ultra_thinking": False,
                "developer_mode": "senior"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/chat/",
                headers=self.get_auth_headers(),
                json=chat_payload
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                model_used = data.get("model", "")
                provider_used = data.get("provider", "")
                
                # Check if we got a meaningful response
                if content and len(content.strip()) > 0:
                    # Check for reasoning model specific issues
                    if "reasoning tokens" in content.lower() and "not available" in content.lower():
                        self.log_result(f"Chat Test - {provider} {model}", False, 
                                      error=f"Reasoning model content not accessible: {content[:100]}...")
                        return False
                    else:
                        self.log_result(f"Chat Test - {provider} {model}", True, 
                                      f"Response received ({len(content)} chars): {content[:50]}...")
                        return True
                else:
                    self.log_result(f"Chat Test - {provider} {model}", False, 
                                  error="Empty response content")
                    return False
            else:
                error_text = response.text
                self.log_result(f"Chat Test - {provider} {model}", False, 
                              error=f"HTTP {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result(f"Chat Test - {provider} {model}", False, error=str(e))
            return False
    
    async def test_reasoning_model_handling(self) -> bool:
        """Test specific reasoning model handling (o1-mini, o1-preview)"""
        reasoning_models = [
            ("openai", "o1-mini"),
            ("openai", "o1")
        ]
        
        success_count = 0
        total_tests = len(reasoning_models)
        
        for provider, model in reasoning_models:
            test_message = "Solve this simple math: 2+2=?"
            success = await self.test_chat_functionality(provider, model, test_message)
            if success:
                success_count += 1
        
        overall_success = success_count > 0  # At least one reasoning model should work
        self.log_result("Reasoning Models - Overall", overall_success, 
                      f"{success_count}/{total_tests} reasoning models working")
        return overall_success
    
    async def test_session_management(self) -> bool:
        """Test session creation and message persistence"""
        try:
            # Create session
            response = await self.client.post(
                f"{BACKEND_URL}/api/sessions/",
                headers=self.get_auth_headers(),
                json={"name": "Test Session Management"}
            )
            
            if response.status_code != 200:
                self.log_result("Session Management", False, 
                              error=f"Failed to create session: {response.status_code}")
                return False
            
            session_data = response.json()
            session_id = session_data.get("id")
            
            # Add a message to the session
            message_response = await self.client.post(
                f"{BACKEND_URL}/api/sessions/messages",
                headers=self.get_auth_headers(),
                json={
                    "session_id": session_id,
                    "role": "user",
                    "content": "Test message for session persistence"
                }
            )
            
            if message_response.status_code != 200:
                self.log_result("Session Management", False, 
                              error=f"Failed to add message: {message_response.status_code}")
                return False
            
            # Retrieve session to verify persistence
            get_response = await self.client.get(
                f"{BACKEND_URL}/api/sessions/{session_id}",
                headers=self.get_auth_headers()
            )
            
            if get_response.status_code == 200:
                session_info = get_response.json()
                message_count = session_info.get("message_count", 0)
                
                if message_count > 0:
                    self.log_result("Session Management", True, 
                                  f"Session created with {message_count} messages")
                    return True
                else:
                    self.log_result("Session Management", False, 
                                  error="No messages found in session")
                    return False
            else:
                self.log_result("Session Management", False, 
                              error=f"Failed to retrieve session: {get_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Session Management", False, error=str(e))
            return False
    
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Backend Testing - GitHub OAuth & Chat Functionality")
        print("=" * 80)
        
        # Step 1: Authentication
        if not await self.authenticate():
            print("❌ Authentication failed - cannot continue with tests")
            return
        
        print("\n📋 PHASE 1: GitHub OAuth Endpoints Testing")
        print("-" * 50)
        
        # Test GitHub OAuth endpoints
        await self.test_github_oauth_authorize_url()
        await self.test_github_oauth_status()
        
        print("\n📋 PHASE 2: API Keys Management Testing")
        print("-" * 50)
        
        # Test API keys management
        configured_providers = await self.test_api_keys_list()
        
        # Test connections for configured providers
        for provider in ["anthropic", "openai", "perplexity"]:
            if configured_providers.get(provider, False):
                await self.test_api_key_connection(provider)
            else:
                self.log_result(f"API Connection - {provider.title()}", False, 
                              error="API key not configured - skipping connection test")
        
        print("\n📋 PHASE 3: Chat Functionality Testing")
        print("-" * 50)
        
        # Test chat with different models
        chat_tests = [
            ("anthropic", "claude-3-5-haiku-20241022", "Claude Haiku"),
            ("anthropic", "claude-sonnet-4-5-20250929", "Claude Sonnet"),
            ("openai", "gpt-4o-mini", "GPT-4o Mini"),
            ("openai", "gpt-4o", "GPT-4o"),
            ("perplexity", "sonar", "Perplexity Sonar"),
            ("perplexity", "sonar-pro", "Perplexity Sonar Pro")
        ]
        
        for provider, model, display_name in chat_tests:
            if configured_providers.get(provider, False):
                await self.test_chat_functionality(provider, model)
            else:
                self.log_result(f"Chat Test - {display_name}", False, 
                              error=f"{provider} API key not configured")
        
        print("\n📋 PHASE 4: Reasoning Models Testing")
        print("-" * 50)
        
        if configured_providers.get("openai", False):
            await self.test_reasoning_model_handling()
        else:
            self.log_result("Reasoning Models - Overall", False, 
                          error="OpenAI API key not configured")
        
        print("\n📋 PHASE 5: Session Management Testing")
        print("-" * 50)
        
        await self.test_session_management()
        
        # Final summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['error']}")
        
        # Critical issues analysis
        critical_issues = []
        
        # Check for authentication issues
        auth_failed = not any(r["success"] for r in self.test_results if r["test"] == "Authentication")
        if auth_failed:
            critical_issues.append("Authentication system not working")
        
        # Check for API key issues
        api_key_issues = [r for r in self.test_results if "API Connection" in r["test"] and not r["success"]]
        if len(api_key_issues) >= 3:  # All 3 providers failing
            critical_issues.append("All API providers failing - check API keys configuration")
        
        # Check for chat functionality issues
        chat_issues = [r for r in self.test_results if "Chat Test" in r["test"] and not r["success"]]
        if len(chat_issues) > 0:
            critical_issues.append(f"Chat functionality issues detected ({len(chat_issues)} models failing)")
        
        # Check for reasoning model issues
        reasoning_failed = not any(r["success"] for r in self.test_results if r["test"] == "Reasoning Models - Overall")
        if reasoning_failed:
            critical_issues.append("Reasoning models (o1-mini, o1) not working - likely token output issue")
        
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for i, issue in enumerate(critical_issues, 1):
                print(f"  {i}. {issue}")
        
        print(f"\n📝 Detailed results saved to test results")

async def main():
    """Main test execution"""
    async with GitHubOAuthChatTester() as tester:
        await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())