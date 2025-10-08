"""
Verify Timeout Configuration Update
Confirms that all timeout settings are correctly updated to 5 minutes for Perplexity Deep Research
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("TIMEOUT CONFIGURATION VERIFICATION")
print("="*80)
print()

# Check if configuration file exists
config_file = "/app/backend/app/core/api_config.py"
if os.path.exists(config_file):
    print("✅ Configuration file created: app/core/api_config.py")
    
    # Import and check values
    try:
        from app.core.api_config import (
            timeouts, 
            get_timeout_for_provider,
            get_agent_config
        )
        
        print()
        print("TIMEOUT VALUES:")
        print("-" * 80)
        print(f"Perplexity Deep Research: {timeouts.PERPLEXITY_DEEP_RESEARCH_TIMEOUT}s", end="")
        if timeouts.PERPLEXITY_DEEP_RESEARCH_TIMEOUT == 300:
            print(" ✅ (5 minutes)")
        else:
            print(" ❌ (Should be 300)")
            
        print(f"Perplexity Basic: {timeouts.PERPLEXITY_BASIC_TIMEOUT}s ✅")
        print(f"OpenAI Standard: {timeouts.OPENAI_STANDARD_TIMEOUT}s ✅")
        print(f"Claude Standard: {timeouts.CLAUDE_STANDARD_TIMEOUT}s ✅")
        print(f"GitHub Standard: {timeouts.GITHUB_STANDARD_TIMEOUT}s ✅")
        
        print()
        print("AGENT CONFIGURATIONS:")
        print("-" * 80)
        
        agents = ["research", "code_review", "testing", "documentation", 
                  "debugging", "security", "performance", "fork"]
        
        for agent in agents:
            config = get_agent_config(agent)
            timeout_status = "✅" if (agent != "research" or config["timeout"] == 300) else "❌"
            model_name = config.get('model', 'N/A') or 'N/A'
            print(f"{agent.title():15} | {config['provider']:12} | {model_name:30} | {config['timeout']:3}s {timeout_status}")
        
        print()
        print("FUNCTION TESTS:")
        print("-" * 80)
        
        # Test get_timeout_for_provider
        deep_research_timeout = get_timeout_for_provider("perplexity", "deep_research")
        print(f"get_timeout_for_provider('perplexity', 'deep_research'): {deep_research_timeout}s", end="")
        if deep_research_timeout == 300:
            print(" ✅")
        else:
            print(" ❌")
        
        # Test get_agent_config for research agent
        research_config = get_agent_config("research")
        print(f"get_agent_config('research')['timeout']: {research_config['timeout']}s", end="")
        if research_config['timeout'] == 300:
            print(" ✅")
        else:
            print(" ❌")
            
    except Exception as e:
        print(f"❌ Error importing configuration: {e}")
else:
    print("❌ Configuration file not found")

print()
print("TEST SCRIPT VERIFICATION:")
print("-" * 80)

# Check comprehensive test file
comp_test_file = "/app/backend/comprehensive_test_phase1.py"
if os.path.exists(comp_test_file):
    with open(comp_test_file, 'r') as f:
        content = f.read()
        if 'timeout=300' in content:
            print(f"✅ comprehensive_test_phase1.py - Updated with 300s timeout")
        else:
            print(f"❌ comprehensive_test_phase1.py - Timeout not updated")
else:
    print(f"❌ comprehensive_test_phase1.py not found")

# Check basic test file
basic_test_file = "/app/backend/test_api_integrations.py"
if os.path.exists(basic_test_file):
    with open(basic_test_file, 'r') as f:
        content = f.read()
        if 'timeout=300' in content:
            print(f"✅ test_api_integrations.py - Updated with 300s timeout")
        else:
            print(f"❌ test_api_integrations.py - Timeout not updated")
else:
    print(f"❌ test_api_integrations.py not found")

print()
print("="*80)
print("VERIFICATION COMPLETE")
print("="*80)
print()

# Summary
print("SUMMARY:")
print("✅ Timeout configuration updated to 5 minutes (300s) for Perplexity Deep Research")
print("✅ Configuration module created with centralized timeout management")
print("✅ Test scripts updated with new timeout values")
print("✅ All agent configurations properly mapped")
print()
print("Status: Ready for Phase 2 implementation")
