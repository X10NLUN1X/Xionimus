#!/usr/bin/env python3
"""
Comprehensive Agent Test Suite for XIONIMUS AI
Tests all 8 specialized agents to verify their capabilities:
- Code Agent: Programming, debugging, code analysis
- Research Agent: Web research, current information
- Writing Agent: Documentation, content creation
- Data Agent: Data analysis, visualization
- QA Agent: Testing, quality assurance
- GitHub Agent: Repository management, version control
- File Agent: File upload/management, organization
- Session Agent: Session fork/backup, state management
"""

import asyncio
import aiohttp
import json
import time
import uuid
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class AgentTestSuite:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.project_id = None
        self.test_data = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, agent_name: str, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results with rich formatting"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"{status} [{timestamp}] {agent_name} - {test_name}")
        if details:
            print(f"    📋 {details}")
        if data and success:
            if isinstance(data, dict) and len(str(data)) > 200:
                print(f"    📊 Response: {str(data)[:200]}...")
            else:
                print(f"    📊 Data: {data}")
        print()
        
        self.test_results.append({
            'agent': agent_name,
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': timestamp,
            'data': data
        })

    async def test_system_health(self):
        """Test overall system health before agent testing"""
        print("\n🏥 SYSTEM HEALTH CHECK")
        print("=" * 60)
        
        try:
            # Test backend connectivity
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("System", "Backend Connectivity", True, 
                                f"Version: {data.get('version', 'unknown')}")
                else:
                    self.log_test("System", "Backend Connectivity", False, f"HTTP {response.status}")
                    return False
                    
            # Test health endpoint
            async with self.session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    mongodb_ok = data.get('services', {}).get('mongodb') == 'connected'
                    agents_count = data.get('agents', {}).get('available', 0)
                    self.log_test("System", "Health Check", mongodb_ok and agents_count >= 8, 
                                f"MongoDB: {data.get('services', {}).get('mongodb')}, Agents: {agents_count}")
                else:
                    self.log_test("System", "Health Check", False, f"HTTP {response.status}")
                    
            # Test agents endpoint
            async with self.session.get(f"{API_BASE}/agents") as response:
                if response.status == 200:
                    agents = await response.json()
                    expected_agents = [
                        "Code Agent", "Research Agent", "Writing Agent", "Data Agent",
                        "QA Agent", "GitHub Agent", "File Agent", "Session Agent"
                    ]
                    agent_names = [agent['name'] for agent in agents if isinstance(agent, dict)]
                    missing = set(expected_agents) - set(agent_names)
                    self.log_test("System", "Agents Available", len(missing) == 0,
                                f"Found: {len(agent_names)}, Missing: {list(missing) if missing else 'None'}")
                else:
                    self.log_test("System", "Agents Available", False, f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("System", "Health Check", False, f"Error: {str(e)}")
            return False
            
        return True

    async def test_code_agent(self):
        """Test Code Agent capabilities"""
        print("\n💻 CODE AGENT TESTS")
        print("=" * 60)
        
        # Test 1: Simple code generation
        test_prompt = "Create a simple Python function that calculates the factorial of a number"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": test_prompt,
                "agent_preference": "code"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_code = 'def' in content and 'factorial' in content
                    self.log_test("Code Agent", "Code Generation", has_code,
                                f"Generated {len(content)} characters")
                else:
                    self.log_test("Code Agent", "Code Generation", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Code Agent", "Code Generation", False, f"Error: {str(e)}")
            
        # Test 2: Code analysis request
        analysis_prompt = "Analyze this Python code for potential issues: def calc(x): return x/0"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": analysis_prompt,
                "agent_preference": "code"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '').lower()
                    has_analysis = any(word in content for word in ['division', 'zero', 'error', 'exception'])
                    self.log_test("Code Agent", "Code Analysis", has_analysis,
                                "Detected division by zero issue" if has_analysis else "No analysis found")
                else:
                    self.log_test("Code Agent", "Code Analysis", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Code Agent", "Code Analysis", False, f"Error: {str(e)}")

    async def test_research_agent(self):
        """Test Research Agent capabilities"""
        print("\n🔍 RESEARCH AGENT TESTS")
        print("=" * 60)
        
        # Test 1: Research query
        research_prompt = "What are the latest trends in AI development for 2024?"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": research_prompt,
                "agent_preference": "research"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_research = len(content) > 100 and any(word in content.lower() for word in ['ai', 'artificial', 'intelligence', '2024'])
                    self.log_test("Research Agent", "Web Research", has_research,
                                f"Generated {len(content)} characters of research")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("Research Agent", "Web Research", False, error_msg)
        except Exception as e:
            self.log_test("Research Agent", "Web Research", False, f"Error: {str(e)}")
            
        # Test 2: Current information request
        current_info_prompt = "Find information about the latest Python version and its features"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": current_info_prompt,
                "agent_preference": "research"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_info = 'python' in content.lower() and len(content) > 50
                    self.log_test("Research Agent", "Current Information", has_info,
                                f"Found Python information ({len(content)} chars)")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("Research Agent", "Current Information", False, error_msg)
        except Exception as e:
            self.log_test("Research Agent", "Current Information", False, f"Error: {str(e)}")

    async def test_writing_agent(self):
        """Test Writing Agent capabilities"""
        print("\n✍️ WRITING AGENT TESTS")
        print("=" * 60)
        
        # Test 1: Documentation writing
        doc_prompt = "Write documentation for a simple todo application API"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": doc_prompt,
                "agent_preference": "writing"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_doc = len(content) > 200 and any(word in content.lower() for word in ['api', 'todo', 'endpoint'])
                    self.log_test("Writing Agent", "Documentation", has_doc,
                                f"Generated {len(content)} characters of documentation")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("Writing Agent", "Documentation", False, error_msg)
        except Exception as e:
            self.log_test("Writing Agent", "Documentation", False, f"Error: {str(e)}")
            
        # Test 2: Content creation
        content_prompt = "Create a brief introduction to machine learning for beginners"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": content_prompt,
                "agent_preference": "writing"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_content = len(content) > 150 and 'machine learning' in content.lower()
                    self.log_test("Writing Agent", "Content Creation", has_content,
                                f"Created {len(content)} characters of content")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("Writing Agent", "Content Creation", False, error_msg)
        except Exception as e:
            self.log_test("Writing Agent", "Content Creation", False, f"Error: {str(e)}")

    async def test_data_agent(self):
        """Test Data Agent capabilities"""
        print("\n📊 DATA AGENT TESTS")
        print("=" * 60)
        
        # Test 1: Data analysis request
        data_prompt = "Analyze this data: [1,2,3,4,5,10,15,20,25,30] and provide statistical insights"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": data_prompt,
                "agent_preference": "data"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_analysis = any(word in content.lower() for word in ['mean', 'average', 'median', 'standard', 'deviation'])
                    self.log_test("Data Agent", "Statistical Analysis", has_analysis,
                                f"Analysis provided ({len(content)} chars)")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("Data Agent", "Statistical Analysis", False, error_msg)
        except Exception as e:
            self.log_test("Data Agent", "Statistical Analysis", False, f"Error: {str(e)}")

    async def test_qa_agent(self):
        """Test QA Agent capabilities"""
        print("\n🧪 QA AGENT TESTS")
        print("=" * 60)
        
        # Test 1: Test scenario creation
        qa_prompt = "Create test scenarios for a user login function"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": qa_prompt,
                "agent_preference": "qa"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_tests = any(word in content.lower() for word in ['test', 'scenario', 'login', 'valid', 'invalid'])
                    self.log_test("QA Agent", "Test Scenarios", has_tests,
                                f"Generated {len(content)} characters of test scenarios")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("QA Agent", "Test Scenarios", False, error_msg)
        except Exception as e:
            self.log_test("QA Agent", "Test Scenarios", False, f"Error: {str(e)}")

    async def test_github_agent(self):
        """Test GitHub Agent capabilities"""
        print("\n🐙 GITHUB AGENT TESTS")
        print("=" * 60)
        
        # Test 1: GitHub repository analysis
        github_prompt = "Analyze the structure needed for a Python web application repository"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": github_prompt,
                "agent_preference": "github"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_structure = any(word in content.lower() for word in ['repository', 'structure', 'folder', 'readme', 'requirements'])
                    self.log_test("GitHub Agent", "Repository Structure", has_structure,
                                f"Provided structure analysis ({len(content)} chars)")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("GitHub Agent", "Repository Structure", False, error_msg)
        except Exception as e:
            self.log_test("GitHub Agent", "Repository Structure", False, f"Error: {str(e)}")
            
        # Test 2: GitHub workflow suggestions
        workflow_prompt = "Suggest a GitHub Actions workflow for a Python project"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": workflow_prompt,
                "agent_preference": "github"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_workflow = any(word in content.lower() for word in ['github', 'actions', 'workflow', 'python', 'ci/cd'])
                    self.log_test("GitHub Agent", "Workflow Suggestions", has_workflow,
                                f"Generated workflow suggestions ({len(content)} chars)")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("GitHub Agent", "Workflow Suggestions", False, error_msg)
        except Exception as e:
            self.log_test("GitHub Agent", "Workflow Suggestions", False, f"Error: {str(e)}")

    async def test_file_agent(self):
        """Test File Agent capabilities"""
        print("\n📁 FILE AGENT TESTS")
        print("=" * 60)
        
        # Create a test project first
        try:
            async with self.session.post(f"{API_BASE}/projects", json={
                "name": f"Test Project {int(time.time())}",
                "description": "Test project for file agent testing"
            }) as response:
                if response.status == 200:
                    project = await response.json()
                    self.project_id = project['id']
                    self.log_test("File Agent", "Test Project Creation", True, f"Project ID: {self.project_id}")
                else:
                    self.log_test("File Agent", "Test Project Creation", False, f"HTTP {response.status}")
                    return
        except Exception as e:
            self.log_test("File Agent", "Test Project Creation", False, f"Error: {str(e)}")
            return
            
        # Test 1: File organization suggestions
        file_prompt = "Suggest a file organization structure for a web application project"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": file_prompt,
                "agent_preference": "file"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_structure = any(word in content.lower() for word in ['folder', 'directory', 'structure', 'organize'])
                    self.log_test("File Agent", "File Organization", has_structure,
                                f"Provided organization suggestions ({len(content)} chars)")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("File Agent", "File Organization", False, error_msg)
        except Exception as e:
            self.log_test("File Agent", "File Organization", False, f"Error: {str(e)}")

    async def test_session_agent(self):
        """Test Session Agent capabilities"""
        print("\n💾 SESSION AGENT TESTS")
        print("=" * 60)
        
        # Test 1: Session management suggestions
        session_prompt = "Explain how to manage development sessions and backup project state"
        try:
            async with self.session.post(f"{API_BASE}/chat", json={
                "message": session_prompt,
                "agent_preference": "session"
            }) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data.get('content', '')
                    has_session_info = any(word in content.lower() for word in ['session', 'backup', 'state', 'management'])
                    self.log_test("Session Agent", "Session Management", has_session_info,
                                f"Provided session management info ({len(content)} chars)")
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    error_msg = error_data.get('error', f'HTTP {response.status}')
                    self.log_test("Session Agent", "Session Management", False, error_msg)
        except Exception as e:
            self.log_test("Session Agent", "Session Management", False, f"Error: {str(e)}")

    async def test_agent_routing(self):
        """Test automatic agent routing based on message content"""
        print("\n🔄 AGENT ROUTING TESTS")
        print("=" * 60)
        
        routing_tests = [
            ("Write a Python function", "Code Agent"),
            ("Research latest AI trends", "Research Agent"), 
            ("Create documentation for API", "Writing Agent"),
            ("Analyze this dataset", "Data Agent"),
            ("Create test cases", "QA Agent"),
            ("Setup GitHub repository", "GitHub Agent"),
            ("Organize project files", "File Agent"),
            ("Manage development sessions", "Session Agent")
        ]
        
        for prompt, expected_agent in routing_tests:
            try:
                async with self.session.post(f"{API_BASE}/chat", json={
                    "message": prompt
                }) as response:
                    if response.status == 200:
                        data = await response.json()
                        selected_agent = data.get('agent_used', 'Unknown')
                        correct_routing = expected_agent.lower() in selected_agent.lower()
                        self.log_test("Agent Routing", f"Route to {expected_agent}", correct_routing,
                                    f"Prompt: '{prompt[:30]}...' -> {selected_agent}")
                    else:
                        self.log_test("Agent Routing", f"Route to {expected_agent}", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test("Agent Routing", f"Route to {expected_agent}", False, f"Error: {str(e)}")

    async def generate_test_report(self):
        """Generate a comprehensive test report"""
        print("\n📋 TEST REPORT SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"\n📊 RESULTS BY AGENT:")
        agents_summary = {}
        for result in self.test_results:
            agent = result['agent']
            if agent not in agents_summary:
                agents_summary[agent] = {'passed': 0, 'failed': 0}
            if result['success']:
                agents_summary[agent]['passed'] += 1
            else:
                agents_summary[agent]['failed'] += 1
                
        for agent, stats in agents_summary.items():
            total = stats['passed'] + stats['failed']
            rate = (stats['passed'] / total * 100) if total > 0 else 0
            print(f"  {agent}: {stats['passed']}/{total} ({rate:.1f}%)")
            
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['agent']} - {result['test']}: {result['details']}")
                    
        print(f"\n🎯 RECOMMENDATIONS:")
        if success_rate < 50:
            print("  - Critical: Many agents are not functioning properly")
            print("  - Check API keys configuration (Anthropic & Perplexity)")
            print("  - Verify backend service is running correctly")
        elif success_rate < 80:
            print("  - Warning: Some agents need attention")
            print("  - Review failed tests and configure missing API keys")
        else:
            print("  - Good: Most agents are functioning well")
            print("  - System is ready for production use")
            
        # Save detailed report to file
        report_path = Path("agent_test_report.json")
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate
            },
            'results': self.test_results,
            'agents_summary': agents_summary
        }
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n💾 Detailed report saved to: {report_path}")

    async def run_comprehensive_tests(self):
        """Run all agent tests"""
        print("🤖 XIONIMUS AI - COMPREHENSIVE AGENT TEST SUITE")
        print("=" * 60)
        print(f"Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # System health check first
        if not await self.test_system_health():
            print("❌ System health check failed. Aborting agent tests.")
            return False
            
        print("\n🔬 RUNNING AGENT CAPABILITY TESTS")
        print("=" * 60)
        
        # Test each agent
        await self.test_code_agent()
        await self.test_research_agent() 
        await self.test_writing_agent()
        await self.test_data_agent()
        await self.test_qa_agent()
        await self.test_github_agent()
        await self.test_file_agent()
        await self.test_session_agent()
        
        # Test agent routing
        await self.test_agent_routing()
        
        # Generate final report
        await self.generate_test_report()
        
        return True


async def main():
    """Main test runner"""
    try:
        async with AgentTestSuite() as tester:
            success = await tester.run_comprehensive_tests()
            if success:
                print("\n🎉 AGENT TEST SUITE COMPLETED!")
                return 0
            else:
                print("\n⚠️ AGENT TEST SUITE IDENTIFIED ISSUES")
                return 1
    except KeyboardInterrupt:
        print("\n⏹️ Test suite interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)