#!/usr/bin/env python3
"""
Test specific language to see detailed error
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_language(language, code):
    # Authenticate
    login_data = {"username": "demo", "password": "demo123"}
    session = requests.Session()
    
    response = session.post(
        "http://localhost:8001/api/auth/login",
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
    
    # Test language execution
    execute_data = {
        "language": language,
        "code": code
    }
    
    response = session.post(
        "http://localhost:8001/api/sandbox/execute",
        json=execute_data,
        headers=headers,
        timeout=30
    )
    
    logger.info(f"=== {language.upper()} TEST ===")
    logger.info(f"Status Code: {response.status_code}")
    
    if response.content:
        try:
            result = response.json()
            logger.info(f"Success: {result.get('success', 'N/A')}")
            logger.info(f"Exit Code: {result.get('exit_code', 'N/A')}")
            logger.info(f"Stdout: {result.get('stdout', 'N/A')}")
            logger.info(f"Stderr: {result.get('stderr', 'N/A')}")
            logger.info(f"Execution Time: {result.get('execution_time', 'N/A')}")
        except Exception as e:
            logger.error(f"JSON decode error: {e}")
            logger.info(f"Raw response: {response.text}")

# Test failing languages
test_language("typescript", "console.log('Hello World');")
test_language("php", "<?php echo 'Hello World\\n'; ?>")
test_language("ruby", "puts 'Hello World'")
test_language("csharp", "using System; class Program { static void Main() { Console.WriteLine(\"Hello World\"); } }")
test_language("java", "public class Main { public static void main(String[] args) { System.out.println(\"Hello World\"); } }")
test_language("go", "package main\nimport \"fmt\"\nfunc main() { fmt.Println(\"Hello World\") }")