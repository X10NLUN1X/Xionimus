#!/usr/bin/env python3
"""
Backend WebSocket Testing Suite
Tests WebSocket functionality and diagnoses connection issues
"""

import asyncio
import websockets
import json
import requests
import time
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        
    async def test_websocket_connection(self, session_id: str = "test_session_123") -> Dict[str, Any]:
        """Test WebSocket connection with proper headers"""
        ws_endpoint = f"{self.ws_url}/ws/chat/{session_id}"
        
        # Test with different origin headers
        test_cases = [
            {"name": "No Origin Header", "headers": None},
            {"name": "Localhost:3000 Origin", "headers": {"Origin": "http://localhost:3000"}},
            {"name": "Localhost:5173 Origin", "headers": {"Origin": "http://localhost:5173"}},
            {"name": "127.0.0.1:3000 Origin", "headers": {"Origin": "http://127.0.0.1:3000"}},
            {"name": "Invalid Origin", "headers": {"Origin": "http://malicious-site.com"}},
        ]
        
        results = []
        
        for test_case in test_cases:
            logger.info(f"Testing: {test_case['name']}")
            try:
                # Create WebSocket connection with headers
                if test_case['headers']:
                    websocket = await websockets.connect(
                        ws_endpoint,
                        additional_headers=test_case['headers']
                    )
                else:
                    websocket = await websockets.connect(ws_endpoint)
                
                logger.info(f"✅ {test_case['name']}: Connection successful")
                
                # Test ping/pong
                await websocket.send(json.dumps({"type": "ping"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=2)
                response_data = json.loads(response)
                
                if response_data.get("type") == "pong":
                    logger.info(f"✅ {test_case['name']}: Ping/Pong successful")
                    results.append({
                        "test": test_case['name'],
                        "connection": "success",
                        "ping_pong": "success",
                        "error": None
                    })
                else:
                    logger.warning(f"⚠️ {test_case['name']}: Unexpected ping response: {response_data}")
                    results.append({
                        "test": test_case['name'],
                        "connection": "success",
                        "ping_pong": "failed",
                        "error": f"Unexpected ping response: {response_data}"
                    })
                
                await websocket.close()
                        
            except websockets.exceptions.ConnectionClosedError as e:
                logger.error(f"❌ {test_case['name']}: Connection closed - {e}")
                results.append({
                    "test": test_case['name'],
                    "connection": "failed",
                    "ping_pong": "n/a",
                    "error": f"Connection closed: {e}"
                })
            except websockets.exceptions.InvalidStatusCode as e:
                logger.error(f"❌ {test_case['name']}: Invalid status code - {e}")
                results.append({
                    "test": test_case['name'],
                    "connection": "failed",
                    "ping_pong": "n/a",
                    "error": f"Invalid status code: {e}"
                })
            except Exception as e:
                logger.error(f"❌ {test_case['name']}: Connection failed - {e}")
                results.append({
                    "test": test_case['name'],
                    "connection": "failed",
                    "ping_pong": "n/a",
                    "error": str(e)
                })
                
        return results
    
    def test_backend_health(self) -> Dict[str, Any]:
        """Test backend health and API endpoints"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend health check passed")
                return {"status": "healthy", "data": response.json()}
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def test_stream_status(self) -> Dict[str, Any]:
        """Test streaming service status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/stream/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Stream status check passed")
                return {"status": "available", "data": response.json()}
            else:
                logger.error(f"❌ Stream status check failed: {response.status_code}")
                return {"status": "unavailable", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"❌ Stream status check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_chat_message(self, session_id: str = "test_session_456") -> Dict[str, Any]:
        """Test sending a chat message through WebSocket"""
        ws_endpoint = f"{self.ws_url}/ws/chat/{session_id}"
        
        try:
            websocket = await websockets.connect(
                ws_endpoint,
                additional_headers={"Origin": "http://localhost:3000"}
            )
            logger.info("✅ WebSocket connected for chat test")
            
            # Send a test chat message
            test_message = {
                "type": "chat",
                "content": "Hello, this is a test message",
                "provider": "openai",
                "model": "gpt-4",
                "ultra_thinking": False,
                "api_keys": {},
                "messages": [
                    {"role": "user", "content": "Hello, this is a test message"}
                ]
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info("✅ Test message sent")
            
            # Wait for responses
            responses = []
            timeout_count = 0
            max_timeout = 5  # 5 seconds total timeout
            
            while timeout_count < max_timeout:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1)
                    response_data = json.loads(response)
                    responses.append(response_data)
                    logger.info(f"📨 Received: {response_data.get('type', 'unknown')}")
                    
                    # Break on completion or error
                    if response_data.get("type") in ["complete", "error"]:
                        break
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    continue
            
            await websocket.close()
                return {
                    "status": "success",
                    "responses": responses,
                    "response_count": len(responses)
                }
                
        except Exception as e:
            logger.error(f"❌ Chat message test failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "responses": []
            }

async def main():
    """Main test runner"""
    logger.info("🚀 Starting WebSocket Backend Tests")
    logger.info("=" * 50)
    
    tester = WebSocketTester()
    
    # Test 1: Backend Health
    logger.info("1️⃣ Testing Backend Health")
    health_result = tester.test_backend_health()
    print(f"Backend Health: {health_result['status']}")
    if health_result['status'] != 'healthy':
        print(f"❌ Backend is not healthy: {health_result.get('error', 'Unknown error')}")
        return
    
    # Test 2: Stream Status
    logger.info("\n2️⃣ Testing Stream Status Endpoint")
    stream_result = tester.test_stream_status()
    print(f"Stream Status: {stream_result['status']}")
    
    # Test 3: WebSocket Connections
    logger.info("\n3️⃣ Testing WebSocket Connections")
    ws_results = await tester.test_websocket_connection()
    
    print("\nWebSocket Connection Test Results:")
    print("-" * 40)
    for result in ws_results:
        status_icon = "✅" if result['connection'] == 'success' else "❌"
        print(f"{status_icon} {result['test']}: {result['connection']}")
        if result['error']:
            print(f"   Error: {result['error']}")
    
    # Test 4: Chat Message (only if at least one connection works)
    successful_connections = [r for r in ws_results if r['connection'] == 'success']
    if successful_connections:
        logger.info("\n4️⃣ Testing Chat Message Flow")
        chat_result = await tester.test_chat_message()
        print(f"Chat Message Test: {chat_result['status']}")
        if chat_result['status'] == 'success':
            print(f"   Received {chat_result['response_count']} responses")
        else:
            print(f"   Error: {chat_result.get('error', 'Unknown error')}")
    else:
        logger.warning("\n4️⃣ Skipping Chat Message Test - No successful WebSocket connections")
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    total_tests = len(ws_results)
    successful_tests = len(successful_connections)
    
    print(f"Backend Health: {'✅ Healthy' if health_result['status'] == 'healthy' else '❌ Unhealthy'}")
    print(f"Stream Endpoint: {'✅ Available' if stream_result['status'] == 'available' else '❌ Unavailable'}")
    print(f"WebSocket Tests: {successful_tests}/{total_tests} successful")
    
    if successful_tests == 0:
        print("\n🔴 CRITICAL: All WebSocket connections failed!")
        print("This explains the 403 error in the frontend.")
        print("\nPossible causes:")
        print("- CORS configuration issue in WebSocket endpoint")
        print("- Origin header validation too strict")
        print("- Missing WebSocket middleware configuration")
    elif successful_tests < total_tests:
        print(f"\n🟡 WARNING: {total_tests - successful_tests} WebSocket tests failed")
        print("Some origin configurations are not working properly.")
    else:
        print("\n🟢 SUCCESS: All WebSocket tests passed!")

if __name__ == "__main__":
    asyncio.run(main())