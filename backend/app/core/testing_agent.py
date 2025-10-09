"""
Testing Agent - Automated Backend & Frontend Testing
Emergent-Style Testing mit Curl und Playwright
"""
import sys
import asyncio
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

IS_WINDOWS = sys.platform == 'win32'

logger = logging.getLogger(__name__)

class TestingAgent:
    """Automated testing agent for backend and frontend"""
    
    def __init__(self, workspace_root: str = "/app/xionimus-ai"):
        self.workspace_root = Path(workspace_root)
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:3000"
        self.test_results: List[Dict] = []
    
    async def test_backend_endpoint(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        expected_status: int = 200
    ) -> Dict[str, Any]:
        """
        Test a backend endpoint using curl
        """
        try:
            url = f"{self.backend_url}{endpoint}"
            
            # Build curl command
            cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method, url]
            
            if headers:
                for key, value in headers.items():
                    cmd.extend(["-H", f"{key}: {value}"])
            
            if data:
                cmd.extend(["-H", "Content-Type: application/json"])
                cmd.extend(["-d", json.dumps(data)])
            
            # Execute
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            output = stdout.decode()
            
            # Parse response
            lines = output.strip().split('\n')
            http_code = int(lines[-1]) if lines else 0
            response_body = '\n'.join(lines[:-1]) if len(lines) > 1 else ''
            
            # Try to parse JSON
            try:
                response_json = json.loads(response_body) if response_body else {}
            except json.JSONDecodeError:
                response_json = {"raw": response_body}
            
            success = http_code == expected_status
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'status_code': http_code,
                'expected_status': expected_status,
                'success': success,
                'response': response_json,
                'timestamp': datetime.now().isoformat()
            }
            
            self.test_results.append(result)
            
            if success:
                logger.info(f"✅ Backend test passed: {method} {endpoint} → {http_code}")
            else:
                logger.error(f"❌ Backend test failed: {method} {endpoint} → {http_code} (expected {expected_status})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Backend test error: {e}")
            result = {
                'endpoint': endpoint,
                'method': method,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.test_results.append(result)
            return result
    
    async def run_backend_test_suite(self) -> Dict[str, Any]:
        """
        Run comprehensive backend test suite
        """
        logger.info("🧪 Starting backend test suite...")
        
        tests = [
            {
                'name': 'Health Check',
                'method': 'GET',
                'endpoint': '/api/health',
                'expected_status': 200
            },
            {
                'name': 'List AI Providers',
                'method': 'GET',
                'endpoint': '/api/chat/providers',
                'expected_status': 200
            },
            {
                'name': 'List Sessions',
                'method': 'GET',
                'endpoint': '/api/chat/sessions',
                'expected_status': 200
            },
            {
                'name': 'Workspace Tree',
                'method': 'GET',
                'endpoint': '/api/workspace/tree',
                'expected_status': 200
            }
        ]
        
        results = []
        for test in tests:
            result = await self.test_backend_endpoint(
                method=test['method'],
                endpoint=test['endpoint'],
                expected_status=test['expected_status']
            )
            result['test_name'] = test['name']
            results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(0.5)
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('success'))
        failed_tests = total_tests - passed_tests
        
        summary = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🧪 Backend test suite complete: {passed_tests}/{total_tests} passed")
        
        return summary
    
    async def test_frontend_page(
        self, 
        page_url: str, 
        check_elements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Test frontend page using simple curl check
        For full Playwright testing, use dedicated playwright_agent
        """
        try:
            url = f"{self.frontend_url}{page_url}"
            
            # Simple HTTP check
            cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            http_code = int(stdout.decode().strip())
            
            success = http_code == 200
            
            result = {
                'page': page_url,
                'status_code': http_code,
                'success': success,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"✅ Frontend test passed: {page_url} → {http_code}")
            else:
                logger.error(f"❌ Frontend test failed: {page_url} → {http_code}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Frontend test error: {e}")
            return {
                'page': page_url,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_frontend_test_suite(self) -> Dict[str, Any]:
        """
        Run basic frontend test suite
        """
        logger.info("🧪 Starting frontend test suite...")
        
        pages = [
            '/',
            '/chat',
            '/workspace',
            '/files',
            '/settings'
        ]
        
        results = []
        for page in pages:
            result = await self.test_frontend_page(page)
            results.append(result)
            await asyncio.sleep(0.5)
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.get('success'))
        failed_tests = total_tests - passed_tests
        
        summary = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🧪 Frontend test suite complete: {passed_tests}/{total_tests} passed")
        
        return summary
    
    def generate_test_report(self, backend_results: Dict, frontend_results: Dict) -> str:
        """
        Generate human-readable test report
        """
        lines = ["# 🧪 Test Report\n"]
        
        # Backend tests
        lines.append("## Backend Tests")
        lines.append(f"**Status**: {backend_results['passed']}/{backend_results['total_tests']} passed ({backend_results['success_rate']})\n")
        
        for test in backend_results['results']:
            status = "✅" if test.get('success') else "❌"
            lines.append(f"{status} {test.get('test_name', 'Unknown')} - {test.get('method')} {test.get('endpoint')}")
        
        lines.append("")
        
        # Frontend tests
        lines.append("## Frontend Tests")
        lines.append(f"**Status**: {frontend_results['passed']}/{frontend_results['total_tests']} passed ({frontend_results['success_rate']})\n")
        
        for test in frontend_results['results']:
            status = "✅" if test.get('success') else "❌"
            lines.append(f"{status} {test.get('page')} - HTTP {test.get('status_code', 'N/A')}")
        
        lines.append("")
        
        # Overall summary
        total = backend_results['total_tests'] + frontend_results['total_tests']
        passed = backend_results['passed'] + frontend_results['passed']
        
        lines.append("## Overall Summary")
        lines.append(f"**Total Tests**: {total}")
        lines.append(f"**Passed**: {passed}")
        lines.append(f"**Failed**: {total - passed}")
        lines.append(f"**Success Rate**: {(passed/total*100):.1f}%")
        
        return "\n".join(lines)


# Global instance
testing_agent = TestingAgent()
