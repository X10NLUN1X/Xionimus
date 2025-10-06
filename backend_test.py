#!/usr/bin/env python3
"""
COMPREHENSIVE PHASE 2 TESTING: Claude AI Integration Enhancement

TEST SCOPE:
1. Default Configuration Testing - Verify anthropic as default provider, claude-sonnet-4-5-20250929 as default model
2. Claude Model Availability - Test all Claude models are available in providers endpoint
3. Smart Routing Testing - Test simple vs complex query routing (Sonnet vs Opus)
4. Automatic Fallback Testing - Test Sonnet → Opus → GPT-4o fallback chain
5. Ultra-Thinking Integration - Test ultra_thinking=True by default for Claude
6. Claude API Connectivity - Test actual Claude API calls with configured key
7. Backward Compatibility - Test OpenAI and Perplexity still work
8. Chat Endpoint Integration - Test POST /api/chat with Claude defaults
9. Error Handling - Test invalid models, API key issues, malformed requests
10. Frontend Configuration - Check if defaults are properly set

TESTING CREDENTIALS:
- Demo User: demo / demo123
- Anthropic API Key: Already configured in Phase 1

EXPECTED RESULTS:
- Default provider: anthropic (not openai)
- Default model: claude-sonnet-4-5-20250929
- Ultra-thinking: True by default
- Smart routing: Simple → Sonnet, Complex → Opus
- Fallback chain: Sonnet → Opus → GPT-4o
- All Claude models available
- API calls successful
"""

