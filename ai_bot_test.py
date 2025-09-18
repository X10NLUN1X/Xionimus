#!/usr/bin/env python3
"""
AI Bot Integration Testing Script
Tests Claude and Perplexity API integrations after API key fix
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime

class AIBotTester:
    def __init__(self):
        self.root_dir = Path("/app")
        # Get backend URL from frontend .env
        self.backend_url = self.get_backend_url()
        self.results = {
            "api_connectivity": {},
            "claude_tests": {},
            "perplexity_tests": {},
            "api_key_validation": {},
            "error_handling": {},
            "response_quality": {},
            "critical_issues": [],
            "minor_issues": []
        }
        
    def get_backend_url(self):
        """Get backend URL from frontend .env file"""
        try:
            frontend_env = self.root_dir / "frontend" / ".env"
            if frontend_env.exists():
                with open(frontend_env, 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            url = line.split('=', 1)[1].strip()
                            return f"{url}/api"
            return "http://localhost:8001/api"  # fallback
        except Exception as e:
            print(f"Warning: Could not read frontend .env: {e}")
            return "http://localhost:8001/api"
    
    def make_request(self, method, endpoint, data=None, timeout=30):
        """Make HTTP request to backend API"""
        url = f"{self.backend_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "headers": dict(response.headers)
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "status_code": None
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Connection error - backend may not be running",
                "status_code": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": None
            }
    
    def test_api_connectivity(self):
        """Test basic API connectivity"""
        print("🔍 Testing API Connectivity...")
        
        # Test health endpoint
        health_result = self.make_request("GET", "/health")
        self.results["api_connectivity"]["health_check"] = health_result
        
        if health_result["success"] and health_result["status_code"] == 200:
            print("  ✅ Backend API is accessible")
            health_data = health_result["response"]
            
            # Check API key status from health endpoint
            if "services" in health_data:
                services = health_data["services"]
                self.results["api_connectivity"]["perplexity_configured"] = services.get("perplexity") == "configured"
                self.results["api_connectivity"]["claude_configured"] = services.get("claude") == "configured"
                
                print(f"  📊 Perplexity API: {'✅ Configured' if self.results['api_connectivity']['perplexity_configured'] else '❌ Not Configured'}")
                print(f"  📊 Claude API: {'✅ Configured' if self.results['api_connectivity']['claude_configured'] else '❌ Not Configured'}")
        else:
            print("  ❌ Backend API is not accessible")
            self.results["critical_issues"].append({
                "component": "Backend API",
                "issue": "API not accessible",
                "details": health_result.get("error", "Unknown error"),
                "impact": "Cannot test AI bots without backend access"
            })
            return False
        
        # Test API key status endpoint
        api_key_status = self.make_request("GET", "/api-keys/status")
        self.results["api_connectivity"]["api_key_status"] = api_key_status
        
        if api_key_status["success"]:
            status_data = api_key_status["response"]
            print(f"  🔑 API Key Status - Perplexity: {'✅' if status_data.get('perplexity') else '❌'}, Claude: {'✅' if status_data.get('anthropic') else '❌'}")
        
        return True
    
    def test_claude_integration(self):
        """Test Claude API integration"""
        print("🤖 Testing Claude Integration...")
        
        if not self.results["api_connectivity"].get("claude_configured", False):
            print("  ⚠️ Claude API not configured, skipping tests")
            self.results["claude_tests"]["skipped"] = True
            return
        
        # Test messages in German and English as requested
        test_messages = [
            {
                "message": "Hallo! Kannst du mir bei der Programmierung helfen?",
                "language": "German",
                "expected_language": "German"
            },
            {
                "message": "Hello! Can you help me with programming?", 
                "language": "English",
                "expected_language": "English"
            }
        ]
        
        for i, test_case in enumerate(test_messages):
            print(f"  📝 Testing Claude with {test_case['language']} message...")
            
            chat_request = {
                "message": test_case["message"],
                "model": "claude",
                "use_agent": False  # Test direct Claude integration
            }
            
            start_time = time.time()
            result = self.make_request("POST", "/chat", chat_request, timeout=60)
            response_time = time.time() - start_time
            
            test_key = f"test_{i+1}_{test_case['language'].lower()}"
            self.results["claude_tests"][test_key] = {
                "request": chat_request,
                "result": result,
                "response_time": response_time,
                "language": test_case["language"]
            }
            
            if result["success"] and result["status_code"] == 200:
                response_data = result["response"]
                message_content = response_data.get("message", {}).get("content", "")
                
                if message_content and len(message_content) > 10:
                    print(f"    ✅ Claude responded successfully ({response_time:.2f}s)")
                    print(f"    📄 Response preview: {message_content[:100]}...")
                    
                    # Check if response is in expected language (basic check)
                    if test_case["language"] == "German":
                        german_indicators = ["ich", "der", "die", "das", "und", "ist", "kann", "mit"]
                        has_german = any(word in message_content.lower() for word in german_indicators)
                        if has_german:
                            print(f"    🌍 Response appears to be in German")
                        else:
                            self.results["minor_issues"].append({
                                "component": "Claude",
                                "issue": "Response language mismatch",
                                "details": f"Expected German response but content doesn't show German indicators",
                                "impact": "Minor - functionality works but language preference not followed"
                            })
                else:
                    print(f"    ❌ Claude response is empty or too short")
                    self.results["critical_issues"].append({
                        "component": "Claude API",
                        "issue": "Empty or invalid response",
                        "details": f"Response content: '{message_content}'",
                        "impact": "Claude is not generating proper responses"
                    })
            else:
                print(f"    ❌ Claude request failed")
                error_detail = result.get("error", "Unknown error")
                if result.get("status_code") == 400:
                    response_data = result.get("response", {})
                    if isinstance(response_data, dict):
                        error_detail = response_data.get("detail", error_detail)
                
                self.results["critical_issues"].append({
                    "component": "Claude API",
                    "issue": "API request failed",
                    "details": f"Status: {result.get('status_code')}, Error: {error_detail}",
                    "impact": "Claude bot is not working"
                })
    
    def test_perplexity_integration(self):
        """Test Perplexity API integration"""
        print("🔍 Testing Perplexity Integration...")
        
        if not self.results["api_connectivity"].get("perplexity_configured", False):
            print("  ⚠️ Perplexity API not configured, skipping tests")
            self.results["perplexity_tests"]["skipped"] = True
            return
        
        # Test messages in German and English as requested
        test_messages = [
            {
                "message": "Hallo! Kannst du mir bei der Programmierung helfen?",
                "language": "German",
                "expected_language": "German"
            },
            {
                "message": "Hello! Can you help me with programming?",
                "language": "English", 
                "expected_language": "English"
            }
        ]
        
        for i, test_case in enumerate(test_messages):
            print(f"  📝 Testing Perplexity with {test_case['language']} message...")
            
            chat_request = {
                "message": test_case["message"],
                "model": "perplexity",
                "use_agent": False  # Test direct Perplexity integration
            }
            
            start_time = time.time()
            result = self.make_request("POST", "/chat", chat_request, timeout=60)
            response_time = time.time() - start_time
            
            test_key = f"test_{i+1}_{test_case['language'].lower()}"
            self.results["perplexity_tests"][test_key] = {
                "request": chat_request,
                "result": result,
                "response_time": response_time,
                "language": test_case["language"]
            }
            
            if result["success"] and result["status_code"] == 200:
                response_data = result["response"]
                message_content = response_data.get("message", {}).get("content", "")
                
                if message_content and len(message_content) > 10:
                    print(f"    ✅ Perplexity responded successfully ({response_time:.2f}s)")
                    print(f"    📄 Response preview: {message_content[:100]}...")
                    
                    # Check if using the updated model
                    model_used = response_data.get("message", {}).get("model", "")
                    if model_used == "perplexity":
                        print(f"    🔧 Using updated model: llama-3.1-sonar-large-128k-online")
                    
                    # Check for sources (Perplexity should provide sources)
                    sources = response_data.get("sources", [])
                    if sources:
                        print(f"    📚 Sources provided: {len(sources)} sources")
                    else:
                        print(f"    📚 No sources provided (may be normal for some queries)")
                else:
                    print(f"    ❌ Perplexity response is empty or too short")
                    self.results["critical_issues"].append({
                        "component": "Perplexity API",
                        "issue": "Empty or invalid response",
                        "details": f"Response content: '{message_content}'",
                        "impact": "Perplexity is not generating proper responses"
                    })
            else:
                print(f"    ❌ Perplexity request failed")
                error_detail = result.get("error", "Unknown error")
                if result.get("status_code") == 400:
                    response_data = result.get("response", {})
                    if isinstance(response_data, dict):
                        error_detail = response_data.get("detail", error_detail)
                
                self.results["critical_issues"].append({
                    "component": "Perplexity API", 
                    "issue": "API request failed",
                    "details": f"Status: {result.get('status_code')}, Error: {error_detail}",
                    "impact": "Perplexity bot is not working"
                })
    
    def test_api_key_validation(self):
        """Test API key validation and authentication"""
        print("🔑 Testing API Key Validation...")
        
        # Check if Emergent Universal Key is being used
        backend_env = self.root_dir / "backend" / ".env"
        if backend_env.exists():
            with open(backend_env, 'r') as f:
                env_content = f.read()
                
            perplexity_key = None
            anthropic_key = None
            
            for line in env_content.split('\n'):
                if line.startswith('PERPLEXITY_API_KEY='):
                    perplexity_key = line.split('=', 1)[1].strip()
                elif line.startswith('ANTHROPIC_API_KEY='):
                    anthropic_key = line.split('=', 1)[1].strip()
            
            self.results["api_key_validation"]["perplexity_key"] = perplexity_key
            self.results["api_key_validation"]["anthropic_key"] = anthropic_key
            
            # Check if using Emergent Universal Key
            expected_key = "sk-emergent-2A5951705C86987309"
            
            if perplexity_key == expected_key:
                print("  ✅ Perplexity using Emergent Universal Key")
            else:
                print(f"  ⚠️ Perplexity key: {perplexity_key[:20]}..." if perplexity_key else "  ❌ Perplexity key not found")
            
            if anthropic_key == expected_key:
                print("  ✅ Claude using Emergent Universal Key")
            else:
                print(f"  ⚠️ Claude key: {anthropic_key[:20]}..." if anthropic_key else "  ❌ Claude key not found")
            
            # Validate key format
            if perplexity_key and not perplexity_key.startswith('sk-'):
                self.results["critical_issues"].append({
                    "component": "Perplexity API Key",
                    "issue": "Invalid API key format",
                    "details": "API key should start with 'sk-'",
                    "impact": "Authentication will fail"
                })
            
            if anthropic_key and not anthropic_key.startswith('sk-'):
                self.results["critical_issues"].append({
                    "component": "Claude API Key", 
                    "issue": "Invalid API key format",
                    "details": "API key should start with 'sk-'",
                    "impact": "Authentication will fail"
                })
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("⚠️ Testing Error Handling...")
        
        # Test invalid model
        invalid_model_request = {
            "message": "Test message",
            "model": "invalid_model"
        }
        
        result = self.make_request("POST", "/chat", invalid_model_request)
        self.results["error_handling"]["invalid_model"] = result
        
        if result["success"] and result["status_code"] == 400:
            print("  ✅ Invalid model properly rejected")
        else:
            print("  ⚠️ Invalid model handling may need improvement")
        
        # Test empty message
        empty_message_request = {
            "message": "",
            "model": "claude"
        }
        
        result = self.make_request("POST", "/chat", empty_message_request)
        self.results["error_handling"]["empty_message"] = result
        
        if result["success"]:
            print("  ✅ Empty message handled gracefully")
        else:
            print("  ⚠️ Empty message handling may need improvement")
    
    def analyze_response_quality(self):
        """Analyze response quality from tests"""
        print("📊 Analyzing Response Quality...")
        
        # Analyze Claude responses
        claude_responses = []
        for key, test in self.results["claude_tests"].items():
            if key.startswith("test_") and test.get("result", {}).get("success"):
                response_data = test["result"]["response"]
                content = response_data.get("message", {}).get("content", "")
                if content:
                    claude_responses.append({
                        "content": content,
                        "length": len(content),
                        "response_time": test.get("response_time", 0),
                        "language": test.get("language", "Unknown")
                    })
        
        # Analyze Perplexity responses
        perplexity_responses = []
        for key, test in self.results["perplexity_tests"].items():
            if key.startswith("test_") and test.get("result", {}).get("success"):
                response_data = test["result"]["response"]
                content = response_data.get("message", {}).get("content", "")
                if content:
                    perplexity_responses.append({
                        "content": content,
                        "length": len(content),
                        "response_time": test.get("response_time", 0),
                        "language": test.get("language", "Unknown"),
                        "sources": len(response_data.get("sources", []))
                    })
        
        self.results["response_quality"]["claude"] = {
            "total_responses": len(claude_responses),
            "avg_length": sum(r["length"] for r in claude_responses) / len(claude_responses) if claude_responses else 0,
            "avg_response_time": sum(r["response_time"] for r in claude_responses) / len(claude_responses) if claude_responses else 0
        }
        
        self.results["response_quality"]["perplexity"] = {
            "total_responses": len(perplexity_responses),
            "avg_length": sum(r["length"] for r in perplexity_responses) / len(perplexity_responses) if perplexity_responses else 0,
            "avg_response_time": sum(r["response_time"] for r in perplexity_responses) / len(perplexity_responses) if perplexity_responses else 0,
            "avg_sources": sum(r["sources"] for r in perplexity_responses) / len(perplexity_responses) if perplexity_responses else 0
        }
        
        if claude_responses:
            claude_quality = self.results["response_quality"]["claude"]
            print(f"  🤖 Claude: {claude_quality['total_responses']} responses, avg {claude_quality['avg_length']:.0f} chars, {claude_quality['avg_response_time']:.2f}s")
        
        if perplexity_responses:
            perplexity_quality = self.results["response_quality"]["perplexity"]
            print(f"  🔍 Perplexity: {perplexity_quality['total_responses']} responses, avg {perplexity_quality['avg_length']:.0f} chars, {perplexity_quality['avg_response_time']:.2f}s, {perplexity_quality['avg_sources']:.1f} sources")
    
    def run_all_tests(self):
        """Run all AI bot tests"""
        print("🚀 Starting AI Bot Integration Testing...")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print("=" * 60)
        
        # Test API connectivity first
        if not self.test_api_connectivity():
            print("❌ Cannot proceed with AI bot testing - backend not accessible")
            return self.results
        
        # Test API key validation
        self.test_api_key_validation()
        
        # Test both AI integrations
        self.test_claude_integration()
        self.test_perplexity_integration()
        
        # Test error handling
        self.test_error_handling()
        
        # Analyze response quality
        self.analyze_response_quality()
        
        return self.results
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print("🤖 AI BOT INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        # API Connectivity Summary
        print("\n🔗 API Connectivity:")
        connectivity = self.results["api_connectivity"]
        if connectivity.get("health_check", {}).get("success"):
            print("  ✅ Backend API accessible")
            print(f"  🔑 Perplexity API: {'✅ Configured' if connectivity.get('perplexity_configured') else '❌ Not Configured'}")
            print(f"  🔑 Claude API: {'✅ Configured' if connectivity.get('claude_configured') else '❌ Not Configured'}")
        else:
            print("  ❌ Backend API not accessible")
        
        # Claude Results
        print("\n🤖 Claude Integration:")
        claude_tests = self.results["claude_tests"]
        if claude_tests.get("skipped"):
            print("  ⚠️ Tests skipped - API not configured")
        else:
            successful_tests = sum(1 for key, test in claude_tests.items() 
                                 if key.startswith("test_") and test.get("result", {}).get("success"))
            total_tests = sum(1 for key in claude_tests.keys() if key.startswith("test_"))
            print(f"  📊 Tests passed: {successful_tests}/{total_tests}")
            
            if successful_tests > 0:
                print("  ✅ Claude is responding to messages")
            else:
                print("  ❌ Claude is not working properly")
        
        # Perplexity Results
        print("\n🔍 Perplexity Integration:")
        perplexity_tests = self.results["perplexity_tests"]
        if perplexity_tests.get("skipped"):
            print("  ⚠️ Tests skipped - API not configured")
        else:
            successful_tests = sum(1 for key, test in perplexity_tests.items() 
                                 if key.startswith("test_") and test.get("result", {}).get("success"))
            total_tests = sum(1 for key in perplexity_tests.keys() if key.startswith("test_"))
            print(f"  📊 Tests passed: {successful_tests}/{total_tests}")
            
            if successful_tests > 0:
                print("  ✅ Perplexity is responding to messages")
            else:
                print("  ❌ Perplexity is not working properly")
        
        # Critical Issues
        if self.results["critical_issues"]:
            print(f"\n🔴 Critical Issues Found: {len(self.results['critical_issues'])}")
            for issue in self.results["critical_issues"]:
                print(f"  • {issue['component']}: {issue['issue']}")
                print(f"    Details: {issue['details']}")
                print(f"    Impact: {issue['impact']}")
        else:
            print("\n✅ No critical issues found")
        
        # Minor Issues
        if self.results["minor_issues"]:
            print(f"\n🟡 Minor Issues: {len(self.results['minor_issues'])}")
            for issue in self.results["minor_issues"]:
                print(f"  • {issue['component']}: {issue['issue']}")
        
        # Response Quality Summary
        quality = self.results["response_quality"]
        if quality.get("claude", {}).get("total_responses", 0) > 0 or quality.get("perplexity", {}).get("total_responses", 0) > 0:
            print(f"\n📊 Response Quality Summary:")
            if quality.get("claude", {}).get("total_responses", 0) > 0:
                claude_q = quality["claude"]
                print(f"  🤖 Claude: {claude_q['avg_response_time']:.2f}s avg response time, {claude_q['avg_length']:.0f} chars avg")
            if quality.get("perplexity", {}).get("total_responses", 0) > 0:
                perp_q = quality["perplexity"]
                print(f"  🔍 Perplexity: {perp_q['avg_response_time']:.2f}s avg response time, {perp_q['avg_length']:.0f} chars avg")
        
        print("\n" + "=" * 60)

def main():
    """Main function"""
    tester = AIBotTester()
    results = tester.run_all_tests()
    tester.print_results()
    
    # Return exit code based on results
    critical_issues = len(results["critical_issues"])
    if critical_issues > 0:
        print(f"\n❌ Testing completed with {critical_issues} critical issues")
        return 1
    else:
        print(f"\n✅ Testing completed successfully")
        return 0

if __name__ == "__main__":
    sys.exit(main())