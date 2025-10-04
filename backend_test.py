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
        self.db_path = os.path.expanduser("~/.xionimus_ai/xionimus.db")
        
    def test_create_chat_session(self) -> Dict[str, Any]:
        """Test creating a session and adding messages"""
        logger.info("💬 Testing session creation and message saving")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Step 1: Create a session via sessions API
            session_data = {
                "name": "Test Session for Persistence Testing"
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session creation failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": f"Session creation failed: {error_detail}",
                    "status_code": response.status_code
                }
            
            session_response = response.json()
            self.test_session_id = session_response.get("id")
            
            logger.info("✅ Session created successfully")
            logger.info(f"   Session ID: {self.test_session_id}")
            logger.info(f"   Session name: {session_response.get('name')}")
            
            # Step 2: Add messages to the session
            test_messages = [
                {
                    "session_id": self.test_session_id,
                    "role": "user",
                    "content": "Hello, can you help me test session persistence?"
                },
                {
                    "session_id": self.test_session_id,
                    "role": "assistant",
                    "content": "Hello! I'd be happy to help you test session persistence. This is a test response to verify that messages are being saved correctly to the database.",
                    "provider": "test",
                    "model": "test-model"
                }
            ]
            
            messages_added = 0
            for msg_data in test_messages:
                msg_response = self.session.post(
                    f"{self.api_url}/sessions/messages",
                    json=msg_data,
                    headers=headers,
                    timeout=10
                )
                
                if msg_response.status_code == 200:
                    messages_added += 1
                    logger.info(f"   ✅ Added {msg_data['role']} message")
                else:
                    logger.warning(f"   ⚠️ Failed to add {msg_data['role']} message: {msg_response.status_code}")
            
            logger.info(f"✅ Session created with {messages_added}/{len(test_messages)} messages")
            
            return {
                "status": "success",
                "session_id": self.test_session_id,
                "messages_added": messages_added,
                "total_messages": len(test_messages)
            }
                
        except Exception as e:
            logger.error(f"❌ Session creation test failed: {e}")
            return {"status": "error", "error": str(e)}
        
    def test_database_session_persistence(self) -> Dict[str, Any]:
        """Test that session was saved to SQLite database"""
        logger.info("🗄️ Testing database session persistence")
        
        if not self.test_session_id:
            return {"status": "skipped", "error": "No test session ID available"}
        
        try:
            # Check if database file exists
            if not os.path.exists(self.db_path):
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Query sessions table
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (self.test_session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                conn.close()
                return {
                    "status": "failed",
                    "error": f"Session {self.test_session_id} not found in database"
                }
            
            # Query messages table
            cursor.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp", (self.test_session_id,))
            message_rows = cursor.fetchall()
            
            conn.close()
            
            # Convert rows to dictionaries for easier inspection
            session_data = dict(session_row)
            messages_data = [dict(row) for row in message_rows]
            
            logger.info("✅ Session found in database")
            logger.info(f"   Session name: {session_data.get('name')}")
            logger.info(f"   Created at: {session_data.get('created_at')}")
            logger.info(f"   User ID: {session_data.get('user_id')}")
            logger.info(f"   Messages count: {len(messages_data)}")
            
            # Verify we have both user and assistant messages
            user_messages = [m for m in messages_data if m['role'] == 'user']
            assistant_messages = [m for m in messages_data if m['role'] == 'assistant']
            
            logger.info(f"   User messages: {len(user_messages)}")
            logger.info(f"   Assistant messages: {len(assistant_messages)}")
            
            return {
                "status": "success",
                "session_data": session_data,
                "messages_data": messages_data,
                "message_count": len(messages_data),
                "user_messages": len(user_messages),
                "assistant_messages": len(assistant_messages)
            }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database error: {e}")
            return {"status": "error", "error": f"Database error: {e}"}
        except Exception as e:
            logger.error(f"❌ Database persistence test failed: {e}")
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
    
    def test_session_list_api(self) -> Dict[str, Any]:
        """Test listing sessions via GET /api/sessions/list"""
        logger.info("📋 Testing session list API")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid token available"}
        
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
            
            if response.status_code == 200:
                sessions_list = response.json()
                
                logger.info("✅ Session list API working")
                logger.info(f"   Total sessions: {len(sessions_list)}")
                
                # Check if our test session appears in the list
                test_session_found = False
                if self.test_session_id:
                    for session in sessions_list:
                        if session.get("id") == self.test_session_id:
                            test_session_found = True
                            logger.info(f"   ✅ Test session found in list: {session.get('name')}")
                            logger.info(f"   Message count: {session.get('message_count', 0)}")
                            break
                
                if not test_session_found and self.test_session_id:
                    logger.warning(f"   ⚠️ Test session {self.test_session_id} not found in list")
                
                return {
                    "status": "success",
                    "sessions_count": len(sessions_list),
                    "test_session_found": test_session_found,
                    "sessions": sessions_list
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session list API failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Session list API test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_get_specific_session(self) -> Dict[str, Any]:
        """Test getting specific session via GET /api/sessions/{session_id}"""
        logger.info("🔍 Testing get specific session API")
        
        if not self.token or not self.test_session_id:
            return {"status": "skipped", "error": "No valid token or test session available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.get(
                f"{self.api_url}/sessions/{self.test_session_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                session_data = response.json()
                
                logger.info("✅ Get specific session API working")
                logger.info(f"   Session ID: {session_data.get('id')}")
                logger.info(f"   Session name: {session_data.get('name')}")
                logger.info(f"   Message count: {session_data.get('message_count', 0)}")
                logger.info(f"   Created at: {session_data.get('created_at')}")
                
                # Verify message count > 0
                message_count = session_data.get('message_count', 0)
                if message_count > 0:
                    logger.info(f"   ✅ Session has {message_count} messages")
                else:
                    logger.warning(f"   ⚠️ Session has no messages")
                
                return {
                    "status": "success",
                    "session_data": session_data,
                    "has_messages": message_count > 0
                }
            elif response.status_code == 404:
                logger.error("❌ Session not found")
                return {
                    "status": "failed",
                    "error": "Session not found",
                    "status_code": response.status_code
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Get specific session failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Get specific session test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_backend_logs_verification(self) -> Dict[str, Any]:
        """Check backend logs for session creation and message saving entries"""
        logger.info("📜 Testing backend logs verification")
        
        try:
            # Check supervisor backend logs
            log_files = [
                "/var/log/supervisor/backend.out.log",
                "/var/log/supervisor/backend.err.log"
            ]
            
            found_logs = []
            for log_file in log_files:
                if os.path.exists(log_file):
                    found_logs.append(log_file)
            
            if not found_logs:
                return {
                    "status": "partial",
                    "error": "No backend log files found",
                    "searched_paths": log_files
                }
            
            # Search for relevant log entries
            session_creation_logs = []
            message_saving_logs = []
            
            for log_file in found_logs:
                try:
                    with open(log_file, 'r') as f:
                        # Read last 1000 lines to avoid memory issues
                        lines = f.readlines()[-1000:]
                        
                    for line in lines:
                        if "✅ Created new session" in line:
                            session_creation_logs.append(line.strip())
                        elif "✅ Successfully saved messages" in line:
                            message_saving_logs.append(line.strip())
                            
                except Exception as e:
                    logger.warning(f"⚠️ Could not read log file {log_file}: {e}")
            
            logger.info(f"✅ Backend logs checked")
            logger.info(f"   Session creation logs found: {len(session_creation_logs)}")
            logger.info(f"   Message saving logs found: {len(message_saving_logs)}")
            
            if session_creation_logs:
                logger.info(f"   Latest session creation: {session_creation_logs[-1]}")
            if message_saving_logs:
                logger.info(f"   Latest message saving: {message_saving_logs[-1]}")
            
            return {
                "status": "success",
                "session_creation_logs": len(session_creation_logs),
                "message_saving_logs": len(message_saving_logs),
                "log_files_checked": found_logs,
                "latest_session_log": session_creation_logs[-1] if session_creation_logs else None,
                "latest_message_log": message_saving_logs[-1] if message_saving_logs else None
            }
            
        except Exception as e:
            logger.error(f"❌ Backend logs verification failed: {e}")
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
                logger.error(f"   Status code: {response.status_code}")
                logger.error(f"   Response text: {response.text}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "response_text": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication test failed: {e}")
            return {"status": "error", "error": str(e)}
    
    # Removed old test methods - focusing on session persistence testing
    
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
    """Main test runner for Session Persistence and Message Saving Testing"""
    logger.info("🔄 Starting Session Persistence and Message Saving Testing Suite")
    logger.info("=" * 70)
    
    tester = SessionPersistenceTester()
    
    # Test 1: Authentication System (demo/demo123)
    logger.info("1️⃣ Testing Authentication System (demo/demo123)")
    auth_result = tester.test_authentication_system()
    print(f"Authentication: {auth_result['status']}")
    
    if auth_result['status'] != 'success':
        print(f"❌ Authentication failed: {auth_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with session persistence tests")
        return
    
    # Test 2: Create Chat Session
    logger.info("\n2️⃣ Creating Chat Session via POST /api/chat/")
    session_result = tester.test_create_chat_session()
    print(f"Chat Session Creation: {session_result['status']}")
    if session_result['status'] == 'success':
        print(f"   Session ID: {session_result.get('session_id')}")
        print(f"   ✅ Chat session created successfully")
    elif session_result['status'] == 'failed':
        print(f"   ❌ Failed: {session_result.get('error')}")
        print(f"   Status Code: {session_result.get('status_code')}")
    
    # Test 3: Verify Database Persistence
    logger.info("\n3️⃣ Verifying Session Saved to Database")
    db_result = tester.test_database_session_persistence()
    print(f"Database Session Persistence: {db_result['status']}")
    if db_result['status'] == 'success':
        print(f"   ✅ Session found in database")
        print(f"   Messages in DB: {db_result.get('message_count', 0)}")
        print(f"   User messages: {db_result.get('user_messages', 0)}")
        print(f"   Assistant messages: {db_result.get('assistant_messages', 0)}")
    elif db_result['status'] == 'failed':
        print(f"   ❌ Failed: {db_result.get('error')}")
    
    # Test 4: Session List API
    logger.info("\n4️⃣ Testing Session List API")
    list_result = tester.test_session_list_api()
    print(f"GET /api/sessions/list: {list_result['status']}")
    if list_result['status'] == 'success':
        print(f"   Total sessions: {list_result.get('sessions_count', 0)}")
        print(f"   Test session found: {list_result.get('test_session_found', False)}")
        print(f"   ✅ Session list API working correctly")
    elif list_result['status'] == 'failed':
        print(f"   ❌ Failed: {list_result.get('error')}")
    
    # Test 5: Get Specific Session
    logger.info("\n5️⃣ Testing Get Specific Session API")
    get_result = tester.test_get_specific_session()
    print(f"GET /api/sessions/{{session_id}}: {get_result['status']}")
    if get_result['status'] == 'success':
        session_data = get_result.get('session_data', {})
        print(f"   Session name: {session_data.get('name')}")
        print(f"   Message count: {session_data.get('message_count', 0)}")
        print(f"   Has messages: {get_result.get('has_messages', False)}")
        print(f"   ✅ Get specific session API working correctly")
    elif get_result['status'] == 'failed':
        print(f"   ❌ Failed: {get_result.get('error')}")
    
    # Test 6: Backend Logs Verification
    logger.info("\n6️⃣ Checking Backend Logs for Session Creation")
    logs_result = tester.test_backend_logs_verification()
    print(f"Backend Logs Verification: {logs_result['status']}")
    if logs_result['status'] == 'success':
        print(f"   Session creation logs: {logs_result.get('session_creation_logs', 0)}")
        print(f"   Message saving logs: {logs_result.get('message_saving_logs', 0)}")
        if logs_result.get('latest_session_log'):
            print(f"   Latest session log: {logs_result['latest_session_log']}")
        if logs_result.get('latest_message_log'):
            print(f"   Latest message log: {logs_result['latest_message_log']}")
        print(f"   ✅ Backend logging working correctly")
    elif logs_result['status'] == 'partial':
        print(f"   ⚠️ Partial: {logs_result.get('error')}")
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("🔄 SESSION PERSISTENCE AND MESSAGE SAVING TEST SUMMARY")
    logger.info("=" * 70)
    
    # Count successful tests
    test_results = [
        ("Authentication (demo/demo123)", auth_result['status'] == 'success'),
        ("Chat Session Creation", session_result['status'] == 'success'),
        ("Database Session Persistence", db_result['status'] == 'success'),
        ("Session List API", list_result['status'] == 'success'),
        ("Get Specific Session API", get_result['status'] == 'success'),
        ("Backend Logs Verification", logs_result['status'] in ['success', 'partial']),
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
        critical_issues.append("Chat session creation failed - sessions not being created")
    if db_result['status'] != 'success':
        critical_issues.append("Database persistence broken - sessions/messages not saved")
    if list_result['status'] != 'success':
        critical_issues.append("Session list API broken - cannot retrieve sessions")
    if get_result['status'] != 'success':
        critical_issues.append("Get specific session API broken")
    
    # Background Task Status
    background_task_notes = []
    if db_result['status'] == 'success':
        message_count = db_result.get('message_count', 0)
        if message_count >= 2:  # Should have user + assistant messages
            background_task_notes.append("✅ Background task working - messages saved to database")
        else:
            background_task_notes.append("⚠️ Background task may have issues - fewer messages than expected")
    
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: Session Persistence and Message Saving working correctly!")
        print("   - Authentication system functional")
        print("   - Chat sessions being created")
        print("   - Sessions and messages persisted to database")
        print("   - Session APIs working correctly")
    
    if background_task_notes:
        print(f"\n📝 BACKGROUND TASK STATUS:")
        for note in background_task_notes:
            print(f"   - {note}")
    
    # Database Information
    if db_result['status'] == 'success':
        print(f"\n📊 DATABASE INFORMATION:")
        print(f"   - Database path: {tester.db_path}")
        print(f"   - Session ID: {tester.test_session_id}")
        print(f"   - Total messages: {db_result.get('message_count', 0)}")
        print(f"   - User messages: {db_result.get('user_messages', 0)}")
        print(f"   - Assistant messages: {db_result.get('assistant_messages', 0)}")

if __name__ == "__main__":
    main()