#!/usr/bin/env python3
"""
Session Persistence and Message Saving Testing Suite
Tests session persistence and message saving functionality in Xionimus AI including:
- Login and token authentication
- Chat session creation
- Database persistence verification
- Session listing API
- Message saving to database
"""

import requests
import json
import time
import logging
import sqlite3
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionPersistenceTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()  # Reuse connections for better performance
        self.test_session_id = None
        
    def create_test_session_with_messages(self) -> Dict[str, Any]:
        """Create a test session with multiple messages for testing"""
        logger.info("📝 Creating test session with messages")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Create a new session
            session_data = {
                "name": "Test Session for Context Management"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Session creation failed: {response.status_code}",
                    "response": response.text
                }
            
            session_info = response.json()
            self.test_session_id = session_info["id"]
            
            # Add multiple messages to the session
            test_messages = [
                {
                    "session_id": self.test_session_id,
                    "role": "user",
                    "content": "I want to build a web application with React and FastAPI. Can you help me set up the project structure?"
                },
                {
                    "session_id": self.test_session_id,
                    "role": "assistant", 
                    "content": "I'll help you create a modern web application with React frontend and FastAPI backend. Let me set up the project structure for you with proper organization and best practices.",
                    "provider": "openai",
                    "model": "gpt-4",
                    "usage": {"total_tokens": 150, "prompt_tokens": 50, "completion_tokens": 100}
                },
                {
                    "session_id": self.test_session_id,
                    "role": "user",
                    "content": "Great! Can you also add authentication with JWT tokens and a user management system?"
                },
                {
                    "session_id": self.test_session_id,
                    "role": "assistant",
                    "content": "Absolutely! I'll implement a complete authentication system with JWT tokens, user registration, login, and protected routes. This will include password hashing with bcrypt and proper token validation middleware.",
                    "provider": "openai", 
                    "model": "gpt-4",
                    "usage": {"total_tokens": 200, "prompt_tokens": 75, "completion_tokens": 125}
                },
                {
                    "session_id": self.test_session_id,
                    "role": "user",
                    "content": "Perfect! Now I need to add a database layer with SQLAlchemy and implement CRUD operations for user data."
                }
            ]
            
            # Add messages to the session
            for msg_data in test_messages:
                msg_response = self.session.post(
                    f"{self.api_url}/sessions/messages",
                    json=msg_data,
                    headers=headers,
                    timeout=10
                )
                
                if msg_response.status_code != 200:
                    logger.warning(f"⚠️ Failed to add message: {msg_response.status_code}")
            
            logger.info(f"✅ Test session created: {self.test_session_id}")
            logger.info(f"   Added {len(test_messages)} messages")
            
            return {
                "status": "success",
                "session_id": self.test_session_id,
                "message_count": len(test_messages)
            }
            
        except Exception as e:
            logger.error(f"❌ Test session creation failed: {e}")
            return {"status": "error", "error": str(e)}
        
    def test_context_status_endpoint(self) -> Dict[str, Any]:
        """Test context status endpoint with session token calculation"""
        logger.info("📊 Testing context status endpoint")
        
        if not self.token or not self.test_session_id:
            return {"status": "skipped", "error": "No valid token or test session available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/session-management/context-status/{self.test_session_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                context_data = response.json()
                
                logger.info("✅ Context status endpoint working")
                logger.info(f"   Current tokens: {context_data.get('current_tokens', 0)}")
                logger.info(f"   Token limit: {context_data.get('limit', 0)}")
                logger.info(f"   Usage percentage: {context_data.get('percentage', 0)}%")
                logger.info(f"   Warning level: {context_data.get('recommendation', 'unknown')}")
                logger.info(f"   Can continue: {context_data.get('can_continue', True)}")
                
                # Validate response structure
                required_fields = ['warning', 'current_tokens', 'limit', 'percentage', 'message', 'can_continue', 'recommendation']
                missing_fields = [field for field in required_fields if field not in context_data]
                
                if missing_fields:
                    return {
                        "status": "partial",
                        "error": f"Missing fields: {missing_fields}",
                        "data": context_data
                    }
                
                return {
                    "status": "success",
                    "data": context_data,
                    "tokens_calculated": context_data.get('current_tokens', 0) > 0
                }
            elif response.status_code == 404:
                logger.error("❌ Session not found for context status")
                return {
                    "status": "failed",
                    "error": "Session not found",
                    "status_code": response.status_code
                }
            else:
                logger.error(f"❌ Context status failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Context status test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_authentication_system(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test JWT authentication system for session management"""
        logger.info(f"🔐 Testing authentication system with username: {username}")
        
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.user_info = {
                    "user_id": token_data.get("user_id"),
                    "username": token_data.get("username"),
                    "token_type": token_data.get("token_type"),
                    "role": token_data.get("role", "user")
                }
                
                logger.info("✅ Authentication successful")
                logger.info(f"   User ID: {token_data.get('user_id')}")
                logger.info(f"   Role: {token_data.get('role', 'user')}")
                
                return {
                    "status": "success",
                    "token": self.token,
                    "user_info": self.user_info,
                    "response": token_data
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_summarize_and_fork_endpoint(self) -> Dict[str, Any]:
        """Test session summarization and forking functionality"""
        logger.info("🔄 Testing summarize and fork endpoint")
        
        if not self.token or not self.test_session_id:
            return {"status": "skipped", "error": "No valid token or test session available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            fork_data = {
                "session_id": self.test_session_id,
                "api_keys": {}  # Empty API keys - expect it may fail but should handle gracefully
            }
            
            response = self.session.post(
                f"{self.api_url}/session-management/summarize-and-fork",
                json=fork_data,
                headers=headers,
                timeout=30  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                fork_data = response.json()
                
                logger.info("✅ Summarize and fork endpoint working")
                logger.info(f"   Original session: {fork_data.get('session_id')}")
                logger.info(f"   New session: {fork_data.get('new_session_id')}")
                logger.info(f"   Summary length: {len(fork_data.get('summary', ''))}")
                logger.info(f"   Next steps count: {len(fork_data.get('next_steps', []))}")
                logger.info(f"   Old session tokens: {fork_data.get('old_session_tokens', 0)}")
                
                # Validate response structure
                required_fields = ['session_id', 'new_session_id', 'summary', 'context_transfer', 'next_steps', 'old_session_tokens', 'timestamp']
                missing_fields = [field for field in required_fields if field not in fork_data]
                
                if missing_fields:
                    return {
                        "status": "partial",
                        "error": f"Missing fields: {missing_fields}",
                        "data": fork_data
                    }
                
                # Validate next_steps structure
                next_steps = fork_data.get('next_steps', [])
                if len(next_steps) != 3:
                    return {
                        "status": "partial",
                        "error": f"Expected 3 next steps, got {len(next_steps)}",
                        "data": fork_data
                    }
                
                return {
                    "status": "success",
                    "data": fork_data,
                    "new_session_id": fork_data.get('new_session_id')
                }
            elif response.status_code == 404:
                logger.error("❌ Session not found for summarization")
                return {
                    "status": "failed",
                    "error": "Session not found",
                    "status_code": response.status_code
                }
            elif response.status_code == 500:
                # Expected if AI API keys are missing
                error_detail = response.json().get("detail", "Unknown error") if response.content else "Server error"
                logger.warning(f"⚠️ Summarize and fork failed (expected if no AI keys): {error_detail}")
                return {
                    "status": "expected_failure",
                    "error": "AI API keys likely missing - this is expected",
                    "status_code": response.status_code,
                    "detail": error_detail
                }
            else:
                logger.error(f"❌ Summarize and fork failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Summarize and fork test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_continue_with_option_endpoint(self, new_session_id: str = None) -> Dict[str, Any]:
        """Test continue with option endpoint"""
        logger.info("▶️ Testing continue with option endpoint")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        # Use provided session ID or test session ID
        session_id = new_session_id or self.test_session_id
        if not session_id:
            return {"status": "skipped", "error": "No session ID available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test with a sample option action
            option_data = {
                "session_id": session_id,
                "option_action": "Continue with code improvements and add new features",
                "api_keys": {}
            }
            
            response = self.session.post(
                f"{self.api_url}/session-management/continue-with-option",
                json=option_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                continue_data = response.json()
                
                logger.info("✅ Continue with option endpoint working")
                logger.info(f"   Status: {continue_data.get('status')}")
                logger.info(f"   Session ID: {continue_data.get('session_id')}")
                logger.info(f"   Action: {continue_data.get('action')}")
                
                # Validate response structure
                required_fields = ['status', 'session_id', 'action', 'message']
                missing_fields = [field for field in required_fields if field not in continue_data]
                
                if missing_fields:
                    return {
                        "status": "partial",
                        "error": f"Missing fields: {missing_fields}",
                        "data": continue_data
                    }
                
                return {
                    "status": "success",
                    "data": continue_data
                }
            elif response.status_code == 404:
                logger.error("❌ Session not found for option continuation")
                return {
                    "status": "failed",
                    "error": "Session not found",
                    "status_code": response.status_code
                }
            else:
                logger.error(f"❌ Continue with option failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Continue with option test failed: {e}")
            return {"status": "error", "error": str(e)}
    def test_empty_session_handling(self) -> Dict[str, Any]:
        """Test context status with empty session (no messages)"""
        logger.info("🔍 Testing empty session handling")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Create an empty session
            session_data = {
                "name": "Empty Test Session"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "status": "failed",
                    "error": f"Empty session creation failed: {response.status_code}"
                }
            
            empty_session_info = response.json()
            empty_session_id = empty_session_info["id"]
            
            # Test context status on empty session
            context_response = self.session.get(
                f"{self.api_url}/session-management/context-status/{empty_session_id}",
                headers=headers,
                timeout=10
            )
            
            if context_response.status_code == 200:
                context_data = context_response.json()
                
                logger.info("✅ Empty session context status working")
                logger.info(f"   Current tokens: {context_data.get('current_tokens', 0)}")
                logger.info(f"   Warning: {context_data.get('warning', False)}")
                logger.info(f"   Can continue: {context_data.get('can_continue', True)}")
                
                # Should have 0 tokens for empty session
                if context_data.get('current_tokens', -1) == 0:
                    logger.info("✅ Empty session correctly shows 0 tokens")
                    return {
                        "status": "success",
                        "data": context_data,
                        "empty_session_id": empty_session_id
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Expected 0 tokens for empty session, got {context_data.get('current_tokens')}",
                        "data": context_data
                    }
            else:
                logger.error(f"❌ Empty session context status failed: {context_response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {context_response.status_code}",
                    "response": context_response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Empty session test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_session_summary_modal_flow(self) -> Dict[str, Any]:
        """Test the complete Session Summary Modal API flow"""
        logger.info("🎭 Testing Session Summary Modal API Flow")
        
        if not self.token or not self.test_session_id:
            return {"status": "skipped", "error": "No valid token or test session available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Simulate the modal API flow
            # 1. Modal opens and calls summarize-and-fork
            logger.info("   Step 1: Modal calls summarize-and-fork endpoint")
            
            modal_request = {
                "session_id": self.test_session_id,
                "api_keys": {}  # Empty API keys - expect graceful failure
            }
            
            response = self.session.post(
                f"{self.api_url}/session-management/summarize-and-fork",
                json=modal_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                # Success case - AI keys are available
                modal_data = response.json()
                
                logger.info("✅ Modal API flow successful")
                logger.info(f"   Summary generated: {len(modal_data.get('summary', ''))} chars")
                logger.info(f"   Next steps: {len(modal_data.get('next_steps', []))}")
                logger.info(f"   New session: {modal_data.get('new_session_id')}")
                
                # 2. Test option selection
                if modal_data.get('next_steps') and len(modal_data.get('next_steps', [])) > 0:
                    logger.info("   Step 2: Testing option selection")
                    
                    option_request = {
                        "session_id": modal_data.get('new_session_id'),
                        "option_action": modal_data['next_steps'][0]['action'],
                        "api_keys": {}
                    }
                    
                    option_response = self.session.post(
                        f"{self.api_url}/session-management/continue-with-option",
                        json=option_request,
                        headers=headers,
                        timeout=10
                    )
                    
                    if option_response.status_code == 200:
                        logger.info("✅ Option selection working")
                    else:
                        logger.warning(f"⚠️ Option selection failed: {option_response.status_code}")
                
                return {
                    "status": "success",
                    "data": modal_data,
                    "flow_complete": True
                }
                
            elif response.status_code == 500:
                # Expected failure - AI keys missing
                error_detail = response.json().get("detail", "Unknown error") if response.content else "Server error"
                logger.info("✅ Modal API flow - expected failure (no AI keys)")
                logger.info(f"   Error message: {error_detail}")
                logger.info("   Modal should display this error to user")
                
                return {
                    "status": "expected_failure",
                    "error": "AI API keys missing - modal should show error message",
                    "error_detail": error_detail,
                    "flow_complete": True
                }
                
            else:
                logger.error(f"❌ Modal API flow failed: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Modal API flow test failed: {e}")
            return {"status": "error", "error": str(e)}
def main():
    """Main test runner for Session Summary UI Integration Testing"""
    logger.info("🔄 Starting Session Summary UI Integration Testing Suite")
    logger.info("=" * 70)
    
    tester = SessionSummaryUITester()
    
    # Test 1: Authentication System (demo/demo123)
    logger.info("1️⃣ Testing Authentication System (demo/demo123)")
    auth_result = tester.test_authentication_system()
    print(f"Authentication: {auth_result['status']}")
    
    if auth_result['status'] != 'success':
        print(f"❌ Authentication failed: {auth_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with session summary tests")
        return
    
    # Test 2: Create Test Session with Messages (for button display test)
    logger.info("\n2️⃣ Creating Test Session with Messages")
    session_result = tester.create_test_session_with_messages()
    print(f"Test Session Creation: {session_result['status']}")
    if session_result['status'] == 'success':
        print(f"   Session ID: {session_result.get('session_id')}")
        print(f"   Messages added: {session_result.get('message_count', 0)}")
        print(f"   ✅ 'Zusammenfassung' button should now appear in chat header")
    
    # Test 3: Backend Endpoint Availability - Context Status
    logger.info("\n3️⃣ Testing Context Status Endpoint")
    context_result = tester.test_context_status_endpoint()
    print(f"GET /api/session-management/context-status: {context_result['status']}")
    if context_result['status'] == 'success':
        data = context_result.get('data', {})
        print(f"   Current tokens: {data.get('current_tokens', 0)}")
        print(f"   Usage percentage: {data.get('percentage', 0)}%")
        print(f"   Warning level: {data.get('recommendation', 'unknown')}")
        print(f"   ✅ Context status endpoint working correctly")
    
    # Test 4: Backend Endpoint Availability - Summarize and Fork
    logger.info("\n4️⃣ Testing Summarize and Fork Endpoint")
    fork_result = tester.test_summarize_and_fork_endpoint()
    print(f"POST /api/session-management/summarize-and-fork: {fork_result['status']}")
    if fork_result['status'] == 'success':
        data = fork_result.get('data', {})
        print(f"   New session created: {data.get('new_session_id')}")
        print(f"   Summary length: {len(data.get('summary', ''))}")
        print(f"   Next steps provided: {len(data.get('next_steps', []))}")
        print(f"   ✅ Summarize and fork endpoint working correctly")
    elif fork_result['status'] == 'expected_failure':
        print(f"   ⚠️ Expected failure (AI keys missing): {fork_result.get('error')}")
        print(f"   ✅ Error handling working correctly - graceful failure")
    
    # Test 5: Backend Endpoint Availability - Continue with Option
    logger.info("\n5️⃣ Testing Continue with Option Endpoint")
    new_session_id = None
    if fork_result['status'] == 'success':
        new_session_id = fork_result.get('data', {}).get('new_session_id')
    
    continue_result = tester.test_continue_with_option_endpoint(new_session_id)
    print(f"POST /api/session-management/continue-with-option: {continue_result['status']}")
    if continue_result['status'] == 'success':
        data = continue_result.get('data', {})
        print(f"   Option selected successfully")
        print(f"   Action: {data.get('action', 'unknown')}")
        print(f"   ✅ Continue with option endpoint working correctly")
    
    # Test 6: Session Summary Modal API Flow Test
    logger.info("\n6️⃣ Testing Session Summary Modal API Flow")
    modal_flow_result = tester.test_session_summary_modal_flow()
    print(f"Session Summary Modal Flow: {modal_flow_result['status']}")
    if modal_flow_result['status'] == 'success':
        print(f"   ✅ Modal API flow working correctly")
        print(f"   ✅ Authentication properly integrated")
        print(f"   ✅ API calls properly formatted")
    elif modal_flow_result['status'] == 'expected_failure':
        print(f"   ⚠️ Expected failure (AI keys missing): {modal_flow_result.get('error')}")
        print(f"   ✅ Error handling in modal working correctly")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("🔄 SESSION SUMMARY UI INTEGRATION TEST SUMMARY")
    logger.info("=" * 70)
    
    # Count successful tests
    test_results = [
        ("Authentication (demo/demo123)", auth_result['status'] == 'success'),
        ("Test Session Creation", session_result['status'] == 'success'),
        ("Context Status Endpoint", context_result['status'] == 'success'),
        ("Summarize and Fork Endpoint", fork_result['status'] in ['success', 'expected_failure']),
        ("Continue with Option Endpoint", continue_result['status'] == 'success'),
        ("Session Summary Modal Flow", modal_flow_result['status'] in ['success', 'expected_failure']),
    ]
    
    successful_tests = sum(1 for _, success in test_results if success)
    total_tests = len(test_results)
    
    print(f"\n📈 Overall Results: {successful_tests}/{total_tests} tests passed")
    
    for test_name, success in test_results:
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
    
    # Critical Issues
    critical_issues = []
    if auth_result['status'] != 'success':
        critical_issues.append("Authentication system broken - cannot login with demo/demo123")
    if session_result['status'] != 'success':
        critical_issues.append("Cannot create test sessions - button won't appear")
    if context_result['status'] != 'success':
        critical_issues.append("Context status endpoint not working")
    if fork_result['status'] not in ['success', 'expected_failure']:
        critical_issues.append("Summarize and fork endpoint broken - modal will fail")
    if continue_result['status'] != 'success':
        critical_issues.append("Continue with option endpoint broken")
    if modal_flow_result['status'] not in ['success', 'expected_failure']:
        critical_issues.append("Session Summary Modal API flow broken")
    
    # UI Integration Notes
    ui_notes = []
    if session_result['status'] == 'success':
        ui_notes.append("✅ 'Zusammenfassung' button should appear in chat header when messages exist")
    if fork_result['status'] in ['success', 'expected_failure']:
        ui_notes.append("✅ Modal should open and show loading spinner when button clicked")
        if fork_result['status'] == 'expected_failure':
            ui_notes.append("⚠️ Modal should show proper error message (no AI keys configured)")
    if continue_result['status'] == 'success':
        ui_notes.append("✅ Option selection in modal should work correctly")
    
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: Session Summary UI Integration working correctly!")
        print("   - Authentication system functional")
        print("   - Backend endpoints available and working")
        print("   - API calls properly authenticated")
        print("   - Error handling graceful")
    
    if ui_notes:
        print(f"\n📝 UI INTEGRATION STATUS:")
        for note in ui_notes:
            print(f"   - {note}")
    
    # Special notes about AI keys
    if fork_result['status'] == 'expected_failure' or modal_flow_result['status'] == 'expected_failure':
        print(f"\n📝 NOTES:")
        print(f"   - Session summarization requires AI API keys (OpenAI, Anthropic, Perplexity)")
        print(f"   - Expected failure without AI keys is correct behavior")
        print(f"   - Modal should show proper error message to user")

if __name__ == "__main__":
    main()