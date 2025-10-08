#!/usr/bin/env python3
"""
Test-Skript für Anthropic Streaming Fix
========================================

Dieses Skript testet, ob der Anthropic streaming fix funktioniert.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_anthropic_streaming():
    """Test Anthropic streaming with system messages"""
    
    from app.core.ai_manager import AIManager
    
    # Test messages with system message
    test_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Always be concise."
        },
        {
            "role": "user",
            "content": "Say hello in exactly 5 words."
        }
    ]
    
    # Mock API key (you need to replace with real one for actual test)
    api_keys = {
        "anthropic": "sk-ant-test-key"  # Replace with real key
    }
    
    print("=" * 60)
    print("TESTING ANTHROPIC STREAMING WITH SYSTEM MESSAGES")
    print("=" * 60)
    print()
    
    print("📝 Test Messages:")
    for msg in test_messages:
        print(f"  - {msg['role']}: {msg['content']}")
    print()
    
    try:
        ai_manager = AIManager()
        
        print("🚀 Starting streaming test...")
        print("-" * 40)
        
        full_response = ""
        chunk_count = 0
        
        async for chunk in ai_manager.stream_response(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            messages=test_messages,
            ultra_thinking=False,
            api_keys=api_keys
        ):
            chunk_text = chunk.get("content", "")
            full_response += chunk_text
            chunk_count += 1
            print(f"Chunk {chunk_count}: {chunk_text}", end="", flush=True)
        
        print()
        print("-" * 40)
        print(f"✅ Streaming completed successfully!")
        print(f"   Total chunks: {chunk_count}")
        print(f"   Response length: {len(full_response)} chars")
        print()
        print("📄 Full Response:")
        print(full_response)
        
    except Exception as e:
        print(f"❌ Error during streaming: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def verify_fix():
    """Verify that the fix is applied correctly"""
    
    print("\n" + "=" * 60)
    print("VERIFYING FIX IN CODE")
    print("=" * 60)
    print()
    
    ai_manager_path = Path("backend/app/core/ai_manager.py")
    
    if not ai_manager_path.exists():
        print("❌ ai_manager.py not found!")
        return False
    
    content = ai_manager_path.read_text()
    
    # Check if the fix is present
    checks = [
        ("System message extraction", "# Extract system message from messages list (Anthropic requirement)"),
        ("anthropic_messages variable", "anthropic_messages = []"),
        ("System parameter", 'stream_params["system"] = system_message'),
    ]
    
    all_good = True
    for check_name, check_string in checks:
        if check_string in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: NOT FOUND")
            all_good = False
    
    if all_good:
        print("\n🎉 All fixes are correctly applied!")
    else:
        print("\n⚠️ Some fixes are missing. Please apply the fix manually.")
    
    return all_good

def main():
    """Main test function"""
    
    print("🔧 ANTHROPIC STREAMING FIX - TEST SUITE")
    print("=" * 60)
    print()
    
    # First verify the fix is applied
    loop = asyncio.get_event_loop()
    fix_applied = loop.run_until_complete(verify_fix())
    
    if not fix_applied:
        print("\n⚠️ Please apply the fix first!")
        print("Run: python anthropic_streaming_fix.py")
        return
    
    print("\n" + "=" * 60)
    print("IMPORTANT: Replace the test API key with a real one!")
    print("Edit line 37: api_keys = {'anthropic': 'YOUR-REAL-KEY'}")
    print("=" * 60)
    
    # Uncomment to run actual streaming test
    # loop.run_until_complete(test_anthropic_streaming())
    
    print("\n✅ Fix verification complete!")
    print("To run the actual streaming test, uncomment line 134")

if __name__ == "__main__":
    main()
