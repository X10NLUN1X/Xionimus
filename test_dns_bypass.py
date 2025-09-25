#!/usr/bin/env python3
"""
DNS Bypass Test Script for Xionimus AI
Tests various DNS bypass methods and validates API connections
"""

import asyncio
import logging
import sys
from backend.dns_bypass import get_bypass_manager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_dns_bypass():
    """Test DNS bypass functionality"""
    print("🔄 XIONIMUS AI - DNS BYPASS TEST")
    print("=" * 50)
    
    try:
        # Test API keys (using the provided ones)
        api_keys = {
            'anthropic': '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',
            'openai': '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',
            'perplexity': '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'
        }
        
        bypass_manager = await get_bypass_manager()
        
        # Test 1: DNS Resolution
        print("\n🔍 Testing DNS resolution...")
        test_hosts = ['api.anthropic.com', 'api.openai.com', 'api.perplexity.ai']
        
        for host in test_hosts:
            ip = bypass_manager.resolve_ip_manually(host)
            if ip:
                print(f"✅ {host} -> {ip}")
            else:
                print(f"❌ {host} -> Failed to resolve")
        
        # Test 2: Bypassed client creation
        print("\n🚀 Testing bypassed client creation...")
        
        # Test Anthropic
        try:
            anthropic_client = await bypass_manager.create_bypassed_anthropic_client(api_keys['anthropic'])
            if anthropic_client:
                print("✅ Anthropic bypass client created successfully")
                
                # Test a simple request
                try:
                    response = await anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=50,
                        messages=[{"role": "user", "content": "Hello, test message"}]
                    )
                    print("🎉 Anthropic API call successful via bypass!")
                    print(f"Response: {response.content[0].text[:100]}...")
                except Exception as e:
                    print(f"⚠️ Anthropic API call failed: {e}")
            else:
                print("❌ Failed to create Anthropic bypass client")
        except Exception as e:
            print(f"❌ Anthropic bypass error: {e}")
        
        # Test OpenAI  
        try:
            openai_client = await bypass_manager.create_bypassed_openai_client(api_keys['openai'])
            if openai_client:
                print("✅ OpenAI bypass client created successfully")
                
                # Test a simple request
                try:
                    response = await openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello, test message"}],
                        max_tokens=50
                    )
                    print("🎉 OpenAI API call successful via bypass!")
                    print(f"Response: {response.choices[0].message.content[:100]}...")
                except Exception as e:
                    print(f"⚠️ OpenAI API call failed: {e}")
            else:
                print("❌ Failed to create OpenAI bypass client")
        except Exception as e:
            print(f"❌ OpenAI bypass error: {e}")
            
        # Test Perplexity
        try:
            perplexity_client = await bypass_manager.create_bypassed_perplexity_client(api_keys['perplexity'])
            if perplexity_client:
                print("✅ Perplexity bypass client created successfully")
                
                # Test a simple request
                try:
                    response = await perplexity_client.chat.completions.create(
                        model="llama-3.1-sonar-small-128k-online",
                        messages=[{"role": "user", "content": "Hello, test message"}],
                        max_tokens=50
                    )
                    print("🎉 Perplexity API call successful via bypass!")
                    print(f"Response: {response.choices[0].message.content[:100]}...")
                except Exception as e:
                    print(f"⚠️ Perplexity API call failed: {e}")
            else:
                print("❌ Failed to create Perplexity bypass client")
        except Exception as e:
            print(f"❌ Perplexity bypass error: {e}")
        
        print("\n" + "=" * 50)
        print("✅ DNS Bypass Test Complete")
        
    except Exception as e:
        print(f"❌ DNS bypass test failed: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    success = await test_dns_bypass()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)