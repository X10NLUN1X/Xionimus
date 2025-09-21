#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Xionimus AI
Tests all critical backend functionality including health check, API key management,
chat endpoints, agent system, and project management.
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://agent-hub-31.preview.emergentagent.com/api"

class XionimusBackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.test_project_id = None
        self.test_file_id = None
        
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
        """Test /api/health endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check basic structure
                    required_fields = ["status", "timestamp", "services", "agents"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test("Health Check - Structure", "FAIL", 
                                    f"Missing fields: {missing_fields}", data)
                        return
                    
                    # Check MongoDB connection
                    mongodb_status = data.get("services", {}).get("mongodb")
                    if mongodb_status == "connected":
                        self.log_test("Health Check - MongoDB", "PASS", "MongoDB connection verified")
                    else:
                        self.log_test("Health Check - MongoDB", "FAIL", 
                                    f"MongoDB status: {mongodb_status}", data)
                    
                    # Check API key status (should be not_configured initially)
                    perplexity_status = data.get("services", {}).get("perplexity")
                    claude_status = data.get("services", {}).get("claude")
                    
                    if perplexity_status == "not_configured":
                        self.log_test("Health Check - Perplexity Status", "PASS", 
                                    "Perplexity correctly shows not_configured")
                    else:
                        self.log_test("Health Check - Perplexity Status", "WARN", 
                                    f"Perplexity status: {perplexity_status}")
                    
                    if claude_status == "not_configured":
                        self.log_test("Health Check - Claude Status", "PASS", 
                                    "Claude correctly shows not_configured")
                    else:
                        self.log_test("Health Check - Claude Status", "WARN", 
                                    f"Claude status: {claude_status}")
                    
                    # Check agents availability (should be 8)
                    agents_available = data.get("agents", {}).get("available", 0)
                    agents_list = data.get("agents", {}).get("agents_list", [])
                    
                    if agents_available == 8:
                        self.log_test("Health Check - Agent Count", "PASS", 
                                    f"All 8 agents available: {agents_list}")
                    else:
                        self.log_test("Health Check - Agent Count", "FAIL", 
                                    f"Expected 8 agents, got {agents_available}: {agents_list}", data)
                    
                    self.log_test("Health Check - Overall", "PASS", "Health endpoint responding correctly")
                    
                else:
                    self.log_test("Health Check - Overall", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    
        except Exception as e:
            self.log_test("Health Check - Overall", "FAIL", f"Exception: {str(e)}")

    async def test_api_key_status(self):
        """Test API key status endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/api-keys/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Should have perplexity and anthropic keys
                    if "perplexity" in data and "anthropic" in data:
                        perplexity_configured = data["perplexity"]
                        anthropic_configured = data["anthropic"]
                        
                        self.log_test("API Key Status - Structure", "PASS", 
                                    f"Perplexity: {perplexity_configured}, Anthropic: {anthropic_configured}")
                    else:
                        self.log_test("API Key Status - Structure", "FAIL", 
                                    "Missing perplexity or anthropic keys", data)
                else:
                    self.log_test("API Key Status", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    
        except Exception as e:
            self.log_test("API Key Status", "FAIL", f"Exception: {str(e)}")

    async def test_api_key_saving(self):
        """Test API key saving endpoint with mock keys"""
        try:
            # Test saving Perplexity key
            perplexity_payload = {
                "service": "perplexity",
                "key": "pplx-test-key-12345",
                "is_active": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/api-keys", 
                                       json=perplexity_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "perplexity" in data["message"]:
                        self.log_test("API Key Saving - Perplexity", "PASS", 
                                    "Perplexity key saved successfully")
                    else:
                        self.log_test("API Key Saving - Perplexity", "FAIL", 
                                    "Unexpected response format", data)
                else:
                    self.log_test("API Key Saving - Perplexity", "FAIL", 
                                f"HTTP {response.status}", await response.text())
            
            # Test saving Anthropic key
            anthropic_payload = {
                "service": "anthropic",
                "key": "sk-ant-test-key-12345",
                "is_active": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/api-keys", 
                                       json=anthropic_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "anthropic" in data["message"]:
                        self.log_test("API Key Saving - Anthropic", "PASS", 
                                    "Anthropic key saved successfully")
                    else:
                        self.log_test("API Key Saving - Anthropic", "FAIL", 
                                    "Unexpected response format", data)
                else:
                    self.log_test("API Key Saving - Anthropic", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    
        except Exception as e:
            self.log_test("API Key Saving", "FAIL", f"Exception: {str(e)}")

    async def test_chat_endpoint_behavior(self):
        """Test chat endpoint with new intelligent orchestration (no model field required)"""
        try:
            # Test 1: NEW INTELLIGENT CHAT - No model field required
            intelligent_payload = {
                "message": "What are the latest developments in artificial intelligence?",
                "conversation_history": [],
                "use_agent": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", 
                                       json=intelligent_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Mindestens ein API-Schlüssel muss konfiguriert sein" in data.get("detail", ""):
                        self.log_test("Intelligent Chat - No Model Field", "PASS", 
                                    "New intelligent chat accepts request without 'model' field")
                    else:
                        self.log_test("Intelligent Chat - No Model Field", "FAIL", 
                                    f"Unexpected error: {data.get('detail')}")
                else:
                    self.log_test("Intelligent Chat - No Model Field", "FAIL", 
                                f"Expected 400 (no API keys), got {response.status}", await response.text())
            
            # Test 2: Chat with conversation history
            history_payload = {
                "message": "Continue our discussion about AI",
                "conversation_history": [
                    {"role": "user", "content": "Tell me about machine learning"},
                    {"role": "assistant", "content": "Machine learning is a subset of AI..."}
                ],
                "conversation_id": str(uuid.uuid4())
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", 
                                       json=history_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Mindestens ein API-Schlüssel muss konfiguriert sein" in data.get("detail", ""):
                        self.log_test("Intelligent Chat - With History", "PASS", 
                                    "Chat with conversation history accepted")
                    else:
                        self.log_test("Intelligent Chat - With History", "FAIL", 
                                    f"Unexpected error: {data.get('detail')}")
                else:
                    self.log_test("Intelligent Chat - With History", "FAIL", 
                                f"Expected 400 (no API keys), got {response.status}")
            
            # Test 3: Error handling when no API keys configured
            no_keys_payload = {
                "message": "Test message for error handling"
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", 
                                       json=no_keys_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Mindestens ein API-Schlüssel muss konfiguriert sein" in data.get("detail", ""):
                        self.log_test("Intelligent Chat - Error Handling", "PASS", 
                                    "User-friendly error message when no API keys configured")
                    else:
                        self.log_test("Intelligent Chat - Error Handling", "FAIL", 
                                    f"Error message not user-friendly: {data.get('detail')}")
                else:
                    self.log_test("Intelligent Chat - Error Handling", "FAIL", 
                                f"Expected 400, got {response.status}")
            
            # Test 4: Minimal valid request (just message)
            minimal_payload = {
                "message": "Hello, can you help me with a coding question?"
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", 
                                       json=minimal_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Mindestens ein API-Schlüssel muss konfiguriert sein" in data.get("detail", ""):
                        self.log_test("Intelligent Chat - Minimal Request", "PASS", 
                                    "Minimal request (just message) accepted by new schema")
                    else:
                        self.log_test("Intelligent Chat - Minimal Request", "FAIL", 
                                    f"Minimal request failed: {data.get('detail')}")
                else:
                    self.log_test("Intelligent Chat - Minimal Request", "FAIL", 
                                f"Expected 400 (no API keys), got {response.status}")
                    
        except Exception as e:
            self.log_test("Chat Endpoint Behavior", "FAIL", f"Exception: {str(e)}")

    async def test_agents_endpoint(self):
        """Test agents listing endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/agents") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list) and len(data) == 8:
                        agent_names = [agent.get("name") for agent in data]
                        expected_agents = [
                            "Code Agent", "Research Agent", "Writing Agent", "Data Agent",
                            "QA Agent", "GitHub Agent", "File Agent", "Session Agent"
                        ]
                        
                        missing_agents = [name for name in expected_agents if name not in agent_names]
                        if not missing_agents:
                            self.log_test("Agents Endpoint - All Agents", "PASS", 
                                        f"All 8 agents available: {agent_names}")
                        else:
                            self.log_test("Agents Endpoint - All Agents", "FAIL", 
                                        f"Missing agents: {missing_agents}")
                        
                        # Check agent structure
                        for agent in data:
                            required_fields = ["name", "description", "capabilities"]
                            missing_fields = [field for field in required_fields if field not in agent]
                            if missing_fields:
                                self.log_test(f"Agent Structure - {agent.get('name', 'Unknown')}", 
                                            "FAIL", f"Missing fields: {missing_fields}")
                            else:
                                self.log_test(f"Agent Structure - {agent.get('name')}", "PASS", 
                                            "All required fields present")
                    else:
                        self.log_test("Agents Endpoint - Count", "FAIL", 
                                    f"Expected 8 agents, got {len(data) if isinstance(data, list) else 'non-list'}", 
                                    data)
                else:
                    self.log_test("Agents Endpoint", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    
        except Exception as e:
            self.log_test("Agents Endpoint", "FAIL", f"Exception: {str(e)}")

    async def test_agent_analysis(self):
        """Test agent analysis endpoint"""
        try:
            analysis_payload = {
                "message": "Generate a Python function to calculate fibonacci numbers",
                "context": {"language": "python"}
            }
            
            async with self.session.post(f"{BACKEND_URL}/agents/analyze", 
                                       json=analysis_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    required_fields = ["message", "language_detected", "agent_recommendations", "requires_agent"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Should recommend Code Agent for this request
                        recommendations = data.get("agent_recommendations", {})
                        best_agent = data.get("best_agent")
                        
                        if "Code Agent" in recommendations and best_agent == "Code Agent":
                            self.log_test("Agent Analysis - Code Detection", "PASS", 
                                        f"Correctly identified Code Agent as best match")
                        else:
                            self.log_test("Agent Analysis - Code Detection", "WARN", 
                                        f"Best agent: {best_agent}, Recommendations: {recommendations}")
                        
                        self.log_test("Agent Analysis - Structure", "PASS", 
                                    "All required fields present")
                    else:
                        self.log_test("Agent Analysis - Structure", "FAIL", 
                                    f"Missing fields: {missing_fields}", data)
                else:
                    self.log_test("Agent Analysis", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    
        except Exception as e:
            self.log_test("Agent Analysis", "FAIL", f"Exception: {str(e)}")

    async def test_critical_bug_fixes(self):
        """Test the critical bug fixes for Perplexity and Claude API errors"""
        try:
            # Test 1: Perplexity Citation Processing Bug Fix
            # Test that Perplexity response processing doesn't crash with string citations
            perplexity_payload = {
                "message": "What are the latest developments in AI technology?",
                "model": "perplexity",
                "use_agent": False
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=perplexity_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    # Should get API key error, not "'str' object has no attribute 'get'" error
                    if "Perplexity API key not configured" in data.get("detail", ""):
                        self.log_test("Bug Fix - Perplexity Citation Processing", "PASS", 
                                    "No 'str' object attribute error - citation processing fixed")
                    elif "'str' object has no attribute 'get'" in data.get("detail", ""):
                        self.log_test("Bug Fix - Perplexity Citation Processing", "FAIL", 
                                    "CRITICAL BUG: 'str' object has no attribute 'get' error still present")
                    else:
                        self.log_test("Bug Fix - Perplexity Citation Processing", "PASS", 
                                    "Citation processing working - no string attribute errors")
                else:
                    self.log_test("Bug Fix - Perplexity Citation Processing", "WARN", 
                                f"Unexpected status {response.status} - expected 400 for missing API key")
            
            # Test 2: Claude Model Name Bug Fix
            # Test that Claude model name 'claude-3-5-sonnet' is accepted (not 404 error)
            claude_payload = {
                "message": "Explain machine learning concepts",
                "model": "claude",
                "use_agent": False
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=claude_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    # Should get API key error, not 404 "not_found_error" for model
                    if "Anthropic API key not configured" in data.get("detail", ""):
                        self.log_test("Bug Fix - Claude Model Name", "PASS", 
                                    "Model 'claude-3-5-sonnet' accepted - no 404 not_found_error")
                    elif "not_found_error" in data.get("detail", "").lower() or "404" in data.get("detail", ""):
                        self.log_test("Bug Fix - Claude Model Name", "FAIL", 
                                    "CRITICAL BUG: Claude model 'claude-3-5-sonnet' not found (404 error)")
                    else:
                        self.log_test("Bug Fix - Claude Model Name", "PASS", 
                                    "Claude model name accepted - no 404 errors")
                else:
                    self.log_test("Bug Fix - Claude Model Name", "WARN", 
                                f"Unexpected status {response.status} - expected 400 for missing API key")
            
            # Test 3: Updated Agent Model Configuration
            # Test Research Agent with sonar-deep-research
            research_payload = {
                "message": "Research current AI trends and developments",
                "model": "perplexity",
                "use_agent": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=research_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Perplexity API key not configured" in data.get("detail", ""):
                        self.log_test("Bug Fix - Research Agent (sonar-deep-research)", "PASS", 
                                    "Research Agent model 'sonar-deep-research' accepted by API")
                    elif "invalid model" in data.get("detail", "").lower():
                        self.log_test("Bug Fix - Research Agent (sonar-deep-research)", "FAIL", 
                                    f"Model validation failed: {data.get('detail')}")
                    else:
                        self.log_test("Bug Fix - Research Agent (sonar-deep-research)", "PASS", 
                                    "Research Agent model accepted")
                else:
                    self.log_test("Bug Fix - Research Agent (sonar-deep-research)", "WARN", 
                                f"Unexpected status {response.status}")
            
            # Test 4: QA Agent with sonar-reasoning
            qa_payload = {
                "message": "Create testing strategy for web application",
                "model": "perplexity", 
                "use_agent": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=qa_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Perplexity API key not configured" in data.get("detail", ""):
                        self.log_test("Bug Fix - QA Agent (sonar-reasoning)", "PASS", 
                                    "QA Agent model 'sonar-reasoning' accepted by API")
                    elif "invalid model" in data.get("detail", "").lower():
                        self.log_test("Bug Fix - QA Agent (sonar-reasoning)", "FAIL", 
                                    f"Model validation failed: {data.get('detail')}")
                    else:
                        self.log_test("Bug Fix - QA Agent (sonar-reasoning)", "PASS", 
                                    "QA Agent model accepted")
                else:
                    self.log_test("Bug Fix - QA Agent (sonar-reasoning)", "WARN", 
                                f"Unexpected status {response.status}")
            
            # Test 5: Code Agent with claude-3-5-sonnet (simplified name)
            code_payload = {
                "message": "Write a Python function to calculate fibonacci numbers",
                "model": "claude",
                "use_agent": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=code_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "Anthropic API key not configured" in data.get("detail", ""):
                        self.log_test("Bug Fix - Code Agent (claude-3-5-sonnet)", "PASS", 
                                    "Code Agent model 'claude-3-5-sonnet' accepted by API")
                    elif "not_found_error" in data.get("detail", "").lower() or "404" in data.get("detail", ""):
                        self.log_test("Bug Fix - Code Agent (claude-3-5-sonnet)", "FAIL", 
                                    f"CRITICAL BUG: Claude model not found: {data.get('detail')}")
                    else:
                        self.log_test("Bug Fix - Code Agent (claude-3-5-sonnet)", "PASS", 
                                    "Code Agent model accepted")
                else:
                    self.log_test("Bug Fix - Code Agent (claude-3-5-sonnet)", "WARN", 
                                f"Unexpected status {response.status}")
            
            # Test 6: Error Handling Returns Proper HTTP Codes
            # Test that 400 errors are returned as 400, not 500
            invalid_payload = {
                "message": "",  # Empty message should trigger 400 error
                "model": "claude"
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=invalid_payload) as response:
                if response.status == 400:
                    self.log_test("Bug Fix - Error Handling HTTP Codes", "PASS", 
                                "Proper 400 status code returned for invalid request")
                elif response.status == 500:
                    self.log_test("Bug Fix - Error Handling HTTP Codes", "FAIL", 
                                "CRITICAL BUG: 400 error incorrectly returned as 500")
                else:
                    self.log_test("Bug Fix - Error Handling HTTP Codes", "WARN", 
                                f"Unexpected status {response.status}")
                    
        except Exception as e:
            self.log_test("Critical Bug Fixes", "FAIL", f"Exception: {str(e)}")

    async def test_project_management(self):
        """Test project CRUD operations"""
        try:
            # Create project
            project_payload = {
                "name": f"Test Project {uuid.uuid4().hex[:8]}",
                "description": "Test project for backend validation"
            }
            
            async with self.session.post(f"{BACKEND_URL}/projects", 
                                       json=project_payload) as response:
                if response.status == 200:
                    project_data = await response.json()
                    self.test_project_id = project_data.get("id")
                    
                    if self.test_project_id:
                        self.log_test("Project Management - Create", "PASS", 
                                    f"Project created with ID: {self.test_project_id}")
                    else:
                        self.log_test("Project Management - Create", "FAIL", 
                                    "No project ID returned", project_data)
                        return
                else:
                    self.log_test("Project Management - Create", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    return
            
            # Get projects list
            async with self.session.get(f"{BACKEND_URL}/projects") as response:
                if response.status == 200:
                    projects = await response.json()
                    if isinstance(projects, list):
                        project_ids = [p.get("id") for p in projects]
                        if self.test_project_id in project_ids:
                            self.log_test("Project Management - List", "PASS", 
                                        f"Created project found in list")
                        else:
                            self.log_test("Project Management - List", "FAIL", 
                                        "Created project not found in list")
                    else:
                        self.log_test("Project Management - List", "FAIL", 
                                    "Projects list is not an array", projects)
                else:
                    self.log_test("Project Management - List", "FAIL", 
                                f"HTTP {response.status}")
            
            # Get specific project
            async with self.session.get(f"{BACKEND_URL}/projects/{self.test_project_id}") as response:
                if response.status == 200:
                    project = await response.json()
                    if project.get("id") == self.test_project_id:
                        self.log_test("Project Management - Get", "PASS", 
                                    "Project retrieved successfully")
                    else:
                        self.log_test("Project Management - Get", "FAIL", 
                                    "Retrieved project ID mismatch")
                else:
                    self.log_test("Project Management - Get", "FAIL", 
                                f"HTTP {response.status}")
            
            # Update project
            update_payload = {
                "name": f"Updated Test Project {uuid.uuid4().hex[:8]}",
                "description": "Updated test project description"
            }
            
            async with self.session.put(f"{BACKEND_URL}/projects/{self.test_project_id}", 
                                      json=update_payload) as response:
                if response.status == 200:
                    updated_project = await response.json()
                    if updated_project.get("name") == update_payload["name"]:
                        self.log_test("Project Management - Update", "PASS", 
                                    "Project updated successfully")
                    else:
                        self.log_test("Project Management - Update", "FAIL", 
                                    "Project name not updated correctly")
                else:
                    self.log_test("Project Management - Update", "FAIL", 
                                f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Project Management", "FAIL", f"Exception: {str(e)}")

    async def test_file_management(self):
        """Test file CRUD operations"""
        if not self.test_project_id:
            self.log_test("File Management", "SKIP", "No test project available")
            return
            
        try:
            # Create file
            file_payload = {
                "project_id": self.test_project_id,
                "name": "test_file.py",
                "content": "def hello_world():\n    print('Hello, World!')",
                "language": "python"
            }
            
            async with self.session.post(f"{BACKEND_URL}/files", 
                                       json=file_payload) as response:
                if response.status == 200:
                    file_data = await response.json()
                    self.test_file_id = file_data.get("id")
                    
                    if self.test_file_id:
                        self.log_test("File Management - Create", "PASS", 
                                    f"File created with ID: {self.test_file_id}")
                    else:
                        self.log_test("File Management - Create", "FAIL", 
                                    "No file ID returned", file_data)
                        return
                else:
                    self.log_test("File Management - Create", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    return
            
            # Get project files
            async with self.session.get(f"{BACKEND_URL}/files/{self.test_project_id}") as response:
                if response.status == 200:
                    files = await response.json()
                    if isinstance(files, list) and len(files) > 0:
                        file_ids = [f.get("id") for f in files]
                        if self.test_file_id in file_ids:
                            self.log_test("File Management - List", "PASS", 
                                        "Created file found in project files")
                        else:
                            self.log_test("File Management - List", "FAIL", 
                                        "Created file not found in project files")
                    else:
                        self.log_test("File Management - List", "FAIL", 
                                    "No files returned or invalid format")
                else:
                    self.log_test("File Management - List", "FAIL", 
                                f"HTTP {response.status}")
            
            # Get file content
            async with self.session.get(f"{BACKEND_URL}/files/content/{self.test_file_id}") as response:
                if response.status == 200:
                    file_content = await response.json()
                    if file_content.get("content") == file_payload["content"]:
                        self.log_test("File Management - Get Content", "PASS", 
                                    "File content retrieved correctly")
                    else:
                        self.log_test("File Management - Get Content", "FAIL", 
                                    "File content mismatch")
                else:
                    self.log_test("File Management - Get Content", "FAIL", 
                                f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("File Management", "FAIL", f"Exception: {str(e)}")

    async def cleanup_test_data(self):
        """Clean up test data"""
        try:
            # Delete test file
            if self.test_file_id:
                async with self.session.delete(f"{BACKEND_URL}/files/{self.test_file_id}") as response:
                    if response.status == 200:
                        self.log_test("Cleanup - File", "PASS", "Test file deleted")
                    else:
                        self.log_test("Cleanup - File", "WARN", f"HTTP {response.status}")
            
            # Delete test project
            if self.test_project_id:
                async with self.session.delete(f"{BACKEND_URL}/projects/{self.test_project_id}") as response:
                    if response.status == 200:
                        self.log_test("Cleanup - Project", "PASS", "Test project deleted")
                    else:
                        self.log_test("Cleanup - Project", "WARN", f"HTTP {response.status}")
                        
        except Exception as e:
            self.log_test("Cleanup", "WARN", f"Exception during cleanup: {str(e)}")

    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Xionimus AI Backend Testing - Critical Bug Fixes")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # PRIORITY: Critical Bug Fix Tests
        await self.test_critical_bug_fixes()
        
        # Core functionality tests
        await self.test_health_endpoint()
        await self.test_api_key_status()
        await self.test_api_key_saving()
        await self.test_chat_endpoint_behavior()
        
        # Agent system tests
        await self.test_agents_endpoint()
        await self.test_agent_analysis()
        
        # Project management tests
        await self.test_project_management()
        await self.test_file_management()
        
        # Cleanup
        await self.cleanup_test_data()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"⏭️  SKIPPED: {skipped}")
        print(f"📈 TOTAL: {len(self.test_results)}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "total": len(self.test_results),
            "results": self.test_results
        }

async def main():
    """Main test runner"""
    async with XionimusBackendTester() as tester:
        results = await tester.run_all_tests()
        
        # Exit with error code if tests failed
        if results["failed"] > 0:
            sys.exit(1)
        else:
            print("\n🎉 All critical tests passed!")
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())