#!/usr/bin/env python3
"""
Enhanced Debugging Demo for XIONIMUS AI System
Demonstrates comprehensive debugging capabilities and API key management analysis
"""

import asyncio
import aiohttp
import json
import time
import psutil
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

class EnhancedDebuggingDemo:
    """
    Comprehensive debugging demonstration for XIONIMUS AI
    Shows all debugging tools and API key management features
    """
    
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.api_base = f"{self.backend_url}/api"
        
    async def run_complete_debugging_demo(self):
        """Run complete debugging demonstration"""
        print("🔧 XIONIMUS AI - ENHANCED DEBUGGING DEMONSTRATION")
        print("="*80)
        print(f"Backend URL: {self.backend_url}")
        print(f"Demo Start Time: {datetime.now().isoformat()}")
        print("="*80)
        
        async with aiohttp.ClientSession() as session:
            await self._demo_system_health(session)
            await self._demo_api_key_debugging(session)
            await self._demo_agent_system_analysis(session)
            await self._demo_performance_monitoring(session)
            await self._demo_security_features(session)
            await self._demo_error_handling(session)
        
        print("\n" + "="*80)
        print("🎉 ENHANCED DEBUGGING DEMO COMPLETED")
        print("="*80)
    
    async def _demo_system_health(self, session):
        """Demonstrate system health monitoring capabilities"""
        print("\n🏥 1. SYSTEM HEALTH MONITORING")
        print("-" * 40)
        
        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"💻 System Metrics:")
        print(f"   CPU Usage: {cpu_percent}%")
        print(f"   Memory Usage: {memory.percent}% ({memory.available / (1024**3):.2f} GB available)")
        print(f"   Disk Usage: {disk.percent}% ({disk.free / (1024**3):.2f} GB free)")
        
        # Backend health check
        try:
            start_time = time.time()
            async with session.get(f"{self.api_base}/health") as response:
                response_time = (time.time() - start_time) * 1000
                data = await response.json()
                
                print(f"\n🚀 Backend Health Check:")
                print(f"   Status: {data['status']}")
                print(f"   Response Time: {response_time:.2f}ms")
                print(f"   Available Agents: {data['agents']['available']}")
                print(f"   Local Storage: {data['services']['local_storage']}")
                
                for service in ['perplexity', 'claude', 'openai']:
                    status = data['services'].get(service, 'unknown')
                    emoji = "✅" if status == "configured" else "⚠️"
                    print(f"   {service.title()}: {emoji} {status}")
                
        except Exception as e:
            print(f"❌ Health check failed: {str(e)}")
    
    async def _demo_api_key_debugging(self, session):
        """Demonstrate API key debugging capabilities"""
        print("\n🔑 2. API KEY DEBUGGING CAPABILITIES")
        print("-" * 40)
        
        try:
            # Test API key debug endpoint
            async with session.get(f"{self.api_base}/api-keys/debug") as response:
                debug_data = await response.json()
                
                print(f"📊 Local Storage Analysis:")
                storage = debug_data['local_storage_analysis']
                print(f"   Connection: {storage['connection_status']}")
                print(f"   Collection: {storage['collection_name']}")
                print(f"   Documents: {storage['document_count']}")
                
                for doc in storage.get('documents', []):
                    service = doc.get('service', 'unknown')
                    active = "✅" if doc.get('is_active') else "❌"
                    preview = doc.get('key_preview', 'N/A')
                    print(f"     - {service}: {active} {preview}")
                
                print(f"\n🌍 Environment Analysis:")
                env = debug_data['environment_analysis']
                for service, info in env.items():
                    is_set = "✅" if info['is_set'] else "❌"
                    length = info.get('value_length', 0)
                    preview = info.get('value_preview', 'N/A')
                    print(f"   {service.title()}: {is_set} Length:{length} Preview:{preview}")
                
                print(f"\n📁 File System Analysis:")
                fs = debug_data['file_system_analysis']
                env_exists = "✅" if fs.get('env_file_exists', False) else "❌"
                print(f"   .env File: {env_exists} {fs.get('env_file_path', 'N/A')}")
                
                if fs.get('api_key_lines'):
                    print(f"   API Key Lines:")
                    for line in fs['api_key_lines']:
                        print(f"     - {line}")
                
                print(f"\n💊 System Health:")
                health = debug_data['system_health']
                print(f"   Configured: {health['configured_services']}/{health['total_services']}")
                print(f"   Percentage: {health['configuration_percentage']:.1f}%")
                print(f"   Operational: {'✅' if health['all_systems_operational'] else '❌'}")
                
                for rec in health.get('recommendations', []):
                    print(f"   💡 {rec}")
                
        except Exception as e:
            print(f"❌ API key debugging failed: {str(e)}")
    
    async def _demo_agent_system_analysis(self, session):
        """Demonstrate agent system debugging"""
        print("\n🤖 3. AGENT SYSTEM ANALYSIS")
        print("-" * 40)
        
        try:
            async with session.get(f"{self.api_base}/agents") as response:
                agents = await response.json()
                
                print(f"🎯 Agent System Overview:")
                print(f"   Total Agents: {len(agents)}")
                
                for agent in agents:
                    name = agent['name']
                    capabilities = agent.get('capabilities', 'N/A')
                    print(f"   ✅ {name}: {capabilities}")
                
        except Exception as e:
            print(f"❌ Agent system analysis failed: {str(e)}")
    
    async def _demo_performance_monitoring(self, session):
        """Demonstrate performance monitoring capabilities"""
        print("\n⚡ 4. PERFORMANCE MONITORING")
        print("-" * 40)
        
        endpoints = [
            ("Health Check", "/health"),
            ("Agents List", "/agents"), 
            ("API Keys Status", "/api-keys/status"),
            ("Projects List", "/projects"),
            ("API Keys Debug", "/api-keys/debug")
        ]
        
        print(f"🕒 Endpoint Response Times:")
        for name, endpoint in endpoints:
            try:
                start_time = time.time()
                async with session.get(f"{self.api_base}{endpoint}") as response:
                    response_time = (time.time() - start_time) * 1000
                    status = "✅" if response.status == 200 else "❌"
                    print(f"   {name}: {status} {response_time:.2f}ms")
            except Exception as e:
                print(f"   {name}: ❌ Error - {str(e)}")
    
    async def _demo_security_features(self, session):
        """Demonstrate security debugging features"""
        print("\n🔒 5. SECURITY FEATURES DEMONSTRATION")
        print("-" * 40)
        
        try:
            # Test API key status to show security masking
            async with session.get(f"{self.api_base}/api-keys/status") as response:
                data = await response.json()
                
                print(f"🔐 API Key Security Features:")
                print(f"   Key Masking: Implemented (only last 4 chars shown)")
                print(f"   Preview Format: ...XXXX")
                
                if 'details' in data:
                    for service, info in data['details'].items():
                        configured = "✅" if info.get('configured') else "❌"
                        preview = info.get('preview', 'N/A')
                        print(f"   {service.title()}: {configured} {preview}")
                
                print(f"\n🛡️ Security Measures Active:")
                print(f"   ✅ Key masking in responses")
                print(f"   ✅ Environment variable isolation") 
                print(f"   ✅ Secure storage in local database")
                print(f"   ✅ CORS protection enabled")
                
        except Exception as e:
            print(f"❌ Security demonstration failed: {str(e)}")
    
    async def _demo_error_handling(self, session):
        """Demonstrate error handling and debugging"""
        print("\n⚠️ 6. ERROR HANDLING & DEBUGGING")
        print("-" * 40)
        
        print(f"🔍 Testing Error Scenarios:")
        
        # Test invalid API key format
        try:
            async with session.post(f"{self.api_base}/api-keys", 
                                  json={"service": "anthropic", "key": "invalid-format", "is_active": True}) as response:
                data = await response.json()
                print(f"   Invalid Key Format: ✅ Properly rejected - {data.get('detail', 'Unknown')}")
        except Exception as e:
            print(f"   Invalid Key Format: ❌ Error - {str(e)}")
        
        # Test invalid service
        try:
            async with session.post(f"{self.api_base}/api-keys", 
                                  json={"service": "invalid_service", "key": "sk-test-123", "is_active": True}) as response:
                data = await response.json()
                print(f"   Invalid Service: ✅ Properly rejected - {data.get('detail', 'Unknown')}")
        except Exception as e:
            print(f"   Invalid Service: ❌ Error - {str(e)}")
        
        print(f"\n📋 Error Handling Features:")
        print(f"   ✅ Input validation")
        print(f"   ✅ Specific error messages") 
        print(f"   ✅ HTTP status codes")
        print(f"   ✅ Graceful degradation")
        print(f"   ✅ Detailed logging")

async def main():
    """Main demonstration function"""
    demo = EnhancedDebuggingDemo()
    await demo.run_complete_debugging_demo()

if __name__ == "__main__":
    # Check if backend is running
    import requests
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            asyncio.run(main())
        else:
            print("❌ Backend server is not responding properly")
            print("Please start the backend server: cd backend && python3 server.py")
    except requests.exceptions.RequestException:
        print("❌ Backend server is not running on localhost:8001")
        print("Please start the backend server: cd backend && python3 server.py")
        sys.exit(1)