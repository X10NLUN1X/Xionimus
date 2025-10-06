#!/usr/bin/env python3
"""
Focused Phase 2 Test - Test default configuration and basic Claude functionality
"""

import requests
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_default_configuration():
    """Test if Claude is the default provider"""
    
    # Authenticate first
    session = requests.Session()
    login_data = {"username": "demo", "password": "demo123"}
    
    auth_response = session.post(
        "http://localhost:8001/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if auth_response.status_code != 200:
        logger.error(f"Authentication failed: {auth_response.status_code}")
        return False
    
    token = auth_response.json().get("access_token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test default configuration with a non-coding question
    chat_data = {
        "messages": [{"role": "user", "content": "Tell me about the weather today."}]
        # No provider or model specified - should use defaults
    }
    
    response = session.post(
        "http://localhost:8001/api/chat/",
        json=chat_data,
        headers=headers,
        timeout=30
    )
    
    logger.info(f"Response status: {response.status_code}")
    logger.info(f"Response text: {response.text[:500]}...")
    
    if response.status_code == 200:
        try:
            result = response.json()
            provider = result.get("provider")
            model = result.get("model")
            
            logger.info(f"Provider: {provider}")
            logger.info(f"Model: {model}")
            logger.info(f"Content length: {len(result.get('content', ''))}")
            logger.info(f"Full response keys: {list(result.keys())}")
            
            # Check if it's using Claude defaults
            if provider == "anthropic" and "claude-sonnet-4-5" in model:
                logger.info("✅ Default configuration correct!")
                return True
            else:
                logger.error(f"❌ Expected anthropic/claude-sonnet-4-5, got {provider}/{model}")
                return False
        except Exception as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return False
    else:
        logger.error(f"Chat request failed: {response.status_code}")
        if response.content:
            try:
                error_data = response.json()
                logger.error(f"Error: {error_data}")
            except:
                logger.error(f"Error text: {response.text}")
        return False

if __name__ == "__main__":
    success = test_default_configuration()
    if success:
        print("🎉 Phase 2 default configuration test PASSED!")
    else:
        print("❌ Phase 2 default configuration test FAILED!")