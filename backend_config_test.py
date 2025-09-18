#!/usr/bin/env python3
"""
Backend Configuration Test
Tests backend configuration and API setup without making actual API calls
"""

import requests
import json
import os
import sys
from pathlib import Path

class BackendConfigTester:
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
        self.results = []
    
    def log_test(self, test_name, status, details):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details
        }
        self.results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"  {status_icon} {test_name}: {details}")
    
    def test_backend_health(self):
        """Test backend health and configuration"""
        print("🏥 Testing Backend Health and Configuration...")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Check basic structure
                self.log_test("Health Endpoint", "PASS", f"Backend is running and accessible")
                
                # Check services
                services = health_data.get("services", {})
                mongodb_status = services.get("mongodb", "unknown")
                perplexity_status = services.get("perplexity", "unknown")
                claude_status = services.get("claude", "unknown")
                
                self.log_test("MongoDB Connection", 
                            "PASS" if mongodb_status == "connected" else "FAIL",
                            f"Status: {mongodb_status}")
                
                self.log_test("Perplexity Configuration", 
                            "INFO",
                            f"Status: {perplexity_status}")
                
                self.log_test("Claude Configuration", 
                            "INFO",
                            f"Status: {claude_status}")
                
                # Check agents
                agents = health_data.get("agents", {})
                available_agents = agents.get("available", 0)
                agents_list = agents.get("agents_list", [])
                
                self.log_test("Agent System", 
                            "PASS" if available_agents > 0 else "FAIL",
                            f"{available_agents} agents available: {agents_list}")
                
            else:
                self.log_test("Health Endpoint", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            self.log_test("Health Endpoint", "FAIL", 
                        f"Cannot connect to backend at {self.api_url}")
        except Exception as e:
            self.log_test("Health Endpoint", "FAIL", f"Error: {str(e)}")
    
    def test_api_key_endpoints(self):
        """Test API key management endpoints"""
        print("\n🔑 Testing API Key Management...")
        
        # Test status endpoint
        try:
            response = requests.get(f"{self.api_url}/api-keys/status", timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                self.log_test("API Key Status Endpoint", "PASS", 
                            f"Response: {status_data}")
                
                # Check if structure is correct
                if "perplexity" in status_data and "anthropic" in status_data:
                    self.log_test("API Key Status Structure", "PASS", 
                                "Contains perplexity and anthropic keys")
                else:
                    self.log_test("API Key Status Structure", "FAIL", 
                                "Missing expected keys in response")
            else:
                self.log_test("API Key Status Endpoint", "FAIL", 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("API Key Status Endpoint", "FAIL", f"Error: {str(e)}")
        
        # Test saving API keys (with dummy keys)
        test_keys = {
            "perplexity": "test-perplexity-key",
            "anthropic": "test-anthropic-key"
        }
        
        for service, test_key in test_keys.items():
            try:
                payload = {
                    "service": service,
                    "key": test_key,
                    "is_active": True
                }
                
                response = requests.post(f"{self.api_url}/api-keys", 
                                       json=payload, timeout=10)
                
                if response.status_code == 200:
                    result_data = response.json()
                    expected_message = f"{service} API key saved successfully"
                    
                    if result_data.get("message") == expected_message:
                        self.log_test(f"Save {service.title()} Key", "PASS", 
                                    "API key endpoint accepts and processes keys")
                    else:
                        self.log_test(f"Save {service.title()} Key", "WARN", 
                                    f"Unexpected response: {result_data}")
                else:
                    self.log_test(f"Save {service.title()} Key", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Save {service.title()} Key", "FAIL", f"Error: {str(e)}")
    
    def test_model_configuration(self):
        """Test model configuration in server.py"""
        print("\n⚙️ Testing Model Configuration...")
        
        server_py_path = self.root_dir / "backend" / "server.py"
        
        if not server_py_path.exists():
            self.log_test("Server.py File", "FAIL", "server.py not found")
            return
        
        try:
            with open(server_py_path, 'r') as f:
                server_content = f.read()
            
            # Check for new Perplexity model
            new_model = "llama-3.1-sonar-large-128k-online"
            old_model = "sonar-pro"
            
            if new_model in server_content:
                self.log_test("Perplexity Model Update", "PASS", 
                            f"New model '{new_model}' configured")
            elif old_model in server_content:
                self.log_test("Perplexity Model Update", "FAIL", 
                            f"Still using old model '{old_model}'")
            else:
                self.log_test("Perplexity Model Update", "WARN", 
                            "Could not determine Perplexity model")
            
            # Check for Claude system message
            claude_system_msg = "Du bist Claude, ein hilfsreicher KI-Assistent"
            if claude_system_msg in server_content:
                self.log_test("Claude System Message", "PASS", 
                            "German system message configured")
            else:
                self.log_test("Claude System Message", "WARN", 
                            "Could not find German system message")
            
            # Check for problematic model override logic
            problematic_logic = 'if request.model == "claude":\n                    request.model = "perplexity"'
            if problematic_logic in server_content:
                self.log_test("Model Selection Logic", "FAIL", 
                            "CRITICAL: Claude requests are being overridden to use Perplexity")
            else:
                self.log_test("Model Selection Logic", "PASS", 
                            "Model selection logic appears correct")
                
        except Exception as e:
            self.log_test("Model Configuration Check", "FAIL", f"Error: {str(e)}")
    
    def test_agent_endpoints(self):
        """Test agent system endpoints"""
        print("\n🤖 Testing Agent System...")
        
        # Test available agents
        try:
            response = requests.get(f"{self.api_url}/agents", timeout=10)
            
            if response.status_code == 200:
                agents_data = response.json()
                
                if isinstance(agents_data, list) and len(agents_data) > 0:
                    agent_names = [agent.get('name', 'Unknown') for agent in agents_data]
                    self.log_test("Available Agents", "PASS", 
                                f"{len(agents_data)} agents: {agent_names}")
                else:
                    self.log_test("Available Agents", "FAIL", 
                                f"No agents or invalid response: {agents_data}")
            else:
                self.log_test("Available Agents", "FAIL", 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Available Agents", "FAIL", f"Error: {str(e)}")
        
        # Test agent analysis
        try:
            payload = {
                "message": "Test message for agent analysis",
                "context": {}
            }
            
            response = requests.post(f"{self.api_url}/agents/analyze", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                analysis_data = response.json()
                
                required_fields = ["message", "language_detected", "agent_recommendations"]
                missing_fields = [field for field in required_fields if field not in analysis_data]
                
                if missing_fields:
                    self.log_test("Agent Analysis", "FAIL", 
                                f"Missing fields: {missing_fields}")
                else:
                    best_agent = analysis_data.get("best_agent")
                    recommendations = len(analysis_data.get("agent_recommendations", {}))
                    self.log_test("Agent Analysis", "PASS", 
                                f"Best agent: {best_agent}, {recommendations} recommendations")
            else:
                self.log_test("Agent Analysis", "FAIL", 
                            f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Agent Analysis", "FAIL", f"Error: {str(e)}")
    
    def test_voice_support_config(self):
        """Test voice functionality support configuration"""
        print("\n🎤 Testing Voice Support Configuration...")
        
        # Check if backend can accept voice context in chat requests
        # This tests the endpoint structure without making AI calls
        try:
            # Test with invalid model to avoid AI API calls but test structure
            payload = {
                "message": "Test voice support",
                "model": "invalid_model_test",
                "context": {
                    "input_method": "voice",
                    "transcription_confidence": 0.95
                }
            }
            
            response = requests.post(f"{self.api_url}/chat", 
                                   json=payload, timeout=10)
            
            # We expect this to fail due to invalid model, but it should accept the structure
            if response.status_code == 400:
                error_detail = response.json().get("detail", "")
                if "Invalid model selection" in error_detail:
                    self.log_test("Voice Context Support", "PASS", 
                                "Backend accepts voice context in chat requests")
                else:
                    self.log_test("Voice Context Support", "WARN", 
                                f"Unexpected error: {error_detail}")
            else:
                self.log_test("Voice Context Support", "WARN", 
                            f"Unexpected response: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Voice Context Support", "FAIL", f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 BACKEND CONFIGURATION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARN"])
        info_tests = len([r for r in self.results if r["status"] == "INFO"])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warnings}")
        print(f"ℹ️ Info: {info_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Show critical issues
        critical_issues = [r for r in self.results if r["status"] == "FAIL" and "CRITICAL" in r["details"]]
        if critical_issues:
            print(f"\n🔴 Critical Issues Found:")
            for issue in critical_issues:
                print(f"  • {issue['test']}: {issue['details']}")
        
        # Show key findings
        key_findings = []
        for result in self.results:
            if "New model" in result["details"] and result["status"] == "PASS":
                key_findings.append(f"✅ {result['details']}")
            elif "CRITICAL" in result["details"]:
                key_findings.append(f"🔴 {result['details']}")
        
        if key_findings:
            print(f"\n🔍 Key Findings:")
            for finding in key_findings:
                print(f"  {finding}")
        
        print("=" * 80)
    
    def run_all_tests(self):
        """Run all configuration tests"""
        print("🚀 Starting Backend Configuration Testing...")
        print(f"Backend URL: {self.backend_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 80)
        
        self.test_backend_health()
        self.test_api_key_endpoints()
        self.test_model_configuration()
        self.test_agent_endpoints()
        self.test_voice_support_config()
        
        return self.results

def main():
    """Main function"""
    tester = BackendConfigTester()
    results = tester.run_all_tests()
    tester.print_summary()
    
    # Return success if no critical failures
    critical_failures = len([r for r in results if r["status"] == "FAIL" and "CRITICAL" in r["details"]])
    return 1 if critical_failures > 0 else 0

if __name__ == "__main__":
    sys.exit(main())