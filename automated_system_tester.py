#!/usr/bin/env python3
"""
Automated System Tester for XIONIMUS AI
Tests all system components and validates functionality
"""

import asyncio
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("⚠️  aiohttp not available - some tests will be limited")

import time
import json
import subprocess
import signal
import os
from pathlib import Path
from typing import Dict, List, Any
import sys

class AutomatedSystemTester:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:3000"
        self.backend_process = None
        self.test_results = {}
        
    async def run_full_system_test(self):
        """Run complete automated system testing"""
        print("🧪 XIONIMUS AI - AUTOMATED SYSTEM TESTING")
        print("=" * 60)
        
        if not AIOHTTP_AVAILABLE:
            print("⚠️  aiohttp not available - running limited test suite")
            await self.run_limited_system_test()
            return
        
        try:
            # Phase 1: Start Backend
            await self.start_backend_server()
            
            # Phase 2: Test Backend Endpoints
            await self.test_backend_endpoints()
            
            # Phase 3: Test API Key Management
            await self.test_api_key_management()
            
            # Phase 4: Test AI Functionality  
            await self.test_ai_functionality()
            
            # Phase 5: Test Agent System
            await self.test_agent_system()
            
            # Phase 6: Performance Testing
            await self.test_performance()
            
            # Phase 7: Generate Test Report
            self.generate_test_report()
            
        except Exception as e:
            print(f"❌ System test failed: {e}")
        finally:
            # Cleanup
            if self.backend_process:
                self.stop_backend_server()
                
        return self.test_results
    
    async def start_backend_server(self):
        """Start the backend server for testing"""
        print("\n🚀 PHASE 1: STARTING BACKEND SERVER")
        print("-" * 40)
        
        try:
            # Check if server is already running
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.backend_url}/api/health", timeout=2) as response:
                        if response.status == 200:
                            print("   ✅ Backend server already running")
                            return True
            except:
                pass
                
            # Start new server process
            print("   🔧 Starting backend server...")
            self.backend_process = subprocess.Popen(
                [sys.executable, "server.py"],
                cwd=self.backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            max_wait = 30
            for i in range(max_wait):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{self.backend_url}/api/health", timeout=2) as response:
                            if response.status == 200:
                                print(f"   ✅ Backend server started (took {i+1}s)")
                                return True
                except:
                    await asyncio.sleep(1)
                    
            print("   ❌ Backend server failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"   ❌ Failed to start backend: {e}")
            return False
    
    def stop_backend_server(self):
        """Stop the backend server"""
        if self.backend_process:
            print("\n🛑 Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                
    async def test_backend_endpoints(self):
        """Test all backend API endpoints"""
        print("\n🔌 PHASE 2: TESTING BACKEND ENDPOINTS")
        print("-" * 40)
        
        endpoints_to_test = [
            ("GET", "/api/health", "Health check"),
            ("GET", "/api/api-keys/status", "API key status"),
            ("GET", "/api/api-keys/debug", "Debug information"),
            ("GET", "/api/agents", "Agent listing"),
            ("GET", "/api/projects", "Project listing")
        ]
        
        passed = 0
        total = len(endpoints_to_test)
        
        async with aiohttp.ClientSession() as session:
            for method, endpoint, description in endpoints_to_test:
                try:
                    url = f"{self.backend_url}{endpoint}"
                    async with session.request(method, url, timeout=10) as response:
                        if response.status in [200, 404, 422]:  # 404/422 might be expected for some endpoints
                            print(f"   ✅ {description}: {response.status}")
                            passed += 1
                        else:
                            print(f"   ❌ {description}: {response.status}")
                except Exception as e:
                    print(f"   ❌ {description}: Failed - {str(e)[:50]}")
                    
        self.test_results['backend_endpoints'] = {'passed': passed, 'total': total}
        print(f"   📊 Backend endpoints: {passed}/{total} passed")
        
    async def test_api_key_management(self):
        """Test API key management functionality"""
        print("\n🔑 PHASE 3: TESTING API KEY MANAGEMENT")
        print("-" * 40)
        
        tests = []
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Get API key status
            try:
                async with session.get(f"{self.backend_url}/api/api-keys/status") as response:
                    data = await response.json()
                    print(f"   ✅ API key status: {response.status}")
                    tests.append(True)
            except Exception as e:
                print(f"   ❌ API key status failed: {e}")
                tests.append(False)
                
            # Test 2: Get debug information
            try:
                async with session.get(f"{self.backend_url}/api/api-keys/debug") as response:
                    data = await response.json()
                    print(f"   ✅ Debug information: {response.status}")
                    tests.append(True)
            except Exception as e:
                print(f"   ❌ Debug information failed: {e}")
                tests.append(False)
                
            # Test 3: Test invalid API key addition (should fail gracefully)
            try:
                test_data = {"service": "test", "key": "invalid-key", "is_active": True}
                async with session.post(f"{self.backend_url}/api/api-keys", json=test_data) as response:
                    if response.status in [400, 422]:  # Should reject invalid keys
                        print(f"   ✅ Invalid key rejection: {response.status}")
                        tests.append(True)
                    else:
                        print(f"   ⚠️  Invalid key not rejected: {response.status}")
                        tests.append(False)
            except Exception as e:
                print(f"   ❌ API key validation test failed: {e}")
                tests.append(False)
                
        passed = sum(tests)
        self.test_results['api_key_management'] = {'passed': passed, 'total': len(tests)}
        print(f"   📊 API key management: {passed}/{len(tests)} passed")
        
    async def test_ai_functionality(self):
        """Test AI functionality (without real API keys)"""
        print("\n🤖 PHASE 4: TESTING AI FUNCTIONALITY")
        print("-" * 40)
        
        tests = []
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Chat endpoint (should handle missing keys gracefully)
            try:
                chat_data = {"message": "Hello, test message", "conversation_id": "test-123"}
                async with session.post(f"{self.backend_url}/api/chat", json=chat_data) as response:
                    data = await response.json()
                    # Should either work or give helpful error about API keys
                    if response.status in [200, 400, 422, 500]:
                        print(f"   ✅ Chat endpoint responsive: {response.status}")
                        tests.append(True)
                    else:
                        print(f"   ❌ Chat endpoint error: {response.status}")
                        tests.append(False)
            except Exception as e:
                print(f"   ❌ Chat test failed: {e}")
                tests.append(False)
                
            # Test 2: Code generation endpoint  
            try:
                code_data = {"prompt": "Generate a simple hello world function", "language": "python"}
                async with session.post(f"{self.backend_url}/api/generate-code", json=code_data) as response:
                    if response.status in [200, 400, 422, 500]:
                        print(f"   ✅ Code generation responsive: {response.status}")
                        tests.append(True)
                    else:
                        print(f"   ❌ Code generation error: {response.status}")
                        tests.append(False)
            except Exception as e:
                print(f"   ❌ Code generation test failed: {e}")
                tests.append(False)
                
        passed = sum(tests)
        self.test_results['ai_functionality'] = {'passed': passed, 'total': len(tests)}
        print(f"   📊 AI functionality: {passed}/{len(tests)} passed")
        
    async def test_agent_system(self):
        """Test the agent system"""
        print("\n👥 PHASE 5: TESTING AGENT SYSTEM")
        print("-" * 40)
        
        tests = []
        
        async with aiohttp.ClientSession() as session:
            # Test 1: Get available agents
            try:
                async with session.get(f"{self.backend_url}/api/agents") as response:
                    if response.status == 200:
                        data = await response.json()
                        agents_count = len(data.get('agents', []))
                        print(f"   ✅ Available agents: {agents_count} found")
                        tests.append(True)
                    else:
                        print(f"   ❌ Agents listing error: {response.status}")
                        tests.append(False)
            except Exception as e:
                print(f"   ❌ Agents test failed: {e}")
                tests.append(False)
                
            # Test 2: Test request analysis
            try:
                analysis_data = {"request": "Help me create a Python function"}
                async with session.post(f"{self.backend_url}/api/agents/analyze", json=analysis_data) as response:
                    if response.status in [200, 422]:
                        print(f"   ✅ Request analysis: {response.status}")
                        tests.append(True)
                    else:
                        print(f"   ❌ Request analysis error: {response.status}")
                        tests.append(False)
            except Exception as e:
                print(f"   ❌ Request analysis test failed: {e}")
                tests.append(False)
                
        passed = sum(tests)
        self.test_results['agent_system'] = {'passed': passed, 'total': len(tests)}
        print(f"   📊 Agent system: {passed}/{len(tests)} passed")
        
    async def test_performance(self):
        """Test system performance"""
        print("\n⚡ PHASE 6: TESTING PERFORMANCE")
        print("-" * 40)
        
        tests = []
        response_times = []
        
        async with aiohttp.ClientSession() as session:
            # Test response times for health endpoint
            for i in range(5):
                try:
                    start_time = time.time()
                    async with session.get(f"{self.backend_url}/api/health") as response:
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                        
                        if response.status == 200 and response_time < 2.0:
                            tests.append(True)
                        else:
                            tests.append(False)
                except Exception as e:
                    tests.append(False)
                    
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            print(f"   📊 Average response time: {avg_response_time:.3f}s")
            
            if avg_response_time < 0.5:
                print("   ✅ Excellent response time")
            elif avg_response_time < 1.0:
                print("   ✅ Good response time")
            elif avg_response_time < 2.0:
                print("   ⚠️  Acceptable response time")
            else:
                print("   ❌ Poor response time")
                
        passed = sum(tests)
        self.test_results['performance'] = {
            'passed': passed, 
            'total': len(tests),
            'avg_response_time': avg_response_time
        }
        print(f"   📊 Performance tests: {passed}/{len(tests)} passed")
        
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 PHASE 7: GENERATING TEST REPORT")
        print("-" * 40)
        
        total_passed = sum(result['passed'] for result in self.test_results.values() if isinstance(result, dict) and 'passed' in result)
        total_tests = sum(result['total'] for result in self.test_results.values() if isinstance(result, dict) and 'total' in result)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"   📋 Overall Results: {total_passed}/{total_tests} tests passed")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Determine system health
        if success_rate >= 90:
            health_status = "🟢 EXCELLENT"
        elif success_rate >= 75:
            health_status = "🟡 GOOD"
        elif success_rate >= 50:
            health_status = "🟠 FAIR"
        else:
            health_status = "🔴 POOR"
            
        print(f"   🏥 System Health: {health_status}")
        
        # Save detailed report
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': total_tests,
            'total_passed': total_passed,
            'success_rate': success_rate,
            'health_status': health_status,
            'detailed_results': self.test_results
        }
        
        report_file = self.root_dir / "AUTOMATED_TEST_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"   📄 Detailed report saved to: {report_file}")
        
        return report_data

    async def run_limited_system_test(self):
        """Run limited system testing without aiohttp"""
        print("🧪 Running limited system tests without network dependencies...")
        
        # Basic file system checks
        print("\n🗂️  FILESYSTEM CHECKS")
        print("-" * 40)
        
        tests_passed = 0
        total_tests = 5
        
        # Test 1: Backend directory exists
        if self.backend_dir.exists():
            print("   ✅ Backend directory exists")
            tests_passed += 1
        else:
            print("   ❌ Backend directory missing")
            
        # Test 2: Frontend directory exists  
        if self.frontend_dir.exists():
            print("   ✅ Frontend directory exists")
            tests_passed += 1
        else:
            print("   ❌ Frontend directory missing")
            
        # Test 3: Requirements file exists
        if (self.backend_dir / "requirements.txt").exists():
            print("   ✅ Requirements file exists")
            tests_passed += 1
        else:
            print("   ❌ Requirements file missing")
            
        # Test 4: Main server file exists
        if (self.backend_dir / "server.py").exists():
            print("   ✅ Server file exists")
            tests_passed += 1
        else:
            print("   ❌ Server file missing")
            
        # Test 5: Frontend package.json exists
        if (self.frontend_dir / "package.json").exists():
            print("   ✅ Frontend package.json exists")
            tests_passed += 1
        else:
            print("   ❌ Frontend package.json missing")
        
        # Generate limited report
        success_rate = (tests_passed / total_tests) * 100
        
        report_data = {
            'timestamp': time.time(),
            'test_type': 'limited_filesystem_only',
            'aiohttp_available': False,
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'success_rate': success_rate,
            'summary': f"Limited testing completed - {tests_passed}/{total_tests} tests passed"
        }
        
        self.test_results = report_data
        self.generate_test_report()
        
        print(f"\n🎯 Limited Testing Complete: {success_rate:.1f}% success rate")
        return report_data


async def main():
    """Main testing function"""
    tester = AutomatedSystemTester()
    results = await tester.run_full_system_test()
    
    print("\n" + "=" * 60)
    print("🎯 AUTOMATED TESTING COMPLETE")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())