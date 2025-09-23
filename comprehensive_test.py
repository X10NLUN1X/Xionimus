#!/usr/bin/env python3
"""
Comprehensive Testing and Debugging Script for XIONIMUS AI
Tests the complete system including MongoDB, APIs, agents, and emergent app creation capabilities
"""

import asyncio
import requests
import json
import time
from typing import Dict, Any, List
import sys
import os

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class XionimusTestSuite:
    def __init__(self):
        self.test_results = []
        self.project_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        if response_data and success:
            print(f"    📊 Response: {json.dumps(response_data, indent=2)[:200]}...")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data
        })
    
    def test_backend_health(self):
        """Test backend health and connectivity"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Root Endpoint", True, 
                             f"Version: {data.get('version')}, Status: {data.get('status')}", data)
            else:
                self.log_test("Backend Root Endpoint", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Backend Root Endpoint", False, f"Connection error: {e}")
    
    def test_health_endpoint(self):
        """Test comprehensive health check"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                mongodb_ok = data.get('services', {}).get('mongodb') == 'connected'
                agents_count = data.get('agents', {}).get('available', 0)
                
                details = f"MongoDB: {data.get('services', {}).get('mongodb')}, Agents: {agents_count}"
                self.log_test("Health Check", mongodb_ok and agents_count == 8, details, data)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {e}")
    
    def test_agents_list(self):
        """Test agents endpoint and validate all agents are loaded"""
        try:
            response = requests.get(f"{API_BASE}/agents", timeout=5)
            if response.status_code == 200:
                agents = response.json()
                expected_agents = [
                    "Code Agent", "Research Agent", "Writing Agent", "Data Agent",
                    "QA Agent", "GitHub Agent", "File Agent", "Session Agent"
                ]
                
                agent_names = [agent['name'] for agent in agents]
                missing_agents = set(expected_agents) - set(agent_names)
                
                if not missing_agents and len(agents) == 8:
                    self.log_test("Agents System", True, f"All {len(agents)} agents loaded", agent_names)
                else:
                    self.log_test("Agents System", False, f"Missing agents: {missing_agents}")
            else:
                self.log_test("Agents System", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Agents System", False, f"Error: {e}")
    
    def test_api_keys_status(self):
        """Test API keys status endpoint"""
        try:
            response = requests.get(f"{API_BASE}/api-keys/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                mongodb_connected = data.get('mongodb_connection') == 'connected'
                total_services = data.get('total_services', 0)
                
                details = f"Services: {total_services}, MongoDB: {data.get('mongodb_connection')}"
                self.log_test("API Keys Management", mongodb_connected and total_services == 3, details, data)
            else:
                self.log_test("API Keys Management", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API Keys Management", False, f"Error: {e}")
    
    def test_project_creation(self):
        """Test emergent app creation via project system"""
        try:
            # Create a test project
            project_data = {
                "name": "Emergent Test App",
                "description": "Testing emergent app creation with multiple AI agents and capabilities"
            }
            
            response = requests.post(f"{API_BASE}/projects", 
                                   json=project_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                project = response.json()
                self.project_id = project.get('id')
                
                # Verify project has required fields
                has_required_fields = all(key in project for key in ['id', 'name', 'description', 'created_at'])
                
                details = f"Project ID: {self.project_id[:8]}..., Name: {project.get('name')}"
                self.log_test("Emergent App Creation", has_required_fields, details, project)
            else:
                self.log_test("Emergent App Creation", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Emergent App Creation", False, f"Error: {e}")
    
    def test_local_storage_persistence(self):
        """Test Local Storage persistence by retrieving projects"""
        try:
            response = requests.get(f"{API_BASE}/projects", timeout=5)
            if response.status_code == 200:
                projects = response.json()
                
                # Check if our created project exists
                project_exists = any(p.get('id') == self.project_id for p in projects) if self.project_id else False
                
                details = f"Total projects: {len(projects)}, Test project exists: {project_exists}"
                self.log_test("Local Storage Data Persistence", len(projects) > 0 and project_exists, details)
            else:
                self.log_test("Local Storage Data Persistence", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Local Storage Data Persistence", False, f"Error: {e}")
    
    def test_code_generation_api(self):
        """Test code generation endpoint (should fail without API keys)"""
        try:
            code_request = {
                "prompt": "Create a simple Flask API with user authentication",
                "language": "python",
                "model": "claude-sonnet-4"
            }
            
            response = requests.post(f"{API_BASE}/generate-code", 
                                   json=code_request,
                                   timeout=10)
            
            # We expect this to fail with 400 due to missing API keys
            if response.status_code == 400:
                error_data = response.json()
                has_api_key_error = "API" in error_data.get('detail', '') or "Schlüssel" in error_data.get('detail', '')
                
                self.log_test("Code Generation API", has_api_key_error, 
                             f"Correctly rejects requests without API keys: {error_data.get('detail', '')[:50]}...")
            else:
                self.log_test("Code Generation API", False, 
                             f"Expected HTTP 400 for missing API keys, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Code Generation API", False, f"Error: {e}")
    
    def test_chat_api(self):
        """Test chat endpoint (should fail without API keys)"""
        try:
            chat_request = {
                "message": "Hello, can you help me create a web application?",
                "conversation_id": "test-conversation",
                "language": "de"
            }
            
            response = requests.post(f"{API_BASE}/chat",
                                   json=chat_request,
                                   timeout=10)
            
            # We expect this to fail due to missing API keys
            if response.status_code == 400:
                error_data = response.json()
                has_api_key_error = "API" in error_data.get('detail', '') or "Schlüssel" in error_data.get('detail', '')
                
                self.log_test("Chat API", has_api_key_error,
                             f"Correctly rejects chat without API keys: {error_data.get('detail', '')[:50]}...")
            else:
                self.log_test("Chat API", False,
                             f"Expected HTTP 400 for missing API keys, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Chat API", False, f"Error: {e}")
    
    def test_file_upload_api(self):
        """Test file upload capability"""
        try:
            if not self.project_id:
                self.log_test("File Upload API", False, "No project ID available for testing")
                return
            
            # Create a simple test file
            test_content = "# Test File\nprint('Hello from emergent app!')\n"
            files = {'file': ('test.py', test_content, 'text/plain')}
            data = {'project_id': self.project_id}
            
            response = requests.post(f"{API_BASE}/files",
                                   files=files,
                                   data=data,
                                   timeout=10)
            
            if response.status_code == 200:
                file_data = response.json()
                self.log_test("File Upload API", True, 
                             f"File uploaded: {file_data.get('filename')}", file_data)
            else:
                self.log_test("File Upload API", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("File Upload API", False, f"Error: {e}")
    
    def test_mongodb_collections(self):
        """Test MongoDB collections via debug endpoint"""
        try:
            response = requests.get(f"{API_BASE}/api-keys/debug", timeout=5)
            if response.status_code == 200:
                debug_data = response.json()
                self.log_test("MongoDB Debug Info", True, 
                             "MongoDB debug endpoint accessible", debug_data)
            else:
                self.log_test("MongoDB Debug Info", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("MongoDB Debug Info", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive XIONIMUS AI Test Suite")
        print("=" * 60)
        print()
        
        # Core system tests
        print("📋 CORE SYSTEM TESTS")
        print("-" * 30)
        self.test_backend_health()
        self.test_health_endpoint()
        
        # Local Storage and persistence tests
        print("🏠 LOCAL STORAGE TESTS")
        print("-" * 30)
        self.test_local_storage_persistence()
        
        # Agent system tests
        print("🤖 AGENT SYSTEM TESTS")
        print("-" * 30)
        self.test_agents_list()
        
        # API key management tests
        print("🔑 API KEY MANAGEMENT TESTS")
        print("-" * 30)
        self.test_api_keys_status()
        
        # Emergent app creation tests
        print("🌟 EMERGENT APP CREATION TESTS")
        print("-" * 30)
        self.test_project_creation()
        self.test_local_storage_persistence()
        
        # AI functionality tests
        print("🧠 AI FUNCTIONALITY TESTS")
        print("-" * 30)
        self.test_code_generation_api()
        self.test_chat_api()
        
        # File management tests
        print("📁 FILE MANAGEMENT TESTS")
        print("-" * 30)
        self.test_file_upload_api()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if total - passed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\n🎯 SYSTEM STATUS:")
        if passed >= total * 0.8:  # 80% success rate
            print("  🟢 System is functioning well!")
            print("  📝 Ready for emergent app creation with AI agents")
            print("  🔧 Add API keys to enable full AI functionality")
        else:
            print("  🟡 System has some issues that need attention")
            print("  🔧 Check failed tests above for troubleshooting")

if __name__ == "__main__":
    # Check if backend is running
    try:
        requests.get(BACKEND_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running on http://localhost:8001")
        print("💡 Start the backend first: cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload")
        sys.exit(1)
    
    # Run tests
    test_suite = XionimusTestSuite()
    test_suite.run_all_tests()