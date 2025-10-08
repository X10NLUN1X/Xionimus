#!/usr/bin/env python3
"""
Focused Reasoning Models Test
Test reasoning models (o1-mini, o1) to verify token output handling
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

# Test Configuration
BACKEND_URL = "http://localhost:8001"
TEST_USER = "demo"
TEST_PASSWORD = "demo123"

class ReasoningModelsTest:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)  # Longer timeout for reasoning models
        self.auth_token = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
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
                print(f"✅ Authenticated as {TEST_USER}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_auth_headers(self):
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
    
    async def test_reasoning_model(self, model: str, test_prompt: str) -> dict:
        """Test specific reasoning model with detailed analysis"""
        print(f"\n🧠 Testing Reasoning Model: {model}")
        print("-" * 50)
        
        try:
            # Create session
            session_response = await self.client.post(
                f"{BACKEND_URL}/api/sessions/",
                headers=self.get_auth_headers(),
                json={"name": f"Reasoning Test - {model}"}
            )
            
            if session_response.status_code != 200:
                return {"success": False, "error": f"Session creation failed: {session_response.status_code}"}
            
            session_id = session_response.json().get("id")
            
            # Test reasoning model
            start_time = datetime.now()
            
            chat_payload = {
                "messages": [{"role": "user", "content": test_prompt}],
                "provider": "openai",
                "model": model,
                "session_id": session_id,
                "ultra_thinking": False,
                "developer_mode": "senior"
            }
            
            print(f"📤 Sending request to {model}...")
            print(f"🔍 Prompt: {test_prompt}")
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/chat/",
                headers=self.get_auth_headers(),
                json=chat_payload
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                usage = data.get("usage", {})
                model_used = data.get("model", "")
                
                print(f"✅ Response received in {response_time:.2f}s")
                print(f"📊 Model used: {model_used}")
                print(f"📊 Content length: {len(content)} characters")
                
                if usage:
                    print(f"📊 Token usage:")
                    print(f"   - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"   - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                    print(f"   - Total tokens: {usage.get('total_tokens', 'N/A')}")
                
                print(f"📝 Response preview: {content[:200]}...")
                
                # Check for reasoning model specific issues
                issues = []
                if not content or len(content.strip()) == 0:
                    issues.append("Empty response content")
                
                if "reasoning tokens" in content.lower() and "not available" in content.lower():
                    issues.append("Reasoning content not accessible via API")
                
                if "⚠️" in content and "Reasoning Model Response Issue" in content:
                    issues.append("Reasoning model API limitation detected")
                
                return {
                    "success": len(issues) == 0,
                    "model": model_used,
                    "content": content,
                    "content_length": len(content),
                    "response_time": response_time,
                    "usage": usage,
                    "issues": issues
                }
            else:
                error_text = response.text
                print(f"❌ Request failed: {response.status_code}")
                print(f"❌ Error: {error_text}")
                return {"success": False, "error": f"HTTP {response.status_code}: {error_text}"}
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_reasoning_tests(self):
        """Run comprehensive reasoning model tests"""
        print("🧠 REASONING MODELS COMPREHENSIVE TEST")
        print("=" * 60)
        
        if not await self.authenticate():
            return
        
        # Test cases for reasoning models
        test_cases = [
            {
                "model": "o1-mini",
                "prompt": "Solve this step by step: If a train travels 120 km in 2 hours, and then 180 km in 3 hours, what is the average speed for the entire journey?",
                "expected_reasoning": True
            },
            {
                "model": "o1",
                "prompt": "Explain the logic behind this puzzle: You have 12 balls, 11 are identical in weight, 1 is different (either heavier or lighter). Using a balance scale only 3 times, how can you identify the different ball and determine if it's heavier or lighter?",
                "expected_reasoning": True
            },
            {
                "model": "o1-mini",
                "prompt": "Simple math: 7 * 8 = ?",
                "expected_reasoning": False  # Simple calculation shouldn't need much reasoning
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 TEST CASE {i}/{len(test_cases)}")
            result = await self.test_reasoning_model(test_case["model"], test_case["prompt"])
            result["test_case"] = test_case
            results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 REASONING MODELS TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = sum(1 for r in results if r.get("success", False))
        total_tests = len(results)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Successful: {successful_tests}")
        print(f"❌ Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        for i, result in enumerate(results, 1):
            test_case = result.get("test_case", {})
            model = test_case.get("model", "Unknown")
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            
            print(f"\n{i}. {status} {model}")
            
            if result.get("success", False):
                print(f"   📊 Response time: {result.get('response_time', 0):.2f}s")
                print(f"   📊 Content length: {result.get('content_length', 0)} chars")
                usage = result.get("usage", {})
                if usage:
                    print(f"   📊 Tokens: {usage.get('total_tokens', 'N/A')} total")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                issues = result.get("issues", [])
                if issues:
                    for issue in issues:
                        print(f"   ⚠️  Issue: {issue}")
        
        # Critical analysis
        print(f"\n🔍 CRITICAL ANALYSIS:")
        
        reasoning_issues = []
        for result in results:
            issues = result.get("issues", [])
            for issue in issues:
                if issue not in reasoning_issues:
                    reasoning_issues.append(issue)
        
        if reasoning_issues:
            print(f"⚠️  Reasoning Model Issues Detected:")
            for issue in reasoning_issues:
                print(f"   - {issue}")
        else:
            print(f"✅ No critical reasoning model issues detected")
        
        # Performance analysis
        response_times = [r.get("response_time", 0) for r in results if r.get("success", False)]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"📊 Average response time: {avg_time:.2f}s")
            if avg_time > 30:
                print(f"⚠️  Response times are high (>{30}s) - this is expected for reasoning models")

async def main():
    async with ReasoningModelsTest() as tester:
        await tester.run_reasoning_tests()

if __name__ == "__main__":
    asyncio.run(main())