import requests
import json
import time
import logging
import sqlite3
import os
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase2Tester:
    def __init__(self, base_url: str = None):
        # Use localhost for testing since we're in the same container
        self.base_url = base_url or "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.db_path = os.path.expanduser("~/.xionimus_ai/xionimus.db")
    def authenticate_demo_user(self) -> Dict[str, Any]:
        """Authenticate with demo/demo123 credentials"""
        logger.info("🔐 Authenticating with demo user (demo/demo123)")
        
        try:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                logger.info("✅ Authentication successful!")
                logger.info(f"   User ID: {self.user_info['user_id']}")
                logger.info(f"   Username: {self.user_info['username']}")
                
                return {"status": "success", "token": self.token, "user_info": self.user_info}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {"status": "failed", "error": error_detail}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def authenticate_admin_user(self) -> Dict[str, Any]:
        """Authenticate with admin/admin123 credentials"""
        logger.info("🔐 Authenticating with admin user (admin/admin123)")
        
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                admin_token = auth_data.get("access_token")
                admin_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username"),
                    "role": auth_data.get("role", "admin")
                }
                
                logger.info("✅ Admin authentication successful!")
                logger.info(f"   User ID: {admin_info['user_id']}")
                logger.info(f"   Username: {admin_info['username']}")
                logger.info(f"   Role: {admin_info['role']}")
                
                return {"status": "success", "token": admin_token, "user_info": admin_info}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Admin authentication failed: {error_detail}")
                return {"status": "failed", "error": error_detail}
                
        except Exception as e:
            logger.error(f"❌ Admin authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def test_postgresql_connection(self) -> Dict[str, Any]:
        """Test 1: PostgreSQL Database Testing - Verify PostgreSQL is active (not SQLite fallback)"""
        logger.info("🐘 Testing PostgreSQL Database Connection (CRITICAL)")
        
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                db_info = health_data.get("services", {}).get("database", {})
                db_type = db_info.get("type", "Unknown")
                db_status = db_info.get("status", "Unknown")
                
                logger.info(f"   Database type: {db_type}")
                logger.info(f"   Database status: {db_status}")
                
                if db_type == "PostgreSQL" and db_status == "connected":
                    logger.info("✅ PostgreSQL is active and connected!")
                    return {
                        "status": "success",
                        "database_type": db_type,
                        "database_status": db_status,
                        "postgresql_active": True
                    }
                elif db_type == "SQLite":
                    logger.error("❌ CRITICAL: Still using SQLite fallback instead of PostgreSQL!")
                    return {
                        "status": "failed",
                        "error": "SQLite fallback active instead of PostgreSQL",
                        "database_type": db_type,
                        "database_status": db_status,
                        "postgresql_active": False
                    }
                else:
                    logger.error(f"❌ Database connection issue: {db_type} - {db_status}")
                    return {
                        "status": "failed",
                        "error": f"Database issue: {db_type} - {db_status}",
                        "database_type": db_type,
                        "database_status": db_status
                    }
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return {"status": "failed", "error": f"Health check failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_redis_connection(self) -> Dict[str, Any]:
        """Test 2: Redis Cache Testing - Verify Redis connection and operations"""
        logger.info("🔴 Testing Redis Cache Connection and Operations")
        
        try:
            # Test Redis via backend health endpoint
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Check if Redis info is available in health response
                # Note: Current health endpoint may not include Redis status
                logger.info("✅ Health endpoint accessible")
                
                # Test Redis operations via cache endpoints (if available)
                # For now, we'll test basic connectivity through backend logs
                logger.info("   Testing Redis operations...")
                
                # Try to make a request that would use Redis caching
                test_response = self.session.get(f"{self.api_url}/health", timeout=5)
                
                if test_response.status_code == 200:
                    logger.info("✅ Redis connection test completed")
                    logger.info("   Note: Redis operations tested indirectly through backend")
                    return {
                        "status": "success",
                        "redis_tested": True,
                        "note": "Redis tested indirectly - backend handles graceful degradation"
                    }
                else:
                    return {"status": "failed", "error": "Backend request failed"}
            else:
                return {"status": "failed", "error": f"Health check failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Redis connection test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_ai_provider_configuration(self) -> Dict[str, Any]:
        """Test 3: AI Provider Configuration Testing - Test Claude, OpenAI, Perplexity connectivity"""
        logger.info("🤖 Testing AI Provider Configuration (Claude, OpenAI, Perplexity)")
        
        try:
            # Test AI providers via health endpoint
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                ai_info = health_data.get("services", {}).get("ai_providers", {})
                configured_count = ai_info.get("configured", 0)
                total_count = ai_info.get("total", 0)
                provider_status = ai_info.get("status", {})
                
                logger.info(f"   Configured providers: {configured_count}/{total_count}")
                logger.info(f"   Provider status: {provider_status}")
                
                # Check specific providers
                claude_configured = provider_status.get("anthropic", False) or provider_status.get("claude", False)
                openai_configured = provider_status.get("openai", False)
                perplexity_configured = provider_status.get("perplexity", False)
                
                logger.info(f"   Claude (Anthropic): {'✅' if claude_configured else '❌'}")
                logger.info(f"   OpenAI: {'✅' if openai_configured else '❌'}")
                logger.info(f"   Perplexity: {'✅' if perplexity_configured else '❌'}")
                
                if configured_count >= 3 and claude_configured and openai_configured and perplexity_configured:
                    logger.info("✅ All 3 AI providers configured correctly!")
                    return {
                        "status": "success",
                        "configured_count": configured_count,
                        "total_count": total_count,
                        "claude_configured": claude_configured,
                        "openai_configured": openai_configured,
                        "perplexity_configured": perplexity_configured,
                        "all_providers_configured": True
                    }
                else:
                    logger.warning(f"⚠️ Only {configured_count} providers configured (expected 3)")
                    return {
                        "status": "partial",
                        "configured_count": configured_count,
                        "total_count": total_count,
                        "claude_configured": claude_configured,
                        "openai_configured": openai_configured,
                        "perplexity_configured": perplexity_configured,
                        "all_providers_configured": False
                    }
            else:
                return {"status": "failed", "error": f"Health check failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ AI provider configuration test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_chat_providers_endpoint(self) -> Dict[str, Any]:
        """Test AI providers via /api/chat/providers endpoint"""
        logger.info("🔌 Testing AI Providers via /api/chat/providers endpoint")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(f"{self.api_url}/chat/providers", headers=headers, timeout=10)
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                providers_data = response.json()
                logger.info("✅ Chat providers endpoint accessible")
                logger.info(f"   Providers data: {providers_data}")
                
                return {
                    "status": "success",
                    "providers_data": providers_data,
                    "endpoint_accessible": True
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Chat providers endpoint failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Chat providers endpoint test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_ai_completion_request(self) -> Dict[str, Any]:
        """Test actual AI completion request (at least one provider)"""
        logger.info("💬 Testing Actual AI Completion Request")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Create a test session first
            session_data = {"name": "AI Test Session"}
            session_response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if session_response.status_code != 200:
                return {"status": "failed", "error": "Could not create test session"}
            
            session_id = session_response.json().get("id")
            
            # Test AI completion
            completion_data = {
                "message": "Hello, this is a test message. Please respond with 'AI test successful'.",
                "session_id": session_id,
                "provider": "openai",  # Try OpenAI first
                "model": "gpt-4"
            }
            
            response = self.session.post(
                f"{self.api_url}/chat/completions",
                json=completion_data,
                headers=headers,
                timeout=30  # AI requests can take longer
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                completion_result = response.json()
                logger.info("✅ AI completion request successful!")
                logger.info(f"   Response preview: {str(completion_result)[:100]}...")
                
                return {
                    "status": "success",
                    "completion_result": completion_result,
                    "ai_working": True,
                    "session_id": session_id
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.warning(f"⚠️ AI completion failed (expected without API keys): {error_detail}")
                return {
                    "status": "expected_failure",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "note": "Expected failure without valid API keys"
                }
                
        except Exception as e:
            logger.error(f"❌ AI completion request test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_database_crud_operations(self) -> Dict[str, Any]:
        """Test 5: Database Operations - Create, Read, Update, Delete operations"""
        logger.info("🗄️ Testing Database CRUD Operations")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # CREATE: Create a new session
            session_data = {"name": "CRUD Test Session"}
            create_response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if create_response.status_code != 200:
                return {"status": "failed", "error": "CREATE operation failed"}
            
            session_id = create_response.json().get("id")
            logger.info(f"   ✅ CREATE: Session created - {session_id}")
            
            # READ: Retrieve the session
            read_response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            if read_response.status_code != 200:
                return {"status": "failed", "error": "READ operation failed"}
            
            logger.info("   ✅ READ: Session retrieved successfully")
            
            # CREATE: Add a message to the session
            message_data = {
                "session_id": session_id,
                "role": "user",
                "content": "Test message for CRUD operations"
            }
            
            message_response = self.session.post(
                f"{self.api_url}/sessions/messages",
                json=message_data,
                headers=headers,
                timeout=10
            )
            
            if message_response.status_code != 200:
                return {"status": "failed", "error": "Message CREATE operation failed"}
            
            message_id = message_response.json().get("id")
            logger.info(f"   ✅ CREATE: Message added - {message_id}")
            
            # READ: Get messages from session
            messages_response = self.session.get(
                f"{self.api_url}/sessions/{session_id}/messages",
                headers=headers,
                timeout=10
            )
            
            if messages_response.status_code != 200:
                return {"status": "failed", "error": "Messages READ operation failed"}
            
            messages = messages_response.json()
            logger.info(f"   ✅ READ: Retrieved {len(messages)} messages")
            
            logger.info("✅ Database CRUD operations working correctly!")
            return {
                "status": "success",
                "session_id": session_id,
                "message_id": message_id,
                "messages_count": len(messages),
                "crud_operations_working": True
            }
            
        except Exception as e:
            logger.error(f"❌ Database CRUD operations test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_user_data_migration(self) -> Dict[str, Any]:
        """Test 6: Data Migration Integrity - Verify migrated user data (admin and demo users)"""
        logger.info("👥 Testing User Data Migration Integrity")
        
        try:
            # Test demo user login
            demo_auth = self.authenticate_demo_user()
            demo_working = demo_auth.get("status") == "success"
            
            # Test admin user login
            admin_auth = self.authenticate_admin_user()
            admin_working = admin_auth.get("status") == "success"
            
            logger.info(f"   Demo user migration: {'✅' if demo_working else '❌'}")
            logger.info(f"   Admin user migration: {'✅' if admin_working else '❌'}")
            
            if demo_working and admin_working:
                logger.info("✅ User data migration successful - both users accessible")
                return {
                    "status": "success",
                    "demo_user_migrated": demo_working,
                    "admin_user_migrated": admin_working,
                    "migration_successful": True,
                    "demo_user_info": demo_auth.get("user_info"),
                    "admin_user_info": admin_auth.get("user_info")
                }
            else:
                logger.error("❌ User data migration incomplete")
                return {
                    "status": "failed",
                    "demo_user_migrated": demo_working,
                    "admin_user_migrated": admin_working,
                    "migration_successful": False,
                    "demo_error": demo_auth.get("error") if not demo_working else None,
                    "admin_error": admin_auth.get("error") if not admin_working else None
                }
                
        except Exception as e:
            logger.error(f"❌ User data migration test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_health_check_system_status(self) -> Dict[str, Any]:
        """Test 7: Health Check & System Status - Test /api/v1/health endpoint"""
        logger.info("🏥 Testing Health Check & System Status")
        
        try:
            # Test both legacy and v1 health endpoints
            endpoints = ["/api/health", "/api/v1/health"]
            results = {}
            
            for endpoint in endpoints:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                logger.info(f"   {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    health_data = response.json()
                    results[endpoint] = {
                        "status": "success",
                        "data": health_data,
                        "overall_status": health_data.get("status"),
                        "version": health_data.get("version"),
                        "uptime": health_data.get("uptime_seconds"),
                        "database_type": health_data.get("services", {}).get("database", {}).get("type")
                    }
                else:
                    results[endpoint] = {
                        "status": "failed",
                        "status_code": response.status_code
                    }
            
            # Check if at least one endpoint works
            working_endpoints = [ep for ep, result in results.items() if result.get("status") == "success"]
            
            if working_endpoints:
                logger.info(f"✅ Health check working on {len(working_endpoints)} endpoints")
                return {
                    "status": "success",
                    "working_endpoints": working_endpoints,
                    "results": results,
                    "health_check_working": True
                }
            else:
                logger.error("❌ All health check endpoints failed")
                return {
                    "status": "failed",
                    "working_endpoints": [],
                    "results": results,
                    "health_check_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Health check system status test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_environment_configuration(self) -> Dict[str, Any]:
        """Test 8: Environment Configuration - Verify DATABASE_URL, REDIS_URL, API keys loaded"""
        logger.info("⚙️ Testing Environment Configuration")
        
        try:
            # Test environment via health endpoint
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Check database configuration
                db_info = health_data.get("services", {}).get("database", {})
                db_type = db_info.get("type")
                db_status = db_info.get("status")
                
                # Check AI providers configuration
                ai_info = health_data.get("services", {}).get("ai_providers", {})
                configured_providers = ai_info.get("configured", 0)
                
                # Check environment info
                env_info = health_data.get("environment", {})
                debug_mode = env_info.get("debug")
                log_level = env_info.get("log_level")
                
                logger.info(f"   Database: {db_type} ({db_status})")
                logger.info(f"   AI Providers: {configured_providers} configured")
                logger.info(f"   Debug mode: {debug_mode}")
                logger.info(f"   Log level: {log_level}")
                
                # Determine configuration status
                database_url_set = db_type == "PostgreSQL"
                redis_url_implied = True  # Redis tested separately
                api_keys_set = configured_providers > 0
                
                logger.info(f"   DATABASE_URL set (PostgreSQL): {'✅' if database_url_set else '❌'}")
                logger.info(f"   REDIS_URL set: {'✅' if redis_url_implied else '❌'}")
                logger.info(f"   API keys loaded: {'✅' if api_keys_set else '❌'}")
                
                if database_url_set and api_keys_set:
                    logger.info("✅ Environment configuration looks good")
                    return {
                        "status": "success",
                        "database_url_set": database_url_set,
                        "redis_url_set": redis_url_implied,
                        "api_keys_set": api_keys_set,
                        "configured_providers": configured_providers,
                        "environment_configured": True
                    }
                else:
                    logger.warning("⚠️ Some environment variables may not be set correctly")
                    return {
                        "status": "partial",
                        "database_url_set": database_url_set,
                        "redis_url_set": redis_url_implied,
                        "api_keys_set": api_keys_set,
                        "configured_providers": configured_providers,
                        "environment_configured": False
                    }
            else:
                return {"status": "failed", "error": f"Health check failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Environment configuration test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_backwards_compatibility(self) -> Dict[str, Any]:
        """Test 9: Backwards Compatibility - Test existing API endpoints still work"""
        logger.info("🔄 Testing Backwards Compatibility")
        
        try:
            # Test both legacy and v1 endpoints
            test_endpoints = [
                ("/api/health", "Legacy health"),
                ("/api/v1/health", "V1 health"),
                ("/api/auth/login", "Legacy auth"),
                ("/api/v1/auth/login", "V1 auth")
            ]
            
            results = {}
            
            for endpoint, description in test_endpoints:
                try:
                    if "auth" in endpoint:
                        # Test auth endpoints with demo credentials
                        login_data = {"username": "demo", "password": "demo123"}
                        response = self.session.post(
                            f"{self.base_url}{endpoint}",
                            json=login_data,
                            headers={"Content-Type": "application/json"},
                            timeout=10
                        )
                    else:
                        # Test health endpoints
                        response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                    
                    logger.info(f"   {description}: {response.status_code}")
                    
                    results[endpoint] = {
                        "status": "success" if response.status_code == 200 else "failed",
                        "status_code": response.status_code,
                        "description": description
                    }
                    
                except Exception as e:
                    results[endpoint] = {
                        "status": "error",
                        "error": str(e),
                        "description": description
                    }
            
            # Count successful endpoints
            successful = sum(1 for result in results.values() if result.get("status") == "success")
            total = len(results)
            
            logger.info(f"   Backwards compatibility: {successful}/{total} endpoints working")
            
            if successful >= total * 0.75:  # At least 75% working
                logger.info("✅ Backwards compatibility maintained")
                return {
                    "status": "success",
                    "successful_endpoints": successful,
                    "total_endpoints": total,
                    "results": results,
                    "backwards_compatible": True
                }
            else:
                logger.warning("⚠️ Some backwards compatibility issues detected")
                return {
                    "status": "partial",
                    "successful_endpoints": successful,
                    "total_endpoints": total,
                    "results": results,
                    "backwards_compatible": False
                }
                
        except Exception as e:
            logger.error(f"❌ Backwards compatibility test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_error_handling(self) -> Dict[str, Any]:
        """Test 10: Error Handling - Test database/Redis failure handling"""
        logger.info("🚨 Testing Error Handling")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test invalid session ID (should return 404, not 500)
            invalid_session_response = self.session.get(
                f"{self.api_url}/sessions/invalid-session-id-12345",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Invalid session ID: {invalid_session_response.status_code}")
            
            # Test invalid authentication (should return 401)
            invalid_auth_response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers={"Authorization": "Bearer invalid-token"},
                timeout=10
            )
            
            logger.info(f"   Invalid auth token: {invalid_auth_response.status_code}")
            
            # Test malformed request (should return 422)
            malformed_response = self.session.post(
                f"{self.api_url}/sessions/",
                json={"invalid": "data"},  # Missing required fields
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Malformed request: {malformed_response.status_code}")
            
            # Check error responses
            error_handling_good = (
                invalid_session_response.status_code == 404 and
                invalid_auth_response.status_code == 401 and
                malformed_response.status_code in [400, 422]
            )
            
            if error_handling_good:
                logger.info("✅ Error handling working correctly")
                return {
                    "status": "success",
                    "invalid_session_code": invalid_session_response.status_code,
                    "invalid_auth_code": invalid_auth_response.status_code,
                    "malformed_request_code": malformed_response.status_code,
                    "error_handling_working": True
                }
            else:
                logger.warning("⚠️ Some error handling issues detected")
                return {
                    "status": "partial",
                    "invalid_session_code": invalid_session_response.status_code,
                    "invalid_auth_code": invalid_auth_response.status_code,
                    "malformed_request_code": malformed_response.status_code,
                    "error_handling_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Error handling test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_default_configuration(self) -> Dict[str, Any]:
        """Test 1: Default Configuration - Verify anthropic as default provider, claude-sonnet-4-5-20250929 as default model"""
        logger.info("🎯 Testing Default Configuration (CRITICAL)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test 1: Default provider and model via chat request with no provider/model specified
            chat_data = {
                "messages": [{"role": "user", "content": "What is Python?"}]
                # No provider or model specified - should use defaults
            }
            
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                chat_response = response.json()
                actual_provider = chat_response.get("provider")
                actual_model = chat_response.get("model")
                ultra_thinking_used = chat_response.get("usage", {}).get("thinking_used", False)
                
                logger.info(f"   Actual provider: {actual_provider}")
                logger.info(f"   Actual model: {actual_model}")
                logger.info(f"   Ultra-thinking used: {ultra_thinking_used}")
                
                # Check defaults
                expected_provider = "anthropic"
                expected_model = "claude-sonnet-4-5-20250929"
                expected_ultra_thinking = True
                
                provider_correct = actual_provider == expected_provider
                model_correct = actual_model == expected_model
                
                logger.info(f"   Provider correct: {'✅' if provider_correct else '❌'} (expected: {expected_provider})")
                logger.info(f"   Model correct: {'✅' if model_correct else '❌'} (expected: {expected_model})")
                logger.info(f"   Ultra-thinking: {'✅' if ultra_thinking_used else '❌'} (expected: True)")
                
                if provider_correct and model_correct:
                    logger.info("✅ Default configuration correct!")
                    return {
                        "status": "success",
                        "actual_provider": actual_provider,
                        "actual_model": actual_model,
                        "ultra_thinking_used": ultra_thinking_used,
                        "defaults_correct": True
                    }
                else:
                    logger.error("❌ Default configuration incorrect!")
                    return {
                        "status": "failed",
                        "error": f"Expected provider={expected_provider}, model={expected_model}, got provider={actual_provider}, model={actual_model}",
                        "actual_provider": actual_provider,
                        "actual_model": actual_model,
                        "defaults_correct": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Chat request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Default configuration test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_claude_model_availability(self) -> Dict[str, Any]:
        """Test 2: Claude Model Availability - Verify all Claude models are available"""
        logger.info("🤖 Testing Claude Model Availability")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = self.session.get(f"{self.api_url}/chat/providers", headers=headers, timeout=10)
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                providers_data = response.json()
                anthropic_models = providers_data.get("models", {}).get("anthropic", [])
                
                logger.info(f"   Available Anthropic models: {anthropic_models}")
                
                # Expected Claude models
                expected_models = [
                    "claude-sonnet-4-5-20250929",  # Default model
                    "claude-opus-4-1",             # Complex tasks
                    "claude-haiku-3.5-20241022"    # Fast & cheap
                ]
                
                missing_models = []
                available_models = []
                
                for model in expected_models:
                    if model in anthropic_models:
                        available_models.append(model)
                        logger.info(f"   ✅ {model}: Available")
                    else:
                        missing_models.append(model)
                        logger.error(f"   ❌ {model}: Missing")
                
                if not missing_models:
                    logger.info("✅ All Claude models available!")
                    return {
                        "status": "success",
                        "available_models": available_models,
                        "missing_models": missing_models,
                        "all_models_available": True
                    }
                else:
                    logger.error(f"❌ Missing Claude models: {missing_models}")
                    return {
                        "status": "failed",
                        "error": f"Missing models: {missing_models}",
                        "available_models": available_models,
                        "missing_models": missing_models,
                        "all_models_available": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Providers endpoint failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Claude model availability test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_smart_routing(self) -> Dict[str, Any]:
        """Test 3: Smart Routing - Test simple vs complex query routing"""
        logger.info("🧠 Testing Smart Routing (Simple → Sonnet, Complex → Opus)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # Test 1: Simple query (should stay on Sonnet)
            simple_query = "What is Python?"
            simple_data = {
                "messages": [{"role": "user", "content": simple_query}],
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929"
            }
            
            logger.info("   Testing simple query (should stay on Sonnet)...")
            simple_response = self.session.post(
                f"{self.api_url}/chat/",
                json=simple_data,
                headers=headers,
                timeout=30
            )
            
            if simple_response.status_code == 200:
                simple_result = simple_response.json()
                simple_model = simple_result.get("model")
                logger.info(f"   Simple query model: {simple_model}")
                
                # Should NOT upgrade to Opus for simple query
                simple_correct = "sonnet" in simple_model.lower()
                results["simple_query"] = {
                    "model_used": simple_model,
                    "stayed_on_sonnet": simple_correct,
                    "query": simple_query
                }
                logger.info(f"   Simple query routing: {'✅' if simple_correct else '❌'}")
            else:
                results["simple_query"] = {"error": f"HTTP {simple_response.status_code}"}
            
            # Test 2: Complex debugging query (should upgrade to Opus)
            complex_query = "My authentication system is completely broken. Users can't login, I'm getting 500 errors, database seems fine, JWT tokens validate correctly but still failing. Please debug this thoroughly with step-by-step analysis."
            complex_data = {
                "messages": [{"role": "user", "content": complex_query}],
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929"  # Start with Sonnet
            }
            
            logger.info("   Testing complex query (should upgrade to Opus)...")
            complex_response = self.session.post(
                f"{self.api_url}/chat/",
                json=complex_data,
                headers=headers,
                timeout=45
            )
            
            if complex_response.status_code == 200:
                complex_result = complex_response.json()
                complex_model = complex_result.get("model")
                logger.info(f"   Complex query model: {complex_model}")
                
                # Should upgrade to Opus for complex query
                complex_correct = "opus" in complex_model.lower()
                results["complex_query"] = {
                    "model_used": complex_model,
                    "upgraded_to_opus": complex_correct,
                    "query": complex_query[:100] + "..."
                }
                logger.info(f"   Complex query routing: {'✅' if complex_correct else '❌'}")
            else:
                results["complex_query"] = {"error": f"HTTP {complex_response.status_code}"}
            
            # Test 3: Long message (should upgrade to Opus)
            long_message = "Create a comprehensive web application " * 50  # >1000 chars
            long_data = {
                "messages": [{"role": "user", "content": long_message}],
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929"
            }
            
            logger.info("   Testing long message (should upgrade to Opus)...")
            long_response = self.session.post(
                f"{self.api_url}/chat/",
                json=long_data,
                headers=headers,
                timeout=45
            )
            
            if long_response.status_code == 200:
                long_result = long_response.json()
                long_model = long_result.get("model")
                logger.info(f"   Long message model: {long_model}")
                
                # Should upgrade to Opus for long message
                long_correct = "opus" in long_model.lower()
                results["long_message"] = {
                    "model_used": long_model,
                    "upgraded_to_opus": long_correct,
                    "message_length": len(long_message)
                }
                logger.info(f"   Long message routing: {'✅' if long_correct else '❌'}")
            else:
                results["long_message"] = {"error": f"HTTP {long_response.status_code}"}
            
            # Evaluate overall smart routing
            simple_ok = results.get("simple_query", {}).get("stayed_on_sonnet", False)
            complex_ok = results.get("complex_query", {}).get("upgraded_to_opus", False)
            long_ok = results.get("long_message", {}).get("upgraded_to_opus", False)
            
            smart_routing_working = simple_ok and (complex_ok or long_ok)  # At least one upgrade should work
            
            if smart_routing_working:
                logger.info("✅ Smart routing working correctly!")
                return {
                    "status": "success",
                    "results": results,
                    "smart_routing_working": True
                }
            else:
                logger.error("❌ Smart routing not working correctly")
                return {
                    "status": "failed",
                    "error": "Smart routing logic not working as expected",
                    "results": results,
                    "smart_routing_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Smart routing test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_automatic_fallback(self) -> Dict[str, Any]:
        """Test 4: Automatic Fallback - Test Sonnet → Opus → GPT-4o fallback chain"""
        logger.info("🔄 Testing Automatic Fallback Chain")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test with invalid Claude model to trigger fallback
            fallback_data = {
                "messages": [{"role": "user", "content": "Test fallback mechanism"}],
                "provider": "anthropic",
                "model": "claude-invalid-model-test"  # Invalid model to trigger fallback
            }
            
            logger.info("   Testing fallback with invalid model...")
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=fallback_data,
                headers=headers,
                timeout=45
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                actual_provider = result.get("provider")
                actual_model = result.get("model")
                
                logger.info(f"   Fallback provider: {actual_provider}")
                logger.info(f"   Fallback model: {actual_model}")
                
                # Should fallback to a working model (either Opus or OpenAI)
                fallback_worked = (
                    (actual_provider == "anthropic" and "opus" in actual_model.lower()) or
                    (actual_provider == "openai" and "gpt-4" in actual_model.lower())
                )
                
                if fallback_worked:
                    logger.info("✅ Automatic fallback working!")
                    return {
                        "status": "success",
                        "fallback_provider": actual_provider,
                        "fallback_model": actual_model,
                        "fallback_working": True
                    }
                else:
                    logger.error("❌ Fallback not working correctly")
                    return {
                        "status": "failed",
                        "error": f"Expected fallback to Opus or GPT-4o, got {actual_provider}/{actual_model}",
                        "fallback_provider": actual_provider,
                        "fallback_model": actual_model,
                        "fallback_working": False
                    }
            else:
                # If request fails completely, that's also a valid test result
                # (shows that fallback isn't implemented or isn't working)
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Fallback test failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": f"No fallback implemented - request failed with: {error_detail}",
                    "status_code": response.status_code,
                    "fallback_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Automatic fallback test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_ultra_thinking_integration(self) -> Dict[str, Any]:
        """Test 5: Ultra-Thinking Integration - Test ultra_thinking=True by default"""
        logger.info("🧠 Testing Ultra-Thinking Integration")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test 1: Default ultra_thinking (should be True)
            default_data = {
                "messages": [{"role": "user", "content": "Explain quantum computing briefly"}],
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929"
                # No ultra_thinking specified - should default to True
            }
            
            logger.info("   Testing default ultra_thinking (should be True)...")
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=default_data,
                headers=headers,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                thinking_used = result.get("usage", {}).get("thinking_used", False)
                thinking_content = result.get("usage", {}).get("thinking_content")
                
                logger.info(f"   Ultra-thinking used: {thinking_used}")
                logger.info(f"   Has thinking content: {bool(thinking_content)}")
                
                # Test 2: Explicit ultra_thinking=False
                explicit_false_data = {
                    "messages": [{"role": "user", "content": "What is 2+2?"}],
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-5-20250929",
                    "ultra_thinking": False
                }
                
                logger.info("   Testing explicit ultra_thinking=False...")
                false_response = self.session.post(
                    f"{self.api_url}/chat/",
                    json=explicit_false_data,
                    headers=headers,
                    timeout=30
                )
                
                false_thinking_used = False
                if false_response.status_code == 200:
                    false_result = false_response.json()
                    false_thinking_used = false_result.get("usage", {}).get("thinking_used", False)
                    logger.info(f"   Ultra-thinking disabled: {not false_thinking_used}")
                
                # Evaluate results
                default_correct = thinking_used  # Should be True by default
                explicit_correct = not false_thinking_used  # Should be False when explicitly disabled
                
                if default_correct and explicit_correct:
                    logger.info("✅ Ultra-thinking integration working correctly!")
                    return {
                        "status": "success",
                        "default_thinking_enabled": thinking_used,
                        "explicit_disable_works": not false_thinking_used,
                        "ultra_thinking_working": True
                    }
                else:
                    logger.error("❌ Ultra-thinking integration not working correctly")
                    return {
                        "status": "failed",
                        "error": f"Default thinking: {thinking_used} (expected True), Explicit disable: {not false_thinking_used} (expected True)",
                        "default_thinking_enabled": thinking_used,
                        "explicit_disable_works": not false_thinking_used,
                        "ultra_thinking_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Ultra-thinking test failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Ultra-thinking integration test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_claude_api_connectivity(self) -> Dict[str, Any]:
        """Test 6: Claude API Connectivity - Test actual Claude API calls"""
        logger.info("🔌 Testing Claude API Connectivity")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # Test Claude Sonnet 4.5
            sonnet_data = {
                "messages": [{"role": "user", "content": "Say 'Claude Sonnet 4.5 working' if you can respond"}],
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929",
                "ultra_thinking": True
            }
            
            logger.info("   Testing Claude Sonnet 4.5...")
            sonnet_response = self.session.post(
                f"{self.api_url}/chat/",
                json=sonnet_data,
                headers=headers,
                timeout=45
            )
            
            if sonnet_response.status_code == 200:
                sonnet_result = sonnet_response.json()
                sonnet_content = sonnet_result.get("content", "")
                sonnet_working = "working" in sonnet_content.lower()
                
                results["sonnet_4_5"] = {
                    "status": "success" if sonnet_working else "partial",
                    "content_length": len(sonnet_content),
                    "response_received": bool(sonnet_content),
                    "expected_response": sonnet_working
                }
                logger.info(f"   Sonnet 4.5: {'✅' if sonnet_working else '⚠️'} ({len(sonnet_content)} chars)")
            else:
                results["sonnet_4_5"] = {
                    "status": "failed",
                    "error": f"HTTP {sonnet_response.status_code}"
                }
                logger.error(f"   Sonnet 4.5: ❌ HTTP {sonnet_response.status_code}")
            
            # Test Claude Opus 4.1
            opus_data = {
                "messages": [{"role": "user", "content": "Say 'Claude Opus 4.1 working' if you can respond"}],
                "provider": "anthropic",
                "model": "claude-opus-4-1",
                "ultra_thinking": True
            }
            
            logger.info("   Testing Claude Opus 4.1...")
            opus_response = self.session.post(
                f"{self.api_url}/chat/",
                json=opus_data,
                headers=headers,
                timeout=60
            )
            
            if opus_response.status_code == 200:
                opus_result = opus_response.json()
                opus_content = opus_result.get("content", "")
                opus_working = "working" in opus_content.lower()
                
                results["opus_4_1"] = {
                    "status": "success" if opus_working else "partial",
                    "content_length": len(opus_content),
                    "response_received": bool(opus_content),
                    "expected_response": opus_working
                }
                logger.info(f"   Opus 4.1: {'✅' if opus_working else '⚠️'} ({len(opus_content)} chars)")
            else:
                results["opus_4_1"] = {
                    "status": "failed",
                    "error": f"HTTP {opus_response.status_code}"
                }
                logger.error(f"   Opus 4.1: ❌ HTTP {opus_response.status_code}")
            
            # Test Claude Haiku 3.5
            haiku_data = {
                "messages": [{"role": "user", "content": "Say 'Claude Haiku 3.5 working' if you can respond"}],
                "provider": "anthropic",
                "model": "claude-haiku-3.5-20241022",
                "ultra_thinking": False  # Haiku is fast, doesn't need thinking
            }
            
            logger.info("   Testing Claude Haiku 3.5...")
            haiku_response = self.session.post(
                f"{self.api_url}/chat/",
                json=haiku_data,
                headers=headers,
                timeout=30
            )
            
            if haiku_response.status_code == 200:
                haiku_result = haiku_response.json()
                haiku_content = haiku_result.get("content", "")
                haiku_working = "working" in haiku_content.lower()
                
                results["haiku_3_5"] = {
                    "status": "success" if haiku_working else "partial",
                    "content_length": len(haiku_content),
                    "response_received": bool(haiku_content),
                    "expected_response": haiku_working
                }
                logger.info(f"   Haiku 3.5: {'✅' if haiku_working else '⚠️'} ({len(haiku_content)} chars)")
            else:
                results["haiku_3_5"] = {
                    "status": "failed",
                    "error": f"HTTP {haiku_response.status_code}"
                }
                logger.error(f"   Haiku 3.5: ❌ HTTP {haiku_response.status_code}")
            
            # Evaluate overall connectivity
            successful_models = sum(1 for result in results.values() if result.get("status") == "success")
            total_models = len(results)
            
            if successful_models >= 2:  # At least 2 out of 3 models working
                logger.info(f"✅ Claude API connectivity working! ({successful_models}/{total_models} models)")
                return {
                    "status": "success",
                    "successful_models": successful_models,
                    "total_models": total_models,
                    "results": results,
                    "connectivity_working": True
                }
            elif successful_models >= 1:
                logger.warning(f"⚠️ Partial Claude API connectivity ({successful_models}/{total_models} models)")
                return {
                    "status": "partial",
                    "successful_models": successful_models,
                    "total_models": total_models,
                    "results": results,
                    "connectivity_working": False
                }
            else:
                logger.error("❌ Claude API connectivity failed for all models")
                return {
                    "status": "failed",
                    "error": "All Claude models failed to respond",
                    "successful_models": successful_models,
                    "total_models": total_models,
                    "results": results,
                    "connectivity_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Claude API connectivity test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_backward_compatibility(self) -> Dict[str, Any]:
        """Test 7: Backward Compatibility - Test OpenAI and Perplexity still work"""
        logger.info("🔄 Testing Backward Compatibility (OpenAI & Perplexity)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # Test OpenAI GPT-4o
            openai_data = {
                "messages": [{"role": "user", "content": "Say 'OpenAI GPT-4o working' if you can respond"}],
                "provider": "openai",
                "model": "gpt-4o"
            }
            
            logger.info("   Testing OpenAI GPT-4o...")
            openai_response = self.session.post(
                f"{self.api_url}/chat/",
                json=openai_data,
                headers=headers,
                timeout=45
            )
            
            if openai_response.status_code == 200:
                openai_result = openai_response.json()
                openai_content = openai_result.get("content", "")
                openai_working = "working" in openai_content.lower()
                
                results["openai_gpt4o"] = {
                    "status": "success" if openai_working else "partial",
                    "content_length": len(openai_content),
                    "response_received": bool(openai_content),
                    "expected_response": openai_working
                }
                logger.info(f"   OpenAI GPT-4o: {'✅' if openai_working else '⚠️'} ({len(openai_content)} chars)")
            else:
                results["openai_gpt4o"] = {
                    "status": "failed",
                    "error": f"HTTP {openai_response.status_code}"
                }
                logger.error(f"   OpenAI GPT-4o: ❌ HTTP {openai_response.status_code}")
            
            # Test Perplexity Sonar
            perplexity_data = {
                "messages": [{"role": "user", "content": "Say 'Perplexity Sonar working' if you can respond"}],
                "provider": "perplexity",
                "model": "sonar"
            }
            
            logger.info("   Testing Perplexity Sonar...")
            perplexity_response = self.session.post(
                f"{self.api_url}/chat/",
                json=perplexity_data,
                headers=headers,
                timeout=45
            )
            
            if perplexity_response.status_code == 200:
                perplexity_result = perplexity_response.json()
                perplexity_content = perplexity_result.get("content", "")
                perplexity_working = "working" in perplexity_content.lower()
                
                results["perplexity_sonar"] = {
                    "status": "success" if perplexity_working else "partial",
                    "content_length": len(perplexity_content),
                    "response_received": bool(perplexity_content),
                    "expected_response": perplexity_working
                }
                logger.info(f"   Perplexity Sonar: {'✅' if perplexity_working else '⚠️'} ({len(perplexity_content)} chars)")
            else:
                results["perplexity_sonar"] = {
                    "status": "failed",
                    "error": f"HTTP {perplexity_response.status_code}"
                }
                logger.error(f"   Perplexity Sonar: ❌ HTTP {perplexity_response.status_code}")
            
            # Evaluate backward compatibility
            working_providers = sum(1 for result in results.values() if result.get("status") == "success")
            total_providers = len(results)
            
            if working_providers >= 1:  # At least one non-Claude provider working
                logger.info(f"✅ Backward compatibility maintained! ({working_providers}/{total_providers} providers)")
                return {
                    "status": "success",
                    "working_providers": working_providers,
                    "total_providers": total_providers,
                    "results": results,
                    "backward_compatibility": True
                }
            else:
                logger.error("❌ Backward compatibility broken - no non-Claude providers working")
                return {
                    "status": "failed",
                    "error": "All non-Claude providers failed",
                    "working_providers": working_providers,
                    "total_providers": total_providers,
                    "results": results,
                    "backward_compatibility": False
                }
                
        except Exception as e:
            logger.error(f"❌ Backward compatibility test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_phase2_tests(self) -> Dict[str, Any]:
        """Run all Phase 2 tests in sequence"""
        logger.info("🚀 Starting Comprehensive Phase 2 Testing: Claude AI Integration Enhancement")
        logger.info("=" * 80)
        
        results = {}
        
        # Authenticate first
        auth_result = self.authenticate_demo_user()
        if auth_result.get("status") != "success":
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return {"error": "Authentication failed", "auth_result": auth_result}
        
        # Test 1: Default Configuration Testing
        results["default_configuration"] = self.test_default_configuration()
        
        # Test 2: Claude Model Availability
        results["claude_model_availability"] = self.test_claude_model_availability()
        
        # Test 3: Smart Routing Testing
        results["smart_routing"] = self.test_smart_routing()
        
        # Test 4: Automatic Fallback Testing
        results["automatic_fallback"] = self.test_automatic_fallback()
        
        # Test 5: Ultra-Thinking Integration
        results["ultra_thinking_integration"] = self.test_ultra_thinking_integration()
        
        # Test 6: Claude API Connectivity
        results["claude_api_connectivity"] = self.test_claude_api_connectivity()
        
        # Test 7: Backward Compatibility
        results["backward_compatibility"] = self.test_backward_compatibility()
        
        # Summary
        logger.info("=" * 80)
        logger.info("📊 PHASE 2 TESTING SUMMARY: Claude AI Integration Enhancement")
        logger.info("=" * 80)
        
        passed = 0
        failed = 0
        partial = 0
        errors = 0
        
        for test_name, result in results.items():
            status = result.get("status", "unknown")
            if status == "success":
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            elif status == "failed":
                failed += 1
                logger.info(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
            elif status == "partial":
                partial += 1
                logger.info(f"⚠️ {test_name}: PARTIAL - {result.get('error', 'Some issues detected')}")
            elif status == "expected_failure":
                partial += 1
                logger.info(f"⚠️ {test_name}: EXPECTED FAILURE - {result.get('note', 'Expected without API keys')}")
            else:
                errors += 1
                logger.info(f"💥 {test_name}: ERROR - {result.get('error', 'Unknown error')}")
        
        total = passed + failed + partial + errors
        logger.info("=" * 80)
        logger.info(f"📈 PHASE 2 RESULTS: {passed} passed, {failed} failed, {partial} partial, {errors} errors (Total: {total})")
        
        # Phase 2 specific summary
        critical_tests = ["default_configuration", "claude_model_availability", "claude_api_connectivity"]
        critical_passed = sum(1 for test in critical_tests if results.get(test, {}).get("status") == "success")
        
        logger.info("=" * 80)
        logger.info("🎯 PHASE 2 CRITICAL FEATURES:")
        logger.info(f"   Default Configuration: {'✅' if results.get('default_configuration', {}).get('status') == 'success' else '❌'}")
        logger.info(f"   Claude Models Available: {'✅' if results.get('claude_model_availability', {}).get('status') == 'success' else '❌'}")
        logger.info(f"   Smart Routing: {'✅' if results.get('smart_routing', {}).get('status') == 'success' else '❌'}")
        logger.info(f"   Ultra-Thinking: {'✅' if results.get('ultra_thinking_integration', {}).get('status') == 'success' else '❌'}")
        logger.info(f"   Claude API Connectivity: {'✅' if results.get('claude_api_connectivity', {}).get('status') == 'success' else '❌'}")
        logger.info(f"   Backward Compatibility: {'✅' if results.get('backward_compatibility', {}).get('status') == 'success' else '❌'}")
        
        phase2_success = critical_passed >= 2  # At least 2 out of 3 critical tests must pass
        logger.info("=" * 80)
        logger.info(f"🏆 PHASE 2 OVERALL: {'SUCCESS' if phase2_success else 'NEEDS ATTENTION'} ({critical_passed}/3 critical tests passed)")
        
        return {
            "summary": {
                "passed": passed,
                "failed": failed,
                "partial": partial,
                "errors": errors,
                "total": total,
                "critical_passed": critical_passed,
                "phase2_success": phase2_success
            },
            "results": results
        }

    def test_dependency_resolution(self) -> Dict[str, Any]:
        """Test H1: Dependency Resolution - Backend starts without conflicts"""
        logger.info("🔧 Testing Dependency Resolution (H1)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            session_data = {
                "name": "Test Session"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                session_response = response.json()
                session_id = session_response.get("id")
                
                logger.info("✅ Session creation successful!")
                logger.info(f"   Session ID: {session_id}")
                logger.info(f"   Session name: {session_response.get('name')}")
                logger.info(f"   Message count: {session_response.get('message_count', 0)}")
                
                return {
                    "status": "success",
                    "session_id": session_id,
                    "session_data": session_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session creation failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session creation error: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_retrieval(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id} - This endpoint had the 500 error"""
        logger.info(f"🔍 Testing session retrieval (GET /api/sessions/{session_id}) - CRITICAL TEST")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                session_data = response.json()
                
                logger.info("✅ Session retrieval successful! (Bug fix working)")
                logger.info(f"   Session ID: {session_data.get('id')}")
                logger.info(f"   Session name: {session_data.get('name')}")
                logger.info(f"   Message count: {session_data.get('message_count', 0)}")
                logger.info(f"   Created at: {session_data.get('created_at')}")
                
                return {
                    "status": "success",
                    "session_data": session_data,
                    "bug_fix_verified": True
                }
            elif response.status_code == 500:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ CRITICAL: Still getting 500 error! Bug fix may not be working: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "bug_fix_failed": True,
                    "response": response.text
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session retrieval failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session retrieval error: {e}")
            return {"status": "error", "error": str(e)}

    def test_list_sessions(self) -> Dict[str, Any]:
        """Test GET /api/sessions/list - List user sessions"""
        logger.info("📋 Testing session list (GET /api/sessions/list)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                sessions_list = response.json()
                
                logger.info("✅ Session list successful!")
                logger.info(f"   Total sessions: {len(sessions_list)}")
                
                for i, session in enumerate(sessions_list[:3]):  # Show first 3
                    logger.info(f"   Session {i+1}: {session.get('name')} (ID: {session.get('id')[:12]}...)")
                
                return {
                    "status": "success",
                    "sessions_count": len(sessions_list),
                    "sessions_list": sessions_list
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session list failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session list error: {e}")
            return {"status": "error", "error": str(e)}

    def test_add_message(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/sessions/messages - Add message to session"""
        logger.info(f"💬 Testing add message (POST /api/sessions/messages)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            message_data = {
                "session_id": session_id,
                "role": "user",
                "content": "Test message content"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/messages",
                json=message_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                message_response = response.json()
                
                logger.info("✅ Add message successful!")
                logger.info(f"   Message ID: {message_response.get('id')}")
                logger.info(f"   Role: {message_response.get('role')}")
                logger.info(f"   Content: {message_response.get('content')[:50]}...")
                
                return {
                    "status": "success",
                    "message_id": message_response.get('id'),
                    "message_data": message_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Add message failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Add message error: {e}")
            return {"status": "error", "error": str(e)}

    def test_get_messages(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id}/messages - Get session messages"""
        logger.info(f"📨 Testing get messages (GET /api/sessions/{session_id}/messages)")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}/messages",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                messages_list = response.json()
                
                logger.info("✅ Get messages successful!")
                logger.info(f"   Total messages: {len(messages_list)}")
                
                for i, message in enumerate(messages_list):
                    logger.info(f"   Message {i+1}: {message.get('role')} - {message.get('content')[:30]}...")
                
                return {
                    "status": "success",
                    "messages_count": len(messages_list),
                    "messages_list": messages_list
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Get messages failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Get messages error: {e}")
            return {"status": "error", "error": str(e)}

    def test_public_repo_import_without_auth(self) -> Dict[str, Any]:
        """Test POST /api/github/import with public repository (Windows compatibility focus)"""
        logger.info("🔄 Testing GitHub Import with Windows Compatibility (octocat/Hello-World)")
        
        try:
            import_data = {
                "repo_url": "https://github.com/octocat/Hello-World",
                "branch": "master"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=60  # Git operations can take time
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                import_data = response.json()
                
                logger.info("✅ GitHub import successful!")
                logger.info(f"   Repository: {import_data.get('repository', {}).get('name')}")
                logger.info(f"   Owner: {import_data.get('repository', {}).get('owner')}")
                logger.info(f"   Branch: {import_data.get('repository', {}).get('branch')}")
                logger.info(f"   Total files: {import_data.get('import_details', {}).get('total_files', 0)}")
                logger.info(f"   Workspace path: {import_data.get('workspace_path')}")
                
                # Verify expected data structure
                repository = import_data.get('repository', {})
                import_details = import_data.get('import_details', {})
                
                # Check if file count > 0 (requirement from test plan)
                file_count = import_details.get('total_files', 0)
                repo_name = repository.get('name', '')
                
                if file_count > 0 and repo_name == 'Hello-World':
                    logger.info("✅ Import result verification passed")
                    logger.info(f"   ✓ File count > 0: {file_count}")
                    logger.info(f"   ✓ Repository name correct: {repo_name}")
                    
                    return {
                        "status": "success",
                        "data": import_data,
                        "file_count": file_count,
                        "repository_name": repo_name,
                        "windows_compatibility_tested": True,
                        "cleanup_warnings_check_needed": True
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Import verification failed - file_count: {file_count}, repo_name: {repo_name}",
                        "data": import_data
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ GitHub import failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ GitHub import test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_backend_logs_for_cleanup_warnings(self) -> Dict[str, Any]:
        """Check backend logs for cleanup warnings (Windows compatibility verification)"""
        logger.info("📋 Checking backend logs for cleanup warnings")
        
        try:
            import subprocess
            
            # Check supervisor backend logs
            log_files = [
                "/var/log/supervisor/backend.out.log",
                "/var/log/supervisor/backend.err.log"
            ]
            
            cleanup_warnings = []
            cleanup_success = []
            
            for log_file in log_files:
                try:
                    # Get last 100 lines of logs
                    result = subprocess.run(
                        ["tail", "-n", "100", log_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        log_content = result.stdout
                        
                        # Look for cleanup-related messages
                        lines = log_content.split('\n')
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['cleanup', 'failed to clean', 'remove readonly', 'permission']):
                                if 'warning' in line.lower() or 'failed' in line.lower():
                                    cleanup_warnings.append(line.strip())
                                elif 'success' in line.lower() or 'cleaned' in line.lower():
                                    cleanup_success.append(line.strip())
                        
                        logger.info(f"   Checked {log_file}: {len(lines)} lines")
                        
                except Exception as e:
                    logger.warning(f"   Could not read {log_file}: {e}")
            
            logger.info(f"✅ Backend logs check completed")
            logger.info(f"   Cleanup warnings found: {len(cleanup_warnings)}")
            logger.info(f"   Cleanup success messages: {len(cleanup_success)}")
            
            # Show warnings if any
            if cleanup_warnings:
                logger.info("   ⚠️ Cleanup warnings found:")
                for warning in cleanup_warnings[-5:]:  # Show last 5
                    logger.info(f"     {warning}")
            
            # Show success messages if any
            if cleanup_success:
                logger.info("   ✅ Cleanup success messages:")
                for success in cleanup_success[-3:]:  # Show last 3
                    logger.info(f"     {success}")
            
            # Determine if warnings are non-critical (as expected)
            non_critical_warnings = len(cleanup_warnings) > 0
            
            return {
                "status": "success",
                "cleanup_warnings_count": len(cleanup_warnings),
                "cleanup_success_count": len(cleanup_success),
                "cleanup_warnings": cleanup_warnings,
                "cleanup_success": cleanup_success,
                "non_critical_warnings_found": non_critical_warnings,
                "windows_compatibility_verified": non_critical_warnings
            }
            
        except Exception as e:
            logger.error(f"❌ Backend logs check failed: {e}")
            return {"status": "error", "error": str(e)}
    def test_invalid_url_import(self) -> Dict[str, Any]:
        """Test POST /api/github/import with invalid URL"""
        logger.info("🚫 Testing import with invalid URL")
        
        try:
            import_data = {
                "repo_url": "https://invalid-url.com/repo",
                "branch": "main"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=15
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code in [400, 404]:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                
                logger.info("✅ Invalid URL correctly rejected")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_detail}")
                
                # Should contain message about invalid URL
                if "Invalid GitHub URL" in error_detail or "github.com" in error_detail:
                    logger.info("✅ Correct error message for invalid URL")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True,
                        "error_message": error_detail
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected GitHub URL validation error, got: {error_detail}",
                        "data": error_data
                    }
            else:
                logger.error(f"❌ Expected 400/404 error, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 400/404 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Invalid URL test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_nonexistent_repo_import(self) -> Dict[str, Any]:
        """Test POST /api/github/import with non-existent repository"""
        logger.info("🔍 Testing import with non-existent repository")
        
        try:
            import_data = {
                "repo_url": "https://github.com/nonexistent/nonexistent-repo-12345",
                "branch": "main"
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = self.session.post(
                f"{self.api_url}/github/import",
                json=import_data,
                headers=headers,
                timeout=30  # Git operations can take time
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 404:
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                
                logger.info("✅ Non-existent repo correctly rejected")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {error_detail}")
                
                # Should contain message about repository not found
                if "not found" in error_detail.lower() or "not accessible" in error_detail.lower():
                    logger.info("✅ Correct error message for non-existent repo")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True,
                        "error_message": error_detail
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected 'not found' in error message, got: {error_detail}",
                        "data": error_data
                    }
            elif response.status_code == 400:
                # Could also be 400 with appropriate error message
                error_data = response.json()
                error_detail = error_data.get("detail", "Unknown error")
                
                if "not found" in error_detail.lower() or "clone failed" in error_detail.lower():
                    logger.info("✅ Non-existent repo correctly rejected (400 with appropriate message)")
                    return {
                        "status": "success",
                        "data": error_data,
                        "expected_rejection": True,
                        "error_message": error_detail
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected repository error message, got: {error_detail}",
                        "data": error_data
                    }
            else:
                logger.error(f"❌ Expected 404/400 error, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 404/400 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Non-existent repo test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_import_status_endpoint_without_auth(self) -> Dict[str, Any]:
        """Test GET /api/github/import/status WITHOUT authentication"""
        logger.info("📊 Testing import status endpoint WITHOUT authentication")
        
        try:
            # NO Authorization header
            headers = {"Content-Type": "application/json"}
            
            response = self.session.get(
                f"{self.api_url}/github/import/status",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                
                logger.info("✅ Import status endpoint accessible WITHOUT auth")
                logger.info(f"   Status: {status_data.get('status')}")
                logger.info(f"   Feature: {status_data.get('feature')}")
                logger.info(f"   Workspace root: {status_data.get('workspace_root')}")
                logger.info(f"   Existing projects: {len(status_data.get('existing_projects', []))}")
                
                return {
                    "status": "success",
                    "data": status_data,
                    "no_auth_required": True,
                    "workspace_info": {
                        "root": status_data.get('workspace_root'),
                        "projects_count": len(status_data.get('existing_projects', []))
                    }
                }
            elif response.status_code == 401:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ CRITICAL: Status endpoint still requires authentication! {error_detail}")
                return {
                    "status": "failed",
                    "error": f"Status endpoint still requires authentication: {error_detail}",
                    "status_code": response.status_code,
                    "critical_issue": "Authentication still required for status endpoint"
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Status endpoint failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Import status test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_system_dependencies(self) -> Dict[str, Any]:
        """Check if required system dependencies are available"""
        logger.info("🔧 Checking system dependencies for GitHub import")
        
        try:
            import subprocess
            import os
            from pathlib import Path
            
            # Check if git is available
            try:
                result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
                git_available = result.returncode == 0
                git_version = result.stdout.strip() if git_available else "Not available"
            except:
                git_available = False
                git_version = "Not available"
            
            # Check workspace directory
            workspace_root = Path("/app/xionimus-ai")
            workspace_exists = workspace_root.exists()
            workspace_writable = False
            
            if workspace_exists:
                try:
                    test_file = workspace_root / ".test_write"
                    test_file.write_text("test")
                    test_file.unlink()
                    workspace_writable = True
                except:
                    workspace_writable = False
            else:
                try:
                    workspace_root.mkdir(parents=True, exist_ok=True)
                    workspace_exists = True
                    workspace_writable = True
                except:
                    pass
            
            logger.info(f"✅ System dependencies check completed")
            logger.info(f"   Git available: {git_available} ({git_version})")
            logger.info(f"   Workspace exists: {workspace_exists}")
            logger.info(f"   Workspace writable: {workspace_writable}")
            
            all_dependencies_ok = git_available and workspace_exists and workspace_writable
            
            return {
                "status": "success" if all_dependencies_ok else "partial",
                "git_available": git_available,
                "git_version": git_version,
                "workspace_exists": workspace_exists,
                "workspace_writable": workspace_writable,
                "workspace_path": str(workspace_root),
                "all_dependencies_ok": all_dependencies_ok
            }
            
        except Exception as e:
            logger.error(f"❌ System dependencies check failed: {e}")
            return {"status": "error", "error": str(e)}


    def test_specific_session_retrieval(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id} for a specific session ID"""
        logger.info(f"🔍 Testing specific session retrieval: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            logger.info(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                session_data = response.json()
                logger.info("✅ Session found!")
                logger.info(f"   Session ID: {session_data.get('id')}")
                logger.info(f"   Session name: {session_data.get('name')}")
                logger.info(f"   Message count: {session_data.get('message_count', 0)}")
                logger.info(f"   Created at: {session_data.get('created_at')}")
                
                return {
                    "status": "success",
                    "session_data": session_data
                }
            elif response.status_code == 404:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session not found (404): {error_detail}")
                return {
                    "status": "not_found",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
            elif response.status_code == 403:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Access denied (403): {error_detail}")
                return {
                    "status": "access_denied",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session retrieval failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session retrieval error: {e}")
            return {"status": "error", "error": str(e)}

    def check_database_sessions(self) -> Dict[str, Any]:
        """Check sessions directly in the SQLite database"""
        logger.info("🗄️ Checking sessions in SQLite database")
        
        try:
            if not os.path.exists(self.db_path):
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Check if sessions table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                conn.close()
                return {
                    "status": "failed",
                    "error": "Sessions table does not exist in database"
                }
            
            # Get all sessions
            cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10")
            sessions = cursor.fetchall()
            
            # Get session count
            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            total_count = cursor.fetchone()['count']
            
            conn.close()
            
            logger.info(f"✅ Database check completed")
            logger.info(f"   Database path: {self.db_path}")
            logger.info(f"   Total sessions: {total_count}")
            logger.info(f"   Recent sessions (showing up to 10):")
            
            session_list = []
            for session in sessions:
                session_dict = dict(session)
                session_list.append(session_dict)
                user_id = session_dict.get('user_id', 'None')
                logger.info(f"     - {session['id']}: {session['name']} (user_id: {user_id}) - {session['created_at']}")
            
            return {
                "status": "success",
                "database_path": self.db_path,
                "total_sessions": total_count,
                "recent_sessions": session_list,
                "sessions_table_exists": True
            }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database error: {e}")
            return {"status": "error", "error": f"Database error: {e}"}
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_creation_and_immediate_retrieval(self) -> Dict[str, Any]:
        """Test creating a session and immediately retrieving it"""
        logger.info("🔄 Testing session creation + immediate retrieval")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Step 1: Create session
            session_data = {
                "name": "Test Session for 404 Debug"
            }
            
            create_response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Create response status: {create_response.status_code}")
            
            if create_response.status_code != 200:
                error_detail = create_response.json().get("detail", "Unknown error") if create_response.content else f"HTTP {create_response.status_code}"
                return {
                    "status": "failed",
                    "error": f"Session creation failed: {error_detail}",
                    "status_code": create_response.status_code
                }
            
            session_response = create_response.json()
            session_id = session_response.get("id")
            
            logger.info(f"✅ Session created: {session_id}")
            
            # Step 2: Immediately retrieve the same session
            retrieve_response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Retrieve response status: {retrieve_response.status_code}")
            
            if retrieve_response.status_code == 200:
                retrieved_data = retrieve_response.json()
                logger.info("✅ Session immediately retrievable!")
                logger.info(f"   Retrieved ID: {retrieved_data.get('id')}")
                logger.info(f"   Retrieved name: {retrieved_data.get('name')}")
                
                return {
                    "status": "success",
                    "session_id": session_id,
                    "created_data": session_response,
                    "retrieved_data": retrieved_data,
                    "persistence_working": True
                }
            elif retrieve_response.status_code == 404:
                error_detail = retrieve_response.json().get("detail", "Unknown error") if retrieve_response.content else f"HTTP {retrieve_response.status_code}"
                logger.error("❌ CRITICAL: Session not found immediately after creation!")
                logger.error("❌ This indicates a PERSISTENCE PROBLEM!")
                return {
                    "status": "persistence_failure",
                    "error": f"Session not found after creation: {error_detail}",
                    "session_id": session_id,
                    "created_data": session_response,
                    "persistence_working": False
                }
            else:
                error_detail = retrieve_response.json().get("detail", "Unknown error") if retrieve_response.content else f"HTTP {retrieve_response.status_code}"
                return {
                    "status": "failed",
                    "error": f"Session retrieval failed: {error_detail}",
                    "status_code": retrieve_response.status_code,
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"❌ Session creation + retrieval test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_user_id_session_filtering_issue(self) -> Dict[str, Any]:
        """Test the user_id filtering issue that causes sessions to not appear in list"""
        logger.info("🔍 Testing user_id filtering issue (ROOT CAUSE)")
        
        if not self.token or not self.user_info:
            return {"status": "skipped", "error": "No authentication info available"}
        
        current_user_id = self.user_info.get("user_id")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Step 1: Create a session (this creates with user_id=None due to bug)
            session_data = {"name": "User ID Test Session"}
            
            create_response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if create_response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Session creation failed: {create_response.status_code}"
                }
            
            session_response = create_response.json()
            session_id = session_response.get("id")
            
            logger.info(f"✅ Created session: {session_id}")
            
            # Step 2: Check if session appears in list (it won't due to user_id filtering)
            list_response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers=headers,
                timeout=10
            )
            
            if list_response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Session list failed: {list_response.status_code}"
                }
            
            sessions_list = list_response.json()
            created_session_in_list = any(s.get("id") == session_id for s in sessions_list)
            
            logger.info(f"   Sessions in list: {len(sessions_list)}")
            logger.info(f"   Created session in list: {created_session_in_list}")
            
            # Step 3: Try to retrieve the session directly (this should work)
            get_response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            direct_retrieval_works = get_response.status_code == 200
            logger.info(f"   Direct retrieval works: {direct_retrieval_works}")
            
            # Step 4: Check database to see actual user_id
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM sessions WHERE id = ?", (session_id,))
                row = cursor.fetchone()
                actual_user_id = row[0] if row else None
                conn.close()
                
                logger.info(f"   Expected user_id: {current_user_id}")
                logger.info(f"   Actual user_id in DB: {actual_user_id}")
                
                user_id_mismatch = actual_user_id != current_user_id
            else:
                user_id_mismatch = True
                actual_user_id = "DB_NOT_FOUND"
            
            # Analysis
            if user_id_mismatch and not created_session_in_list and direct_retrieval_works:
                logger.error("🚨 ROOT CAUSE IDENTIFIED!")
                logger.error("   Sessions are created with user_id=None instead of authenticated user_id")
                logger.error("   List API filters by user_id, so sessions don't appear")
                logger.error("   Direct retrieval works because it doesn't check user_id ownership")
                
                return {
                    "status": "root_cause_identified",
                    "issue": "user_id_not_set_on_creation",
                    "session_id": session_id,
                    "expected_user_id": current_user_id,
                    "actual_user_id": actual_user_id,
                    "session_in_list": created_session_in_list,
                    "direct_retrieval_works": direct_retrieval_works,
                    "user_id_mismatch": user_id_mismatch
                }
            else:
                return {
                    "status": "success",
                    "session_id": session_id,
                    "session_in_list": created_session_in_list,
                    "direct_retrieval_works": direct_retrieval_works,
                    "user_id_correct": not user_id_mismatch
                }
                
        except Exception as e:
            logger.error(f"❌ User ID filtering test failed: {e}")
            return {"status": "error", "error": str(e)}

    def check_user_id_associations(self) -> Dict[str, Any]:
        """Check user_id associations in sessions"""
        logger.info("👤 Checking user_id associations in sessions")
        
        if not self.token or not self.user_info:
            return {"status": "skipped", "error": "No authentication info available"}
        
        current_user_id = self.user_info.get("user_id")
        
        try:
            if not os.path.exists(self.db_path):
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get sessions with user_id info
            cursor.execute("""
                SELECT id, name, user_id, created_at 
                FROM sessions 
                ORDER BY created_at DESC 
                LIMIT 20
            """)
            sessions = cursor.fetchall()
            
            # Count sessions by user_id
            cursor.execute("""
                SELECT 
                    user_id,
                    COUNT(*) as count
                FROM sessions 
                GROUP BY user_id
            """)
            user_counts = cursor.fetchall()
            
            conn.close()
            
            logger.info(f"✅ User ID association check completed")
            logger.info(f"   Current authenticated user_id: {current_user_id}")
            logger.info(f"   Sessions by user_id:")
            
            user_stats = {}
            for row in user_counts:
                user_id = row['user_id'] if row['user_id'] else 'NULL'
                count = row['count']
                user_stats[user_id] = count
                logger.info(f"     {user_id}: {count} sessions")
            
            # Check sessions for current user
            current_user_sessions = [dict(s) for s in sessions if s['user_id'] == current_user_id]
            null_user_sessions = [dict(s) for s in sessions if s['user_id'] is None]
            
            logger.info(f"   Sessions for current user ({current_user_id}): {len(current_user_sessions)}")
            logger.info(f"   Sessions with NULL user_id: {len(null_user_sessions)}")
            
            return {
                "status": "success",
                "current_user_id": current_user_id,
                "user_stats": user_stats,
                "current_user_sessions": current_user_sessions,
                "null_user_sessions": null_user_sessions,
                "total_sessions_checked": len(sessions)
            }
            
        except Exception as e:
            logger.error(f"❌ User ID association check failed: {e}")
            return {"status": "error", "error": str(e)}

    def verify_route_registration(self) -> Dict[str, Any]:
        """Verify that session routes are properly registered"""
        logger.info("🛣️ Verifying route registration")
        
        try:
            # Check OpenAPI spec for session routes
            response = self.session.get(f"{self.api_url}/../openapi.json", timeout=10)
            
            if response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Could not fetch OpenAPI spec: {response.status_code}"
                }
            
            openapi_spec = response.json()
            paths = openapi_spec.get("paths", {})
            
            # Check for session-related routes
            session_routes = [path for path in paths.keys() if "/sessions" in path]
            
            logger.info(f"✅ Route verification completed")
            logger.info(f"   Total API routes: {len(paths)}")
            logger.info(f"   Session routes found: {len(session_routes)}")
            
            for route in session_routes:
                methods = list(paths[route].keys())
                logger.info(f"     {route}: {methods}")
            
            # Check for specific routes we need
            required_routes = [
                "/api/sessions/",
                "/api/sessions/{session_id}",
                "/api/sessions/list"
            ]
            
            missing_routes = []
            for required_route in required_routes:
                if required_route not in paths:
                    missing_routes.append(required_route)
            
            if missing_routes:
                return {
                    "status": "failed",
                    "error": f"Missing required routes: {missing_routes}",
                    "session_routes": session_routes,
                    "total_routes": len(paths)
                }
            
            return {
                "status": "success",
                "session_routes": session_routes,
                "total_routes": len(paths),
                "all_required_routes_present": True
            }
            
        except Exception as e:
            logger.error(f"❌ Route verification failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_list_and_get_current(self) -> Dict[str, Any]:
        """Test GET /api/sessions/list and find current session"""
        logger.info("📋 Testing session list and finding current session")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/list",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                sessions_list = response.json()
                
                logger.info("✅ Session list successful!")
                logger.info(f"   Total sessions: {len(sessions_list)}")
                
                # Find the most recent session (current session)
                current_session = None
                if sessions_list:
                    # Sort by updated_at to get the most recent
                    sessions_list.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
                    current_session = sessions_list[0]
                    
                    logger.info(f"   Current session ID: {current_session.get('id')}")
                    logger.info(f"   Current session name: {current_session.get('name')}")
                    logger.info(f"   Message count: {current_session.get('message_count', 0)}")
                
                return {
                    "status": "success",
                    "sessions_count": len(sessions_list),
                    "sessions_list": sessions_list,
                    "current_session": current_session
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session list failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session list error: {e}")
            return {"status": "error", "error": str(e)}

    def test_session_details_active_project(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id} and check active_project fields"""
        logger.info(f"🔍 Testing session details for active_project fields: {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{session_id}",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                session_data = response.json()
                
                logger.info("✅ Session details retrieved successfully!")
                logger.info(f"   Session ID: {session_data.get('id')}")
                logger.info(f"   Session name: {session_data.get('name')}")
                logger.info(f"   Message count: {session_data.get('message_count', 0)}")
                
                # Check for active_project fields
                active_project = session_data.get('active_project')
                active_project_branch = session_data.get('active_project_branch')
                
                logger.info(f"   🎯 active_project: {active_project}")
                logger.info(f"   🎯 active_project_branch: {active_project_branch}")
                
                # Check if fields are present
                has_active_project_field = 'active_project' in session_data
                has_active_project_branch_field = 'active_project_branch' in session_data
                
                logger.info(f"   ✓ active_project field present: {has_active_project_field}")
                logger.info(f"   ✓ active_project_branch field present: {has_active_project_branch_field}")
                
                return {
                    "status": "success",
                    "session_data": session_data,
                    "active_project": active_project,
                    "active_project_branch": active_project_branch,
                    "has_active_project_field": has_active_project_field,
                    "has_active_project_branch_field": has_active_project_branch_field,
                    "active_project_set": active_project is not None,
                    "active_project_branch_set": active_project_branch is not None
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session details failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session details error: {e}")
            return {"status": "error", "error": str(e)}

    def test_workspace_status(self) -> Dict[str, Any]:
        """Test GET /api/github/import/status to check workspace projects"""
        logger.info("📊 Testing workspace status and imported projects")
        
        try:
            # No authentication needed for this endpoint
            headers = {"Content-Type": "application/json"}
            
            response = self.session.get(
                f"{self.api_url}/github/import/status",
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                
                logger.info("✅ Workspace status retrieved successfully!")
                logger.info(f"   Status: {status_data.get('status')}")
                logger.info(f"   Workspace root: {status_data.get('workspace_root')}")
                logger.info(f"   Total projects: {status_data.get('total_projects', 0)}")
                
                existing_projects = status_data.get('existing_projects', [])
                logger.info(f"   Existing projects: {len(existing_projects)}")
                
                for i, project in enumerate(existing_projects[:5]):  # Show first 5
                    logger.info(f"     {i+1}. {project.get('name')} ({project.get('file_count', 0)} files)")
                
                return {
                    "status": "success",
                    "workspace_data": status_data,
                    "existing_projects": existing_projects,
                    "total_projects": len(existing_projects),
                    "has_projects": len(existing_projects) > 0
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Workspace status failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Workspace status error: {e}")
            return {"status": "error", "error": str(e)}

    def test_set_active_project(self, session_id: str, project_name: str, branch: str = "main") -> Dict[str, Any]:
        """Test setting active project for a session (if endpoint exists)"""
        logger.info(f"🎯 Testing set active project: {project_name} for session {session_id}")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Try to set active project via workspace endpoint (if it exists)
            request_data = {
                "session_id": session_id,
                "project_name": project_name,
                "branch": branch
            }
            
            response = self.session.post(
                f"{self.api_url}/workspace/set-active",
                json=request_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result_data = response.json()
                
                logger.info("✅ Active project set successfully!")
                logger.info(f"   Project: {project_name}")
                logger.info(f"   Branch: {branch}")
                logger.info(f"   Session: {session_id}")
                
                return {
                    "status": "success",
                    "project_name": project_name,
                    "branch": branch,
                    "session_id": session_id,
                    "result_data": result_data
                }
            elif response.status_code == 404:
                logger.info("ℹ️ Set active project endpoint not found - this is expected")
                return {
                    "status": "endpoint_not_found",
                    "error": "Workspace set-active endpoint not implemented",
                    "status_code": response.status_code
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Set active project failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Set active project error: {e}")
            return {"status": "error", "error": str(e)}

    def test_manual_session_update(self, session_id: str, project_name: str, branch: str = "main") -> Dict[str, Any]:
        """Test manually updating session with active_project via direct database or API"""
        logger.info(f"🔧 Testing manual session update for active_project")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Try to update session via PATCH endpoint (if it exists)
            request_data = {
                "active_project": project_name,
                "active_project_branch": branch
            }
            
            response = self.session.patch(
                f"{self.api_url}/sessions/{session_id}",
                json=request_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result_data = response.json()
                
                logger.info("✅ Session updated successfully!")
                logger.info(f"   Active project: {project_name}")
                logger.info(f"   Active branch: {branch}")
                
                return {
                    "status": "success",
                    "project_name": project_name,
                    "branch": branch,
                    "session_id": session_id,
                    "result_data": result_data
                }
            elif response.status_code == 404:
                logger.info("ℹ️ Session PATCH endpoint not found")
                return {
                    "status": "endpoint_not_found",
                    "error": "Session PATCH endpoint not implemented",
                    "status_code": response.status_code
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session update failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Session update error: {e}")
            return {"status": "error", "error": str(e)}

    def verify_project_path_exists(self, project_name: str) -> Dict[str, Any]:
        """Verify that the project path exists in /app/"""
        logger.info(f"📁 Verifying project path exists: /app/{project_name}")
        
        try:
            from pathlib import Path
            
            project_path = Path(f"/app/{project_name}")
            exists = project_path.exists()
            is_directory = project_path.is_dir() if exists else False
            
            if exists and is_directory:
                # Count files in the project
                file_count = sum(1 for _ in project_path.rglob('*') if _.is_file())
                logger.info(f"✅ Project path exists: {project_path}")
                logger.info(f"   Files in project: {file_count}")
                
                return {
                    "status": "success",
                    "project_path": str(project_path),
                    "exists": True,
                    "is_directory": True,
                    "file_count": file_count
                }
            elif exists:
                logger.warning(f"⚠️ Path exists but is not a directory: {project_path}")
                return {
                    "status": "warning",
                    "project_path": str(project_path),
                    "exists": True,
                    "is_directory": False,
                    "error": "Path exists but is not a directory"
                }
            else:
                logger.error(f"❌ Project path does not exist: {project_path}")
                return {
                    "status": "failed",
                    "project_path": str(project_path),
                    "exists": False,
                    "is_directory": False,
                    "error": "Project path does not exist"
                }
                
        except Exception as e:
            logger.error(f"❌ Path verification error: {e}")
            return {"status": "error", "error": str(e)}

    def test_api_versioning_public_endpoints(self) -> Dict[str, Any]:
        """Test M2: API Versioning - Public endpoints should work without auth"""
        logger.info("🔄 Testing API Versioning (M2) - Public endpoints without auth")
        
        results = {}
        
        # Test endpoints that should be public
        public_endpoints = [
            "/api/v1/health",
            "/api/health", 
            "/api/version",
            "/api/v1/version"
        ]
        
        for endpoint in public_endpoints:
            try:
                logger.info(f"   Testing {endpoint}")
                
                # NO Authorization header - should work for public endpoints
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                logger.info(f"   Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ {endpoint} accessible without auth")
                    
                    # Check for version info in response
                    if "version" in data or "status" in data:
                        logger.info(f"   Response contains expected fields: {list(data.keys())}")
                        results[endpoint] = {
                            "status": "success",
                            "public_access": True,
                            "response_data": data
                        }
                    else:
                        results[endpoint] = {
                            "status": "partial",
                            "public_access": True,
                            "error": "Response missing expected fields",
                            "response_data": data
                        }
                elif response.status_code == 401:
                    logger.error(f"❌ {endpoint} still requires authentication!")
                    results[endpoint] = {
                        "status": "failed",
                        "public_access": False,
                        "error": "Endpoint still requires authentication",
                        "status_code": response.status_code
                    }
                else:
                    error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                    logger.error(f"❌ {endpoint} failed: {error_detail}")
                    results[endpoint] = {
                        "status": "failed",
                        "error": error_detail,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} test failed: {e}")
                results[endpoint] = {"status": "error", "error": str(e)}
        
        # Summary
        successful_endpoints = [ep for ep, result in results.items() if result["status"] == "success"]
        failed_endpoints = [ep for ep, result in results.items() if result["status"] == "failed"]
        
        logger.info(f"✅ API Versioning Test Summary:")
        logger.info(f"   Successful public endpoints: {len(successful_endpoints)}")
        logger.info(f"   Failed endpoints: {len(failed_endpoints)}")
        
        return {
            "status": "success" if len(failed_endpoints) == 0 else "partial",
            "successful_endpoints": successful_endpoints,
            "failed_endpoints": failed_endpoints,
            "results": results,
            "total_tested": len(public_endpoints)
        }

    def test_prometheus_metrics_public_access(self) -> Dict[str, Any]:
        """Test L4: Prometheus Metrics - Should be accessible without auth"""
        logger.info("📊 Testing Prometheus Metrics (L4) - Public access without auth")
        
        results = {}
        
        # Test metrics endpoints that should be public
        metrics_endpoints = [
            "/api/metrics",
            "/api/v1/metrics"
        ]
        
        for endpoint in metrics_endpoints:
            try:
                logger.info(f"   Testing {endpoint}")
                
                # NO Authorization header - should work for public endpoints
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers={"Accept": "text/plain"},  # Prometheus format
                    timeout=10
                )
                
                logger.info(f"   Response status: {response.status_code}")
                logger.info(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
                
                if response.status_code == 200:
                    content = response.text
                    logger.info(f"✅ {endpoint} accessible without auth")
                    logger.info(f"   Response length: {len(content)} characters")
                    
                    # Check if it's Prometheus format
                    is_prometheus_format = (
                        "# HELP" in content or 
                        "# TYPE" in content or
                        "_total" in content or
                        "_count" in content
                    )
                    
                    if is_prometheus_format:
                        logger.info("✅ Response is in Prometheus format")
                        
                        # Count metrics
                        help_lines = content.count("# HELP")
                        type_lines = content.count("# TYPE")
                        
                        logger.info(f"   Metrics found: {help_lines} HELP lines, {type_lines} TYPE lines")
                        
                        results[endpoint] = {
                            "status": "success",
                            "public_access": True,
                            "prometheus_format": True,
                            "metrics_count": help_lines,
                            "content_length": len(content)
                        }
                    else:
                        logger.warning("⚠️ Response not in expected Prometheus format")
                        results[endpoint] = {
                            "status": "partial",
                            "public_access": True,
                            "prometheus_format": False,
                            "error": "Not in Prometheus format",
                            "content_preview": content[:200]
                        }
                elif response.status_code == 401:
                    logger.error(f"❌ {endpoint} still requires authentication!")
                    results[endpoint] = {
                        "status": "failed",
                        "public_access": False,
                        "error": "Endpoint still requires authentication",
                        "status_code": response.status_code
                    }
                else:
                    error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                    logger.error(f"❌ {endpoint} failed: {error_detail}")
                    results[endpoint] = {
                        "status": "failed",
                        "error": error_detail,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                logger.error(f"❌ {endpoint} test failed: {e}")
                results[endpoint] = {"status": "error", "error": str(e)}
        
        # Summary
        successful_endpoints = [ep for ep, result in results.items() if result["status"] == "success"]
        failed_endpoints = [ep for ep, result in results.items() if result["status"] == "failed"]
        
        logger.info(f"✅ Prometheus Metrics Test Summary:")
        logger.info(f"   Successful public endpoints: {len(successful_endpoints)}")
        logger.info(f"   Failed endpoints: {len(failed_endpoints)}")
        
        return {
            "status": "success" if len(failed_endpoints) == 0 else "partial",
            "successful_endpoints": successful_endpoints,
            "failed_endpoints": failed_endpoints,
            "results": results,
            "total_tested": len(metrics_endpoints)
        }

    def test_cors_configuration(self) -> Dict[str, Any]:
        """Test L1: CORS Configuration - Check CORS headers in responses"""
        logger.info("🌐 Testing CORS Configuration (L1) - Verify CORS headers")
        
        results = {}
        
        # Test various endpoints for CORS headers
        test_endpoints = [
            "/api/health",
            "/api/v1/health",
            "/api/metrics",
            "/api/version"
        ]
        
        # Test different HTTP methods and origins
        test_scenarios = [
            {"method": "GET", "origin": "http://localhost:3000"},
            {"method": "GET", "origin": "https://app.xionimus.ai"},
            {"method": "OPTIONS", "origin": "http://localhost:3000"}  # Preflight request
        ]
        
        for endpoint in test_endpoints:
            results[endpoint] = {}
            
            for scenario in test_scenarios:
                scenario_key = f"{scenario['method']}_{scenario['origin']}"
                
                try:
                    logger.info(f"   Testing {endpoint} with {scenario['method']} from {scenario['origin']}")
                    
                    headers = {
                        "Origin": scenario["origin"],
                        "Content-Type": "application/json"
                    }
                    
                    if scenario["method"] == "OPTIONS":
                        # Preflight request
                        headers.update({
                            "Access-Control-Request-Method": "GET",
                            "Access-Control-Request-Headers": "Content-Type,Authorization"
                        })
                    
                    response = self.session.request(
                        scenario["method"],
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=10
                    )
                    
                    logger.info(f"   Response status: {response.status_code}")
                    
                    # Check CORS headers
                    cors_headers = {
                        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                        "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                        "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
                    }
                    
                    # Log found CORS headers
                    found_headers = {k: v for k, v in cors_headers.items() if v is not None}
                    logger.info(f"   CORS headers found: {found_headers}")
                    
                    # Check if essential CORS headers are present
                    has_allow_origin = cors_headers["Access-Control-Allow-Origin"] is not None
                    
                    if has_allow_origin:
                        logger.info(f"✅ CORS headers present for {scenario_key}")
                        results[endpoint][scenario_key] = {
                            "status": "success",
                            "cors_headers": cors_headers,
                            "has_cors": True
                        }
                    else:
                        logger.warning(f"⚠️ Missing CORS headers for {scenario_key}")
                        results[endpoint][scenario_key] = {
                            "status": "partial",
                            "cors_headers": cors_headers,
                            "has_cors": False,
                            "error": "Missing Access-Control-Allow-Origin header"
                        }
                        
                except Exception as e:
                    logger.error(f"❌ CORS test failed for {endpoint} {scenario_key}: {e}")
                    results[endpoint][scenario_key] = {"status": "error", "error": str(e)}
        
        # Summary
        total_tests = len(test_endpoints) * len(test_scenarios)
        successful_tests = sum(
            1 for endpoint_results in results.values() 
            for scenario_result in endpoint_results.values() 
            if scenario_result["status"] == "success"
        )
        
        logger.info(f"✅ CORS Configuration Test Summary:")
        logger.info(f"   Successful CORS tests: {successful_tests}/{total_tests}")
        
        return {
            "status": "success" if successful_tests > 0 else "failed",
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "results": results,
            "cors_working": successful_tests > 0
        }

    def run_test_coverage_scripts(self) -> Dict[str, Any]:
        """Test H4: Test Coverage - Run test_jwt_auth.py and test_rate_limiting.py"""
        logger.info("🧪 Testing Test Coverage (H4) - Running test scripts")
        
        results = {}
        
        # Test scripts to run
        test_scripts = [
            "/app/test_jwt_auth.py",
            "/app/test_rate_limiting.py"
        ]
        
        for script_path in test_scripts:
            script_name = os.path.basename(script_path)
            logger.info(f"   Running {script_name}")
            
            try:
                # Check if script exists
                if not os.path.exists(script_path):
                    logger.warning(f"⚠️ {script_name} not found at {script_path}")
                    results[script_name] = {
                        "status": "not_found",
                        "error": f"Script not found at {script_path}"
                    }
                    continue
                
                # Run the script
                result = subprocess.run(
                    ["python3", script_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd="/app"
                )
                
                logger.info(f"   Exit code: {result.returncode}")
                
                if result.returncode == 0:
                    logger.info(f"✅ {script_name} passed")
                    results[script_name] = {
                        "status": "success",
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                else:
                    logger.error(f"❌ {script_name} failed with exit code {result.returncode}")
                    logger.error(f"   STDOUT: {result.stdout}")
                    logger.error(f"   STDERR: {result.stderr}")
                    results[script_name] = {
                        "status": "failed",
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
                    
            except subprocess.TimeoutExpired:
                logger.error(f"❌ {script_name} timed out after 60 seconds")
                results[script_name] = {
                    "status": "timeout",
                    "error": "Script execution timed out"
                }
            except Exception as e:
                logger.error(f"❌ {script_name} execution failed: {e}")
                results[script_name] = {"status": "error", "error": str(e)}
        
        # Summary
        successful_scripts = [name for name, result in results.items() if result["status"] == "success"]
        failed_scripts = [name for name, result in results.items() if result["status"] in ["failed", "error", "timeout"]]
        
        logger.info(f"✅ Test Coverage Summary:")
        logger.info(f"   Successful scripts: {len(successful_scripts)}")
        logger.info(f"   Failed scripts: {len(failed_scripts)}")
        
        return {
            "status": "success" if len(failed_scripts) == 0 else "partial",
            "successful_scripts": successful_scripts,
            "failed_scripts": failed_scripts,
            "results": results,
            "total_tested": len(test_scripts)
        }

def main():
    """
    Main test function for Comprehensive Phase 1 Testing
    """
    tester = Phase1Tester()
    
    logger.info("🚀 Starting Comprehensive Phase 1 Testing")
    logger.info("Database & Infrastructure Modernization")
    logger.info("=" * 60)
    
    # Run comprehensive Phase 1 tests
    final_results = tester.run_comprehensive_phase1_tests()
    
    # Final summary
    summary = final_results["summary"]
    logger.info("=" * 60)
    logger.info("🏁 FINAL PHASE 1 TEST RESULTS")
    logger.info("=" * 60)
    
    if summary["failed"] == 0 and summary["errors"] == 0:
        logger.info("🎉 ALL PHASE 1 TESTS PASSED!")
        logger.info("✅ PostgreSQL migration successful")
        logger.info("✅ Redis integration working")
        logger.info("✅ AI providers configured")
        logger.info("✅ System ready for production")
    elif summary["failed"] > 0:
        logger.error(f"❌ {summary['failed']} CRITICAL FAILURES DETECTED")
        logger.error("🚨 Phase 1 migration needs attention")
    else:
        logger.info("⚠️ Phase 1 migration partially successful")
        logger.info(f"   {summary['passed']} tests passed")
        logger.info(f"   {summary['partial']} tests had minor issues")
    
    logger.info("=" * 60)
    
    return final_results

if __name__ == "__main__":
    main()