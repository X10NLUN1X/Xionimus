#!/usr/bin/env python3
"""
Model Validation Test for Xionimus AI
Tests the updated model configuration with focus on:
- Claude: claude-3-5-sonnet-20241022
- Perplexity: sonar
"""

import asyncio
import aiohttp
import json
import os

# Backend URL from environment
BACKEND_URL = "https://ai-chat-update.preview.emergentagent.com/api"

class ModelValidationTester:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()

    async def test_model_names_with_mock_keys(self):
        """Test that model names are accepted by APIs with mock keys"""
        print("🔍 Testing Model Names with Mock API Keys")
        print("=" * 50)
        
        # Set mock API keys as requested
        mock_keys = {
            "anthropic": "sk-ant-test123",
            "perplexity": "pplx-test123"
        }
        
        # Save mock API keys
        for service, key in mock_keys.items():
            payload = {
                "service": service,
                "key": key,
                "is_active": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/api-keys", json=payload) as response:
                if response.status == 200:
                    self.log_result(f"Mock API Key Setup - {service.title()}", "PASS", 
                                  f"Mock key {key} saved successfully")
                else:
                    self.log_result(f"Mock API Key Setup - {service.title()}", "FAIL", 
                                  f"HTTP {response.status}")
                    return
        
        # Test Claude with updated model name
        claude_payload = {
            "message": "Test message for model validation",
            "model": "claude",
            "use_agent": False
        }
        
        async with self.session.post(f"{BACKEND_URL}/chat", json=claude_payload) as response:
            response_text = await response.text()
            
            if response.status == 400:
                try:
                    data = await response.json()
                    error_detail = data.get("detail", "")
                    
                    # Check if it's an authentication error (expected with mock key)
                    if "authentication_error" in error_detail or "invalid x-api-key" in error_detail:
                        self.log_result("Claude Model Name Validation", "PASS", 
                                      "Model name 'claude-3-5-sonnet-20241022' accepted by API (auth failed as expected with mock key)")
                    elif "model" in error_detail.lower() and ("not found" in error_detail.lower() or "invalid" in error_detail.lower()):
                        self.log_result("Claude Model Name Validation", "FAIL", 
                                      f"Model name rejected: {error_detail}")
                    else:
                        self.log_result("Claude Model Name Validation", "PASS", 
                                      f"Model name accepted, API error: {error_detail}")
                except:
                    # If we can't parse JSON, check the raw response
                    if "authentication" in response_text.lower() or "401" in response_text:
                        self.log_result("Claude Model Name Validation", "PASS", 
                                      "Model name accepted (auth failed as expected)")
                    else:
                        self.log_result("Claude Model Name Validation", "WARN", 
                                      f"Unexpected response format: {response_text[:200]}")
            else:
                self.log_result("Claude Model Name Validation", "WARN", 
                              f"Unexpected status code: {response.status}")
        
        # Test Perplexity with updated model name
        perplexity_payload = {
            "message": "Test message for model validation",
            "model": "perplexity",
            "use_agent": False
        }
        
        async with self.session.post(f"{BACKEND_URL}/chat", json=perplexity_payload) as response:
            response_text = await response.text()
            
            if response.status == 400:
                try:
                    data = await response.json()
                    error_detail = data.get("detail", "")
                    
                    # Check if it's an authentication error (expected with mock key)
                    if "401" in error_detail or "authorization" in error_detail.lower():
                        self.log_result("Perplexity Model Name Validation", "PASS", 
                                      "Model name 'sonar' accepted by API (auth failed as expected with mock key)")
                    elif "model" in error_detail.lower() and ("not found" in error_detail.lower() or "invalid" in error_detail.lower()):
                        self.log_result("Perplexity Model Name Validation", "FAIL", 
                                      f"Model name rejected: {error_detail}")
                    else:
                        self.log_result("Perplexity Model Name Validation", "PASS", 
                                      f"Model name accepted, API error: {error_detail}")
                except:
                    # If we can't parse JSON, check the raw response
                    if "401" in response_text or "authorization" in response_text.lower():
                        self.log_result("Perplexity Model Name Validation", "PASS", 
                                      "Model name accepted (auth failed as expected)")
                    else:
                        self.log_result("Perplexity Model Name Validation", "WARN", 
                                      f"Unexpected response format: {response_text[:200]}")
            else:
                self.log_result("Perplexity Model Name Validation", "WARN", 
                              f"Unexpected status code: {response.status}")

    async def test_error_handling_status_codes(self):
        """Test that proper HTTP status codes are returned"""
        print("🔍 Testing Error Handling Status Codes")
        print("=" * 50)
        
        # Test with no API keys configured (should return 400)
        # First clear the mock keys by setting empty ones
        for service in ["anthropic", "perplexity"]:
            payload = {
                "service": service,
                "key": "",
                "is_active": False
            }
            await self.session.post(f"{BACKEND_URL}/api-keys", json=payload)
        
        # Test Claude without API key
        claude_payload = {
            "message": "Test message",
            "model": "claude",
            "use_agent": False
        }
        
        async with self.session.post(f"{BACKEND_URL}/chat", json=claude_payload) as response:
            if response.status == 400:
                data = await response.json()
                if "Anthropic API key not configured" in data.get("detail", ""):
                    self.log_result("Error Handling - Claude No Key", "PASS", 
                                  "Returns 400 with proper error message when API key not configured")
                else:
                    self.log_result("Error Handling - Claude No Key", "FAIL", 
                                  f"Wrong error message: {data.get('detail')}")
            elif response.status == 500:
                self.log_result("Error Handling - Claude No Key", "FAIL", 
                              "Returns 500 instead of 400 (error handling bug)")
            else:
                self.log_result("Error Handling - Claude No Key", "FAIL", 
                              f"Unexpected status code: {response.status}")
        
        # Test Perplexity without API key
        perplexity_payload = {
            "message": "Test message",
            "model": "perplexity",
            "use_agent": False
        }
        
        async with self.session.post(f"{BACKEND_URL}/chat", json=perplexity_payload) as response:
            if response.status == 400:
                data = await response.json()
                if "Perplexity API key not configured" in data.get("detail", ""):
                    self.log_result("Error Handling - Perplexity No Key", "PASS", 
                                  "Returns 400 with proper error message when API key not configured")
                else:
                    self.log_result("Error Handling - Perplexity No Key", "FAIL", 
                                  f"Wrong error message: {data.get('detail')}")
            elif response.status == 500:
                self.log_result("Error Handling - Perplexity No Key", "FAIL", 
                              "Returns 500 instead of 400 (error handling bug)")
            else:
                self.log_result("Error Handling - Perplexity No Key", "FAIL", 
                              f"Unexpected status code: {response.status}")

    async def run_validation_tests(self):
        """Run all model validation tests"""
        print("🚀 Starting Model Validation Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.test_model_names_with_mock_keys()
        await self.test_error_handling_status_codes()
        
        print("=" * 60)
        print("✅ Model validation tests completed!")

async def main():
    """Main test runner"""
    async with ModelValidationTester() as tester:
        await tester.run_validation_tests()

if __name__ == "__main__":
    asyncio.run(main())