#!/usr/bin/env python3
"""
Quick Verification Test for Xionimus AI Backend
Tests essential endpoints after UI redesign to ensure backend functionality is maintained.

Focus Areas:
1. Health Check: Verify /api/health endpoint is responding correctly
2. API Key Status: Test /api/api-keys/status endpoint 
3. Chat System: Verify /api/chat endpoint is functional
4. Agent System: Check /api/agents endpoint returns all 8 agents
5. MongoDB Connection: Ensure database connectivity is maintained
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Backend URL
BACKEND_URL = "http://127.0.0.1:8001/api"

class QuickVerificationTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_data and status == "FAIL":
            print(f"   Response: {response_data}")
        print()

    async def test_health_endpoint(self):
        """Test /api/health endpoint - Core requirement #1"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check basic structure
                    required_fields = ["status", "timestamp", "services"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Health Check - Structure", "FAIL", 
                                    f"Missing fields: {missing_fields}", data)
                        return False
                    
                    # Check MongoDB connection
                    mongodb_status = data.get("services", {}).get("mongodb")
                    if mongodb_status == "connected":
                        self.log_test("Health Check - MongoDB Connection", "PASS", 
                                    "Database connectivity maintained")
                    else:
                        self.log_test("Health Check - MongoDB Connection", "FAIL", 
                                    f"MongoDB status: {mongodb_status}", data)
                        return False
                    
                    self.log_test("Health Check - Overall", "PASS", 
                                "Health endpoint responding correctly")
                    return True
                    
                else:
                    self.log_test("Health Check - Overall", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    return False
                    
        except Exception as e:
            self.log_test("Health Check - Overall", "FAIL", f"Exception: {str(e)}")
            return False

    async def test_api_key_status(self):
        """Test API key status endpoint - Core requirement #2"""
        try:
            async with self.session.get(f"{BACKEND_URL}/api-keys/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for status field (new format)
                    if "status" in data:
                        status_data = data["status"]
                        required_services = ["perplexity", "anthropic", "openai"]
                        missing_services = [service for service in required_services if service not in status_data]
                        
                        if not missing_services:
                            self.log_test("API Key Status - All Services", "PASS", 
                                        f"All 3 services present: {list(status_data.keys())}")
                            return True
                        else:
                            self.log_test("API Key Status - All Services", "FAIL", 
                                        f"Missing services: {missing_services}", data)
                            return False
                    else:
                        # Fallback to old format
                        required_services = ["perplexity", "anthropic", "openai"]
                        missing_services = [service for service in required_services if service not in data]
                        
                        if not missing_services:
                            self.log_test("API Key Status - All Services", "PASS", 
                                        f"All 3 services present: {list(data.keys())}")
                            return True
                        else:
                            self.log_test("API Key Status - All Services", "FAIL", 
                                        f"Missing services: {missing_services}", data)
                            return False
                else:
                    self.log_test("API Key Status", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    return False
                    
        except Exception as e:
            self.log_test("API Key Status", "FAIL", f"Exception: {str(e)}")
            return False

    async def test_chat_endpoint(self):
        """Test chat endpoint functionality - Core requirement #3"""
        try:
            # Test with minimal valid request
            test_payload = {
                "message": "Hello, this is a test message to verify chat functionality"
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", 
                                       json=test_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and data["message"].get("role") == "assistant":
                        self.log_test("Chat System - Functionality", "PASS", 
                                    "Chat endpoint is functional and returns proper response")
                        return True
                    else:
                        self.log_test("Chat System - Functionality", "FAIL", 
                                    f"Invalid response structure: {data}")
                        return False
                elif response.status == 400:
                    data = await response.json()
                    if "API" in data.get("detail", "") or "Schlüssel" in data.get("detail", ""):
                        self.log_test("Chat System - Functionality", "PASS", 
                                    "Chat endpoint is functional (API key error expected)")
                        return True
                    else:
                        self.log_test("Chat System - Functionality", "FAIL", 
                                    f"Unexpected error: {data.get('detail')}")
                        return False
                else:
                    self.log_test("Chat System - Functionality", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    return False
                    
        except Exception as e:
            self.log_test("Chat System - Functionality", "FAIL", f"Exception: {str(e)}")
            return False

    async def test_agents_endpoint(self):
        """Test agents endpoint returns all 8 agents - Core requirement #4"""
        try:
            async with self.session.get(f"{BACKEND_URL}/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Handle both old and new response formats
                    if isinstance(data, dict) and "agents" in data:
                        agents_list = data["agents"]
                        total_agents = data.get("total_agents", len(agents_list))
                    elif isinstance(data, list):
                        agents_list = data
                        total_agents = len(agents_list)
                    else:
                        self.log_test("Agent System - Response Format", "FAIL", 
                                    f"Unexpected response format: {type(data)}", data)
                        return False
                    
                    if total_agents >= 8:  # Allow for additional agents
                        agent_names = [agent.get("name") for agent in agents_list]
                        expected_agents = [
                            "Code Agent", "Research Agent", "Writing Agent", "Data Agent",
                            "QA Agent", "GitHub Agent", "File Agent", "Session Agent"
                        ]
                        
                        missing_agents = [name for name in expected_agents if name not in agent_names]
                        if not missing_agents:
                            self.log_test("Agent System - All Required Agents", "PASS", 
                                        f"All {total_agents} agents available (including {total_agents - 8} additional): {agent_names}")
                            return True
                        else:
                            self.log_test("Agent System - Missing Required Agents", "FAIL", 
                                        f"Missing required agents: {missing_agents}")
                            return False
                    else:
                        self.log_test("Agent System - Agent Count", "FAIL", 
                                    f"Expected at least 8 agents, got {total_agents}")
                        return False
                else:
                    self.log_test("Agent System - Endpoint", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    return False
                    
        except Exception as e:
            self.log_test("Agent System - Endpoint", "FAIL", f"Exception: {str(e)}")
            return False

    async def test_mongodb_connection(self):
        """Test MongoDB connection through various endpoints - Core requirement #5"""
        try:
            # Test 1: Health endpoint MongoDB status
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    mongodb_status = data.get("services", {}).get("mongodb")
                    if mongodb_status == "connected":
                        self.log_test("MongoDB Connection - Health Check", "PASS", 
                                    "MongoDB connection verified via health endpoint")
                    else:
                        self.log_test("MongoDB Connection - Health Check", "FAIL", 
                                    f"MongoDB status: {mongodb_status}")
                        return False
                else:
                    self.log_test("MongoDB Connection - Health Check", "FAIL", 
                                f"Health endpoint failed: HTTP {response.status}")
                    return False
            
            # Test 2: Try to access projects (requires MongoDB)
            async with self.session.get(f"{BACKEND_URL}/projects") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_test("MongoDB Connection - Projects Access", "PASS", 
                                    "MongoDB connection working - projects endpoint accessible")
                        return True
                    else:
                        self.log_test("MongoDB Connection - Projects Access", "FAIL", 
                                    "Projects endpoint returned invalid format")
                        return False
                else:
                    self.log_test("MongoDB Connection - Projects Access", "FAIL", 
                                f"Projects endpoint failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("MongoDB Connection - Overall", "FAIL", f"Exception: {str(e)}")
            return False

    async def run_verification_tests(self):
        """Run all verification tests"""
        print("🚀 Quick Verification Test - Xionimus AI Backend")
        print("Testing essential endpoints after UI redesign")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        results = {}
        
        print("1️⃣ Testing Health Check Endpoint...")
        results['health'] = await self.test_health_endpoint()
        
        print("2️⃣ Testing API Key Status Endpoint...")
        results['api_keys'] = await self.test_api_key_status()
        
        print("3️⃣ Testing Chat System...")
        results['chat'] = await self.test_chat_endpoint()
        
        print("4️⃣ Testing Agent System (8+ agents)...")
        results['agents'] = await self.test_agents_endpoint()
        
        print("5️⃣ Testing MongoDB Connection...")
        results['mongodb'] = await self.test_mongodb_connection()
        
        print("=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.upper()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL VERIFICATION TESTS PASSED")
            print("Backend functionality maintained after UI redesign")
            return True
        else:
            print("⚠️ SOME TESTS FAILED")
            print("Backend may have issues after UI redesign")
            return False

async def main():
    """Main test runner"""
    async with QuickVerificationTester() as tester:
        success = await tester.run_verification_tests()
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)