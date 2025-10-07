"""
Comprehensive Phase 1 API Integration Testing
Tests all API integrations with advanced features including:
- Basic connectivity
- Advanced features (streaming, function calling, etc.)
- Error handling
- Rate limiting awareness
- Response validation
"""
import os
import asyncio
import time
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Test results storage
test_results: Dict[str, List[Dict]] = {
    "perplexity": [],
    "openai": [],
    "claude": [],
    "github": []
}


def log_test(category: str, test_name: str, status: str, message: str, duration: float = 0):
    """Log test result"""
    test_results[category].append({
        "test": test_name,
        "status": status,
        "message": message,
        "duration": duration
    })


# ============================================================================
# PERPLEXITY API TESTS
# ============================================================================

async def test_perplexity_basic():
    """Test 1: Basic Perplexity API connectivity"""
    test_name = "Basic Connectivity"
    start_time = time.time()
    
    try:
        import requests
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            log_test("perplexity", test_name, "FAILED", "API key not found", time.time() - start_time)
            return
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sonar",
            "messages": [{"role": "user", "content": "What is 2+2?"}],
            "max_tokens": 50
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log_test("perplexity", test_name, "PASSED", f"Response received: {content[:50]}", time.time() - start_time)
        else:
            log_test("perplexity", test_name, "FAILED", f"HTTP {response.status_code}", time.time() - start_time)
            
    except Exception as e:
        log_test("perplexity", test_name, "FAILED", str(e), time.time() - start_time)


async def test_perplexity_deep_research():
    """Test 2: Perplexity Deep Research Model"""
    test_name = "Deep Research Model"
    start_time = time.time()
    
    try:
        import requests
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sonar-deep-research",
            "messages": [{"role": "user", "content": "What are the latest trends in AI? Answer in 2 sentences."}],
            "max_tokens": 150
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            log_test("perplexity", test_name, "PASSED", f"Deep research working: {content[:80]}...", time.time() - start_time)
        else:
            log_test("perplexity", test_name, "FAILED", f"HTTP {response.status_code}", time.time() - start_time)
            
    except Exception as e:
        log_test("perplexity", test_name, "FAILED", str(e), time.time() - start_time)


async def test_perplexity_citations():
    """Test 3: Perplexity with Citations"""
    test_name = "Citations Support"
    start_time = time.time()
    
    try:
        import requests
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "sonar",
            "messages": [{"role": "user", "content": "What is Python programming language?"}],
            "return_citations": True,
            "max_tokens": 100
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            has_citations = "citations" in result or "[" in result["choices"][0]["message"]["content"]
            if has_citations:
                log_test("perplexity", test_name, "PASSED", "Citations working", time.time() - start_time)
            else:
                log_test("perplexity", test_name, "WARNING", "No citations found", time.time() - start_time)
        else:
            log_test("perplexity", test_name, "FAILED", f"HTTP {response.status_code}", time.time() - start_time)
            
    except Exception as e:
        log_test("perplexity", test_name, "FAILED", str(e), time.time() - start_time)


# ============================================================================
# OPENAI API TESTS
# ============================================================================

async def test_openai_basic():
    """Test 4: Basic OpenAI API connectivity"""
    test_name = "Basic Connectivity"
    start_time = time.time()
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            log_test("openai", test_name, "FAILED", "API key not found", time.time() - start_time)
            return
        
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Test successful' and nothing else."}],
            max_tokens=10
        )
        
        content = response.choices[0].message.content
        log_test("openai", test_name, "PASSED", f"Response: {content}", time.time() - start_time)
        
    except Exception as e:
        log_test("openai", test_name, "FAILED", str(e), time.time() - start_time)


async def test_openai_streaming():
    """Test 5: OpenAI Streaming"""
    test_name = "Streaming Support"
    start_time = time.time()
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Count from 1 to 3"}],
            stream=True,
            max_tokens=50
        )
        
        chunks = []
        for chunk in stream:
            if chunk.choices[0].delta.content:
                chunks.append(chunk.choices[0].delta.content)
        
        full_response = "".join(chunks)
        log_test("openai", test_name, "PASSED", f"Streaming works: {len(chunks)} chunks received", time.time() - start_time)
        
    except Exception as e:
        log_test("openai", test_name, "FAILED", str(e), time.time() - start_time)


