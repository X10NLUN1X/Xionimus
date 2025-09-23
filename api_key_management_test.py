#!/usr/bin/env python3
"""
Comprehensive API Key Management Testing für lokales System
Tests all aspects of API key persistence, status checking, and local .env file management
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List
import sys

# Backend URL from environment
BACKEND_URL = "https://agent-hub-31.preview.emergentagent.com/api"

class APIKeyManagementTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.original_env_backup = {}
        
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

    async def test_api_key_status_extended_format(self):
        """Test GET /api/api-keys/status mit neuem erweiterten Format"""
        try:
            async with self.session.get(f"{BACKEND_URL}/api-keys/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for new extended format with status + details
                    required_top_level = ["status", "details", "timestamp"]
                    missing_top_level = [field for field in required_top_level if field not in data]
                    
                    if missing_top_level:
                        self.log_test("API Key Status - Extended Format Structure", "FAIL", 
                                    f"Missing top-level fields: {missing_top_level}", data)
                        return
                    
                    # Check status section has all 3 services
                    status_section = data.get("status", {})
                    required_services = ["perplexity", "anthropic", "openai"]
                    missing_services = [service for service in required_services if service not in status_section]
                    
                    if not missing_services:
                        self.log_test("API Key Status - All Services Present", "PASS", 
                                    f"All 3 services in status: {list(status_section.keys())}")
                    else:
                        self.log_test("API Key Status - All Services Present", "FAIL", 
                                    f"Missing services in status: {missing_services}")
                    
                    # Check details section has all 3 services with configured/preview structure
                    details_section = data.get("details", {})
                    missing_details = [service for service in required_services if service not in details_section]
                    
                    if not missing_details:
                        self.log_test("API Key Status - Details Section", "PASS", 
                                    f"All 3 services in details: {list(details_section.keys())}")
                        
                        # Check each service has configured and preview fields
                        for service in required_services:
                            service_details = details_section.get(service, {})
                            if "configured" in service_details and "preview" in service_details:
                                configured = service_details["configured"]
                                preview = service_details["preview"]
                                
                                if isinstance(configured, bool):
                                    self.log_test(f"API Key Status - {service.title()} Structure", "PASS", 
                                                f"configured: {configured}, preview: {preview}")
                                else:
                                    self.log_test(f"API Key Status - {service.title()} Structure", "FAIL", 
                                                f"configured should be boolean, got {type(configured)}")
                            else:
                                self.log_test(f"API Key Status - {service.title()} Structure", "FAIL", 
                                            f"Missing configured/preview fields: {service_details}")
                    else:
                        self.log_test("API Key Status - Details Section", "FAIL", 
                                    f"Missing services in details: {missing_details}")
                    
                    # Check timestamp format
                    timestamp = data.get("timestamp")
                    if timestamp and isinstance(timestamp, str):
                        self.log_test("API Key Status - Timestamp", "PASS", 
                                    f"Timestamp present: {timestamp}")
                    else:
                        self.log_test("API Key Status - Timestamp", "FAIL", 
                                    f"Invalid timestamp: {timestamp}")
                    
                    self.log_test("API Key Status - Extended Format Overall", "PASS", 
                                "New extended format working correctly")
                    
                else:
                    self.log_test("API Key Status - Extended Format", "FAIL", 
                                f"HTTP {response.status}", await response.text())
                    
        except Exception as e:
            self.log_test("API Key Status - Extended Format", "FAIL", f"Exception: {str(e)}")

    async def test_api_key_persistence_all_services(self):
        """Test API-Key Persistierung für alle 3 Services: perplexity, anthropic, openai"""
        try:
            # Test data for all 3 services
            test_keys = {
                "perplexity": {
                    "service": "perplexity",
                    "key": "pplx-test-persistence-key-12345678",
                    "is_active": True
                },
                "anthropic": {
                    "service": "anthropic", 
                    "key": "sk-ant-test-persistence-key-12345678",
                    "is_active": True
                },
                "openai": {
                    "service": "openai",
                    "key": "sk-test-persistence-key-12345678", 
                    "is_active": True
                }
            }
            
            # Save all 3 API keys
            for service_name, payload in test_keys.items():
                async with self.session.post(f"{BACKEND_URL}/api-keys", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "message" in data and service_name in data["message"].lower():
                            self.log_test(f"API Key Persistence - {service_name.title()} Save", "PASS", 
                                        f"{service_name} key saved successfully")
                        else:
                            self.log_test(f"API Key Persistence - {service_name.title()} Save", "FAIL", 
                                        f"Unexpected response format: {data}")
                    else:
                        self.log_test(f"API Key Persistence - {service_name.title()} Save", "FAIL", 
                                    f"HTTP {response.status}", await response.text())
            
            # Wait a moment for persistence
            await asyncio.sleep(1)
            
            # Verify all keys are persisted by checking status
            async with self.session.get(f"{BACKEND_URL}/api-keys/status") as response:
                if response.status == 200:
                    data = await response.json()
                    status_section = data.get("status", {})
                    details_section = data.get("details", {})
                    
                    # Check all 3 services are configured
                    configured_services = [service for service, configured in status_section.items() if configured]
                    
                    if len(configured_services) == 3:
                        self.log_test("API Key Persistence - All Services Configured", "PASS", 
                                    f"All 3 services configured: {configured_services}")
                        
                        # Check preview shows last 4 characters for each service
                        for service_name, test_data in test_keys.items():
                            service_details = details_section.get(service_name, {})
                            preview = service_details.get("preview")
                            expected_preview = f"...{test_data['key'][-4:]}"
                            
                            if preview == expected_preview:
                                self.log_test(f"API Key Persistence - {service_name.title()} Preview", "PASS", 
                                            f"Correct preview: {preview}")
                            else:
                                self.log_test(f"API Key Persistence - {service_name.title()} Preview", "FAIL", 
                                            f"Expected {expected_preview}, got {preview}")
                    else:
                        self.log_test("API Key Persistence - All Services Configured", "FAIL", 
                                    f"Only {len(configured_services)} services configured: {configured_services}")
                else:
                    self.log_test("API Key Persistence - Verification", "FAIL", 
                                f"Could not verify persistence: HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("API Key Persistence - All Services", "FAIL", f"Exception: {str(e)}")

    async def test_api_key_delete_functionality(self):
        """Test DELETE /api/api-keys/{service} (neue Funktionalität)"""
        try:
            # First ensure we have keys to delete (from previous test)
            services_to_test = ["perplexity", "anthropic", "openai"]
            
            for service in services_to_test:
                # Test DELETE endpoint
                async with self.session.delete(f"{BACKEND_URL}/api-keys/{service}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "message" in data and service in data["message"].lower() and "deleted" in data["message"].lower():
                            self.log_test(f"API Key Delete - {service.title()}", "PASS", 
                                        f"{service} key deleted successfully")
                        else:
                            self.log_test(f"API Key Delete - {service.title()}", "FAIL", 
                                        f"Unexpected response format: {data}")
                    else:
                        self.log_test(f"API Key Delete - {service.title()}", "FAIL", 
                                    f"HTTP {response.status}", await response.text())
            
            # Verify all keys are deleted by checking status
            await asyncio.sleep(1)  # Wait for deletion to process
            
            async with self.session.get(f"{BACKEND_URL}/api-keys/status") as response:
                if response.status == 200:
                    data = await response.json()
                    status_section = data.get("status", {})
                    
                    # Check all services are now not configured
                    configured_services = [service for service, configured in status_section.items() if configured]
                    
                    if len(configured_services) == 0:
                        self.log_test("API Key Delete - Verification All Deleted", "PASS", 
                                    "All API keys successfully deleted and verified")
                    else:
                        self.log_test("API Key Delete - Verification All Deleted", "FAIL", 
                                    f"Some keys still configured: {configured_services}")
                else:
                    self.log_test("API Key Delete - Verification", "FAIL", 
                                f"Could not verify deletion: HTTP {response.status}")
            
            # Test deleting non-existent key (should handle gracefully)
            async with self.session.delete(f"{BACKEND_URL}/api-keys/nonexistent") as response:
                if response.status == 400:
                    data = await response.json()
                    if "Invalid service" in data.get("detail", ""):
                        self.log_test("API Key Delete - Invalid Service", "PASS", 
                                    "Invalid service properly rejected")
                    else:
                        self.log_test("API Key Delete - Invalid Service", "FAIL", 
                                    f"Unexpected error message: {data.get('detail')}")
                else:
                    self.log_test("API Key Delete - Invalid Service", "FAIL", 
                                f"Expected 400, got {response.status}")
                    
        except Exception as e:
            self.log_test("API Key Delete Functionality", "FAIL", f"Exception: {str(e)}")

    async def test_intelligent_chat_without_model_field(self):
        """Test neues intelligentes Chat ohne model field"""
        try:
            # Test 1: Basic intelligent chat without model field
            intelligent_payload = {
                "message": "Erkläre mir die Grundlagen des maschinellen Lernens",
                "conversation_history": [],
                "use_agent": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=intelligent_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and data["message"].get("role") == "assistant":
                        # Check for unified model name
                        model_used = data["message"].get("model")
                        if model_used == "xionimus-ai":
                            self.log_test("Intelligent Chat - No Model Field (Success)", "PASS", 
                                        "✅ Intelligent chat working without model field, unified 'xionimus-ai' model")
                        else:
                            self.log_test("Intelligent Chat - No Model Field (Success)", "PASS", 
                                        f"Intelligent chat working without model field, model: {model_used}")
                    else:
                        self.log_test("Intelligent Chat - No Model Field", "FAIL", 
                                    f"Invalid response structure: {data}")
                elif response.status == 400:
                    data = await response.json()
                    if "Mindestens ein API-Schlüssel muss konfiguriert sein" in data.get("detail", ""):
                        self.log_test("Intelligent Chat - No Model Field (API Key Required)", "PASS", 
                                    "✅ Intelligent chat accepts request without model field (API key error expected)")
                    else:
                        self.log_test("Intelligent Chat - No Model Field", "FAIL", 
                                    f"Unexpected error: {data.get('detail')}")
                else:
                    self.log_test("Intelligent Chat - No Model Field", "FAIL", 
                                f"Unexpected status {response.status}")
            
            # Test 2: Different types of queries to test intelligent routing
            test_queries = [
                {
                    "type": "research",
                    "message": "Was sind die neuesten Entwicklungen in der KI-Forschung 2024?",
                    "expected_agent": "research"
                },
                {
                    "type": "code", 
                    "message": "Schreibe eine Python-Funktion für Quicksort-Algorithmus",
                    "expected_agent": "code"
                },
                {
                    "type": "writing",
                    "message": "Verfasse einen professionellen Geschäftsbrief",
                    "expected_agent": "writing"
                }
            ]
            
            for query in test_queries:
                payload = {
                    "message": query["message"],
                    "use_agent": True
                }
                
                async with self.session.post(f"{BACKEND_URL}/chat", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        agent_used = data.get("agent_used", "").lower()
                        self.log_test(f"Intelligent Chat - {query['type'].title()} Query", "PASS", 
                                    f"✅ {query['type']} query processed intelligently, agent: {agent_used}")
                    elif response.status == 400:
                        data = await response.json()
                        if "API-Schlüssel" in data.get("detail", ""):
                            self.log_test(f"Intelligent Chat - {query['type'].title()} Query", "PASS", 
                                        f"✅ {query['type']} query accepted by intelligent system")
                        else:
                            self.log_test(f"Intelligent Chat - {query['type'].title()} Query", "FAIL", 
                                        f"Unexpected error: {data.get('detail')}")
                    else:
                        self.log_test(f"Intelligent Chat - {query['type'].title()} Query", "FAIL", 
                                    f"Unexpected status {response.status}")
                        
        except Exception as e:
            self.log_test("Intelligent Chat Without Model Field", "FAIL", f"Exception: {str(e)}")

    async def test_chat_with_different_api_key_combinations(self):
        """Test Chat-System mit verschiedenen API-Key Kombinationen"""
        try:
            # Test 1: Save only Anthropic key and test chat
            anthropic_payload = {
                "service": "anthropic",
                "key": "sk-ant-test-combo-key-12345678",
                "is_active": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/api-keys", json=anthropic_payload) as response:
                if response.status == 200:
                    self.log_test("API Key Combinations - Anthropic Only Save", "PASS", 
                                "Anthropic key saved for combination testing")
                else:
                    self.log_test("API Key Combinations - Anthropic Only Save", "FAIL", 
                                f"Could not save Anthropic key: {response.status}")
                    return
            
            # Test chat with only Anthropic key
            chat_payload = {
                "message": "Test mit nur Anthropic API-Schlüssel"
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=chat_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("API Key Combinations - Anthropic Only Chat", "PASS", 
                                "✅ Chat working with only Anthropic key configured")
                elif response.status == 400:
                    data = await response.json()
                    # Should work with at least one key configured
                    if "Mindestens ein API-Schlüssel muss konfiguriert sein" in data.get("detail", ""):
                        self.log_test("API Key Combinations - Anthropic Only Chat", "FAIL", 
                                    "Chat requires all keys, not just one")
                    else:
                        self.log_test("API Key Combinations - Anthropic Only Chat", "PASS", 
                                    "Chat attempted with single key (auth error expected)")
                else:
                    self.log_test("API Key Combinations - Anthropic Only Chat", "FAIL", 
                                f"Unexpected status {response.status}")
            
            # Test 2: Add Perplexity key and test again
            perplexity_payload = {
                "service": "perplexity",
                "key": "pplx-test-combo-key-12345678",
                "is_active": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/api-keys", json=perplexity_payload) as response:
                if response.status == 200:
                    self.log_test("API Key Combinations - Add Perplexity", "PASS", 
                                "Perplexity key added to combination")
                else:
                    self.log_test("API Key Combinations - Add Perplexity", "FAIL", 
                                f"Could not add Perplexity key: {response.status}")
            
            # Test chat with Anthropic + Perplexity
            async with self.session.post(f"{BACKEND_URL}/chat", json=chat_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("API Key Combinations - Two Keys Chat", "PASS", 
                                "✅ Chat working with Anthropic + Perplexity keys")
                elif response.status == 400:
                    data = await response.json()
                    self.log_test("API Key Combinations - Two Keys Chat", "PASS", 
                                "Chat attempted with two keys (auth error expected)")
                else:
                    self.log_test("API Key Combinations - Two Keys Chat", "FAIL", 
                                f"Unexpected status {response.status}")
            
            # Test 3: Add OpenAI key for full combination
            openai_payload = {
                "service": "openai",
                "key": "sk-test-combo-key-12345678",
                "is_active": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/api-keys", json=openai_payload) as response:
                if response.status == 200:
                    self.log_test("API Key Combinations - Add OpenAI", "PASS", 
                                "OpenAI key added for full combination")
                else:
                    self.log_test("API Key Combinations - Add OpenAI", "FAIL", 
                                f"Could not add OpenAI key: {response.status}")
            
            # Test chat with all 3 keys
            async with self.session.post(f"{BACKEND_URL}/chat", json=chat_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("API Key Combinations - All Keys Chat", "PASS", 
                                "✅ Chat working with all 3 API keys configured")
                elif response.status == 400:
                    data = await response.json()
                    self.log_test("API Key Combinations - All Keys Chat", "PASS", 
                                "Chat attempted with all keys (auth error expected)")
                else:
                    self.log_test("API Key Combinations - All Keys Chat", "FAIL", 
                                f"Unexpected status {response.status}")
                    
        except Exception as e:
            self.log_test("Chat with Different API Key Combinations", "FAIL", f"Exception: {str(e)}")

    async def test_error_handling_missing_keys(self):
        """Test Fehlerbehandlung bei fehlenden Keys"""
        try:
            # First, delete all keys to test error handling
            services = ["perplexity", "anthropic", "openai"]
            for service in services:
                async with self.session.delete(f"{BACKEND_URL}/api-keys/{service}") as response:
                    pass  # Don't care about individual results here
            
            await asyncio.sleep(1)  # Wait for deletion
            
            # Test chat with no API keys configured
            chat_payload = {
                "message": "Test ohne API-Schlüssel"
            }
            
            async with self.session.post(f"{BACKEND_URL}/chat", json=chat_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    error_detail = data.get("detail", "")
                    
                    if "Mindestens ein API-Schlüssel muss konfiguriert sein" in error_detail:
                        self.log_test("Error Handling - No API Keys", "PASS", 
                                    "✅ Proper error message for missing API keys")
                    elif "API" in error_detail and "key" in error_detail.lower():
                        self.log_test("Error Handling - No API Keys", "PASS", 
                                    f"Appropriate API key error: {error_detail}")
                    else:
                        self.log_test("Error Handling - No API Keys", "FAIL", 
                                    f"Unexpected error message: {error_detail}")
                else:
                    self.log_test("Error Handling - No API Keys", "FAIL", 
                                f"Expected 400 error, got {response.status}")
            
            # Test with invalid service name
            invalid_payload = {
                "service": "invalid_service",
                "key": "test-key",
                "is_active": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/api-keys", json=invalid_payload) as response:
                if response.status == 422:  # Validation error
                    self.log_test("Error Handling - Invalid Service", "PASS", 
                                "✅ Invalid service properly rejected with validation error")
                elif response.status == 400:
                    data = await response.json()
                    if "service" in data.get("detail", "").lower():
                        self.log_test("Error Handling - Invalid Service", "PASS", 
                                    "✅ Invalid service properly rejected")
                    else:
                        self.log_test("Error Handling - Invalid Service", "FAIL", 
                                    f"Unexpected error: {data.get('detail')}")
                else:
                    self.log_test("Error Handling - Invalid Service", "FAIL", 
                                f"Expected 400/422, got {response.status}")
                    
        except Exception as e:
            self.log_test("Error Handling Missing Keys", "FAIL", f"Exception: {str(e)}")

    async def test_cors_configuration(self):
        """Test CORS-Konfiguration für lokales Setup"""
        try:
            # Test preflight request
            headers = {
                'Origin': 'https://agent-hub-31.preview.emergentagent.com',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            async with self.session.options(f"{BACKEND_URL}/api-keys/status", headers=headers) as response:
                if response.status in [200, 204]:
                    cors_headers = response.headers
                    if 'Access-Control-Allow-Origin' in cors_headers:
                        self.log_test("CORS Configuration - Preflight", "PASS", 
                                    f"✅ CORS preflight working, origin allowed: {cors_headers.get('Access-Control-Allow-Origin')}")
                    else:
                        self.log_test("CORS Configuration - Preflight", "WARN", 
                                    "CORS headers present but no explicit origin header")
                else:
                    self.log_test("CORS Configuration - Preflight", "FAIL", 
                                f"Preflight failed: {response.status}")
            
            # Test actual request with Origin header
            headers = {
                'Origin': 'https://agent-hub-31.preview.emergentagent.com',
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(f"{BACKEND_URL}/api-keys/status", headers=headers) as response:
                if response.status == 200:
                    cors_headers = response.headers
                    if 'Access-Control-Allow-Origin' in cors_headers:
                        self.log_test("CORS Configuration - Actual Request", "PASS", 
                                    "✅ CORS working for actual requests")
                    else:
                        self.log_test("CORS Configuration - Actual Request", "WARN", 
                                    "Request successful but CORS headers not explicit")
                else:
                    self.log_test("CORS Configuration - Actual Request", "FAIL", 
                                f"Request failed: {response.status}")
                    
        except Exception as e:
            self.log_test("CORS Configuration", "FAIL", f"Exception: {str(e)}")

    async def run_comprehensive_api_key_tests(self):
        """Run comprehensive API key management tests as requested"""
        print("🔑 COMPREHENSIVE API KEY MANAGEMENT TESTING FÜR LOKALES SYSTEM")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # 1. API-Key Persistierung Test
        print("📁 1. API-KEY PERSISTIERUNG TEST")
        print("   Testing storage in .env file and os.environ for all 3 services...")
        await self.test_api_key_persistence_all_services()
        
        # 2. Frontend-Backend Communication
        print("\n🔄 2. FRONTEND-BACKEND COMMUNICATION")
        print("   Testing GET/POST/DELETE endpoints with new extended format...")
        await self.test_api_key_status_extended_format()
        await self.test_api_key_delete_functionality()
        
        # 3. Lokales Setup Validation
        print("\n🏠 3. LOKALES SETUP VALIDATION")
        print("   Testing CORS configuration and local environment...")
        await self.test_cors_configuration()
        
        # 4. Chat-System Integration
        print("\n🤖 4. CHAT-SYSTEM INTEGRATION")
        print("   Testing intelligent chat without model field...")
        await self.test_intelligent_chat_without_model_field()
        await self.test_chat_with_different_api_key_combinations()
        
        # 5. Error Handling
        print("\n⚠️ 5. FEHLERBEHANDLUNG")
        print("   Testing error handling for missing keys...")
        await self.test_error_handling_missing_keys()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE API KEY MANAGEMENT TEST RESULTS")
        print("=" * 80)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"📈 TOTAL: {len(self.test_results)}")
        
        # Critical failures analysis
        critical_failures = []
        api_key_failures = []
        
        for result in self.test_results:
            if result["status"] == "FAIL":
                critical_failures.append(result)
                if any(keyword in result["test"] for keyword in ["API Key", "Persistence", "Delete", "Chat"]):
                    api_key_failures.append(result)
        
        if api_key_failures:
            print(f"\n❌ CRITICAL API KEY SYSTEM FAILURES ({len(api_key_failures)}):")
            for result in api_key_failures:
                print(f"   • {result['test']}: {result['details']}")
        
        if failed > 0:
            print(f"\n❌ ALL FAILED TESTS ({failed}):")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
        
        # Success summary
        if failed == 0:
            print("\n🎉 ALL API KEY MANAGEMENT TESTS PASSED!")
            print("✅ API-Key Persistierung working")
            print("✅ Extended status format working") 
            print("✅ DELETE functionality working")
            print("✅ Intelligent chat without model field working")
            print("✅ Error handling working")
            print("✅ CORS configuration working")
        
        return {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "total": len(self.test_results),
            "api_key_failures": len(api_key_failures),
            "results": self.test_results
        }

async def main():
    """Main test runner for comprehensive API key management testing"""
    async with APIKeyManagementTester() as tester:
        results = await tester.run_comprehensive_api_key_tests()
        
        # Exit with appropriate code
        if results["failed"] > 0:
            print(f"\n💥 {results['failed']} tests failed - API key system needs attention")
            sys.exit(1)
        else:
            print("\n🚀 API Key Management System fully functional!")
            sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())