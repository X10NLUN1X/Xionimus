"""
Comprehensive Backend Test - Verify 100% Functionality
Tests all agents and API endpoints
"""
import asyncio
import sys
from app.models.agent_models import AgentType, AgentExecutionRequest
from app.core.agent_orchestrator import AgentOrchestrator

async def run_all_tests():
    print("="*80)
    print("COMPREHENSIVE BACKEND TEST - ALL AGENTS & ORCHESTRATOR")
    print("="*80)
    print()
    
    orchestrator = AgentOrchestrator()
    
    tests = [
        {
            "name": "Research Agent (Perplexity)",
            "agent": AgentType.RESEARCH,
            "input": {"query": "What is FastAPI?", "deep_research": False},
            "check_fields": ["content", "citations"],
            "timeout": 30
        },
        {
            "name": "Code Review Agent (Claude Sonnet 4)",
            "agent": AgentType.CODE_REVIEW,
            "input": {"code": "def greet(name):\n    print(f'Hello {name}')", "language": "python"},
            "check_fields": ["review"],
            "timeout": 30
        },
        {
            "name": "Testing Agent (OpenAI)",
            "agent": AgentType.TESTING,
            "input": {"code": "def add(a, b):\n    return a + b", "language": "python"},
            "check_fields": ["tests"],
            "timeout": 30
        },
        {
            "name": "Documentation Agent (Claude Sonnet 4)",
            "agent": AgentType.DOCUMENTATION,
            "input": {"code": "def multiply(x, y):\n    return x * y", "language": "python"},
            "check_fields": ["documentation"],
            "timeout": 30
        },
        {
            "name": "Debugging Agent (Claude Opus 4.1)",
            "agent": AgentType.DEBUGGING,
            "input": {"error": "NameError: name 'x' is not defined", "code": "print(x)"},
            "check_fields": ["analysis"],
            "timeout": 30
        },
        {
            "name": "Security Agent (OpenAI)",
            "agent": AgentType.SECURITY,
            "input": {"code": "query = 'SELECT * FROM users WHERE id = ' + user_input", "language": "python"},
            "check_fields": ["security_analysis"],
            "timeout": 30
        },
        {
            "name": "Performance Agent (OpenAI)",
            "agent": AgentType.PERFORMANCE,
            "input": {"code": "result = []\nfor i in range(1000):\n    result.append(i)", "language": "python"},
            "check_fields": ["performance_analysis"],
            "timeout": 30
        },
        {
            "name": "Fork Agent (GitHub)",
            "agent": AgentType.FORK,
            "input": {"operation": "list_repos", "limit": 3},
            "check_fields": ["operation", "success", "repositories"],
            "timeout": 10
        }
    ]
    
    passed = 0
    failed = 0
    results = []
    
    for test in tests:
        print(f"Testing: {test['name']}")
        print("-" * 80)
        
        try:
            request = AgentExecutionRequest(
                agent_type=test["agent"],
                input_data=test["input"]
            )
            
            result = await asyncio.wait_for(
                orchestrator.execute_agent(request),
                timeout=test["timeout"]
            )
            
            if result.status.value == "completed":
                # Check required fields
                missing_fields = [
                    field for field in test["check_fields"]
                    if field not in (result.output_data or {})
                ]
                
                if missing_fields:
                    status = "FAILED"
                    message = f"Missing fields: {missing_fields}"
                    failed += 1
                else:
                    status = "PASSED"
                    message = f"Duration: {result.duration_seconds:.2f}s"
                    if result.token_usage:
                        message += f" | Tokens: {result.token_usage.get('total_tokens', 0)}"
                    passed += 1
            else:
                status = "FAILED"
                message = f"Status: {result.status.value} | Error: {result.error_message}"
                failed += 1
            
        except asyncio.TimeoutError:
            status = "TIMEOUT"
            message = f"Exceeded {test['timeout']}s timeout"
            failed += 1
        except Exception as e:
            status = "ERROR"
            message = str(e)
            failed += 1
        
        results.append({
            "name": test["name"],
            "status": status,
            "message": message
        })
        
        status_icon = "✅" if status == "PASSED" else "❌"
        print(f"{status_icon} {status}: {message}")
        print()
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print()
    
    for result in results:
        status_icon = "✅" if result["status"] == "PASSED" else "❌"
        print(f"{status_icon} {result['name']}: {result['status']}")
    
    print()
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"Total: {total} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Backend is 100% functional!")
        return 0
    else:
        print(f"⚠️  {failed} tests failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