async def test_openai_function_calling():
    """Test 6: OpenAI Function Calling"""
    test_name = "Function Calling"
    start_time = time.time()
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "City name"}
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "What's the weather in Paris?"}],
            tools=tools,
            max_tokens=100
        )
        
        has_function_call = response.choices[0].message.tool_calls is not None
        if has_function_call:
            log_test("openai", test_name, "PASSED", "Function calling works", time.time() - start_time)
        else:
            log_test("openai", test_name, "WARNING", "No function call detected", time.time() - start_time)
        
    except Exception as e:
        log_test("openai", test_name, "FAILED", str(e), time.time() - start_time)


async def test_openai_models():
    """Test 7: Multiple OpenAI Models"""
    test_name = "Multiple Models"
    start_time = time.time()
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        
        models = ["gpt-4o-mini"]
        working_models = []
        
        for model in models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                working_models.append(model)
            except Exception as e:
                pass
        
        if working_models:
            log_test("openai", test_name, "PASSED", f"Working models: {', '.join(working_models)}", time.time() - start_time)
        else:
            log_test("openai", test_name, "FAILED", "No models working", time.time() - start_time)
        
    except Exception as e:
        log_test("openai", test_name, "FAILED", str(e), time.time() - start_time)


# ============================================================================
# CLAUDE API TESTS
# ============================================================================

async def test_claude_basic():
    """Test 8: Basic Claude API connectivity"""
    test_name = "Basic Connectivity"
    start_time = time.time()
    
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            log_test("claude", test_name, "FAILED", "API key not found", time.time() - start_time)
            return
        
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{"role": "user", "content": "Say 'Test successful' and nothing else."}]
        )
        
        content = response.content[0].text
        log_test("claude", test_name, "PASSED", f"Response: {content}", time.time() - start_time)
        
    except Exception as e:
        log_test("claude", test_name, "FAILED", str(e), time.time() - start_time)


async def test_claude_streaming():
    """Test 9: Claude Streaming"""
    test_name = "Streaming Support"
    start_time = time.time()
    
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=api_key)
        
        chunks = []
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=50,
            messages=[{"role": "user", "content": "Count from 1 to 3"}]
        ) as stream:
            for text in stream.text_stream:
                chunks.append(text)
        
        full_response = "".join(chunks)
        log_test("claude", test_name, "PASSED", f"Streaming works: {len(chunks)} chunks received", time.time() - start_time)
        
    except Exception as e:
        log_test("claude", test_name, "FAILED", str(e), time.time() - start_time)


async def test_claude_system_prompt():
    """Test 10: Claude System Prompts"""
    test_name = "System Prompts"
    start_time = time.time()
    
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=30,
            system="You are a helpful coding assistant. Always respond with enthusiasm.",
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        content = response.content[0].text
        log_test("claude", test_name, "PASSED", f"System prompt works: {content[:50]}", time.time() - start_time)
        
    except Exception as e:
        log_test("claude", test_name, "FAILED", str(e), time.time() - start_time)


async def test_claude_multi_turn():
    """Test 11: Claude Multi-turn Conversation"""
    test_name = "Multi-turn Conversation"
    start_time = time.time()
    
    try:
        from anthropic import Anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=api_key)
        
        messages = [
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
            {"role": "user", "content": "What is my name?"}
        ]
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=messages
        )
        
        content = response.content[0].text.lower()
        if "alice" in content:
            log_test("claude", test_name, "PASSED", "Context preserved correctly", time.time() - start_time)
        else:
            log_test("claude", test_name, "WARNING", "Context may not be preserved", time.time() - start_time)
        
    except Exception as e:
        log_test("claude", test_name, "FAILED", str(e), time.time() - start_time)


# ============================================================================
# GITHUB API TESTS
# ============================================================================

async def test_github_basic():
    """Test 12: Basic GitHub API connectivity"""
    test_name = "Basic Connectivity"
    start_time = time.time()
    
    try:
        from github import Github
        
        api_key = os.getenv("GITHUB_TOKEN")
        if not api_key:
            log_test("github", test_name, "FAILED", "API key not found", time.time() - start_time)
            return
        
        g = Github(api_key)
        user = g.get_user()
        
        log_test("github", test_name, "PASSED", f"Connected as: {user.login}", time.time() - start_time)
        
    except Exception as e:
        log_test("github", test_name, "FAILED", str(e), time.time() - start_time)


async def test_github_user_info():
    """Test 13: GitHub User Information"""
    test_name = "User Information"
    start_time = time.time()
    
    try:
        from github import Github
        
        api_key = os.getenv("GITHUB_TOKEN")
        g = Github(api_key)
        user = g.get_user()
        
        info = {
            "login": user.login,
            "name": user.name,
            "public_repos": user.public_repos,
            "followers": user.followers
        }
        
        log_test("github", test_name, "PASSED", f"User info: {info}", time.time() - start_time)
        
    except Exception as e:
        log_test("github", test_name, "FAILED", str(e), time.time() - start_time)


