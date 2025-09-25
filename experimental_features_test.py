#!/usr/bin/env python3
"""
Test script for the new experimental AI features in XIONIMUS AI
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent / "backend"))

from agents.experimental_agent import ExperimentalAgent
from agents.agent_manager import AgentManager

class ExperimentalFeaturesTest:
    def __init__(self):
        self.agent = ExperimentalAgent()
        self.agent_manager = AgentManager()
        self.results = []

    async def test_ai_code_review(self):
        """Test AI Code Review feature"""
        print("🧪 Testing AI Code Review...")
        
        test_code = """
def calculate_factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
"""
        
        message = f"Please review this code for quality and provide suggestions:\n```python\n{test_code}\n```"
        
        try:
            result = await self.agent.execute_task(message, {"code": test_code})
            self.results.append({
                "feature": "ai_code_review",
                "success": result.get("status") == "completed",
                "result": result
            })
            print(f"   ✅ AI Code Review: {result.get('status', 'unknown')}")
            if "review_results" in result:
                print(f"   📊 Overall Score: {result['review_results'].get('overall_score', 'N/A')}")
        except Exception as e:
            print(f"   ❌ AI Code Review failed: {e}")
            self.results.append({
                "feature": "ai_code_review", 
                "success": False,
                "error": str(e)
            })

    async def test_predictive_coding(self):
        """Test Predictive Coding feature"""
        print("🎯 Testing Predictive Coding...")
        
        context_code = """
class TaskManager:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, task):
        self.tasks.append(task)
"""
        
        message = f"Based on this TaskManager class, predict what methods I should implement next:\n```python\n{context_code}\n```"
        
        try:
            result = await self.agent.execute_task(message, {"code": context_code})
            self.results.append({
                "feature": "predictive_coding",
                "success": result.get("status") == "completed",
                "result": result
            })
            print(f"   ✅ Predictive Coding: {result.get('status', 'unknown')}")
            if "predictions" in result:
                print(f"   🔮 Predictions generated: {len(result['predictions'].get('next_functions', []))}")
        except Exception as e:
            print(f"   ❌ Predictive Coding failed: {e}")
            self.results.append({
                "feature": "predictive_coding",
                "success": False, 
                "error": str(e)
            })

    async def test_auto_refactoring(self):
        """Test Auto-Refactoring feature"""
        print("🔄 Testing Auto-Refactoring...")
        
        messy_code = """
def process_data(data):
    result = []
    for item in data:
        if item != None:
            if item > 0:
                if item % 2 == 0:
                    result.append(item * 2)
                else:
                    result.append(item * 3)
    return result
