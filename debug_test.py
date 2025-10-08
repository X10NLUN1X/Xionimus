#!/usr/bin/env python3
"""
Debug test to identify specific issues
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebugTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        
    def authenticate(self):
        """Authenticate with demo user"""
        login_data = {
            "username": "demo",
            "password": "demo123"
        }
        
        response = self.session.post(
            f"{self.api_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            auth_data = response.json()
            self.token = auth_data.get("access_token")
            logger.info(f"✅ Authentication successful, token: {self.token[:20]}...")
            return True
        else:
            logger.error(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def test_api_keys_list(self):
        """Test API keys list endpoint"""
        if not self.token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        response = self.session.get(
            f"{self.api_url}/api-keys/list",
            headers=headers,
            timeout=10
        )
        
        logger.info(f"API Keys List - Status: {response.status_code}")
        if response.content:
            try:
                data = response.json()
                logger.info(f"Response: {data}")
                logger.info(f"Response type: {type(data)}")
                if isinstance(data, list):
                    logger.info(f"List length: {len(data)}")
                    for i, item in enumerate(data):
                        logger.info(f"Item {i}: {item} (type: {type(item)})")
            except Exception as e:
                logger.error(f"JSON decode error: {e}")
                logger.info(f"Raw response: {response.text}")
    
    def test_chat_format(self):
        """Test correct chat format"""
        if not self.token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        # Test correct format
        chat_data = {
            "messages": [
                {"role": "user", "content": "Hello, this is a test"}
            ]
        }
        
        response = self.session.post(
            f"{self.api_url}/chat/",
            json=chat_data,
            headers=headers,
            timeout=30
        )
        
        logger.info(f"Chat Test - Status: {response.status_code}")
        if response.content:
            try:
                data = response.json()
                logger.info(f"Chat Response: {data}")
            except Exception as e:
                logger.error(f"JSON decode error: {e}")
                logger.info(f"Raw response: {response.text}")
    
    def test_sandbox_languages(self):
        """Test sandbox languages"""
        if not self.token:
            return
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        response = self.session.get(
            f"{self.api_url}/sandbox/languages",
            headers=headers,
            timeout=10
        )
        
        logger.info(f"Sandbox Languages - Status: {response.status_code}")
        if response.content:
            try:
                data = response.json()
                logger.info(f"Languages: {data}")
                logger.info(f"Languages type: {type(data)}")
                if isinstance(data, list):
                    logger.info(f"Available languages: {[lang.get('language', lang) for lang in data]}")
                elif isinstance(data, dict):
                    logger.info(f"Languages dict keys: {data.keys()}")
            except Exception as e:
                logger.error(f"JSON decode error: {e}")
                logger.info(f"Raw response: {response.text}")

def main():
    tester = DebugTester()
    
    if tester.authenticate():
        logger.info("\n=== Testing API Keys List ===")
        tester.test_api_keys_list()
        
        logger.info("\n=== Testing Chat Format ===")
        tester.test_chat_format()
        
        logger.info("\n=== Testing Sandbox Languages ===")
        tester.test_sandbox_languages()

if __name__ == "__main__":
    main()