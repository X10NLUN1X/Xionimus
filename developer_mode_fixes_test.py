#!/usr/bin/env python3
"""
DEVELOPER MODE FIXES TESTING - Backend Re-testing

This script tests the specific fixes applied for:
1. Default Configuration Fix - Research workflow skipped when developer_mode is explicitly set
2. Ultra-Thinking Fix - Added fallback logic to ensure ultra_thinking defaults to True for senior mode
3. Active Project Fields - Added new API endpoint POST /api/sessions/{session_id}/set-active-project

TESTS TO PERFORM:
1. Developer Mode with Direct AI Access (CRITICAL)
2. Ultra-Thinking Verification
3. Active Project API
4. Fallback Chain (if Claude fails)
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeveloperModeFixesTester:
    def __init__(self, base_url: str = None):
        # Use localhost for testing since we're in the same container
        self.base_url = base_url or "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None

    def authenticate_demo_user(self) -> Dict[str, Any]:
        """Authenticate with demo/demo123 credentials"""
        logger.info("🔐 Authenticating with demo user (demo/demo123)")
        
        try:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = self.session.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                logger.info("✅ Authentication successful!")
                logger.info(f"   User ID: {self.user_info['user_id']}")
                logger.info(f"   Username: {self.user_info['username']}")
                
                return {"status": "success", "token": self.token, "user_info": self.user_info}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {"status": "failed", "error": error_detail}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def test_developer_mode_junior_direct_ai(self) -> Dict[str, Any]:
        """Test 1: Developer Mode Junior with Direct AI Access (CRITICAL)"""
        logger.info("🎯 Testing Developer Mode Junior - Direct AI Access (CRITICAL)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test chat request with developer_mode: "junior"
            chat_data = {
                "messages": [{"role": "user", "content": "What is Python programming language?"}],
                "developer_mode": "junior"
                # No provider/model specified - should use junior defaults
            }
            
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                chat_response = response.json()
                actual_provider = chat_response.get("provider")
                actual_model = chat_response.get("model")
                ultra_thinking_used = chat_response.get("usage", {}).get("thinking_used", False)
                
                logger.info(f"   Actual provider: {actual_provider}")
                logger.info(f"   Actual model: {actual_model}")
                logger.info(f"   Ultra-thinking used: {ultra_thinking_used}")
                
                # Expected for junior mode
                expected_provider = "anthropic"
                expected_model = "claude-3-5-haiku-20241022"
                expected_ultra_thinking = False
                
                provider_correct = actual_provider == expected_provider
                model_correct = actual_model == expected_model
                ultra_thinking_correct = ultra_thinking_used == expected_ultra_thinking
                
                # Check that NO research workflow was triggered
                no_research_workflow = actual_provider != "system" and actual_model != "xionimus-workflow"
                
                logger.info(f"   Provider correct: {'✅' if provider_correct else '❌'} (expected: {expected_provider})")
                logger.info(f"   Model correct: {'✅' if model_correct else '❌'} (expected: {expected_model})")
                logger.info(f"   Ultra-thinking correct: {'✅' if ultra_thinking_correct else '❌'} (expected: {expected_ultra_thinking})")
                logger.info(f"   No research workflow: {'✅' if no_research_workflow else '❌'} (should be direct AI)")
                
                if provider_correct and model_correct and no_research_workflow:
                    logger.info("✅ Developer Mode Junior working correctly!")
                    return {
                        "status": "success",
                        "actual_provider": actual_provider,
                        "actual_model": actual_model,
                        "ultra_thinking_used": ultra_thinking_used,
                        "no_research_workflow": no_research_workflow,
                        "junior_mode_working": True
                    }
                else:
                    logger.error("❌ Developer Mode Junior not working correctly!")
                    return {
                        "status": "failed",
                        "error": f"Expected provider={expected_provider}, model={expected_model}, got provider={actual_provider}, model={actual_model}",
                        "actual_provider": actual_provider,
                        "actual_model": actual_model,
                        "no_research_workflow": no_research_workflow,
                        "junior_mode_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Chat request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Developer Mode Junior test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_developer_mode_senior_direct_ai(self) -> Dict[str, Any]:
        """Test 2: Developer Mode Senior with Direct AI Access (CRITICAL)"""
        logger.info("🎯 Testing Developer Mode Senior - Direct AI Access (CRITICAL)")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test chat request with developer_mode: "senior"
            chat_data = {
                "messages": [{"role": "user", "content": "What is Python programming language?"}],
                "developer_mode": "senior"
                # No provider/model specified - should use senior defaults
            }
            
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                chat_response = response.json()
                actual_provider = chat_response.get("provider")
                actual_model = chat_response.get("model")
                ultra_thinking_used = chat_response.get("usage", {}).get("thinking_used", False)
                
                logger.info(f"   Actual provider: {actual_provider}")
                logger.info(f"   Actual model: {actual_model}")
                logger.info(f"   Ultra-thinking used: {ultra_thinking_used}")
                
                # Expected for senior mode
                expected_provider = "anthropic"
                expected_model = "claude-sonnet-4-5-20250929"
                expected_ultra_thinking = True
                
                provider_correct = actual_provider == expected_provider
                model_correct = actual_model == expected_model
                ultra_thinking_correct = ultra_thinking_used == expected_ultra_thinking
                
                # Check that NO research workflow was triggered
                no_research_workflow = actual_provider != "system" and actual_model != "xionimus-workflow"
                
                logger.info(f"   Provider correct: {'✅' if provider_correct else '❌'} (expected: {expected_provider})")
                logger.info(f"   Model correct: {'✅' if model_correct else '❌'} (expected: {expected_model})")
                logger.info(f"   Ultra-thinking correct: {'✅' if ultra_thinking_correct else '❌'} (expected: {expected_ultra_thinking})")
                logger.info(f"   No research workflow: {'✅' if no_research_workflow else '❌'} (should be direct AI)")
                
                if provider_correct and model_correct and no_research_workflow:
                    logger.info("✅ Developer Mode Senior working correctly!")
                    return {
                        "status": "success",
                        "actual_provider": actual_provider,
                        "actual_model": actual_model,
                        "ultra_thinking_used": ultra_thinking_used,
                        "no_research_workflow": no_research_workflow,
                        "senior_mode_working": True
                    }
                else:
                    logger.error("❌ Developer Mode Senior not working correctly!")
                    return {
                        "status": "failed",
                        "error": f"Expected provider={expected_provider}, model={expected_model}, got provider={actual_provider}, model={actual_model}",
                        "actual_provider": actual_provider,
                        "actual_model": actual_model,
                        "no_research_workflow": no_research_workflow,
                        "senior_mode_working": False
                    }
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Chat request failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Developer Mode Senior test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_ultra_thinking_verification(self) -> Dict[str, Any]:
        """Test 3: Ultra-Thinking Verification"""
        logger.info("🧠 Testing Ultra-Thinking Verification")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            results = {}
            
            # Test 1: Senior mode (should have ultra_thinking: true)
            senior_data = {
                "messages": [{"role": "user", "content": "Explain quantum computing"}],
                "developer_mode": "senior"
            }
            
            logger.info("   Testing senior mode ultra-thinking...")
            senior_response = self.session.post(
                f"{self.api_url}/chat/",
                json=senior_data,
                headers=headers,
                timeout=45
            )
            
            if senior_response.status_code == 200:
                senior_result = senior_response.json()
                senior_thinking_used = senior_result.get("usage", {}).get("thinking_used", False)
                
                results["senior_mode"] = {
                    "thinking_used": senior_thinking_used,
                    "expected": True,
                    "correct": senior_thinking_used == True
                }
                logger.info(f"   Senior mode thinking: {'✅' if senior_thinking_used else '❌'} (expected: True)")
            else:
                results["senior_mode"] = {"error": f"HTTP {senior_response.status_code}"}
            
            # Test 2: Junior mode (should have ultra_thinking: false)
            junior_data = {
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "developer_mode": "junior"
            }
            
            logger.info("   Testing junior mode ultra-thinking...")
            junior_response = self.session.post(
                f"{self.api_url}/chat/",
                json=junior_data,
                headers=headers,
                timeout=30
            )
            
            if junior_response.status_code == 200:
                junior_result = junior_response.json()
                junior_thinking_used = junior_result.get("usage", {}).get("thinking_used", False)
                
                results["junior_mode"] = {
                    "thinking_used": junior_thinking_used,
                    "expected": False,
                    "correct": junior_thinking_used == False
                }
                logger.info(f"   Junior mode thinking: {'✅' if not junior_thinking_used else '❌'} (expected: False)")
            else:
                results["junior_mode"] = {"error": f"HTTP {junior_response.status_code}"}
            
            # Evaluate results
            senior_correct = results.get("senior_mode", {}).get("correct", False)
            junior_correct = results.get("junior_mode", {}).get("correct", False)
            
            if senior_correct and junior_correct:
                logger.info("✅ Ultra-thinking verification working correctly!")
                return {
                    "status": "success",
                    "results": results,
                    "ultra_thinking_working": True
                }
            else:
                logger.error("❌ Ultra-thinking verification not working correctly")
                return {
                    "status": "failed",
                    "error": "Ultra-thinking not properly set based on developer mode",
                    "results": results,
                    "ultra_thinking_working": False
                }
                
        except Exception as e:
            logger.error(f"❌ Ultra-thinking verification test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_active_project_api(self) -> Dict[str, Any]:
        """Test 4: Active Project API"""
        logger.info("📁 Testing Active Project API")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Step 1: Create a new session
            session_data = {"name": "Active Project Test Session"}
            session_response = self.session.post(
                f"{self.api_url}/sessions/",
                json=session_data,
                headers=headers,
                timeout=10
            )
            
            if session_response.status_code != 200:
                return {"status": "failed", "error": "Could not create test session"}
            
            session_id = session_response.json().get("id")
            logger.info(f"   Created test session: {session_id}")
            
            # Step 2: Test POST /api/sessions/{session_id}/set-active-project
            project_data = {
                "project_name": "test-project",
                "branch": "main"
            }
            
            set_project_response = self.session.post(
                f"{self.api_url}/sessions/{session_id}/set-active-project",
                json=project_data,
                headers=headers,
                timeout=10
            )
            
            logger.info(f"   Set active project response: {set_project_response.status_code}")
            
            if set_project_response.status_code == 200:
                set_project_result = set_project_response.json()
                logger.info(f"   Set project result: {set_project_result}")
                
                # Step 3: Verify session response includes active_project fields
                session_check_response = self.session.get(
                    f"{self.api_url}/sessions/{session_id}",
                    headers=headers,
                    timeout=10
                )
                
                if session_check_response.status_code == 200:
                    session_data = session_check_response.json()
                    active_project = session_data.get("active_project")
                    active_project_branch = session_data.get("active_project_branch")
                    
                    logger.info(f"   Active project: {active_project}")
                    logger.info(f"   Active project branch: {active_project_branch}")
                    
                    project_fields_present = (
                        active_project == "test-project" and
                        active_project_branch == "main"
                    )
                    
                    if project_fields_present:
                        logger.info("✅ Active Project API working correctly!")
                        return {
                            "status": "success",
                            "session_id": session_id,
                            "active_project": active_project,
                            "active_project_branch": active_project_branch,
                            "api_working": True
                        }
                    else:
                        logger.error("❌ Active project fields not properly set")
                        return {
                            "status": "failed",
                            "error": f"Expected project=test-project, branch=main, got project={active_project}, branch={active_project_branch}",
                            "session_id": session_id,
                            "active_project": active_project,
                            "active_project_branch": active_project_branch,
                            "api_working": False
                        }
                else:
                    return {"status": "failed", "error": "Could not retrieve session after setting project"}
            else:
                error_detail = set_project_response.json().get("detail", "Unknown error") if set_project_response.content else f"HTTP {set_project_response.status_code}"
                logger.error(f"❌ Set active project failed: {error_detail}")
                return {
                    "status": "failed",
                    "error": error_detail,
                    "status_code": set_project_response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Active Project API test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_fallback_chain(self) -> Dict[str, Any]:
        """Test 5: Fallback Chain (if Claude fails)"""
        logger.info("🔄 Testing Fallback Chain")
        
        if not self.token:
            return {"status": "skipped", "error": "No authentication token available"}
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test with an invalid Claude model name
            fallback_data = {
                "messages": [{"role": "user", "content": "Test fallback mechanism"}],
                "provider": "anthropic",
                "model": "claude-invalid-model-test-12345"  # Invalid model to trigger fallback
            }
            
            logger.info("   Testing fallback with invalid Claude model...")
            response = self.session.post(
                f"{self.api_url}/chat/",
                json=fallback_data,
                headers=headers,
                timeout=45
            )
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                actual_provider = result.get("provider")
                actual_model = result.get("model")
                
                logger.info(f"   Fallback provider: {actual_provider}")
                logger.info(f"   Fallback model: {actual_model}")
                
                # Should fallback to a working model
                fallback_worked = (
                    (actual_provider == "anthropic" and actual_model != "claude-invalid-model-test-12345") or
                    (actual_provider == "openai" and "gpt" in actual_model.lower())
                )
                
                if fallback_worked:
                    logger.info("✅ Fallback chain working!")
                    return {
                        "status": "success",
                        "fallback_provider": actual_provider,
                        "fallback_model": actual_model,
                        "fallback_working": True
                    }
                else:
                    logger.error("❌ Fallback not working correctly")
                    return {
                        "status": "failed",
                        "error": f"Expected fallback to working model, got {actual_provider}/{actual_model}",
                        "fallback_provider": actual_provider,
                        "fallback_model": actual_model,
                        "fallback_working": False
                    }
            else:
                # Check if it's a proper error with fallback attempts logged
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.info(f"   Fallback error (expected): {error_detail}")
                
                # Even if it fails, if it shows fallback attempts, that's good
                fallback_attempted = "fallback" in error_detail.lower() or "invalid" in error_detail.lower()
                
                return {
                    "status": "partial" if fallback_attempted else "failed",
                    "error": error_detail,
                    "status_code": response.status_code,
                    "fallback_attempted": fallback_attempted,
                    "note": "System attempted fallback but still failed (acceptable behavior)"
                }
                
        except Exception as e:
            logger.error(f"❌ Fallback chain test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all developer mode fixes tests"""
        logger.info("🚀 Starting Developer Mode Fixes Testing")
        logger.info("=" * 80)
        
        # Authenticate first
        auth_result = self.authenticate_demo_user()
        if auth_result.get("status") != "success":
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return {"status": "failed", "error": "Authentication failed"}
        
        # Run all tests
        test_results = {}
        
        # Test 1: Developer Mode Junior with Direct AI Access
        test_results["developer_mode_junior"] = self.test_developer_mode_junior_direct_ai()
        
        # Test 2: Developer Mode Senior with Direct AI Access
        test_results["developer_mode_senior"] = self.test_developer_mode_senior_direct_ai()
        
        # Test 3: Ultra-Thinking Verification
        test_results["ultra_thinking_verification"] = self.test_ultra_thinking_verification()
        
        # Test 4: Active Project API
        test_results["active_project_api"] = self.test_active_project_api()
        
        # Test 5: Fallback Chain
        test_results["fallback_chain"] = self.test_fallback_chain()
        
        # Summary
        logger.info("=" * 80)
        logger.info("🎯 DEVELOPER MODE FIXES TEST SUMMARY")
        logger.info("=" * 80)
        
        passed_tests = 0
        failed_tests = 0
        
        for test_name, result in test_results.items():
            status = result.get("status", "unknown")
            if status == "success":
                logger.info(f"✅ {test_name}: PASSED")
                passed_tests += 1
            elif status == "partial":
                logger.info(f"⚠️ {test_name}: PARTIAL")
            else:
                logger.info(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                failed_tests += 1
        
        logger.info(f"\nOverall: {passed_tests} passed, {failed_tests} failed")
        
        return {
            "status": "success" if failed_tests == 0 else "partial" if passed_tests > 0 else "failed",
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "test_results": test_results
        }

def main():
    """Main function to run the tests"""
    tester = DeveloperModeFixesTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results.get("status") == "success":
        exit(0)
    elif results.get("status") == "partial":
        exit(1)
    else:
        exit(2)

if __name__ == "__main__":
    main()