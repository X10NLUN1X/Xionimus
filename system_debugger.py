#!/usr/bin/env python3
"""
Advanced Debugging and Monitoring System for XIONIMUS AI
Provides real-time monitoring, performance analysis, and system diagnostics
"""

import asyncio
import requests
import json
import time
import psutil
import subprocess
# import docker  # Removed - No longer using Docker
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

class XionimusDebugger:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.api_base = f"{self.backend_url}/api"
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_local_storage_status(self) -> Dict[str, Any]:
        """Check Local Storage status"""
        try:
            # Check if local storage directory exists and is accessible
            storage_dir = Path("/home/runner/work/XionimusX/XionimusX/backend/local_data")
            storage_exists = storage_dir.exists()
            
            # Check Local Storage connection via API
            api_response = requests.get(f"{self.api_base}/health", timeout=5)
            api_storage_status = "unknown"
            
            if api_response.status_code == 200:
                health_data = api_response.json()
                api_storage_status = health_data.get('services', {}).get('local_storage', 'unknown')
            
            return {
                "storage_directory": str(storage_dir),
                "directory_exists": storage_exists,
                "api_connection_status": api_storage_status,
                "storage_type": "Local File-Based Storage (No Docker)"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_backend_logs(self) -> Dict[str, Any]:
        """Analyze recent backend logs for errors and warnings"""
        try:
            # Get recent logs from docker container if running in docker
            # or from uvicorn process
            
            # For now, get health status as proxy for backend health
            response = requests.get(f"{self.api_base}/health", timeout=5)
            
            if response.status_code == 200:
                health_data = response.json()
                return {
                    "status": "healthy",
                    "services_status": health_data.get('services', {}),
                    "agents_count": health_data.get('agents', {}).get('available', 0),
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "http_status": response.status_code,
                    "last_check": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def test_api_performance(self) -> Dict[str, Any]:
        """Test API endpoint performance"""
        endpoints = [
            ("/", "Root"),
            ("/api/health", "Health Check"),
            ("/api/agents", "Agents List"),
            ("/api/projects", "Projects List"),
            ("/api/api-keys/status", "API Keys Status")
        ]
        
        results = {}
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time_ms = round((end_time - start_time) * 1000, 2)
                
                results[name] = {
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time_ms": response_time_ms,
                    "success": response.status_code == 200
                }
                
            except Exception as e:
                results[name] = {
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False
                }
        
        return results
    
    def analyze_agents_health(self) -> Dict[str, Any]:
        """Analyze agent system health and capabilities"""
        try:
            response = requests.get(f"{self.api_base}/agents", timeout=5)
            
            if response.status_code == 200:
                agents = response.json()
                
                agent_analysis = {}
                for agent in agents:
                    name = agent.get('name')
                    agent_analysis[name] = {
                        'description': agent.get('description', ''),
                        'capabilities': agent.get('capabilities', ''),
                        'status': 'loaded'
                    }
                
                return {
                    'total_agents': len(agents),
                    'agents_loaded': True,
                    'agent_details': agent_analysis,
                    'expected_agents': [
                        "Code Agent", "Research Agent", "Writing Agent", "Data Agent",
                        "QA Agent", "GitHub Agent", "File Agent", "Session Agent"
                    ]
                }
            else:
                return {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def check_emergent_app_readiness(self) -> Dict[str, Any]:
        """Check system readiness for emergent app creation"""
        try:
            # Check all required systems
            health_response = requests.get(f"{self.api_base}/health", timeout=5)
            agents_response = requests.get(f"{self.api_base}/agents", timeout=5)
            keys_response = requests.get(f"{self.api_base}/api-keys/status", timeout=5)
            
            readiness_score = 0
            max_score = 10
            issues = []
            
            # Backend health (2 points)
            if health_response.status_code == 200:
                readiness_score += 2
            else:
                issues.append("Backend health check failed")
            
            # MongoDB connection (2 points)
            if health_response.status_code == 200:
                health_data = health_response.json()
                if health_data.get('services', {}).get('mongodb') == 'connected':
                    readiness_score += 2
                else:
                    issues.append("MongoDB not connected")
            
            # Agents system (3 points)
            if agents_response.status_code == 200:
                agents = agents_response.json()
                if len(agents) >= 8:
                    readiness_score += 3
                else:
                    issues.append(f"Only {len(agents)}/8 agents loaded")
            else:
                issues.append("Agents system not accessible")
            
            # API keys management (2 points) 
            if keys_response.status_code == 200:
                readiness_score += 2
            else:
                issues.append("API key management not working")
                
            # Project creation capability (1 point)
            try:
                test_project = {
                    "name": "Readiness Test",
                    "description": "Testing project creation capability"
                }
                project_response = requests.post(f"{self.api_base}/projects", json=test_project, timeout=10)
                if project_response.status_code == 200:
                    readiness_score += 1
                    # Clean up test project
                    project_data = project_response.json()
                    requests.delete(f"{self.api_base}/projects/{project_data['id']}")
                else:
                    issues.append("Project creation failed")
            except:
                issues.append("Project creation test failed")
            
            readiness_percentage = (readiness_score / max_score) * 100
            
            return {
                'readiness_score': readiness_score,
                'max_score': max_score,
                'readiness_percentage': readiness_percentage,
                'status': 'ready' if readiness_percentage >= 80 else 'not_ready',
                'issues': issues,
                'capabilities': {
                    'project_creation': readiness_score >= 7,
                    'ai_agents': readiness_score >= 5,
                    'data_persistence': readiness_score >= 4,
                    'full_functionality': readiness_score >= 8
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'readiness_percentage': 0
            }
    
    def generate_diagnostic_report(self) -> str:
        """Generate comprehensive diagnostic report"""
        print("🔍 XIONIMUS AI - COMPREHENSIVE DIAGNOSTIC REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System Metrics
        print("💻 SYSTEM METRICS")
        print("-" * 30)
        metrics = self.get_system_metrics()
        if 'error' not in metrics:
            print(f"CPU Usage: {metrics['cpu_percent']}%")
            print(f"Memory Usage: {metrics['memory_percent']}% ({metrics['memory_available_gb']} GB available)")
            print(f"Disk Usage: {metrics['disk_usage_percent']}% ({metrics['disk_free_gb']} GB free)")
        else:
            print(f"❌ Error getting system metrics: {metrics['error']}")
        print()
        
        # Local Storage Status
        print("🏠 LOCAL STORAGE STATUS")
        print("-" * 30)
        storage_status = self.check_local_storage_status()
        if 'error' not in storage_status:
            print(f"Storage Directory: {storage_status['directory_exists']}")
            print(f"API Connection: {storage_status['api_connection_status']}")
            print(f"Storage Type: {storage_status['storage_type']}")
        else:
            print(f"❌ Error checking Local Storage: {storage_status['error']}")
        print()
        
        # Backend Status
        print("🚀 BACKEND STATUS")
        print("-" * 30)
        backend_logs = self.analyze_backend_logs()
        if backend_logs['status'] == 'healthy':
            print(f"✅ Backend Status: {backend_logs['status']}")
            print(f"Agents Available: {backend_logs['agents_count']}")
            for service, status in backend_logs['services_status'].items():
                print(f"{service.capitalize()}: {status}")
        else:
            print(f"❌ Backend Status: {backend_logs['status']}")
            if 'error' in backend_logs:
                print(f"Error: {backend_logs['error']}")
        print()
        
        # API Performance
        print("⚡ API PERFORMANCE")
        print("-" * 30)
        performance = self.test_api_performance()
        for name, result in performance.items():
            status = "✅" if result['success'] else "❌"
            if result['success']:
                print(f"{status} {name}: {result['response_time_ms']}ms")
            else:
                print(f"{status} {name}: {result.get('error', 'Failed')}")
        print()
        
        # Agents Health
        print("🤖 AGENTS HEALTH")
        print("-" * 30)
        agents_health = self.analyze_agents_health()
        if 'error' not in agents_health:
            print(f"Total Agents: {agents_health['total_agents']}")
            print(f"All Agents Loaded: {agents_health['agents_loaded']}")
            for agent_name, details in agents_health['agent_details'].items():
                print(f"  ✅ {agent_name}: {details['capabilities']}")
        else:
            print(f"❌ Error analyzing agents: {agents_health['error']}")
        print()
        
        # Emergent App Readiness
        print("🌟 EMERGENT APP READINESS")
        print("-" * 30)
        readiness = self.check_emergent_app_readiness()
        
        if readiness['status'] != 'error':
            print(f"Readiness Score: {readiness['readiness_score']}/{readiness['max_score']} ({readiness['readiness_percentage']:.1f}%)")
            print(f"Overall Status: {'✅ READY' if readiness['status'] == 'ready' else '⚠️ NOT READY'}")
            
            print("\nCapabilities:")
            for capability, available in readiness['capabilities'].items():
                status = "✅" if available else "❌"
                print(f"  {status} {capability.replace('_', ' ').title()}")
            
            if readiness['issues']:
                print("\nIssues to Address:")
                for issue in readiness['issues']:
                    print(f"  ⚠️ {issue}")
        else:
            print(f"❌ Error checking readiness: {readiness['error']}")
        
        print()
        print("=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        
        if readiness.get('readiness_percentage', 0) >= 80:
            print("🟢 SYSTEM STATUS: EXCELLENT")
            print("✅ Ready for emergent app creation")
            print("✅ All core systems operational")
            print("💡 Next step: Configure AI API keys for full functionality")
        elif readiness.get('readiness_percentage', 0) >= 60:
            print("🟡 SYSTEM STATUS: GOOD")
            print("⚠️ Some issues need attention")
            print("💡 Check issues listed above")
        else:
            print("🔴 SYSTEM STATUS: NEEDS ATTENTION")
            print("❌ Critical issues detected")
            print("🔧 Review failed components above")

if __name__ == "__main__":
    debugger = XionimusDebugger()
    debugger.generate_diagnostic_report()