#!/usr/bin/env python3
"""
WebSocket Test Script for Xionimus AI
Tests real-time chat streaming functionality
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime

BACKEND_URL = "ws://localhost:8001"
TEST_SESSION_ID = "test-session-123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

async def test_websocket_connection():
    """Test basic WebSocket connection"""
    print(f"\n{Colors.BLUE}[TEST 1]{Colors.END} Testing WebSocket connection...")
    
    try:
        uri = f"{BACKEND_URL}/ws/chat/{TEST_SESSION_ID}"
        async with websockets.connect(uri, ping_interval=20, ping_timeout=10) as websocket:
            print(f"{Colors.GREEN}✓ Connected to {uri}{Colors.END}")
            return True
    except Exception as e:
        print(f"{Colors.RED}✗ Connection failed: {e}{Colors.END}")
        return False

async def test_send_message():
    """Test sending a message and receiving response"""
    print(f"\n{Colors.BLUE}[TEST 2]{Colors.END} Testing message send/receive...")
    
    try:
        uri = f"{BACKEND_URL}/ws/chat/{TEST_SESSION_ID}"
        async with websockets.connect(uri) as websocket:
            # Send test message
            test_message = {
                "message": "Hello, this is a test message!",
                "provider": "openai",
                "model": "gpt-4"
            }
            
            print(f"{Colors.YELLOW}→ Sending:{Colors.END} {test_message['message']}")
            await websocket.send(json.dumps(test_message))
            
            # Receive response
            response = await asyncio.wait_for(websocket.recv(), timeout=30)
            data = json.loads(response)
            
            print(f"{Colors.GREEN}✓ Received response:{Colors.END}")
            print(f"  Type: {data.get('type', 'unknown')}")
            print(f"  Content: {data.get('content', 'N/A')[:100]}...")
            
            return True
    except asyncio.TimeoutError:
        print(f"{Colors.RED}✗ Timeout waiting for response{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ Test failed: {e}{Colors.END}")
        return False

async def test_streaming():
    """Test streaming response chunks"""
    print(f"\n{Colors.BLUE}[TEST 3]{Colors.END} Testing streaming response...")
    
    try:
        uri = f"{BACKEND_URL}/ws/chat/{TEST_SESSION_ID}"
        async with websockets.connect(uri) as websocket:
            # Send message
            test_message = {
                "message": "Tell me a short joke",
                "provider": "openai"
            }
            
            await websocket.send(json.dumps(test_message))
            
            chunks_received = 0
            full_response = ""
            
            print(f"{Colors.YELLOW}→ Streaming response:{Colors.END}")
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30)
                    data = json.loads(response)
                    
                    if data.get('type') == 'stream_chunk':
                        content = data.get('content', '')
                        full_response += content
                        chunks_received += 1
                        print(f"{content}", end='', flush=True)
                    elif data.get('type') == 'stream_end':
                        print(f"\n{Colors.GREEN}✓ Stream completed{Colors.END}")
                        print(f"  Chunks: {chunks_received}")
                        print(f"  Total length: {len(full_response)} chars")
                        return True
                    elif data.get('type') == 'error':
                        print(f"\n{Colors.RED}✗ Error: {data.get('content')}{Colors.END}")
                        return False
                except asyncio.TimeoutError:
                    print(f"\n{Colors.RED}✗ Stream timeout{Colors.END}")
                    return False
    except Exception as e:
        print(f"\n{Colors.RED}✗ Streaming test failed: {e}{Colors.END}")
        return False

async def test_multiple_connections():
    """Test multiple simultaneous connections"""
    print(f"\n{Colors.BLUE}[TEST 4]{Colors.END} Testing multiple connections...")
    
    async def connect_and_send(session_id: str):
        try:
            uri = f"{BACKEND_URL}/ws/chat/{session_id}"
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({"message": f"Test from {session_id}"}))
                response = await asyncio.wait_for(websocket.recv(), timeout=10)
                return True
        except:
            return False
    
    tasks = [
        connect_and_send(f"test-{i}") 
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    successful = sum(results)
    
    if successful == len(tasks):
        print(f"{Colors.GREEN}✓ All {len(tasks)} connections successful{Colors.END}")
        return True
    else:
        print(f"{Colors.YELLOW}⚠ {successful}/{len(tasks)} connections successful{Colors.END}")
        return False

async def test_disconnect_handling():
    """Test graceful disconnect"""
    print(f"\n{Colors.BLUE}[TEST 5]{Colors.END} Testing disconnect handling...")
    
    try:
        uri = f"{BACKEND_URL}/ws/chat/{TEST_SESSION_ID}"
        websocket = await websockets.connect(uri)
        
        # Send message
        await websocket.send(json.dumps({"message": "Test disconnect"}))
        
        # Close connection
        await websocket.close()
        print(f"{Colors.GREEN}✓ Graceful disconnect successful{Colors.END}")
        
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Disconnect test failed: {e}{Colors.END}")
        return False

async def run_all_tests():
    """Run all WebSocket tests"""
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}Xionimus AI WebSocket Test Suite{Colors.END}")
    print(f"{'='*60}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    tests = [
        ("Connection Test", test_websocket_connection),
        ("Send/Receive Test", test_send_message),
        ("Streaming Test", test_streaming),
        ("Multiple Connections", test_multiple_connections),
        ("Disconnect Handling", test_disconnect_handling),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"{Colors.RED}✗ {name} crashed: {e}{Colors.END}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print(f"{'='*60}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {name:30} [{status}]")
    
    print(f"\n{'='*60}")
    print(f"  TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"  {Colors.GREEN}✓ All tests passed!{Colors.END}")
        return 0
    else:
        print(f"  {Colors.RED}✗ Some tests failed{Colors.END}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        sys.exit(1)
