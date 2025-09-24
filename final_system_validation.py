#!/usr/bin/env python3
"""
Final System Health Check and Integration Testing
Complete validation of the XIONIMUS AI system after comprehensive debugging
"""

import asyncio
import requests
import json
import sys
import time
import psutil
import os
from typing import Dict, Any, List
from datetime import datetime

BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class FinalSystemValidation:
    def __init__(self):
        self.test_results = []
        self.system_metrics = {}
        
    def log_test(self, test_name: str, success: bool, details: str = "", metrics: Dict = None):
        """Log test results with detailed metrics"""
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} {test_name}")
        if details:
            print(f"    📝 {details}")
        if metrics:
            for key, value in metrics.items():
                print(f"    📊 {key}: {value}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'metrics': metrics or {},
            'timestamp': datetime.now().isoformat()
        })
    
    def collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            # System resources
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process information
            current_process = psutil.Process()
            process_memory = current_process.memory_info()
            
            self.system_metrics = {
                "cpu_usage_percent": cpu_percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_usage_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_usage_percent": round((disk.used / disk.total) * 100, 1),
                "process_memory_mb": round(process_memory.rss / (1024**2), 1),
                "process_threads": current_process.num_threads(),
                "timestamp": datetime.now().isoformat()
            }
            
            return True
        except Exception as e:
            print(f"⚠️ Could not collect system metrics: {e}")
            return False
    
    def test_complete_system_health(self):
        """Comprehensive system health check"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                
                # Check all required services
                services = health_data.get('services', {})
                mongodb_ok = services.get('mongodb') == 'connected'
                
                # Check agents
                agents = health_data.get('agents', {})
                agents_available = agents.get('available', 0)
                agents_ok = agents_available == 8
                
                # Overall health
                system_healthy = health_data.get('status') == 'healthy'
                
                metrics = {
                    "mongodb_status": services.get('mongodb', 'unknown'),
                    "agents_available": agents_available,
                    "perplexity_status": services.get('perplexity', 'not_configured'),
                    "claude_status": services.get('claude', 'not_configured'),
                    "openai_status": services.get('openai', 'not_configured')
                }
                
                overall_success = mongodb_ok and agents_ok and system_healthy
                
                self.log_test("Complete System Health Check", overall_success,
                             f"MongoDB: {mongodb_ok}, Agents: {agents_ok}, Overall: {system_healthy}",
                             metrics)
            else:
                self.log_test("Complete System Health Check", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Complete System Health Check", False, f"Error: {e}")
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        workflow_success = True
        workflow_steps = []
        
        try:
            # Step 1: Create Project
            project_data = {
                "name": "Final Integration Test Project",
                "description": "Testing complete workflow from project creation to AI interaction"
            }
            
            response = requests.post(f"{API_BASE}/projects", json=project_data, timeout=10)
            if response.status_code == 200:
                project = response.json()
                project_id = project.get('id')
                workflow_steps.append("✅ Project Created")
            else:
                workflow_success = False
                workflow_steps.append("❌ Project Creation Failed")
                project_id = None
            
            # Step 2: Upload File (if project created)
            if project_id:
                test_content = """
# Final Integration Test File
def integration_test():
    '''Test function for final integration validation'''
    return "Integration test successful"

if __name__ == "__main__":
    result = integration_test()
    print(result)
