#!/usr/bin/env python3
"""
Ultra-Thinking Debug Test - Detailed debugging of ultra-thinking functionality
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ultra_thinking_debug():
    """Debug ultra-thinking functionality in detail"""
    base_url = "http://localhost:8001"
    api_url = f"{base_url}/api"
    
    # Authenticate
    login_data = {"username": "demo", "password": "demo123"}
    session = requests.Session()
    
    response = session.post(
        f"{api_url}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code != 200:
        logger.error("Authentication failed")
        return
    
    token = response.json().get("access_token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Explicit ultra_thinking=True
    logger.info("=== TEST 1: Explicit ultra_thinking=True ===")
    chat_data = {
        "messages": [{"role": "user", "content": "Explain quantum computing in detail"}],
        "provider": "anthropic",
        "model": "claude-sonnet-4-5-20250929",
        "ultra_thinking": True
    }
    
    response = session.post(
        f"{api_url}/chat/",
        json=chat_data,
        headers=headers,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Provider: {result.get('provider')}")
        logger.info(f"Model: {result.get('model')}")
        logger.info(f"Usage: {result.get('usage')}")
        logger.info(f"Content length: {len(result.get('content', ''))}")
        logger.info(f"Content preview: {result.get('content', '')[:200]}...")
    else:
        logger.error(f"Request failed: {response.status_code} - {response.text}")
    
    # Test 2: Senior developer mode (should enable ultra_thinking)
    logger.info("\n=== TEST 2: Senior developer mode ===")
    chat_data = {
        "messages": [{"role": "user", "content": "Explain machine learning algorithms"}],
        "developer_mode": "senior"
    }
    
    response = session.post(
        f"{api_url}/chat/",
        json=chat_data,
        headers=headers,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Provider: {result.get('provider')}")
        logger.info(f"Model: {result.get('model')}")
        logger.info(f"Usage: {result.get('usage')}")
        logger.info(f"Content length: {len(result.get('content', ''))}")
        logger.info(f"Content preview: {result.get('content', '')[:200]}...")
    else:
        logger.error(f"Request failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_ultra_thinking_debug()