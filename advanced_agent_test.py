#!/usr/bin/env python3
"""
Advanced Agent Integration Testing
Tests complex agent interactions, error handling, and edge cases
"""

import asyncio
import requests
import json
import sys
import time
from typing import Dict, Any, List
from datetime import datetime

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class AdvancedAgentTests:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
    
    def test_agent_error_recovery(self):
        """Test how agents handle invalid inputs and recover from errors"""
        
        # Test with empty message
        try:
            response = requests.post(f"{API_BASE}/chat", json={
                "message": "",
                "conversation_id": "test-error"
            }, timeout=30)
            
            # Should still work (graceful handling of empty input)
            success = response.status_code == 200 or response.status_code == 400
            self.log_test("Agent Error Recovery - Empty Input", success, 
                         f"Status: {response.status_code}, handled gracefully")
        except Exception as e:
            self.log_test("Agent Error Recovery - Empty Input", False, f"Error: {e}")
    
    def test_agent_context_handling(self):
        """Test how agents handle context and conversation history"""
        
        try:
            # First message
            response1 = requests.post(f"{API_BASE}/chat", json={
                "message": "Create a Python function called fibonacci",
                "conversation_id": "test-context"
            }, timeout=30)
            
            if response1.status_code == 200:
                # Follow-up message with context
                response2 = requests.post(f"{API_BASE}/chat", json={
                    "message": "Now add error handling to that function",
                    "conversation_id": "test-context"
                }, timeout=30)
                
                success = response2.status_code == 200
                result = response2.json() if success else {}
                content_length = len(result.get('message', {}).get('content', ''))
                
                self.log_test("Agent Context Handling", success and content_length > 50,
                             f"Context preserved, response length: {content_length} chars")
            else:
                self.log_test("Agent Context Handling", False, f"First request failed: {response1.status_code}")
                
        except Exception as e:
            self.log_test("Agent Context Handling", False, f"Error: {e}")
    
    def test_agent_concurrent_requests(self):
        """Test how the system handles concurrent agent requests"""
        
        import threading
        import time
        
        results = []
        
        def make_request(i):
            try:
                response = requests.post(f"{API_BASE}/chat", json={
                    "message": f"Generate a simple comment: Test {i}",
                    "conversation_id": f"concurrent-{i}"
                }, timeout=45)
                results.append({
                    "id": i,
                    "status": response.status_code,
                    "success": response.status_code == 200
                })
            except Exception as e:
                results.append({
                    "id": i,
                    "status": "error",
                    "success": False,
                    "error": str(e)
                })
        
        # Create 3 concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        successful_requests = len([r for r in results if r['success']])
        
        self.log_test("Agent Concurrent Requests", successful_requests >= 2,
                     f"Successful concurrent requests: {successful_requests}/3")
    
    def test_agent_memory_and_state(self):
        """Test agent memory and state management"""
        
        try:
            # Create a conversation with specific context
            response = requests.post(f"{API_BASE}/chat", json={
                "message": "My name is Alice and I'm working on a Python project",
                "conversation_id": "memory-test"
            }, timeout=30)
            
            if response.status_code == 200:
                # Test if agent remembers the context
                response2 = requests.post(f"{API_BASE}/chat", json={
                    "message": "What was my name again?",
                    "conversation_id": "memory-test"  # Same conversation
                }, timeout=30)
                
                success = response2.status_code == 200
                if success:
                    content = response2.json().get('message', {}).get('content', '').lower()
                    has_name = 'alice' in content
                    self.log_test("Agent Memory & State", has_name,
                                 f"Agent {'remembered' if has_name else 'did not remember'} the name Alice")
                else:
                    self.log_test("Agent Memory & State", False, f"Second request failed: {response2.status_code}")
            else:
                self.log_test("Agent Memory & State", False, f"First request failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Agent Memory & State", False, f"Error: {e}")
    
    def test_agent_multilingual_support(self):
        """Test agent support for multiple languages"""
        
        test_cases = [
            {"message": "Hallo, können Sie mir helfen?", "language": "German"},
            {"message": "Bonjour, pouvez-vous m'aider?", "language": "French"},
            {"message": "Hola, ¿puedes ayudarme?", "language": "Spanish"}
        ]
        
        successful = 0
        
        for test_case in test_cases:
            try:
                response = requests.post(f"{API_BASE}/chat", json={
                    "message": test_case["message"],
                    "conversation_id": f"lang-test-{test_case['language'].lower()}"
                }, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    language_detected = result.get('language_detected')
                    
                    # Check if language was detected (even if not perfectly)
                    if language_detected:
                        successful += 1
                        
            except Exception:
                continue
        
        self.log_test("Agent Multilingual Support", successful >= 2,
                     f"Successfully handled {successful}/3 different languages")
    
    def test_agent_file_integration(self):
        """Test agent integration with file operations"""
        
        # First create a project for file testing
        try:
            project_response = requests.post(f"{API_BASE}/projects", json={
                "name": "Agent File Test",
                "description": "Testing agent file integration"
            }, timeout=10)
            
            if project_response.status_code == 200:
                project_id = project_response.json().get('id')
                
                # Upload a test file
                test_content = "def hello_world():\n    print('Hello from agent test!')\n"
                files = {'file': ('test_agent.py', test_content, 'text/plain')}
                data = {'project_id': project_id}
                
                file_response = requests.post(f"{API_BASE}/files", files=files, data=data, timeout=10)
                
                success = file_response.status_code == 200
                if success:
                    file_data = file_response.json()
                    filename = file_data.get('filename')
                
                self.log_test("Agent File Integration", success,
                             f"File operations working: {filename if success else 'Failed'}")
            else:
                self.log_test("Agent File Integration", False, f"Project creation failed: {project_response.status_code}")
                
        except Exception as e:
            self.log_test("Agent File Integration", False, f"Error: {e}")
    
    def test_agent_performance_monitoring(self):
        """Test agent performance monitoring and metrics"""
        
        try:
            start_time = time.time()
            
            response = requests.post(f"{API_BASE}/chat", json={
                "message": "Write a short comment about performance",
                "conversation_id": "perf-test"
            }, timeout=30)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response.status_code == 200 and response_time < 25.0
            
            self.log_test("Agent Performance Monitoring", success,
                         f"Response time: {response_time:.2f}s (threshold: 25s)")
                         
        except Exception as e:
            self.log_test("Agent Performance Monitoring", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all advanced agent tests"""
        print("🚀 ADVANCED AGENT INTEGRATION TESTING")
        print("=" * 70)
        print(f"🕒 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()
        
        print("⚡ ERROR RECOVERY & RESILIENCE")
        print("-" * 40)
        self.test_agent_error_recovery()
        
        print("🧠 CONTEXT & MEMORY MANAGEMENT")
        print("-" * 40)
        self.test_agent_context_handling()
        self.test_agent_memory_and_state()
        
        print("⚙️ PERFORMANCE & CONCURRENCY")
        print("-" * 40)
        self.test_agent_concurrent_requests()
        self.test_agent_performance_monitoring()
        
        print("🌍 ADVANCED FEATURES")
        print("-" * 40)
        self.test_agent_multilingual_support()
        self.test_agent_file_integration()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 70)
        print("📊 ADVANCED AGENT TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print()
        if success_rate >= 85:
            print("🎯 ADVANCED AGENT STATUS: ✅ Excellent - Advanced features working well")
        elif success_rate >= 70:
            print("🎯 ADVANCED AGENT STATUS: 🟡 Good - Most advanced features functional")
        elif success_rate >= 50:
            print("🎯 ADVANCED AGENT STATUS: 🟠 Needs Attention - Some advanced issues")
        else:
            print("🎯 ADVANCED AGENT STATUS: 🔴 Critical - Major advanced feature problems")
        
        print("=" * 70)


if __name__ == "__main__":
    # Check if backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server is not responding properly")
            sys.exit(1)
    except:
        print("❌ Backend server is not running")
        sys.exit(1)
    
    # Run tests
    test_suite = AdvancedAgentTests()
    test_suite.run_all_tests()