"""
                files = {'file': ('integration_test.py', test_content, 'text/plain')}
                data = {'project_id': project_id}
                
                response = requests.post(f"{API_BASE}/files", files=files, data=data, timeout=10)
                if response.status_code == 200:
                    workflow_steps.append("✅ File Uploaded")
                else:
                    workflow_success = False
                    workflow_steps.append("❌ File Upload Failed")
            
            # Step 3: AI Interaction
            response = requests.post(f"{API_BASE}/chat", json={
                "message": "Analyze the integration test and suggest improvements",
                "conversation_id": "final-integration-test"
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content_length = len(result.get('message', {}).get('content', ''))
                if content_length > 50:
                    workflow_steps.append("✅ AI Analysis Completed")
                else:
                    workflow_success = False
                    workflow_steps.append("❌ AI Analysis Too Short")
            else:
                workflow_success = False
                workflow_steps.append("❌ AI Analysis Failed")
            
            # Step 4: Retrieve Project Data
            if project_id:
                response = requests.get(f"{API_BASE}/projects/{project_id}", timeout=10)
                if response.status_code == 200:
                    workflow_steps.append("✅ Project Data Retrieved")
                else:
                    workflow_success = False
                    workflow_steps.append("❌ Project Retrieval Failed")
            
            self.log_test("End-to-End Workflow", workflow_success,
                         " → ".join(workflow_steps))
                         
        except Exception as e:
            self.log_test("End-to-End Workflow", False, f"Error: {e}")
    
    def test_api_documentation_coverage(self):
        """Test API documentation and endpoint coverage"""
        try:
            # Check if docs are available
            response = requests.get(f"{BACKEND_URL}/docs", timeout=10)
            docs_available = response.status_code == 200
            
            # Test key endpoints
            endpoints_to_test = [
                "/api/health",
                "/api/agents", 
                "/api/projects",
                "/api/api-keys/status",
                "/api/chat",
                "/api/generate-code"
            ]
            
            available_endpoints = 0
            for endpoint in endpoints_to_test:
                try:
                    if endpoint == "/api/chat" or endpoint == "/api/generate-code":
                        # These require POST, so just check if they don't return 404
                        test_response = requests.post(f"{BACKEND_URL}{endpoint}", 
                                                    json={"test": "endpoint_check"}, 
                                                    timeout=5)
                        if test_response.status_code != 404:
                            available_endpoints += 1
                    else:
                        test_response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
                        if test_response.status_code != 404:
                            available_endpoints += 1
                except:
                    continue
            
            coverage_percent = (available_endpoints / len(endpoints_to_test)) * 100
            
            metrics = {
                "docs_available": docs_available,
                "endpoint_coverage_percent": coverage_percent,
                "available_endpoints": f"{available_endpoints}/{len(endpoints_to_test)}"
            }
            
            success = docs_available and coverage_percent >= 80
            
            self.log_test("API Documentation Coverage", success,
                         f"Docs: {docs_available}, Coverage: {coverage_percent:.1f}%",
                         metrics)
                         
        except Exception as e:
            self.log_test("API Documentation Coverage", False, f"Error: {e}")
    
    def test_data_persistence_integrity(self):
        """Test data persistence and integrity across operations"""
        try:
            # Get initial counts
            projects_response = requests.get(f"{API_BASE}/projects", timeout=10)
            initial_project_count = len(projects_response.json()) if projects_response.status_code == 200 else 0
            
            # Create test data
            project_response = requests.post(f"{API_BASE}/projects", json={
                "name": "Data Integrity Test",
                "description": "Testing data persistence integrity"
            }, timeout=10)
            
            if project_response.status_code == 200:
                project_id = project_response.json().get('id')
                
                # Verify immediate persistence
                verify_response = requests.get(f"{API_BASE}/projects", timeout=10)
                if verify_response.status_code == 200:
                    current_count = len(verify_response.json())
                    persistence_ok = current_count == initial_project_count + 1
                    
                    # Check if specific project exists
                    projects = verify_response.json()
                    project_exists = any(p.get('id') == project_id for p in projects)
                    
                    success = persistence_ok and project_exists
                    
                    self.log_test("Data Persistence Integrity", success,
                                 f"Project count: {initial_project_count} → {current_count}, Project exists: {project_exists}")
                else:
                    self.log_test("Data Persistence Integrity", False, "Could not verify data persistence")
            else:
                self.log_test("Data Persistence Integrity", False, f"Project creation failed: {project_response.status_code}")
                
        except Exception as e:
            self.log_test("Data Persistence Integrity", False, f"Error: {e}")
    
    def test_security_and_error_handling(self):
        """Test security measures and comprehensive error handling"""
        security_tests = []
        
        # Test 1: Invalid API key format protection
        try:
            response = requests.post(f"{API_BASE}/api-keys", json={
                "service": "anthropic",
                "key": "invalid-key-format",
                "is_active": True
            }, timeout=10)
            
            if response.status_code == 400:
                security_tests.append("✅ Invalid API key format rejected")
            else:
                security_tests.append("❌ Invalid API key format accepted")
        except:
            security_tests.append("❌ API key validation error")
        
        # Test 2: Invalid service name protection
        try:
            response = requests.post(f"{API_BASE}/api-keys", json={
                "service": "invalid_service",
                "key": "sk-test-123",
                "is_active": True
            }, timeout=10)
            
            if response.status_code == 400:
                security_tests.append("✅ Invalid service name rejected")
            else:
                security_tests.append("❌ Invalid service name accepted")
        except:
            security_tests.append("❌ Service validation error")
        
        # Test 3: Empty request handling
        try:
            response = requests.post(f"{API_BASE}/chat", json={}, timeout=10)
            if response.status_code in [400, 422]:  # Bad request or validation error
                security_tests.append("✅ Empty request properly rejected")
            else:
                security_tests.append("❌ Empty request not handled")
        except:
            security_tests.append("❌ Empty request handling error")
        
        successful_security_tests = len([t for t in security_tests if t.startswith("✅")])
        success = successful_security_tests >= 2
        
        self.log_test("Security & Error Handling", success,
                     " | ".join(security_tests),
                     {"successful_tests": f"{successful_security_tests}/3"})
    
    def test_performance_benchmarks(self):
        """Test performance benchmarks and response times"""
        try:
            performance_metrics = {}
            
            # Test 1: Health check response time
            start_time = time.time()
            health_response = requests.get(f"{API_BASE}/health", timeout=10)
            health_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Test 2: Project list response time
            start_time = time.time()
            projects_response = requests.get(f"{API_BASE}/projects", timeout=10)
            projects_time = (time.time() - start_time) * 1000
            
            # Test 3: Agent list response time
            start_time = time.time()
            agents_response = requests.get(f"{API_BASE}/agents", timeout=10)
            agents_time = (time.time() - start_time) * 1000
            
            performance_metrics = {
                "health_check_ms": round(health_time, 2),
                "projects_list_ms": round(projects_time, 2),
                "agents_list_ms": round(agents_time, 2),
                "average_response_ms": round((health_time + projects_time + agents_time) / 3, 2)
            }
            
            # Performance thresholds (in milliseconds)
            health_ok = health_time < 1000  # 1 second
            projects_ok = projects_time < 2000  # 2 seconds
            agents_ok = agents_time < 1000  # 1 second
            
            success = health_ok and projects_ok and agents_ok
            
            self.log_test("Performance Benchmarks", success,
                         f"All endpoints under threshold: {success}",
                         performance_metrics)
                         
        except Exception as e:
            self.log_test("Performance Benchmarks", False, f"Error: {e}")
    
    def run_final_validation(self):
        """Run complete final system validation"""
        print("🏁 FINAL SYSTEM VALIDATION & HEALTH CHECK")
        print("=" * 80)
        print(f"🕒 Validation Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Collect system metrics first
        print("📊 SYSTEM METRICS COLLECTION")
        print("-" * 40)
        metrics_collected = self.collect_system_metrics()
        if metrics_collected:
            for key, value in self.system_metrics.items():
                if key != "timestamp":
                    print(f"    {key}: {value}")
            print()
        
        # Core system validation
        print("🔍 CORE SYSTEM VALIDATION")
        print("-" * 40)
        self.test_complete_system_health()
        self.test_data_persistence_integrity()
        
        # Integration testing
        print("🔄 INTEGRATION TESTING")
        print("-" * 40)
        self.test_end_to_end_workflow()
        self.test_api_documentation_coverage()
        
        # Security and performance
        print("🛡️ SECURITY & PERFORMANCE")
        print("-" * 40)
        self.test_security_and_error_handling()
        self.test_performance_benchmarks()
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print comprehensive final summary"""
        print("=" * 80)
        print("🏆 FINAL SYSTEM VALIDATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Test Results:")
        print(f"    Total Tests: {total_tests}")
        print(f"    Passed: {passed_tests} ✅")
        print(f"    Failed: {failed_tests} ❌")
        print(f"    Success Rate: {success_rate:.1f}%")
        print()
        
        # System metrics summary
        if self.system_metrics:
            print(f"💻 System Resources:")
            print(f"    CPU Usage: {self.system_metrics.get('cpu_usage_percent', 'N/A')}%")
            print(f"    Memory Usage: {self.system_metrics.get('memory_usage_percent', 'N/A')}%")
            print(f"    Disk Usage: {self.system_metrics.get('disk_usage_percent', 'N/A')}%")
            print(f"    Process Memory: {self.system_metrics.get('process_memory_mb', 'N/A')} MB")
            print()
        
        if failed_tests > 0:
            print("🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
            print()
        
        # Final system status
        print("🎯 FINAL SYSTEM STATUS:")
        if success_rate >= 95:
            print("    ✅ EXCELLENT - System is production-ready and highly optimized")
        elif success_rate >= 85:
            print("    🟢 VERY GOOD - System is stable and ready for use")
        elif success_rate >= 75:
            print("    🟡 GOOD - System is functional with minor issues")
        elif success_rate >= 60:
            print("    🟠 NEEDS IMPROVEMENT - Several issues need attention")
        else:
            print("    🔴 CRITICAL - Major system issues require immediate attention")
        
        print()
        print("📋 SYSTEM READINESS CHECKLIST:")
        
        # Check key components
        health_test = next((t for t in self.test_results if 'System Health' in t['test']), None)
        workflow_test = next((t for t in self.test_results if 'End-to-End' in t['test']), None)
        performance_test = next((t for t in self.test_results if 'Performance' in t['test']), None)
        security_test = next((t for t in self.test_results if 'Security' in t['test']), None)
        
        print(f"    {'✅' if health_test and health_test['success'] else '❌'} Core System Health")
        print(f"    {'✅' if workflow_test and workflow_test['success'] else '❌'} End-to-End Workflows")
        print(f"    {'✅' if performance_test and performance_test['success'] else '❌'} Performance Standards")
        print(f"    {'✅' if security_test and security_test['success'] else '❌'} Security Measures")
        print()
        
        print("🚀 DEPLOYMENT RECOMMENDATION:")
        if success_rate >= 90:
            print("    ✅ READY FOR PRODUCTION - All major systems operational")
        elif success_rate >= 80:
            print("    🟡 READY FOR STAGING - Minor optimizations recommended")
        else:
            print("    ❌ NOT READY - Address critical issues before deployment")
        
        print("=" * 80)


if __name__ == "__main__":
    # Check if backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server is not responding properly")
            print("Please ensure the backend server is running")
            sys.exit(1)
    except:
        print("❌ Backend server is not running")
        print("Please start the backend server first")
        sys.exit(1)
    
    # Run final validation
    validator = FinalSystemValidation()
    validator.run_final_validation()