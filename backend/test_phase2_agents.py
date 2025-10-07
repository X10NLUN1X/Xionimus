"""
Test Phase 2: Agent System
Quick test to verify all agents are properly initialized and working
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.models.agent_models import AgentType, AgentExecutionRequest
from app.core.agent_orchestrator import AgentOrchestrator


async def test_agent_initialization():
    """Test that all agents can be initialized"""
    print("="*80)
    print("PHASE 2: AGENT SYSTEM INITIALIZATION TEST")
    print("="*80)
    print()
    
    try:
        orchestrator = AgentOrchestrator()
        print(f"✅ Agent Orchestrator initialized with {len(orchestrator.agents)} agents")
        print()
        
        print("Initialized Agents:")
        print("-" * 80)
        for agent_type, agent in orchestrator.agents.items():
            print(f"  {agent_type.value:15} | {agent.provider.value:12} | {agent.model or 'N/A':30}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agents: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_health():
    """Test health check for all agents"""
    print("="*80)
    print("AGENT HEALTH CHECK")
    print("="*80)
    print()
    
    try:
        orchestrator = AgentOrchestrator()
        health_status = await orchestrator.get_agent_health()
        
        print(f"Overall Health: {'✅ HEALTHY' if health_status['overall_healthy'] else '❌ UNHEALTHY'}")
        print(f"Healthy Agents: {health_status['healthy_agents']}/{health_status['total_agents']}")
        print()
        
        print("Individual Agent Status:")
        print("-" * 80)
        for agent_name, status in health_status['agents'].items():
            is_healthy = status.get('is_healthy', False)
            status_icon = "✅" if is_healthy else "❌"
            response_time = status.get('response_time_ms', 0)
            
            print(f"{status_icon} {agent_name:15} | ", end="")
            if is_healthy:
                print(f"Response: {response_time:.0f}ms")
            else:
                print(f"Error: {status.get('error', 'Unknown error')[:60]}")
        print()
        
        return health_status['overall_healthy']
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_simple_agent_execution():
    """Test simple execution of each agent type"""
    print("="*80)
    print("SIMPLE AGENT EXECUTION TEST")
    print("="*80)
    print()
    
    orchestrator = AgentOrchestrator()
    
    # Define simple test cases for each agent
    test_cases = [
        {
            "agent_type": AgentType.RESEARCH,
            "input_data": {
                "query": "What is FastAPI?",
                "deep_research": False
            },
            "description": "Quick research query"
        },
        {
            "agent_type": AgentType.CODE_REVIEW,
            "input_data": {
                "code": "def hello():\n    print('world')",
                "language": "python"
            },
            "description": "Simple code review"
        },
        {
            "agent_type": AgentType.DEBUGGING,
            "input_data": {
                "error": "NameError: name 'x' is not defined",
                "code": "print(x)"
            },
            "description": "Debug simple error"
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        agent_type = test_case["agent_type"]
        print(f"Testing {agent_type.value} agent: {test_case['description']}")
        print("-" * 80)
        
        try:
            request = AgentExecutionRequest(
                agent_type=agent_type,
                input_data=test_case["input_data"]
            )
            
            result = await orchestrator.execute_agent(request)
            
            if result.status.value == "completed":
                print(f"✅ {agent_type.value} execution completed")
                print(f"   Duration: {result.duration_seconds:.2f}s")
                print(f"   Tokens: {result.token_usage.get('total_tokens', 0) if result.token_usage else 0}")
                results[agent_type.value] = "PASSED"
            else:
                print(f"❌ {agent_type.value} execution failed: {result.error_message}")
                results[agent_type.value] = "FAILED"
                
        except Exception as e:
            print(f"❌ {agent_type.value} test error: {str(e)}")
            results[agent_type.value] = "ERROR"
        
        print()
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(1 for status in results.values() if status == "PASSED")
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print()
    
    for agent, status in results.items():
        status_icon = "✅" if status == "PASSED" else "❌"
        print(f"{status_icon} {agent}: {status}")
    
    print()
    return passed == total


async def main():
    """Run all tests"""
    print()
    
    # Test 1: Initialization
    init_success = await test_agent_initialization()
    if not init_success:
        print("⚠️  Initialization failed, skipping further tests")
        return
    
    print()
    
    # Test 2: Health Check
    health_success = await test_agent_health()
    if not health_success:
        print("⚠️  Some agents are unhealthy")
    
    print()
    
    # Test 3: Simple Execution (only if agents are healthy)
    if health_success:
        print("🚀 Running execution tests (this will take ~30-60 seconds)...")
        print()
        execution_success = await test_simple_agent_execution()
        
        if execution_success:
            print("🎉 ALL TESTS PASSED!")
        else:
            print("⚠️  Some execution tests failed")
    else:
        print("⚠️  Skipping execution tests due to unhealthy agents")
    
    print()
    print("="*80)
    print("PHASE 2 AGENT SYSTEM TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
