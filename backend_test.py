#!/usr/bin/env python3
"""
Xionimus AI Backend Testing Script
Tests complete backend functionality after emergentintegrations removal
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
import time
import asyncio
import aiohttp

class XionimusBackendTester:
    def __init__(self):
        self.root_dir = Path("/app")
        self.backend_url = None
        self.results = {
            "backend_startup": {},
            "health_endpoint": {},
            "api_key_management": {},
            "agents_system": {},
            "chat_endpoints": {},
            "dependency_check": {},
            "configuration_issues": [],
            "test_summary": {}
        }
        
        # Get backend URL from frontend .env
        self._get_backend_url()
    
    def _get_backend_url(self):
        """Get backend URL from frontend .env file"""
        frontend_env = self.root_dir / "frontend" / ".env"
        if frontend_env.exists():
            with open(frontend_env, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
        
        if not self.backend_url:
            self.backend_url = "http://localhost:8001"
        
        print(f"🌐 Using backend URL: {self.backend_url}")
    
    def run_command(self, command, capture_output=True, timeout=30):
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True, 
                timeout=timeout,
                cwd=self.root_dir
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def test_backend_startup(self):
        """Test if backend is running and accessible"""
        print("🚀 Testing Backend Startup...")
        
        try:
            # Test root endpoint
            response = requests.get(f"{self.backend_url}/", timeout=10)
            self.results["backend_startup"]["root_endpoint"] = {
                "accessible": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:200]
            }
        except Exception as e:
            self.results["backend_startup"]["root_endpoint"] = {
                "accessible": False,
                "error": str(e)
            }
        
        # Check if backend process is running
        backend_process = self.run_command("ps aux | grep 'python.*server.py' | grep -v grep")
        self.results["backend_startup"]["process_running"] = backend_process["success"]
        
        # Check supervisor status
        supervisor_status = self.run_command("sudo supervisorctl status backend")
        self.results["backend_startup"]["supervisor_status"] = {
            "success": supervisor_status["success"],
            "output": supervisor_status["stdout"] if supervisor_status["success"] else supervisor_status["stderr"]
        }
    
    def test_health_endpoint(self):
        """Test health endpoint functionality"""
        print("🏥 Testing Health Endpoint...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.results["health_endpoint"] = {
                    "accessible": True,
                    "status_code": response.status_code,
                    "data": health_data,
                    "mongodb_connected": health_data.get("services", {}).get("mongodb") == "connected",
                    "agents_available": health_data.get("agents", {}).get("available", 0),
                    "agents_list": health_data.get("agents", {}).get("agents_list", [])
                }
            else:
                self.results["health_endpoint"] = {
                    "accessible": False,
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            self.results["health_endpoint"] = {
                "accessible": False,
                "error": str(e)
            }
    
    def test_api_key_management(self):
        """Test API key management endpoints"""
        print("🔑 Testing API Key Management...")
        
        # Test API key status endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/api-keys/status", timeout=10)
            if response.status_code == 200:
                status_data = response.json()
                self.results["api_key_management"]["status_endpoint"] = {
                    "accessible": True,
                    "data": status_data,
                    "perplexity_configured": status_data.get("perplexity", False),
                    "anthropic_configured": status_data.get("anthropic", False)
                }
            else:
                self.results["api_key_management"]["status_endpoint"] = {
                    "accessible": False,
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            self.results["api_key_management"]["status_endpoint"] = {
                "accessible": False,
                "error": str(e)
            }
        
        # Test API key save endpoint (with test data)
        try:
            test_key_data = {
                "service": "anthropic",
                "key": "sk-ant-test-key-for-validation",
                "is_active": True
            }
            response = requests.post(
                f"{self.backend_url}/api/api-keys", 
                json=test_key_data,
                timeout=10
            )
            self.results["api_key_management"]["save_endpoint"] = {
                "accessible": response.status_code in [200, 201],
                "status_code": response.status_code,
                "response": response.json() if response.status_code in [200, 201] else response.text[:200]
            }
        except Exception as e:
            self.results["api_key_management"]["save_endpoint"] = {
                "accessible": False,
                "error": str(e)
            }
    
    def test_agents_system(self):
        """Test agents system functionality"""
        print("🤖 Testing Agents System...")
        
        # Test agents list endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/agents", timeout=10)
            if response.status_code == 200:
                agents_data = response.json()
                self.results["agents_system"]["list_endpoint"] = {
                    "accessible": True,
                    "agents_count": len(agents_data),
                    "agents": agents_data,
                    "has_8_agents": len(agents_data) == 8
                }
                
                # Check for expected agents
                expected_agents = [
                    "Code Agent", "Research Agent", "Writing Agent", "Data Agent",
                    "QA Agent", "GitHub Agent", "File Agent", "Session Agent"
                ]
                found_agents = [agent.get("name") for agent in agents_data]
                self.results["agents_system"]["expected_agents_found"] = {
                    "all_found": all(agent in found_agents for agent in expected_agents),
                    "found": found_agents,
                    "missing": [agent for agent in expected_agents if agent not in found_agents]
                }
            else:
                self.results["agents_system"]["list_endpoint"] = {
                    "accessible": False,
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            self.results["agents_system"]["list_endpoint"] = {
                "accessible": False,
                "error": str(e)
            }
        
        # Test agent analysis endpoint
        try:
            test_analysis_data = {
                "message": "Generate a Python function to calculate fibonacci numbers",
                "context": {}
            }
            response = requests.post(
                f"{self.backend_url}/api/agents/analyze",
                json=test_analysis_data,
                timeout=10
            )
            if response.status_code == 200:
                analysis_data = response.json()
                self.results["agents_system"]["analyze_endpoint"] = {
                    "accessible": True,
                    "data": analysis_data,
                    "language_detected": analysis_data.get("language_detected"),
                    "best_agent": analysis_data.get("best_agent"),
                    "requires_agent": analysis_data.get("requires_agent")
                }
            else:
                self.results["agents_system"]["analyze_endpoint"] = {
                    "accessible": False,
                    "status_code": response.status_code,
                    "error": response.text[:200]
                }
        except Exception as e:
            self.results["agents_system"]["analyze_endpoint"] = {
                "accessible": False,
                "error": str(e)
            }
    
    def test_chat_endpoints(self):
        """Test chat endpoints with both Claude and Perplexity"""
        print("💬 Testing Chat Endpoints...")
        
        # Test Claude chat (without API key - should fail gracefully)
        try:
            claude_request = {
                "message": "Hello, can you help me with programming?",
                "model": "claude",
                "use_agent": False
            }
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json=claude_request,
                timeout=30
            )
            self.results["chat_endpoints"]["claude"] = {
                "endpoint_accessible": True,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:200],
                "works_without_key": response.status_code == 200
            }
        except Exception as e:
            self.results["chat_endpoints"]["claude"] = {
                "endpoint_accessible": False,
                "error": str(e)
            }
        
        # Test Perplexity chat (without API key - should fail gracefully)
        try:
            perplexity_request = {
                "message": "What is the latest news in AI?",
                "model": "perplexity",
                "use_agent": False
            }
            response = requests.post(
                f"{self.backend_url}/api/chat",
                json=perplexity_request,
                timeout=30
            )
            self.results["chat_endpoints"]["perplexity"] = {
                "endpoint_accessible": True,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:200],
                "works_without_key": response.status_code == 200
            }
        except Exception as e:
            self.results["chat_endpoints"]["perplexity"] = {
                "endpoint_accessible": False,
                "error": str(e)
            }
    
    def check_emergentintegrations_removal(self):
        """Check that emergentintegrations dependency has been completely removed"""
        print("🔍 Checking Emergentintegrations Removal...")
        
        # Check requirements.txt
        requirements_file = self.root_dir / "backend" / "requirements.txt"
        emergent_in_requirements = False
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                content = f.read()
                emergent_in_requirements = "emergentintegrations" in content and not content.count("# emergentintegrations")
        
        # Check server.py for emergentintegrations imports
        server_file = self.root_dir / "backend" / "server.py"
        emergent_in_server = False
        if server_file.exists():
            with open(server_file, 'r') as f:
                content = f.read()
                emergent_in_server = "from emergentintegrations" in content or "import emergentintegrations" in content
        
        # Check agent files for emergentintegrations
        agent_files_with_emergent = []
        agents_dir = self.root_dir / "backend" / "agents"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.py"):
                with open(agent_file, 'r') as f:
                    content = f.read()
                    if "emergentintegrations" in content:
                        agent_files_with_emergent.append(str(agent_file))
        
        # Check for direct API clients
        anthropic_import = False
        openai_import = False
        if server_file.exists():
            with open(server_file, 'r') as f:
                content = f.read()
                anthropic_import = "import anthropic" in content
                openai_import = "from openai import AsyncOpenAI" in content
        
        self.results["dependency_check"] = {
            "emergent_in_requirements": emergent_in_requirements,
            "emergent_in_server": emergent_in_server,
            "agent_files_with_emergent": agent_files_with_emergent,
            "anthropic_import_found": anthropic_import,
            "openai_import_found": openai_import,
            "removal_complete": not emergent_in_requirements and not emergent_in_server and len(agent_files_with_emergent) == 0,
            "direct_clients_implemented": anthropic_import and openai_import
        }
    
    def check_backend_logs(self):
        """Check backend logs for any errors"""
        print("📋 Checking Backend Logs...")
        
        # Check supervisor logs
        backend_logs = self.run_command("tail -n 50 /var/log/supervisor/backend.*.log")
        if backend_logs["success"]:
            log_content = backend_logs["stdout"]
            has_errors = "ERROR" in log_content or "Exception" in log_content
            self.results["backend_logs"] = {
                "accessible": True,
                "has_errors": has_errors,
                "log_sample": log_content[-500:] if log_content else "No logs found"
            }
        else:
            self.results["backend_logs"] = {
                "accessible": False,
                "error": backend_logs["stderr"]
            }
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Xionimus AI Backend Testing...")
        print("=" * 60)
        
        self.test_backend_startup()
        self.test_health_endpoint()
        self.test_api_key_management()
        self.test_agents_system()
        self.test_chat_endpoints()
        self.check_emergentintegrations_removal()
        self.check_backend_logs()
        
        # Generate test summary
        self._generate_test_summary()
        
        return self.results
    
    def _generate_test_summary(self):
        """Generate overall test summary"""
        total_tests = 0
        passed_tests = 0
        critical_failures = []
        
        # Backend startup
        if self.results["backend_startup"].get("root_endpoint", {}).get("accessible"):
            passed_tests += 1
        else:
            critical_failures.append("Backend root endpoint not accessible")
        total_tests += 1
        
        # Health endpoint
        if self.results["health_endpoint"].get("accessible"):
            passed_tests += 1
        else:
            critical_failures.append("Health endpoint not accessible")
        total_tests += 1
        
        # API key management
        if self.results["api_key_management"].get("status_endpoint", {}).get("accessible"):
            passed_tests += 1
        else:
            critical_failures.append("API key status endpoint not accessible")
        total_tests += 1
        
        # Agents system
        if self.results["agents_system"].get("list_endpoint", {}).get("accessible"):
            passed_tests += 1
            if self.results["agents_system"]["list_endpoint"].get("has_8_agents"):
                passed_tests += 1
            else:
                critical_failures.append("Not all 8 agents are available")
            total_tests += 1
        else:
            critical_failures.append("Agents list endpoint not accessible")
        total_tests += 1
        
        # Chat endpoints
        claude_accessible = self.results["chat_endpoints"].get("claude", {}).get("endpoint_accessible", False)
        perplexity_accessible = self.results["chat_endpoints"].get("perplexity", {}).get("endpoint_accessible", False)
        
        if claude_accessible:
            passed_tests += 1
        else:
            critical_failures.append("Claude chat endpoint not accessible")
        total_tests += 1
        
        if perplexity_accessible:
            passed_tests += 1
        else:
            critical_failures.append("Perplexity chat endpoint not accessible")
        total_tests += 1
        
        # Emergentintegrations removal
        if self.results["dependency_check"].get("removal_complete"):
            passed_tests += 1
        else:
            critical_failures.append("Emergentintegrations not completely removed")
        total_tests += 1
        
        # Direct API clients
        if self.results["dependency_check"].get("direct_clients_implemented"):
            passed_tests += 1
        else:
            critical_failures.append("Direct API clients not properly implemented")
        total_tests += 1
        
        self.results["test_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "critical_failures": critical_failures,
            "overall_status": "PASS" if len(critical_failures) == 0 else "FAIL"
        }
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print("🔍 XIONIMUS AI BACKEND TEST RESULTS")
        print("=" * 60)
        
        # Test Summary
        summary = self.results["test_summary"]
        print(f"\n📊 Test Summary:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Passed: {summary['passed_tests']} ✅")
        print(f"  Failed: {summary['failed_tests']} ❌")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Overall Status: {summary['overall_status']}")
        
        # Backend Startup
        print(f"\n🚀 Backend Startup:")
        startup = self.results["backend_startup"]
        root_status = "✅" if startup.get("root_endpoint", {}).get("accessible") else "❌"
        print(f"  Root Endpoint: {root_status}")
        if startup.get("root_endpoint", {}).get("accessible"):
            response = startup["root_endpoint"]["response"]
            if isinstance(response, dict):
                print(f"    Version: {response.get('version', 'Unknown')}")
                print(f"    Status: {response.get('status', 'Unknown')}")
        
        # Health Endpoint
        print(f"\n🏥 Health Endpoint:")
        health = self.results["health_endpoint"]
        health_status = "✅" if health.get("accessible") else "❌"
        print(f"  Accessible: {health_status}")
        if health.get("accessible"):
            print(f"  MongoDB Connected: {'✅' if health.get('mongodb_connected') else '❌'}")
            print(f"  Agents Available: {health.get('agents_available', 0)}")
        
        # API Key Management
        print(f"\n🔑 API Key Management:")
        api_keys = self.results["api_key_management"]
        status_endpoint = "✅" if api_keys.get("status_endpoint", {}).get("accessible") else "❌"
        save_endpoint = "✅" if api_keys.get("save_endpoint", {}).get("accessible") else "❌"
        print(f"  Status Endpoint: {status_endpoint}")
        print(f"  Save Endpoint: {save_endpoint}")
        
        # Agents System
        print(f"\n🤖 Agents System:")
        agents = self.results["agents_system"]
        list_endpoint = "✅" if agents.get("list_endpoint", {}).get("accessible") else "❌"
        print(f"  List Endpoint: {list_endpoint}")
        if agents.get("list_endpoint", {}).get("accessible"):
            print(f"  Agents Count: {agents['list_endpoint'].get('agents_count', 0)}")
            print(f"  Has 8 Agents: {'✅' if agents['list_endpoint'].get('has_8_agents') else '❌'}")
            if agents.get("expected_agents_found"):
                missing = agents["expected_agents_found"].get("missing", [])
                if missing:
                    print(f"  Missing Agents: {', '.join(missing)}")
        
        # Chat Endpoints
        print(f"\n💬 Chat Endpoints:")
        chat = self.results["chat_endpoints"]
        claude_status = "✅" if chat.get("claude", {}).get("endpoint_accessible") else "❌"
        perplexity_status = "✅" if chat.get("perplexity", {}).get("endpoint_accessible") else "❌"
        print(f"  Claude Endpoint: {claude_status}")
        print(f"  Perplexity Endpoint: {perplexity_status}")
        
        # Dependency Check
        print(f"\n🔍 Emergentintegrations Removal:")
        dep_check = self.results["dependency_check"]
        removal_complete = "✅" if dep_check.get("removal_complete") else "❌"
        direct_clients = "✅" if dep_check.get("direct_clients_implemented") else "❌"
        print(f"  Removal Complete: {removal_complete}")
        print(f"  Direct API Clients: {direct_clients}")
        
        if not dep_check.get("removal_complete"):
            if dep_check.get("emergent_in_requirements"):
                print("    ❌ Still found in requirements.txt")
            if dep_check.get("emergent_in_server"):
                print("    ❌ Still found in server.py")
            if dep_check.get("agent_files_with_emergent"):
                print(f"    ❌ Found in agent files: {len(dep_check['agent_files_with_emergent'])}")
        
        # Critical Failures
        if summary["critical_failures"]:
            print(f"\n🔴 Critical Failures:")
            for failure in summary["critical_failures"]:
                print(f"  • {failure}")
        
        print("\n" + "=" * 60)

def main():
    """Main function"""
    tester = XionimusBackendTester()
    results = tester.run_all_tests()
    tester.print_results()
    
    # Return exit code based on results
    if results["test_summary"]["overall_status"] == "PASS":
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())