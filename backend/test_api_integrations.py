"""
Test script to verify all API integrations for Phase 1: Agent System
Tests: Perplexity, OpenAI, Claude, and GitHub API connections
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test results storage
test_results = {
    "perplexity": {"status": "pending", "message": ""},
    "openai": {"status": "pending", "message": ""},
    "claude": {"status": "pending", "message": ""},
    "github": {"status": "pending", "message": ""}
}


async def test_perplexity_api():
    """Test Perplexity API connection"""
    try:
        import requests
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            test_results["perplexity"]["status"] = "failed"
            test_results["perplexity"]["message"] = "API key not found in environment"
            return
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sonar",
            "messages": [
                {"role": "user", "content": "Say 'Hello from Perplexity!' in one sentence."}
            ]
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            test_results["perplexity"]["status"] = "success"
            test_results["perplexity"]["message"] = f"Connected successfully. Response: {message[:50]}..."
        else:
            test_results["perplexity"]["status"] = "failed"
            test_results["perplexity"]["message"] = f"HTTP {response.status_code}: {response.text[:100]}"
            
    except Exception as e:
        test_results["perplexity"]["status"] = "failed"
        test_results["perplexity"]["message"] = f"Error: {str(e)}"


async def test_openai_api():
    """Test OpenAI API connection"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            test_results["openai"]["status"] = "failed"
            test_results["openai"]["message"] = "API key not found in environment"
            return
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello from OpenAI!' in one sentence."}
            ],
            max_tokens=50
        )
        
        message = response.choices[0].message.content
        test_results["openai"]["status"] = "success"
        test_results["openai"]["message"] = f"Connected successfully. Response: {message[:50]}..."
        
    except Exception as e:
        test_results["openai"]["status"] = "failed"
        test_results["openai"]["message"] = f"Error: {str(e)}"


async def test_claude_api():
    """Test Claude API connection"""
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            test_results["claude"]["status"] = "failed"
            test_results["claude"]["message"] = "API key not found in environment"
            return
        
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Hello from Claude!' in one sentence."}
            ]
        )
        
        message = response.content[0].text
        test_results["claude"]["status"] = "success"
        test_results["claude"]["message"] = f"Connected successfully. Response: {message[:50]}..."
        
    except Exception as e:
        test_results["claude"]["status"] = "failed"
        test_results["claude"]["message"] = f"Error: {str(e)}"


async def test_github_api():
    """Test GitHub API connection"""
    try:
        from github import Github
        
        api_key = os.getenv("GITHUB_TOKEN")
        if not api_key:
            test_results["github"]["status"] = "failed"
            test_results["github"]["message"] = "API key not found in environment"
            return
        
        g = Github(api_key)
        user = g.get_user()
        
        test_results["github"]["status"] = "success"
        test_results["github"]["message"] = f"Connected successfully. User: {user.login}"
        
    except Exception as e:
        test_results["github"]["status"] = "failed"
        test_results["github"]["message"] = f"Error: {str(e)}"


async def run_all_tests():
    """Run all API integration tests"""
    print("="*70)
    print("PHASE 1: API INTEGRATION TESTING")
    print("="*70)
    print()
    
    print("Testing Perplexity API...")
    await test_perplexity_api()
    print(f"✓ Perplexity: {test_results['perplexity']['status'].upper()}")
    print(f"  {test_results['perplexity']['message']}")
    print()
    
    print("Testing OpenAI API...")
    await test_openai_api()
    print(f"✓ OpenAI: {test_results['openai']['status'].upper()}")
    print(f"  {test_results['openai']['message']}")
    print()
    
    print("Testing Claude API...")
    await test_claude_api()
    print(f"✓ Claude: {test_results['claude']['status'].upper()}")
    print(f"  {test_results['claude']['message']}")
    print()
    
    print("Testing GitHub API...")
    await test_github_api()
    print(f"✓ GitHub: {test_results['github']['status'].upper()}")
    print(f"  {test_results['github']['message']}")
    print()
    
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results.values() if result["status"] == "success")
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print()
    
    if successful_tests == total_tests:
        print("✅ ALL API INTEGRATIONS WORKING! Ready to proceed to Phase 2.")
    else:
        print("⚠️  Some integrations failed. Please check the errors above.")
    
    print("="*70)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
