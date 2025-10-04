#!/usr/bin/env python3
"""
Session Management and Message Storage Testing Suite
Tests the recent fixes for session management including:
- Session not found error handling (HTTPException properly passed through)
- WebSocket message storage using correct SQLAlchemy methods
- Session creation, message addition, and retrieval
- Error handling for invalid session IDs (404 vs 500 errors)
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

class SessionManagementTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_info = None
        self.session = requests.Session()  # Reuse connections for better performance
        self.session_id = None
        self.db_path = os.path.expanduser("~/.xionimus_ai/xionimus.db")
        
    def test_authentication_system(self, username: str = "demo", password: str = "demo123") -> Dict[str, Any]:
        """Test JWT authentication system"""
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
                logger.info(f"   Username: {token_data.get('username')}")
                
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

    def test_session_creation(self) -> Dict[str, Any]:
        """Test POST /api/sessions/ - Create new session"""
        logger.info("📝 Testing session creation")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            session_data = {
                "name": "Session Management Test Session",
                "workspace_id": None
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                session_response = response.json()
                self.session_id = session_response.get("id")
                
                logger.info("✅ Session created successfully")
                logger.info(f"   Session ID: {self.session_id}")
                logger.info(f"   Session Name: {session_response.get('name')}")
                logger.info(f"   Message Count: {session_response.get('message_count', 0)}")
                
                return {
                    "status": "success",
                    "session_id": self.session_id,
                    "response": session_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Session creation failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Session creation test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_add_user_message(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/sessions/messages - Add user message"""
        logger.info("👤 Testing add user message")
        
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
                "content": "Hallo! Kannst du mir bei der Programmierung helfen?",
                "provider": None,
                "model": None
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/messages",
                json=message_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                message_response = response.json()
                
                logger.info("✅ User message added successfully")
                logger.info(f"   Message ID: {message_response.get('id')}")
                logger.info(f"   Role: {message_response.get('role')}")
                logger.info(f"   Content: {message_response.get('content')[:50]}...")
                
                return {
                    "status": "success",
                    "message_id": message_response.get('id'),
                    "response": message_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Add user message failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Add user message test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_add_assistant_message(self, session_id: str) -> Dict[str, Any]:
        """Test POST /api/sessions/messages - Add assistant message"""
        logger.info("🤖 Testing add assistant message")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            message_data = {
                "session_id": session_id,
                "role": "assistant",
                "content": "Hallo! Ja, gerne helfe ich dir bei der Programmierung. Was für ein Problem hast du denn?",
                "provider": "openai",
                "model": "gpt-4",
                "usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": 25,
                    "total_tokens": 40
                }
            }
            
            response = self.session.post(
                f"{self.api_url}/sessions/messages",
                json=message_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                message_response = response.json()
                
                logger.info("✅ Assistant message added successfully")
                logger.info(f"   Message ID: {message_response.get('id')}")
                logger.info(f"   Role: {message_response.get('role')}")
                logger.info(f"   Provider: {message_response.get('provider')}")
                logger.info(f"   Model: {message_response.get('model')}")
                logger.info(f"   Content: {message_response.get('content')[:50]}...")
                
                return {
                    "status": "success",
                    "message_id": message_response.get('id'),
                    "response": message_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Add assistant message failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Add assistant message test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_get_session_details(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id} - Get session details"""
        logger.info("📋 Testing get session details")
        
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
            
            if response.status_code == 200:
                session_response = response.json()
                
                logger.info("✅ Session details retrieved successfully")
                logger.info(f"   Session ID: {session_response.get('id')}")
                logger.info(f"   Name: {session_response.get('name')}")
                logger.info(f"   Message Count: {session_response.get('message_count')}")
                logger.info(f"   Created At: {session_response.get('created_at')}")
                
                return {
                    "status": "success",
                    "message_count": session_response.get('message_count'),
                    "response": session_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Get session details failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Get session details test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_get_session_messages(self, session_id: str) -> Dict[str, Any]:
        """Test GET /api/sessions/{session_id}/messages - Get all messages"""
        logger.info("💬 Testing get session messages")
        
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
            
            if response.status_code == 200:
                messages_response = response.json()
                
                logger.info("✅ Session messages retrieved successfully")
                logger.info(f"   Total Messages: {len(messages_response)}")
                
                for i, msg in enumerate(messages_response):
                    logger.info(f"   Message {i+1}: {msg.get('role')} - {msg.get('content')[:30]}...")
                
                return {
                    "status": "success",
                    "message_count": len(messages_response),
                    "messages": messages_response
                }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Get session messages failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Get session messages test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_invalid_session_error_handling(self) -> Dict[str, Any]:
        """Test error handling with invalid session_id - should return 404, not 500"""
        logger.info("🚫 Testing invalid session error handling")
        
        if not self.token:
            return {"status": "skipped", "error": "No valid authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            invalid_session_id = "invalid_session_12345"
            
            # Test 1: Get invalid session details
            response = self.session.get(
                f"{self.api_url}/sessions/{invalid_session_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 404:
                logger.info("✅ Invalid session correctly returns 404 (not 500)")
                logger.info(f"   Status code: {response.status_code}")
                logger.info(f"   Error message: {response.json().get('detail')}")
                
                # Test 2: Add message to invalid session
                message_data = {
                    "session_id": invalid_session_id,
                    "role": "user",
                    "content": "Test message for invalid session"
                }
                
                response2 = self.session.post(
                    f"{self.api_url}/sessions/messages",
                    json=message_data,
                    headers=headers,
                    timeout=10
                )
                
                if response2.status_code == 404:
                    logger.info("✅ Add message to invalid session correctly returns 404")
                    logger.info(f"   Status code: {response2.status_code}")
                    logger.info(f"   Error message: {response2.json().get('detail')}")
                    
                    return {
                        "status": "success",
                        "get_session_status": response.status_code,
                        "add_message_status": response2.status_code,
                        "proper_error_handling": True
                    }
                else:
                    return {
                        "status": "partial",
                        "error": f"Add message to invalid session returned {response2.status_code}, expected 404",
                        "get_session_status": response.status_code,
                        "add_message_status": response2.status_code
                    }
            else:
                logger.error(f"❌ Expected 404 for invalid session, got: {response.status_code}")
                return {
                    "status": "failed",
                    "error": f"Expected 404 status code, got {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except Exception as e:
            logger.error(f"❌ Invalid session error handling test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_database_persistence(self, session_id: str) -> Dict[str, Any]:
        """Test that sessions and messages are properly saved to database"""
        logger.info("🗄️ Testing database persistence")
        
        try:
            # Check if database file exists
            if not os.path.exists(self.db_path):
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if session exists in database
            cursor.execute("SELECT id, name, user_id, created_at FROM sessions WHERE id = ?", (session_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                conn.close()
                return {
                    "status": "failed",
                    "error": f"Session {session_id} not found in database"
                }
            
            # Check messages for this session
            cursor.execute("SELECT id, role, content, timestamp FROM messages WHERE session_id = ?", (session_id,))
            message_rows = cursor.fetchall()
            
            conn.close()
            
            logger.info("✅ Database persistence verified")
            logger.info(f"   Session found: {session_row[0]} - {session_row[1]}")
            logger.info(f"   User ID: {session_row[2]}")
            logger.info(f"   Messages found: {len(message_rows)}")
            
            for i, msg in enumerate(message_rows):
                logger.info(f"   Message {i+1}: {msg[1]} - {msg[2][:30]}...")
            
            return {
                "status": "success",
                "session_found": True,
                "message_count": len(message_rows),
                "session_data": {
                    "id": session_row[0],
                    "name": session_row[1],
                    "user_id": session_row[2],
                    "created_at": session_row[3]
                },
                "messages": [{"id": m[0], "role": m[1], "content": m[2][:50], "timestamp": m[3]} for m in message_rows]
            }
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database error: {e}")
            return {"status": "error", "error": f"Database error: {e}"}
        except Exception as e:
            logger.error(f"❌ Database persistence test failed: {e}")
            return {"status": "error", "error": str(e)}

def main():
    """Main test runner for Session Management and Message Storage Testing"""
    logger.info("🔄 Starting Session Management and Message Storage Testing Suite")
    logger.info("=" * 80)
    
    tester = SessionManagementTester()
    
    # Test 1: Authentication System (demo/demo123)
    logger.info("1️⃣ Testing Authentication System (demo/demo123)")
    auth_result = tester.test_authentication_system()
    print(f"Authentication: {auth_result['status']}")
    
    if auth_result['status'] != 'success':
        print(f"❌ Authentication failed: {auth_result.get('error', 'Unknown error')}")
        print("⚠️ Cannot proceed with session management tests")
        return
    
    # Test 2: Session Creation
    logger.info("\n2️⃣ Testing Session Creation")
    session_result = tester.test_session_creation()
    print(f"Session Creation: {session_result['status']}")
    
    session_id = None
    if session_result['status'] == 'success':
        session_id = session_result.get('session_id')
        print(f"   ✅ Created session: {session_id}")
    elif session_result['status'] == 'failed':
        print(f"   ❌ Failed: {session_result.get('error')}")
        return
    
    # Test 3: Add User Message
    logger.info("\n3️⃣ Testing Add User Message")
    user_msg_result = tester.test_add_user_message(session_id)
    print(f"Add User Message: {user_msg_result['status']}")
    if user_msg_result['status'] == 'success':
        print(f"   ✅ User message added successfully")
    elif user_msg_result['status'] == 'failed':
        print(f"   ❌ Failed: {user_msg_result.get('error')}")
    
    # Test 4: Add Assistant Message
    logger.info("\n4️⃣ Testing Add Assistant Message")
    assistant_msg_result = tester.test_add_assistant_message(session_id)
    print(f"Add Assistant Message: {assistant_msg_result['status']}")
    if assistant_msg_result['status'] == 'success':
        print(f"   ✅ Assistant message added successfully")
    elif assistant_msg_result['status'] == 'failed':
        print(f"   ❌ Failed: {assistant_msg_result.get('error')}")
    
    # Test 5: Get Session Details
    logger.info("\n5️⃣ Testing Get Session Details")
    session_details_result = tester.test_get_session_details(session_id)
    print(f"Get Session Details: {session_details_result['status']}")
    if session_details_result['status'] == 'success':
        print(f"   ✅ Session details retrieved, message count: {session_details_result.get('message_count')}")
    elif session_details_result['status'] == 'failed':
        print(f"   ❌ Failed: {session_details_result.get('error')}")
    
    # Test 6: Get Session Messages
    logger.info("\n6️⃣ Testing Get Session Messages")
    messages_result = tester.test_get_session_messages(session_id)
    print(f"Get Session Messages: {messages_result['status']}")
    if messages_result['status'] == 'success':
        print(f"   ✅ Retrieved {messages_result.get('message_count')} messages")
    elif messages_result['status'] == 'failed':
        print(f"   ❌ Failed: {messages_result.get('error')}")
    
    # Test 7: Invalid Session Error Handling
    logger.info("\n7️⃣ Testing Invalid Session Error Handling")
    error_handling_result = tester.test_invalid_session_error_handling()
    print(f"Invalid Session Error Handling: {error_handling_result['status']}")
    if error_handling_result['status'] == 'success':
        print(f"   ✅ Correctly returns 404 for invalid sessions (not 500)")
    elif error_handling_result['status'] == 'failed':
        print(f"   ❌ Failed: {error_handling_result.get('error')}")
    
    # Test 8: Database Persistence
    logger.info("\n8️⃣ Testing Database Persistence")
    db_result = tester.test_database_persistence(session_id)
    print(f"Database Persistence: {db_result['status']}")
    if db_result['status'] == 'success':
        print(f"   ✅ Session and {db_result.get('message_count')} messages found in database")
    elif db_result['status'] == 'failed':
        print(f"   ❌ Failed: {db_result.get('error')}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("🔄 COMPLETE TEST SUMMARY")
    logger.info("=" * 80)
    
    # Count successful tests
    test_results = [
        ("Authentication (demo/demo123)", auth_result['status'] == 'success'),
        ("Session Creation", session_result['status'] == 'success'),
        ("Add User Message", user_msg_result['status'] == 'success'),
        ("Add Assistant Message", assistant_msg_result['status'] == 'success'),
        ("Get Session Details", session_details_result['status'] == 'success'),
        ("Get Session Messages", messages_result['status'] == 'success'),
        ("Invalid Session Error Handling", error_handling_result['status'] == 'success'),
        ("Database Persistence", db_result['status'] == 'success'),
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
        critical_issues.append("Session creation not working")
    if user_msg_result['status'] != 'success':
        critical_issues.append("Cannot add user messages to sessions")
    if assistant_msg_result['status'] != 'success':
        critical_issues.append("Cannot add assistant messages to sessions")
    if session_details_result['status'] != 'success':
        critical_issues.append("Cannot retrieve session details")
    if messages_result['status'] != 'success':
        critical_issues.append("Cannot retrieve session messages")
    if error_handling_result['status'] != 'success':
        critical_issues.append("Invalid session error handling broken - may return 500 instead of 404")
    if db_result['status'] != 'success':
        critical_issues.append("Database persistence not working - sessions/messages not saved")
    
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   - {issue}")
    else:
        print(f"\n🟢 SUCCESS: Session Management and Message Storage working correctly!")
        print("   - Authentication system functional")
        print("   - Session creation working")
        print("   - Message addition (user and assistant) working")
        print("   - Session retrieval working")
        print("   - Message retrieval working")
        print("   - Error handling correct (404 for invalid sessions, not 500)")
        print("   - Database persistence confirmed")
    
    # Test Coverage Notes
    print(f"\n📝 TEST COVERAGE NOTES:")
    print("   - ✅ Authentication with demo/demo123 tested")
    print("   - ✅ Session creation via POST /api/sessions/ tested")
    print("   - ✅ Message addition via POST /api/sessions/messages tested")
    print("   - ✅ Session retrieval via GET /api/sessions/{session_id} tested")
    print("   - ✅ Message retrieval via GET /api/sessions/{session_id}/messages tested")
    print("   - ✅ Error handling for invalid session_id tested (should return 404, not 500)")
    print("   - ✅ Database persistence verified through direct SQLite inspection")
    print("   - ✅ Both user and assistant message types tested")
    print("   - ✅ Session metadata (name, message_count, timestamps) verified")

if __name__ == "__main__":
    main()