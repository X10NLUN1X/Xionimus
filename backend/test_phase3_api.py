"""
Test Phase 3: API Endpoints
Test the multi-agent API endpoints
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001"

def test_agent_types():
    """Test getting agent types (no auth required for this one hopefully)"""
    print("="*80)
    print("TESTING: GET /api/multi-agents/types")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/multi-agents/types")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data['total_agents']} agents")
            print()
            print("Available Agents:")
            print("-" * 80)
            for agent in data['agents']:
                print(f"  {agent['type']:15} | {agent['provider']:12} | {agent['model'] or 'N/A'}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_agent_health():
    """Test agent health check"""
    print()
    print("="*80)
    print("TESTING: GET /api/multi-agents/health")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/multi-agents/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Overall Health: {'HEALTHY' if data['overall_healthy'] else 'UNHEALTHY'}")
            print(f"Healthy Agents: {data['healthy_agents']}/{data['total_agents']}")
            return True
        else:
            print(f"⚠️  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_simple_research():
    """Test simple research agent execution"""
    print()
    print("="*80)
    print("TESTING: POST /api/multi-agents/execute (Research Agent)")
    print("="*80)
    
    payload = {
        "agent_type": "research",
        "input_data": {
            "query": "What is Python?",
            "deep_research": False
        },
        "options": {
            "max_tokens": 500
        }
    }
    
    try:
        print("Sending request...")
        response = requests.post(
            f"{BASE_URL}/api/multi-agents/execute",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Research completed!")
            print(f"   Execution ID: {data['execution_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Duration: {data['duration_seconds']:.2f}s")
            print(f"   Model: {data['model']}")
            
            if data.get('output_data'):
                output = data['output_data']
                print(f"   Content length: {len(output.get('content', ''))} chars")
                print(f"   Citations: {output.get('sources_count', 0)}")
            
            return True
        else:
            print(f"⚠️  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print()
    print("🚀 PHASE 3: API ENDPOINT TESTING")
    print()
    
    results = []
    
    # Test 1: Agent Types
    results.append(("Agent Types", test_agent_types()))
    
    # Test 2: Health Check  
    results.append(("Health Check", test_agent_health()))
    
    # Test 3: Research Execution (may require auth)
    results.append(("Research Execution", test_simple_research()))
    
    # Summary
    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {test_name}")
    
    print()
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print()
        print("🎉 ALL API TESTS PASSED!")
    elif passed > 0:
        print()
        print("⚠️  Some tests passed, some failed (may be due to authentication)")
    else:
        print()
        print("❌ All tests failed")


if __name__ == "__main__":
    main()
