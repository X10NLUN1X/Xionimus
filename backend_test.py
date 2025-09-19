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
        self.created_project_id = None  # For tracking test project
        self.results = {
            "backend_startup": {},
            "health_endpoint": {},
            "projects_api": {},  # Added projects API results
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
    
    def test_projects_api(self):
        """Test projects API endpoints - MAIN FOCUS"""
        print("📁 Testing Projects API Endpoints...")
        
        # Initialize projects results
        self.results["projects_api"] = {}
        
        # Test GET /api/projects (should return empty array or projects list)
        try:
            response = requests.get(f"{self.backend_url}/api/projects", timeout=10)
            self.results["projects_api"]["get_projects"] = {
                "accessible": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text[:200],
                "is_array": isinstance(response.json(), list) if response.status_code == 200 else False,
                "projects_count": len(response.json()) if response.status_code == 200 and isinstance(response.json(), list) else 0
            }
            print(f"  GET /api/projects: {'✅' if response.status_code == 200 else '❌'} (Status: {response.status_code})")
            if response.status_code == 200:
                projects_data = response.json()
                print(f"    Projects found: {len(projects_data) if isinstance(projects_data, list) else 'Invalid format'}")
        except Exception as e:
            self.results["projects_api"]["get_projects"] = {
                "accessible": False,
                "error": str(e)
            }
            print(f"  GET /api/projects: ❌ Error: {str(e)}")
        
        # Test POST /api/projects with sample project data
        try:
            sample_project = {
                "name": "Test AI Project",
                "description": "Ein Testprojekt für KI-Entwicklung mit Python und Machine Learning Komponenten"
            }
            response = requests.post(
                f"{self.backend_url}/api/projects",
                json=sample_project,
                timeout=10
            )
            self.results["projects_api"]["post_project"] = {
                "accessible": response.status_code in [200, 201],
                "status_code": response.status_code,
                "response": response.json() if response.status_code in [200, 201] else response.text[:200],
                "project_created": response.status_code in [200, 201]
            }
            print(f"  POST /api/projects: {'✅' if response.status_code in [200, 201] else '❌'} (Status: {response.status_code})")
            
            # Store created project ID for further testing
            if response.status_code in [200, 201]:
                created_project = response.json()
                self.created_project_id = created_project.get("id")
                print(f"    Created project ID: {self.created_project_id}")
                
        except Exception as e:
            self.results["projects_api"]["post_project"] = {
                "accessible": False,
                "error": str(e)
            }
            print(f"  POST /api/projects: ❌ Error: {str(e)}")
        
        # Test GET /api/projects/{project_id} if we created a project
        if hasattr(self, 'created_project_id') and self.created_project_id:
            try:
                response = requests.get(f"{self.backend_url}/api/projects/{self.created_project_id}", timeout=10)
                self.results["projects_api"]["get_project_by_id"] = {
                    "accessible": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text[:200],
                    "project_found": response.status_code == 200
                }
                print(f"  GET /api/projects/{self.created_project_id}: {'✅' if response.status_code == 200 else '❌'} (Status: {response.status_code})")
            except Exception as e:
                self.results["projects_api"]["get_project_by_id"] = {
                    "accessible": False,
                    "error": str(e)
                }
                print(f"  GET /api/projects/{{id}}: ❌ Error: {str(e)}")
        
        # Test PUT /api/projects/{project_id} if we created a project
        if hasattr(self, 'created_project_id') and self.created_project_id:
            try:
                updated_project = {
                    "name": "Updated Test AI Project",
                    "description": "Aktualisiertes Testprojekt mit erweiterten KI-Funktionen"
                }
                response = requests.put(
                    f"{self.backend_url}/api/projects/{self.created_project_id}",
                    json=updated_project,
                    timeout=10
                )
                self.results["projects_api"]["put_project"] = {
                    "accessible": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text[:200],
                    "project_updated": response.status_code == 200
                }
                print(f"  PUT /api/projects/{self.created_project_id}: {'✅' if response.status_code == 200 else '❌'} (Status: {response.status_code})")
            except Exception as e:
                self.results["projects_api"]["put_project"] = {
                    "accessible": False,
                    "error": str(e)
                }
                print(f"  PUT /api/projects/{{id}}: ❌ Error: {str(e)}")
        
        # Test MongoDB connection specifically for projects collection
        try:
            # Try to get projects again to verify MongoDB connection
            response = requests.get(f"{self.backend_url}/api/projects", timeout=10)
            mongodb_projects_working = response.status_code == 200
            self.results["projects_api"]["mongodb_connection"] = {
                "projects_collection_accessible": mongodb_projects_working,
                "status_code": response.status_code
            }
            print(f"  MongoDB Projects Collection: {'✅' if mongodb_projects_working else '❌'}")
        except Exception as e:
            self.results["projects_api"]["mongodb_connection"] = {
                "projects_collection_accessible": False,
                "error": str(e)
            }
            print(f"  MongoDB Projects Collection: ❌ Error: {str(e)}")
        
        # Test CORS by checking response headers
        try:
            response = requests.options(f"{self.backend_url}/api/projects", timeout=10)
            cors_headers = {
                "access_control_allow_origin": response.headers.get("access-control-allow-origin"),
                "access_control_allow_methods": response.headers.get("access-control-allow-methods"),
                "access_control_allow_headers": response.headers.get("access-control-allow-headers")
            }
            self.results["projects_api"]["cors_check"] = {
                "options_accessible": response.status_code in [200, 204],
                "status_code": response.status_code,
                "cors_headers": cors_headers,
                "cors_configured": bool(cors_headers["access_control_allow_origin"])
            }
            print(f"  CORS Configuration: {'✅' if cors_headers['access_control_allow_origin'] else '❌'}")
        except Exception as e:
            self.results["projects_api"]["cors_check"] = {
                "options_accessible": False,
                "error": str(e)
            }
            print(f"  CORS Configuration: ❌ Error: {str(e)}")
        
        # Clean up - delete the test project if created
        if hasattr(self, 'created_project_id') and self.created_project_id:
            try:
                response = requests.delete(f"{self.backend_url}/api/projects/{self.created_project_id}", timeout=10)
                self.results["projects_api"]["delete_project"] = {
                    "accessible": response.status_code == 200,
                    "status_code": response.status_code,
                    "project_deleted": response.status_code == 200
                }
                print(f"  DELETE /api/projects/{self.created_project_id}: {'✅' if response.status_code == 200 else '❌'} (Status: {response.status_code})")
            except Exception as e:
                self.results["projects_api"]["delete_project"] = {
                    "accessible": False,
                    "error": str(e)
                }
                print(f"  DELETE /api/projects/{{id}}: ❌ Error: {str(e)}")

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
        self.test_projects_api()  # MAIN FOCUS - Projects API testing
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
        
        # Projects API - MAIN FOCUS
        projects_api = self.results.get("projects_api", {})
        
        # GET /api/projects
        if projects_api.get("get_projects", {}).get("accessible"):
            passed_tests += 1
        else:
            critical_failures.append("GET /api/projects endpoint not working")
        total_tests += 1
        
        # POST /api/projects
        if projects_api.get("post_project", {}).get("accessible"):
            passed_tests += 1
        else:
            critical_failures.append("POST /api/projects endpoint not working")
        total_tests += 1
        
        # MongoDB projects collection
        if projects_api.get("mongodb_connection", {}).get("projects_collection_accessible"):
            passed_tests += 1
        else:
            critical_failures.append("MongoDB projects collection not accessible")
        total_tests += 1
        
        # CORS configuration
        if projects_api.get("cors_check", {}).get("cors_configured"):
            passed_tests += 1
        else:
            critical_failures.append("CORS not properly configured for projects API")
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
        
        # Projects API - MAIN FOCUS
        print(f"\n📁 Projects API (MAIN FOCUS):")
        projects = self.results.get("projects_api", {})
        
        get_projects_status = "✅" if projects.get("get_projects", {}).get("accessible") else "❌"
        post_project_status = "✅" if projects.get("post_project", {}).get("accessible") else "❌"
        mongodb_projects_status = "✅" if projects.get("mongodb_connection", {}).get("projects_collection_accessible") else "❌"
        cors_status = "✅" if projects.get("cors_check", {}).get("cors_configured") else "❌"
        
        print(f"  GET /api/projects: {get_projects_status}")
        if projects.get("get_projects", {}).get("accessible"):
            projects_count = projects["get_projects"].get("projects_count", 0)
            print(f"    Projects found: {projects_count}")
            print(f"    Returns array: {'✅' if projects['get_projects'].get('is_array') else '❌'}")
        
        print(f"  POST /api/projects: {post_project_status}")
        if projects.get("post_project", {}).get("accessible"):
            print(f"    Project creation: ✅")
        
        print(f"  MongoDB Projects Collection: {mongodb_projects_status}")
        print(f"  CORS Configuration: {cors_status}")
        
        # Additional project operations if tested
        if projects.get("get_project_by_id"):
            get_by_id_status = "✅" if projects["get_project_by_id"].get("accessible") else "❌"
            print(f"  GET /api/projects/{{id}}: {get_by_id_status}")
        
        if projects.get("put_project"):
            put_status = "✅" if projects["put_project"].get("accessible") else "❌"
            print(f"  PUT /api/projects/{{id}}: {put_status}")
        
        if projects.get("delete_project"):
            delete_status = "✅" if projects["delete_project"].get("accessible") else "❌"
            print(f"  DELETE /api/projects/{{id}}: {delete_status}")

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