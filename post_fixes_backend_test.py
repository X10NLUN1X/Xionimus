#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - POST-FIXES VERIFICATION
Re-run comprehensive backend testing after fixes to verify 100% success rate.

FIXES APPLIED (as per review request):
1. ✅ Multi-agent health endpoint - Added fast_health_check() without API calls
2. ✅ Session DELETE endpoint - Fixed route pattern and SQLAlchemy query
3. ✅ Developer mode endpoints - Added /junior and /senior endpoints
4. ✅ Agent health check - Fixed API key detection for all providers

TEST PRIORITIES:
1. Multi-Agent System (CRITICAL) - GET /api/v1/multi-agents/health?full_check=false
2. Session DELETE (HIGH) - DELETE /api/v1/sessions/{id}
3. Developer Modes (MEDIUM) - GET /api/developer-modes/junior & /senior
4. Research History (verify still working)
5. All Other Endpoints (regression testing)

EXPECTED RESULTS:
- Multi-agent health: <1 second response time
- Session DELETE: 200 OK response
- Developer modes: 200 OK with proper configs
- Overall success rate: >95%

TEST CREDENTIALS: demo/demo123
"""

import requests
import json
import time
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PostFixesBackendTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.test_results = {}
        self.start_time = time.time()
        
    def authenticate(self) -> Dict[str, Any]:
        """🔐 AUTHENTICATION - Login with demo/demo123"""
        logger.info("🔐 AUTHENTICATION TEST - Login with demo/demo123")
        
        try:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_info = data.get("user", {})
                
                # Set authorization header for future requests
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                logger.info(f"✅ Authentication successful - User: {self.user_info.get('username', 'unknown')}")
                return {"status": "success", "user": self.user_info}
            else:
                logger.error(f"❌ Authentication failed - Status: {response.status_code}, Response: {response.text}")
                return {"status": "failed", "error": response.text}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_multi_agent_health_fast(self) -> Dict[str, Any]:
        """🚀 MULTI-AGENT HEALTH (CRITICAL) - Fast health check without API calls"""
        logger.info("🚀 TESTING MULTI-AGENT HEALTH - Fast check (should be <1s)")
        
        try:
            start_time = time.time()
            
            # Test fast health check (should be <1s)
            response = self.session.get(
                f"{self.api_url}/v1/multi-agents/health?full_check=false",
                timeout=5
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                total_agents = data.get("total_agents", 0)
                agents = data.get("agents", {})
                
                logger.info(f"✅ Multi-agent health check successful - {total_agents} agents, Response time: {response_time:.3f}s")
                
                # Check if response time is under 1 second as expected
                performance_ok = response_time < 1.0
                if performance_ok:
                    logger.info(f"✅ Performance target met: {response_time:.3f}s < 1.0s")
                else:
                    logger.warning(f"⚠️ Performance target missed: {response_time:.3f}s >= 1.0s")
                
                return {
                    "status": "success",
                    "response_time": response_time,
                    "performance_ok": performance_ok,
                    "total_agents": total_agents,
                    "agents": agents
                }
            else:
                logger.error(f"❌ Multi-agent health check failed - Status: {response.status_code}")
                return {"status": "failed", "error": response.text, "response_time": response_time}
                
        except Exception as e:
            logger.error(f"❌ Multi-agent health check error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_multi_agent_types(self) -> Dict[str, Any]:
        """🚀 MULTI-AGENT TYPES - List available agent types"""
        logger.info("🚀 TESTING MULTI-AGENT TYPES")
        
        try:
            response = self.session.get(
                f"{self.api_url}/v1/multi-agents/types",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_types = data.get("agent_types", [])
                
                logger.info(f"✅ Multi-agent types retrieved - {len(agent_types)} types available")
                return {"status": "success", "agent_types": agent_types}
            else:
                logger.error(f"❌ Multi-agent types failed - Status: {response.status_code}")
                return {"status": "failed", "error": response.text}
                
        except Exception as e:
            logger.error(f"❌ Multi-agent types error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_session_delete(self) -> Dict[str, Any]:
        """💬 SESSION DELETE (HIGH PRIORITY) - Test session creation and deletion"""
        logger.info("💬 TESTING SESSION DELETE - Create and delete session")
        
        try:
            # First create a test session
            create_response = self.session.post(
                f"{self.api_url}/sessions/",
                json={"title": "Test Session for Deletion"},
                timeout=10
            )
            
            if create_response.status_code != 200:
                logger.error(f"❌ Session creation failed - Status: {create_response.status_code}")
                return {"status": "failed", "error": "Could not create test session"}
            
            session_data = create_response.json()
            session_id = session_data.get("id")
            
            if not session_id:
                logger.error("❌ Session creation failed - No session ID returned")
                return {"status": "failed", "error": "No session ID returned"}
            
            logger.info(f"✅ Test session created - ID: {session_id}")
            
            # Now test DELETE endpoint (this was returning 405 before fix)
            delete_response = self.session.delete(
                f"{self.api_url}/sessions/{session_id}",
                timeout=10
            )
            
            if delete_response.status_code == 200:
                delete_data = delete_response.json()
                logger.info(f"✅ Session DELETE successful - Status: {delete_data.get('status')}")
                
                # Verify session is actually deleted
                verify_response = self.session.get(
                    f"{self.api_url}/sessions/list",
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    sessions = verify_response.json()
                    session_exists = any(s.get("id") == session_id for s in sessions)
                    
                    if not session_exists:
                        logger.info("✅ Session deletion verified - Session no longer in list")
                        return {"status": "success", "session_id": session_id, "verified": True}
                    else:
                        logger.warning("⚠️ Session still exists in list after deletion")
                        return {"status": "partial", "session_id": session_id, "verified": False}
                
                return {"status": "success", "session_id": session_id, "verified": "unknown"}
            else:
                logger.error(f"❌ Session DELETE failed - Status: {delete_response.status_code}, Response: {delete_response.text}")
                return {"status": "failed", "error": f"DELETE returned {delete_response.status_code}", "session_id": session_id}
                
        except Exception as e:
            logger.error(f"❌ Session DELETE error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_developer_modes(self) -> Dict[str, Any]:
        """🎨 DEVELOPER MODES (MEDIUM PRIORITY) - Test junior and senior endpoints"""
        logger.info("🎨 TESTING DEVELOPER MODES - Junior and Senior endpoints")
        
        results = {}
        
        try:
            # Test main developer modes endpoint
            main_response = self.session.get(
                f"{self.api_url}/developer-modes/",
                timeout=10
            )
            
            if main_response.status_code == 200:
                main_data = main_response.json()
                logger.info("✅ Main developer modes endpoint working")
                results["main"] = {"status": "success", "data": main_data}
            else:
                logger.error(f"❌ Main developer modes failed - Status: {main_response.status_code}")
                results["main"] = {"status": "failed", "error": main_response.text}
            
            # Test junior endpoint (new endpoint as per fix)
            junior_response = self.session.get(
                f"{self.api_url}/developer-modes/junior",
                timeout=10
            )
            
            if junior_response.status_code == 200:
                junior_data = junior_response.json()
                logger.info(f"✅ Junior developer mode endpoint working - Mode: {junior_data.get('mode')}")
                results["junior"] = {"status": "success", "data": junior_data}
            else:
                logger.error(f"❌ Junior developer mode failed - Status: {junior_response.status_code}")
                results["junior"] = {"status": "failed", "error": junior_response.text}
            
            # Test senior endpoint (new endpoint as per fix)
            senior_response = self.session.get(
                f"{self.api_url}/developer-modes/senior",
                timeout=10
            )
            
            if senior_response.status_code == 200:
                senior_data = senior_response.json()
                logger.info(f"✅ Senior developer mode endpoint working - Mode: {senior_data.get('mode')}")
                results["senior"] = {"status": "success", "data": senior_data}
            else:
                logger.error(f"❌ Senior developer mode failed - Status: {senior_response.status_code}")
                results["senior"] = {"status": "failed", "error": senior_response.text}
            
            # Calculate overall success
            successful = sum(1 for r in results.values() if r["status"] == "success")
            total = len(results)
            
            return {
                "status": "success" if successful == total else "partial",
                "successful": successful,
                "total": total,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Developer modes error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_research_history(self) -> Dict[str, Any]:
        """📚 RESEARCH HISTORY - Verify still working after fixes"""
        logger.info("📚 TESTING RESEARCH HISTORY - Verify functionality")
        
        results = {}
        
        try:
            # Test research history endpoint
            history_response = self.session.get(
                f"{self.api_url}/research/history",
                timeout=10
            )
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                logger.info(f"✅ Research history working - {len(history_data)} items")
                results["history"] = {"status": "success", "count": len(history_data)}
            else:
                logger.error(f"❌ Research history failed - Status: {history_response.status_code}")
                results["history"] = {"status": "failed", "error": history_response.text}
            
            # Test research stats
            stats_response = self.session.get(
                f"{self.api_url}/research/stats",
                timeout=10
            )
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                logger.info(f"✅ Research stats working - Total queries: {stats_data.get('total_queries', 0)}")
                results["stats"] = {"status": "success", "data": stats_data}
            else:
                logger.error(f"❌ Research stats failed - Status: {stats_response.status_code}")
                results["stats"] = {"status": "failed", "error": stats_response.text}
            
            # Calculate overall success
            successful = sum(1 for r in results.values() if r["status"] == "success")
            total = len(results)
            
            return {
                "status": "success" if successful == total else "partial",
                "successful": successful,
                "total": total,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"❌ Research history error: {str(e)}")
            return {"status": "error", "error": str(e)}

    def test_regression_endpoints(self) -> Dict[str, Any]:
        """🔄 REGRESSION TESTING - Test other critical endpoints"""
        logger.info("🔄 REGRESSION TESTING - Critical endpoints")
        
        endpoints = [
            ("Health Check", "GET", "/health"),
            ("Version", "GET", "/version"),
            ("Rate Limits Quota", "GET", "/rate-limits/quota"),
            ("API Keys List", "GET", "/api-keys/list"),
            ("Sessions List", "GET", "/sessions/list"),
            ("Sandbox Languages", "GET", "/sandbox/languages"),
            ("GitHub Health", "GET", "/github/health"),
        ]
        
        results = {}
        
        for name, method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.api_url}{endpoint}", timeout=10)
                else:
                    continue  # Skip non-GET for now
                
                if response.status_code == 200:
                    logger.info(f"✅ {name} working")
                    results[name] = {"status": "success", "endpoint": endpoint}
                else:
                    logger.error(f"❌ {name} failed - Status: {response.status_code}")
                    results[name] = {"status": "failed", "endpoint": endpoint, "error": response.status_code}
                    
            except Exception as e:
                logger.error(f"❌ {name} error: {str(e)}")
                results[name] = {"status": "error", "endpoint": endpoint, "error": str(e)}
        
        successful = sum(1 for r in results.values() if r["status"] == "success")
        total = len(results)
        
        return {
            "status": "success" if successful == total else "partial",
            "successful": successful,
            "total": total,
            "results": results
        }

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """🎯 RUN COMPREHENSIVE TEST SUITE"""
        logger.info("🎯 STARTING COMPREHENSIVE BACKEND TESTING - POST-FIXES VERIFICATION")
        logger.info("=" * 80)
        
        # Test results storage
        all_results = {}
        
        # 1. Authentication (Required for other tests)
        auth_result = self.authenticate()
        all_results["authentication"] = auth_result
        
        if auth_result["status"] != "success":
            logger.error("❌ Authentication failed - Cannot proceed with other tests")
            return {"status": "failed", "error": "Authentication required", "results": all_results}
        
        # 2. Multi-Agent System (CRITICAL PRIORITY)
        logger.info("\n" + "="*50)
        logger.info("CRITICAL PRIORITY TESTS")
        logger.info("="*50)
        
        multi_agent_health = self.test_multi_agent_health_fast()
        all_results["multi_agent_health"] = multi_agent_health
        
        multi_agent_types = self.test_multi_agent_types()
        all_results["multi_agent_types"] = multi_agent_types
        
        # 3. Session DELETE (HIGH PRIORITY)
        logger.info("\n" + "="*50)
        logger.info("HIGH PRIORITY TESTS")
        logger.info("="*50)
        
        session_delete = self.test_session_delete()
        all_results["session_delete"] = session_delete
        
        # 4. Developer Modes (MEDIUM PRIORITY)
        logger.info("\n" + "="*50)
        logger.info("MEDIUM PRIORITY TESTS")
        logger.info("="*50)
        
        developer_modes = self.test_developer_modes()
        all_results["developer_modes"] = developer_modes
        
        # 5. Research History (Verify still working)
        logger.info("\n" + "="*50)
        logger.info("REGRESSION VERIFICATION")
        logger.info("="*50)
        
        research_history = self.test_research_history()
        all_results["research_history"] = research_history
        
        # 6. Other Endpoints (Regression testing)
        regression_tests = self.test_regression_endpoints()
        all_results["regression_tests"] = regression_tests
        
        # Calculate overall statistics
        total_time = time.time() - self.start_time
        
        # Count successful tests
        successful_tests = 0
        total_tests = 0
        
        for test_name, result in all_results.items():
            if test_name == "authentication":
                continue  # Skip auth from main count
                
            if isinstance(result, dict):
                if result.get("status") == "success":
                    successful_tests += 1
                elif result.get("successful") and result.get("total"):
                    successful_tests += result["successful"]
                    total_tests += result["total"] - 1  # Adjust for double counting
                total_tests += 1
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Final summary
        logger.info("\n" + "="*80)
        logger.info("🎯 COMPREHENSIVE BACKEND TESTING COMPLETED")
        logger.info("="*80)
        logger.info(f"📊 SUCCESS RATE: {success_rate:.1f}% ({successful_tests}/{total_tests} tests passed)")
        logger.info(f"⏱️  TOTAL TIME: {total_time:.2f} seconds")
        
        # Performance check for multi-agent health
        if multi_agent_health.get("performance_ok"):
            logger.info("✅ Multi-agent health performance target met (<1s)")
        else:
            logger.warning("⚠️ Multi-agent health performance target missed (>=1s)")
        
        # Check if we met the >95% success rate target
        target_met = success_rate > 95.0
        if target_met:
            logger.info("🎉 SUCCESS RATE TARGET MET: >95%")
        else:
            logger.warning(f"⚠️ SUCCESS RATE TARGET MISSED: {success_rate:.1f}% < 95%")
        
        return {
            "status": "success" if target_met else "partial",
            "success_rate": success_rate,
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "total_time": total_time,
            "target_met": target_met,
            "results": all_results
        }

def main():
    """Main test execution"""
    tester = PostFixesBackendTester()
    
    try:
        results = tester.run_comprehensive_test()
        
        # Print final summary
        print("\n" + "="*80)
        print("📋 FINAL TEST REPORT")
        print("="*80)
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Tests Passed: {results['successful_tests']}/{results['total_tests']}")
        print(f"Total Time: {results['total_time']:.2f}s")
        print(f"Target Met (>95%): {'✅ YES' if results['target_met'] else '❌ NO'}")
        
        # Detailed results
        print("\n📊 DETAILED RESULTS:")
        for test_name, result in results['results'].items():
            if isinstance(result, dict):
                status = result.get('status', 'unknown')
                if status == 'success':
                    print(f"  ✅ {test_name}")
                elif status == 'partial':
                    successful = result.get('successful', 0)
                    total = result.get('total', 0)
                    print(f"  ⚠️  {test_name} ({successful}/{total})")
                else:
                    print(f"  ❌ {test_name}")
        
        return results
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
        return {"status": "interrupted"}
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    main()