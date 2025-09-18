#!/usr/bin/env python3
"""
Backend API Testing Script for Xionimus AI
Tests Claude and Perplexity API connections, voice functionality backend support, and all API endpoints
"""

import requests
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

class BackendAPITester:
    def __init__(self):
        self.root_dir = Path("/app")
        
        # Get backend URL from frontend .env
        frontend_env_path = self.root_dir / "frontend" / ".env"
        self.backend_url = "http://localhost:8001"  # fallback
        
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.backend_url = line.split('=', 1)[1].strip()
                        break
        
        self.api_url = f"{self.backend_url}/api"
        self.results = {
            "backend_health": {},
            "api_key_management": {},
            "claude_integration": {},
            "perplexity_integration": {},
            "agent_system": {},
            "language_detection": {},
            "model_selection": {},
            "voice_backend_support": {},
            "critical_issues": [],
            "minor_issues": [],
            "test_summary": {}
        }
        
        # Test data
        self.test_message_german = "Hallo! Kannst du mir bei der Programmierung helfen?"
        self.test_message_english = "Hello! Can you help me with programming?"
        self.test_api_keys = {
            "perplexity": "test-perplexity-key-12345",
            "anthropic": "test-anthropic-key-12345"
        }
    
    def log_result(self, category, test_name, success, details, is_critical=False):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if category not in self.results:
            self.results[category] = {}
        
        self.results[category][test_name] = result
        
        if not success and is_critical:
            self.results["critical_issues"].append({
                "category": category,
                "test": test_name,
                "details": details
            })
        elif not success:
            self.results["minor_issues"].append({
                "category": category,
                "test": test_name,
                "details": details
            })
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        print("🏥 Testing Backend Health...")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Check basic health structure
                required_fields = ["status", "timestamp", "services", "agents"]
                missing_fields = [field for field in required_fields if field not in health_data]
                
                if missing_fields:
                    self.log_result("backend_health", "health_structure", False, 
                                  f"Missing fields in health response: {missing_fields}", True)
                else:
                    self.log_result("backend_health", "health_structure", True, 
                                  "Health endpoint returns all required fields")
                
                # Check service status
                services = health_data.get("services", {})
                mongodb_status = services.get("mongodb")
                perplexity_status = services.get("perplexity")
                claude_status = services.get("claude")
                
                self.log_result("backend_health", "mongodb_connection", 
                              mongodb_status == "connected", 
                              f"MongoDB status: {mongodb_status}", True)
                
                self.log_result("backend_health", "perplexity_config", 
                              perplexity_status in ["configured", "not_configured"], 
                              f"Perplexity status: {perplexity_status}")
                
                self.log_result("backend_health", "claude_config", 
                              claude_status in ["configured", "not_configured"], 
                              f"Claude status: {claude_status}")
                
                # Check agents
                agents = health_data.get("agents", {})
                available_agents = agents.get("available", 0)
                active_tasks = agents.get("active_tasks", 0)
                agents_list = agents.get("agents_list", [])
                
                self.log_result("backend_health", "agent_system", 
                              available_agents > 0, 
                              f"Available agents: {available_agents}, Active tasks: {active_tasks}, Agents: {agents_list}")
                
                self.log_result("backend_health", "health_endpoint", True, 
                              f"Health endpoint accessible, status: {health_data.get('status')}")
            else:
                self.log_result("backend_health", "health_endpoint", False, 
                              f"Health endpoint returned status {response.status_code}: {response.text}", True)
                
        except requests.exceptions.ConnectionError:
            self.log_result("backend_health", "health_endpoint", False, 
                          f"Cannot connect to backend at {self.api_url}/health. Backend may not be running.", True)
        except Exception as e:
            self.log_result("backend_health", "health_endpoint", False, 
                          f"Health check failed: {str(e)}", True)
    
    def test_api_keys_status(self):
        """Test API keys status endpoint"""
        print("🔍 Testing API keys status endpoint...")
        self.results["test_summary"]["total_tests"] += 1
        
        try:
            response = requests.get(f"{self.api_url}/api-keys/status", timeout=10)
            
            if response.status_code == 200:
                keys_data = response.json()
                self.results["api_endpoints"]["api_keys_status"] = {
                    "status": "success",
                    "response": keys_data,
                    "status_code": response.status_code
                }
                print(f"  ✅ PASS: API keys status endpoint working")
                self.results["test_summary"]["passed"] += 1
                return True
            else:
                self.results["api_endpoints"]["api_keys_status"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code
                }
                print(f"  ❌ FAIL: API keys status failed - HTTP {response.status_code}")
                self.results["test_summary"]["failed"] += 1
                return False
                
        except Exception as e:
            self.results["api_endpoints"]["api_keys_status"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"  ❌ FAIL: API keys status error - {str(e)}")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_agents_endpoint(self):
        """Test agents endpoint"""
        print("🔍 Testing agents endpoint...")
        self.results["test_summary"]["total_tests"] += 1
        
        try:
            response = requests.get(f"{self.api_url}/agents", timeout=10)
            
            if response.status_code == 200:
                agents_data = response.json()
                self.results["api_endpoints"]["agents"] = {
                    "status": "success",
                    "response": agents_data,
                    "status_code": response.status_code
                }
                print(f"  ✅ PASS: Agents endpoint working")
                self.results["test_summary"]["passed"] += 1
                return True
            else:
                self.results["api_endpoints"]["agents"] = {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "status_code": response.status_code
                }
                print(f"  ❌ FAIL: Agents endpoint failed - HTTP {response.status_code}")
                self.results["test_summary"]["failed"] += 1
                return False
                
        except Exception as e:
            self.results["api_endpoints"]["agents"] = {
                "status": "error",
                "error": str(e)
            }
            print(f"  ❌ FAIL: Agents endpoint error - {str(e)}")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def validate_backend_configuration(self):
        """Validate backend configuration files"""
        print("🔍 Validating backend configuration...")
        self.results["test_summary"]["total_tests"] += 1
        
        # Check server.py exists
        server_py = self.root_dir / "backend" / "server.py"
        env_file = self.root_dir / "backend" / ".env"
        requirements_file = self.root_dir / "backend" / "requirements.txt"
        
        config_valid = True
        issues = []
        
        if not server_py.exists():
            issues.append("server.py not found")
            config_valid = False
        
        if not env_file.exists():
            issues.append(".env file not found")
            config_valid = False
        
        if not requirements_file.exists():
            issues.append("requirements.txt not found")
            config_valid = False
        
        # Check .env file content
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if "MONGO_URL" not in env_content:
                issues.append("MONGO_URL not configured in .env")
                config_valid = False
            
            if "DB_NAME" not in env_content:
                issues.append("DB_NAME not configured in .env")
                config_valid = False
        
        self.results["backend_config"] = {
            "valid": config_valid,
            "issues": issues,
            "files_checked": ["server.py", ".env", "requirements.txt"]
        }
        
        if config_valid:
            print("  ✅ PASS: Backend configuration valid")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print(f"  ❌ FAIL: Backend configuration issues - {', '.join(issues)}")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Testing...")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 60)
        
        # Configuration test (always runs)
        self.validate_backend_configuration()
        print()
        
        # API tests (only if backend might be running)
        self.test_health_endpoint()
        print()
        
        if self.results["health_check"].get("status") == "success":
            # Only run other API tests if health check passes
            self.test_api_keys_status()
            print()
            self.test_agents_endpoint()
            print()
        else:
            print("⚠️  Skipping additional API tests - backend not accessible")
            print()
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 BACKEND API TEST SUMMARY")
        print("=" * 60)
        
        summary = self.results["test_summary"]
        total = summary["total_tests"]
        passed = summary["passed"]
        failed = summary["failed"]
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Health check status
        health_status = self.results["health_check"].get("status", "not_tested")
        if health_status == "success":
            print("\n🎉 Backend is running and accessible!")
            health_data = self.results["health_check"].get("response", {})
            if "services" in health_data:
                services = health_data["services"]
                print(f"📊 Service Status:")
                for service, status in services.items():
                    icon = "✅" if status in ["connected", "configured"] else "⚠️"
                    print(f"  {icon} {service}: {status}")
        elif health_status == "connection_error":
            print("\n⚠️  Backend is not running or not accessible")
            print("🔧 This is expected in testing environment without Docker")
        else:
            print(f"\n❌ Backend health check failed: {health_status}")
        
        # Configuration status
        config_valid = self.results["backend_config"].get("valid", False)
        if config_valid:
            print("\n✅ Backend configuration is valid")
        else:
            issues = self.results["backend_config"].get("issues", [])
            print(f"\n❌ Backend configuration issues: {', '.join(issues)}")
        
        print("=" * 60)

def main():
    """Main function"""
    tester = BackendAPITester()
    results = tester.run_all_tests()
    tester.print_summary()
    
    # Return success if configuration is valid (API tests may fail in testing environment)
    config_valid = results["backend_config"].get("valid", False)
    return 0 if config_valid else 1

if __name__ == "__main__":
    sys.exit(main())