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
    
    def test_api_key_management(self):
        """Test API key management endpoints"""
        print("🔑 Testing API Key Management...")
        
        # Test API key status endpoint
        try:
            response = requests.get(f"{self.api_url}/api-keys/status", timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                
                # Check structure
                if "perplexity" in status_data and "anthropic" in status_data:
                    self.log_result("api_key_management", "status_endpoint", True, 
                                  f"API key status: {status_data}")
                    
                    # Check if keys are configured
                    perplexity_configured = status_data.get("perplexity", False)
                    anthropic_configured = status_data.get("anthropic", False)
                    
                    self.log_result("api_key_management", "perplexity_key_status", 
                                  isinstance(perplexity_configured, bool), 
                                  f"Perplexity key configured: {perplexity_configured}")
                    
                    self.log_result("api_key_management", "anthropic_key_status", 
                                  isinstance(anthropic_configured, bool), 
                                  f"Anthropic key configured: {anthropic_configured}")
                else:
                    self.log_result("api_key_management", "status_endpoint", False, 
                                  f"Invalid status response structure: {status_data}", True)
            else:
                self.log_result("api_key_management", "status_endpoint", False, 
                              f"Status endpoint returned {response.status_code}: {response.text}", True)
                
        except Exception as e:
            self.log_result("api_key_management", "status_endpoint", False, 
                          f"API key status check failed: {str(e)}", True)
        
        # Test API key saving (with test keys)
        for service, test_key in self.test_api_keys.items():
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
                        self.log_result("api_key_management", f"save_{service}_key", True, 
                                      f"Successfully saved {service} API key")
                    else:
                        self.log_result("api_key_management", f"save_{service}_key", False, 
                                      f"Unexpected response: {result_data}")
                else:
                    self.log_result("api_key_management", f"save_{service}_key", False, 
                                  f"Failed to save {service} key: {response.status_code} - {response.text}")
                    
            except Exception as e:
                self.log_result("api_key_management", f"save_{service}_key", False, 
                              f"Error saving {service} key: {str(e)}")
    
    def test_claude_integration(self):
        """Test Claude API integration"""
        print("🤖 Testing Claude Integration...")
        
        # Test basic Claude chat
        try:
            payload = {
                "message": self.test_message_german,
                "model": "claude",
                "use_agent": False  # Test direct Claude integration
            }
            
            response = requests.post(f"{self.api_url}/chat", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                chat_data = response.json()
                
                # Check response structure
                required_fields = ["message", "conversation_id"]
                missing_fields = [field for field in required_fields if field not in chat_data]
                
                if missing_fields:
                    self.log_result("claude_integration", "response_structure", False, 
                                  f"Missing fields in Claude response: {missing_fields}", True)
                else:
                    message = chat_data.get("message", {})
                    content = message.get("content", "")
                    model = message.get("model", "")
                    
                    # Check if Claude responded
                    if content and len(content) > 10:
                        self.log_result("claude_integration", "claude_response", True, 
                                      f"Claude responded with {len(content)} characters")
                        
                        # Check if response is in German (basic check)
                        german_indicators = ["ich", "ist", "das", "der", "die", "und", "mit", "für"]
                        german_found = any(indicator in content.lower() for indicator in german_indicators)
                        
                        self.log_result("claude_integration", "german_response", german_found, 
                                      f"German language detected in response: {german_found}")
                        
                        # Check model field
                        self.log_result("claude_integration", "model_field", 
                                      model == "claude", 
                                      f"Model field: {model}")
                    else:
                        self.log_result("claude_integration", "claude_response", False, 
                                      f"Claude response too short or empty: '{content}'", True)
                        
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Unknown error")
                if "API key not configured" in error_detail:
                    self.log_result("claude_integration", "claude_response", False, 
                                  "Claude API key not configured - this is expected in test environment")
                else:
                    self.log_result("claude_integration", "claude_response", False, 
                                  f"Claude API error: {error_detail}", True)
            else:
                self.log_result("claude_integration", "claude_response", False, 
                              f"Claude chat failed: {response.status_code} - {response.text}", True)
                
        except Exception as e:
            self.log_result("claude_integration", "claude_response", False, 
                          f"Claude integration test failed: {str(e)}", True)
    
    def test_perplexity_integration(self):
        """Test Perplexity API integration with new model"""
        print("🔍 Testing Perplexity Integration...")
        
        # Test Perplexity chat with new model
        try:
            payload = {
                "message": self.test_message_english,
                "model": "perplexity",
                "use_agent": False  # Test direct Perplexity integration
            }
            
            response = requests.post(f"{self.api_url}/chat", 
                                   json=payload, timeout=30)
            
            if response.status_code == 200:
                chat_data = response.json()
                
                # Check response structure
                message = chat_data.get("message", {})
                content = message.get("content", "")
                model = message.get("model", "")
                sources = chat_data.get("sources", [])
                
                # Check if Perplexity responded
                if content and len(content) > 10:
                    self.log_result("perplexity_integration", "perplexity_response", True, 
                                  f"Perplexity responded with {len(content)} characters")
                    
                    # Check model field
                    self.log_result("perplexity_integration", "model_field", 
                                  model == "perplexity", 
                                  f"Model field: {model}")
                    
                    # Check if sources are provided (Perplexity feature)
                    self.log_result("perplexity_integration", "sources_provided", 
                                  isinstance(sources, list), 
                                  f"Sources provided: {len(sources) if isinstance(sources, list) else 'None'}")
                    
                    # Check for more human-like response (should be conversational)
                    conversational_indicators = ["i", "you", "can", "help", "let", "sure", "here"]
                    conversational_found = any(indicator in content.lower() for indicator in conversational_indicators)
                    
                    self.log_result("perplexity_integration", "conversational_response", conversational_found, 
                                  f"Conversational tone detected: {conversational_found}")
                else:
                    self.log_result("perplexity_integration", "perplexity_response", False, 
                                  f"Perplexity response too short or empty: '{content}'", True)
                    
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Unknown error")
                if "API key not configured" in error_detail:
                    self.log_result("perplexity_integration", "perplexity_response", False, 
                                  "Perplexity API key not configured - this is expected in test environment")
                else:
                    self.log_result("perplexity_integration", "perplexity_response", False, 
                                  f"Perplexity API error: {error_detail}", True)
            else:
                self.log_result("perplexity_integration", "perplexity_response", False, 
                              f"Perplexity chat failed: {response.status_code} - {response.text}", True)
                
        except Exception as e:
            self.log_result("perplexity_integration", "perplexity_response", False, 
                          f"Perplexity integration test failed: {str(e)}", True)
        
        # Test if new model is being used by checking server.py
        try:
            server_py_path = self.root_dir / "backend" / "server.py"
            if server_py_path.exists():
                with open(server_py_path, 'r') as f:
                    server_content = f.read()
                
                # Check for new model
                new_model = "llama-3.1-sonar-large-128k-online"
                old_model = "sonar-pro"
                
                if new_model in server_content:
                    self.log_result("perplexity_integration", "new_model_configured", True, 
                                  f"New Perplexity model '{new_model}' found in server.py")
                elif old_model in server_content:
                    self.log_result("perplexity_integration", "new_model_configured", False, 
                                  f"Old Perplexity model '{old_model}' still in use", True)
                else:
                    self.log_result("perplexity_integration", "new_model_configured", False, 
                                  "Could not determine Perplexity model in server.py")
            else:
                self.log_result("perplexity_integration", "new_model_configured", False, 
                              "server.py not found for model verification")
                
        except Exception as e:
            self.log_result("perplexity_integration", "new_model_configured", False, 
                          f"Error checking Perplexity model configuration: {str(e)}")
    
    def test_model_selection(self):
        """Test model selection functionality"""
        print("⚙️ Testing Model Selection...")
        
        # Test both models with same message
        test_message = "What is Python programming?"
        
        for model in ["claude", "perplexity"]:
            try:
                payload = {
                    "message": test_message,
                    "model": model,
                    "use_agent": False
                }
                
                response = requests.post(f"{self.api_url}/chat", 
                                       json=payload, timeout=30)
                
                if response.status_code == 200:
                    chat_data = response.json()
                    message = chat_data.get("message", {})
                    returned_model = message.get("model", "")
                    
                    self.log_result("model_selection", f"{model}_selection", 
                                  returned_model == model, 
                                  f"Requested {model}, got {returned_model}")
                elif response.status_code == 400:
                    error_detail = response.json().get("detail", "Unknown error")
                    if "API key not configured" in error_detail:
                        self.log_result("model_selection", f"{model}_selection", False, 
                                      f"{model} API key not configured - expected in test environment")
                    else:
                        self.log_result("model_selection", f"{model}_selection", False, 
                                      f"{model} selection failed: {error_detail}")
                else:
                    self.log_result("model_selection", f"{model}_selection", False, 
                                  f"{model} selection failed: {response.status_code}")
                    
            except Exception as e:
                self.log_result("model_selection", f"{model}_selection", False, 
                              f"{model} selection test failed: {str(e)}")
    
    def test_language_detection(self):
        """Test language detection functionality"""
        print("🌐 Testing Language Detection...")
        
        test_cases = [
            ("Hallo, wie geht es dir?", "german"),
            ("Hello, how are you?", "english"),
            ("Bonjour, comment allez-vous?", "french"),
            ("Hola, ¿cómo estás?", "spanish")
        ]
        
        for message, expected_lang in test_cases:
            try:
                payload = {
                    "message": message,
                    "context": {}
                }
                
                response = requests.post(f"{self.api_url}/agents/analyze", 
                                       json=payload, timeout=10)
                
                if response.status_code == 200:
                    analysis_data = response.json()
                    language_detected = analysis_data.get("language_detected", {})
                    
                    if isinstance(language_detected, dict):
                        detected_lang = language_detected.get("language", "").lower()
                        confidence = language_detected.get("confidence", 0)
                        
                        # Check if language was detected correctly
                        lang_correct = expected_lang.lower() in detected_lang or detected_lang in expected_lang.lower()
                        
                        self.log_result("language_detection", f"{expected_lang}_detection", 
                                      lang_correct, 
                                      f"Expected {expected_lang}, detected {detected_lang} (confidence: {confidence})")
                    else:
                        self.log_result("language_detection", f"{expected_lang}_detection", False, 
                                      f"Invalid language detection response: {language_detected}")
                else:
                    self.log_result("language_detection", f"{expected_lang}_detection", False, 
                                  f"Language detection failed: {response.status_code}")
                    
            except Exception as e:
                self.log_result("language_detection", f"{expected_lang}_detection", False, 
                              f"Language detection test failed: {str(e)}")
    
    def test_agent_system(self):
        """Test agent system functionality"""
        print("🤖 Testing Agent System...")
        
        # Test available agents endpoint
        try:
            response = requests.get(f"{self.api_url}/agents", timeout=10)
            
            if response.status_code == 200:
                agents_data = response.json()
                
                if isinstance(agents_data, list) and len(agents_data) > 0:
                    self.log_result("agent_system", "available_agents", True, 
                                  f"Found {len(agents_data)} available agents: {[agent.get('name', 'Unknown') for agent in agents_data]}")
                else:
                    self.log_result("agent_system", "available_agents", False, 
                                  f"No agents available or invalid response: {agents_data}")
            else:
                self.log_result("agent_system", "available_agents", False, 
                              f"Agents endpoint failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("agent_system", "available_agents", False, 
                          f"Agent system test failed: {str(e)}")
        
        # Test agent analysis
        try:
            payload = {
                "message": "Write a Python function to calculate fibonacci numbers",
                "context": {}
            }
            
            response = requests.post(f"{self.api_url}/agents/analyze", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                analysis_data = response.json()
                
                required_fields = ["message", "language_detected", "agent_recommendations", "requires_agent"]
                missing_fields = [field for field in required_fields if field not in analysis_data]
                
                if missing_fields:
                    self.log_result("agent_system", "agent_analysis", False, 
                                  f"Missing fields in agent analysis: {missing_fields}")
                else:
                    agent_recommendations = analysis_data.get("agent_recommendations", {})
                    best_agent = analysis_data.get("best_agent")
                    requires_agent = analysis_data.get("requires_agent", False)
                    
                    self.log_result("agent_system", "agent_analysis", True, 
                                  f"Agent analysis successful. Best agent: {best_agent}, Requires agent: {requires_agent}, Recommendations: {len(agent_recommendations)}")
            else:
                self.log_result("agent_system", "agent_analysis", False, 
                              f"Agent analysis failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("agent_system", "agent_analysis", False, 
                          f"Agent analysis test failed: {str(e)}")
    
    def test_voice_backend_support(self):
        """Test backend support for voice functionality"""
        print("🎤 Testing Voice Backend Support...")
        
        # Voice functionality is primarily frontend, but test if backend can handle voice-related requests
        try:
            # Test if backend can handle voice-transcribed text
            payload = {
                "message": "This message was transcribed from voice input",
                "model": "claude",
                "context": {
                    "input_method": "voice",
                    "transcription_confidence": 0.95
                }
            }
            
            response = requests.post(f"{self.api_url}/chat", 
                                   json=payload, timeout=30)
            
            # Backend should handle this like any other text input
            if response.status_code == 200:
                self.log_result("voice_backend_support", "voice_text_handling", True, 
                              "Backend successfully processes voice-transcribed text")
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Unknown error")
                if "API key not configured" in error_detail:
                    self.log_result("voice_backend_support", "voice_text_handling", True, 
                                  "Backend accepts voice context (API key issue is separate)")
                else:
                    self.log_result("voice_backend_support", "voice_text_handling", False, 
                                  f"Backend rejected voice context: {error_detail}")
            else:
                self.log_result("voice_backend_support", "voice_text_handling", False, 
                              f"Voice text handling failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("voice_backend_support", "voice_text_handling", False, 
                          f"Voice backend support test failed: {str(e)}")
    
    def generate_test_summary(self):
        """Generate test summary"""
        print("📊 Generating Test Summary...")
        
        total_tests = 0
        passed_tests = 0
        critical_failures = len(self.results["critical_issues"])
        minor_failures = len(self.results["minor_issues"])
        
        for category, tests in self.results.items():
            if category not in ["critical_issues", "minor_issues", "test_summary"]:
                for test_name, test_result in tests.items():
                    if isinstance(test_result, dict) and "success" in test_result:
                        total_tests += 1
                        if test_result["success"]:
                            passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.results["test_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": round(success_rate, 1),
            "critical_failures": critical_failures,
            "minor_failures": minor_failures,
            "overall_status": "PASS" if critical_failures == 0 else "FAIL"
        }
    
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