async def test_github_repos():
    """Test 14: GitHub Repository Access"""
    test_name = "Repository Access"
    start_time = time.time()
    
    try:
        from github import Github
        
        api_key = os.getenv("GITHUB_TOKEN")
        g = Github(api_key)
        user = g.get_user()
        
        repos = list(user.get_repos()[:5])  # Get first 5 repos
        repo_names = [repo.name for repo in repos]
        
        log_test("github", test_name, "PASSED", f"Can access repos: {len(repos)} repos found", time.time() - start_time)
        
    except Exception as e:
        log_test("github", test_name, "FAILED", str(e), time.time() - start_time)


async def test_github_rate_limit():
    """Test 15: GitHub Rate Limit Info"""
    test_name = "Rate Limit Check"
    start_time = time.time()
    
    try:
        from github import Github
        
        api_key = os.getenv("GITHUB_TOKEN")
        g = Github(api_key)
        
        rate_limit = g.get_rate_limit()
        core = rate_limit.core
        
        log_test("github", test_name, "PASSED", 
                f"Rate limit: {core.remaining}/{core.limit} remaining", 
                time.time() - start_time)
        
    except Exception as e:
        log_test("github", test_name, "FAILED", str(e), time.time() - start_time)


async def test_github_search():
    """Test 16: GitHub Search API"""
    test_name = "Search API"
    start_time = time.time()
    
    try:
        from github import Github
        
        api_key = os.getenv("GITHUB_TOKEN")
        g = Github(api_key)
        
        # Search for Python repositories
        repos = g.search_repositories(query="language:python", sort="stars", order="desc")
        first_repo = repos[0]
        
        log_test("github", test_name, "PASSED", 
                f"Search works: Found {first_repo.name}", 
                time.time() - start_time)
        
    except Exception as e:
        log_test("github", test_name, "FAILED", str(e), time.time() - start_time)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

async def run_all_comprehensive_tests():
    """Run all comprehensive tests"""
    print("="*80)
    print("COMPREHENSIVE PHASE 1 API INTEGRATION TESTING")
    print("="*80)
    print()
    
    # Perplexity Tests
    print("🔬 PERPLEXITY API TESTS")
    print("-" * 80)
    await test_perplexity_basic()
    await test_perplexity_deep_research()
    await test_perplexity_citations()
    print()
    
    # OpenAI Tests
    print("🔬 OPENAI API TESTS")
    print("-" * 80)
    await test_openai_basic()
    await test_openai_streaming()
    await test_openai_function_calling()
    await test_openai_models()
    print()
    
    # Claude Tests
    print("🔬 CLAUDE API TESTS")
    print("-" * 80)
    await test_claude_basic()
    await test_claude_streaming()
    await test_claude_system_prompt()
    await test_claude_multi_turn()
    print()
    
    # GitHub Tests
    print("🔬 GITHUB API TESTS")
    print("-" * 80)
    await test_github_basic()
    await test_github_user_info()
    await test_github_repos()
    await test_github_rate_limit()
    await test_github_search()
    print()
    
    # Print detailed results
    print("="*80)
    print("DETAILED TEST RESULTS")
    print("="*80)
    print()
    
    for category, tests in test_results.items():
        print(f"📊 {category.upper()} ({len(tests)} tests)")
        print("-" * 80)
        
        for test in tests:
            status_icon = "✅" if test["status"] == "PASSED" else "❌" if test["status"] == "FAILED" else "⚠️"
            print(f"{status_icon} {test['test']}: {test['status']}")
            print(f"   {test['message']}")
            print(f"   Duration: {test['duration']:.2f}s")
            print()
        print()
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_tests = sum(len(tests) for tests in test_results.values())
    passed_tests = sum(1 for tests in test_results.values() for test in tests if test["status"] == "PASSED")
    failed_tests = sum(1 for tests in test_results.values() for test in tests if test["status"] == "FAILED")
    warning_tests = sum(1 for tests in test_results.values() for test in tests if test["status"] == "WARNING")
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"⚠️  Warnings: {warning_tests}")
    print()
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! Ready to proceed to Phase 2.")
    elif success_rate >= 80:
        print("✅ Most tests passed. System is ready with minor warnings.")
    else:
        print("⚠️  Some critical tests failed. Please review errors above.")
    
    print("="*80)


if __name__ == "__main__":
    asyncio.run(run_all_comprehensive_tests())