"""
        
        message = f"Refactor this code to make it cleaner and more efficient:\n```python\n{messy_code}\n```"
        
        try:
            result = await self.agent.execute_task(message, {"code": messy_code})
            self.results.append({
                "feature": "auto_refactoring",
                "success": result.get("status") == "completed",
                "result": result
            })
            print(f"   ✅ Auto-Refactoring: {result.get('status', 'unknown')}")
            if "improvements" in result:
                print(f"   🔧 Improvements identified: {len(result.get('improvements', []))}")
        except Exception as e:
            print(f"   ❌ Auto-Refactoring failed: {e}")
            self.results.append({
                "feature": "auto_refactoring",
                "success": False,
                "error": str(e)
            })

    async def test_performance_profiling(self):
        """Test Performance Profiling feature"""
        print("📈 Testing Performance Profiling...")
        
        code_to_profile = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        message = f"Analyze the performance of this code and suggest optimizations:\n```python\n{code_to_profile}\n```"
        
        try:
            result = await self.agent.execute_task(message, {"code": code_to_profile})
            self.results.append({
                "feature": "performance_profiling",
                "success": result.get("status") == "completed",
                "result": result
            })
            print(f"   ✅ Performance Profiling: {result.get('status', 'unknown')}")
            if "complexity_analysis" in result:
                print(f"   ⏱️  Complexity Analysis: {result['complexity_analysis'].get('time', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Performance Profiling failed: {e}")
            self.results.append({
                "feature": "performance_profiling",
                "success": False,
                "error": str(e)
            })

    async def test_smart_suggestions(self):
        """Test Smart Suggestions feature"""
        print("🌟 Testing Smart Suggestions...")
        
        message = "I'm building a REST API with Python Flask. What are some smart suggestions to improve my development workflow?"
        context = {
            "project_type": "web_api",
            "framework": "flask",
            "language": "python"
        }
        
        try:
            result = await self.agent.execute_task(message, context)
            self.results.append({
                "feature": "smart_suggestions",
                "success": result.get("status") == "completed",
                "result": result
            })
            print(f"   ✅ Smart Suggestions: {result.get('status', 'unknown')}")
            if "immediate_suggestions" in result:
                print(f"   💡 Immediate suggestions: {len(result.get('immediate_suggestions', []))}")
        except Exception as e:
            print(f"   ❌ Smart Suggestions failed: {e}")
            self.results.append({
                "feature": "smart_suggestions",
                "success": False,
                "error": str(e)
            })

    async def test_agent_selection(self):
        """Test that the agent manager correctly selects the experimental agent"""
        print("🤖 Testing Agent Selection for Experimental Features...")
        
        test_messages = [
            "Review this code for quality issues",
            "Predict what I should code next",
            "Refactor this function to be more efficient", 
            "Profile the performance of this algorithm",
            "Give me smart suggestions for my project"
        ]
        
        correct_selections = 0
        total_tests = len(test_messages)
        
        for message in test_messages:
            try:
                result = await self.agent_manager.process_request(message, {})
                
                if result.get("requires_agent") and result.get("agent_used") == "Experimental Agent":
                    correct_selections += 1
                    print(f"   ✅ '{message[:30]}...' → Experimental Agent")
                else:
                    print(f"   ⚠️  '{message[:30]}...' → {result.get('agent_used', 'No Agent')}")
                    
            except Exception as e:
                print(f"   ❌ Agent selection failed for '{message[:30]}...': {e}")
        
        selection_rate = (correct_selections / total_tests) * 100
        print(f"   📊 Agent Selection Rate: {selection_rate:.1f}% ({correct_selections}/{total_tests})")
        
        self.results.append({
            "feature": "agent_selection",
            "success": selection_rate >= 60,  # Accept 60%+ selection rate
            "selection_rate": selection_rate,
            "correct_selections": correct_selections,
            "total_tests": total_tests
        })

    async def run_all_tests(self):
        """Run all experimental feature tests"""
        print("🚀 STARTING EXPERIMENTAL FEATURES TEST")
        print("=" * 60)
        
        # Check API key
        if not os.environ.get('ANTHROPIC_API_KEY'):
            print("⚠️  Warning: ANTHROPIC_API_KEY not set. Some features may not work.")
        
        # Run individual feature tests
        await self.test_ai_code_review()
        print()
        await self.test_predictive_coding()
        print()
        await self.test_auto_refactoring()
        print()
        await self.test_performance_profiling()
        print()
        await self.test_smart_suggestions()
        print()
        await self.test_agent_selection()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 EXPERIMENTAL FEATURES TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = [r for r in self.results if r.get("success", False)]
        total_tests = len(self.results)
        success_rate = (len(successful_tests) / total_tests * 100) if total_tests > 0 else 0
        
        for result in self.results:
            feature = result.get("feature", "unknown").replace("_", " ").title()
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"   {status} {feature}")
            
            if not result.get("success", False) and "error" in result:
                print(f"      Error: {result['error']}")
        
        print(f"\n🏆 OVERALL SUCCESS RATE: {success_rate:.1f}% ({len(successful_tests)}/{total_tests})")
        
        if success_rate >= 80:
            print("🌟 Excellent! All experimental features are working well!")
        elif success_rate >= 60:
            print("✅ Good! Most experimental features are functional.")
        elif success_rate >= 40:
            print("⚠️  Partial success. Some features need attention.")
        else:
            print("❌ Many features need fixing. Check API configuration and implementation.")
        
        # Save results
        try:
            with open("experimental_features_test_results.json", "w") as f:
                json.dump({
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "success_rate": success_rate,
                    "successful_tests": len(successful_tests),
                    "total_tests": total_tests,
                    "results": self.results
                }, f, indent=2)
            print(f"\n📄 Results saved to: experimental_features_test_results.json")
        except Exception as e:
            print(f"⚠️  Could not save results: {e}")
        
        return success_rate >= 60

async def main():
    """Main test function"""
    test_runner = ExperimentalFeaturesTest()
    success = await test_runner.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)