import requests
import sys
import json
from datetime import datetime

class EmergentDesktopAPITester:
    def __init__(self, base_url="https://matrix-agents-1.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.project_id = None
        self.file_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        if success:
            print(f"   Services: {response.get('services', {})}")
        return success

    def test_api_keys_status(self):
        """Test API keys status endpoint"""
        success, response = self.run_test(
            "API Keys Status",
            "GET",
            "api-keys/status",
            200
        )
        if success:
            print(f"   Perplexity configured: {response.get('perplexity', False)}")
            print(f"   Anthropic configured: {response.get('anthropic', False)}")
        return success

    def test_save_api_key(self):
        """Test saving API key (with test key)"""
        test_key_data = {
            "service": "perplexity",
            "key": "test-key-12345",
            "is_active": True
        }
        
        success, response = self.run_test(
            "Save API Key",
            "POST",
            "api-keys",
            200,
            data=test_key_data
        )
        return success

    def test_create_project(self):
        """Test creating a new project"""
        project_data = {
            "name": f"Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "This is a test project created by automated testing"
        }
        
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data=project_data
        )
        
        if success and 'id' in response:
            self.project_id = response['id']
            print(f"   Created project ID: {self.project_id}")
        
        return success

    def test_get_projects(self):
        """Test getting all projects"""
        success, response = self.run_test(
            "Get Projects",
            "GET",
            "projects",
            200
        )
        
        if success:
            print(f"   Found {len(response)} projects")
        
        return success

    def test_get_project_by_id(self):
        """Test getting a specific project"""
        if not self.project_id:
            print("❌ Skipping - No project ID available")
            return False
            
        success, response = self.run_test(
            "Get Project by ID",
            "GET",
            f"projects/{self.project_id}",
            200
        )
        return success

    def test_update_project(self):
        """Test updating a project"""
        if not self.project_id:
            print("❌ Skipping - No project ID available")
            return False
            
        update_data = {
            "name": f"Updated Test Project {datetime.now().strftime('%H%M%S')}",
            "description": "This project has been updated by automated testing"
        }
        
        success, response = self.run_test(
            "Update Project",
            "PUT",
            f"projects/{self.project_id}",
            200,
            data=update_data
        )
        return success

    def test_create_code_file(self):
        """Test creating a code file"""
        if not self.project_id:
            print("❌ Skipping - No project ID available")
            return False
            
        file_data = {
            "project_id": self.project_id,
            "name": "test_file.py",
            "content": "# Test Python file\nprint('Hello, World!')\n\ndef test_function():\n    return 'This is a test'",
            "language": "python"
        }
        
        success, response = self.run_test(
            "Create Code File",
            "POST",
            "files",
            200,
            data=file_data
        )
        
        if success and 'id' in response:
            self.file_id = response['id']
            print(f"   Created file ID: {self.file_id}")
        
        return success

    def test_get_project_files(self):
        """Test getting files for a project"""
        if not self.project_id:
            print("❌ Skipping - No project ID available")
            return False
            
        success, response = self.run_test(
            "Get Project Files",
            "GET",
            f"files/{self.project_id}",
            200
        )
        
        if success:
            print(f"   Found {len(response)} files")
        
        return success

    def test_get_file_content(self):
        """Test getting file content"""
        if not self.file_id:
            print("❌ Skipping - No file ID available")
            return False
            
        success, response = self.run_test(
            "Get File Content",
            "GET",
            f"files/content/{self.file_id}",
            200
        )
        return success

    def test_update_file(self):
        """Test updating file content"""
        if not self.file_id:
            print("❌ Skipping - No file ID available")
            return False
            
        update_data = {
            "project_id": self.project_id,
            "name": "updated_test_file.py",
            "content": "# Updated Test Python file\nprint('Hello, Updated World!')\n\ndef updated_function():\n    return 'This file has been updated'",
            "language": "python"
        }
        
        success, response = self.run_test(
            "Update File",
            "PUT",
            f"files/{self.file_id}",
            200,
            data=update_data
        )
        return success

    def test_chat_without_api_key(self):
        """Test chat functionality without API key (should fail gracefully)"""
        chat_data = {
            "message": "Hello, this is a test message",
            "model": "claude"
        }
        
        success, response = self.run_test(
            "Chat without API Key",
            "POST",
            "chat",
            400,  # Should return 400 for missing API key
            data=chat_data
        )
        return success

    def test_generate_code_without_api_key(self):
        """Test code generation without API key (should fail gracefully)"""
        code_gen_data = {
            "prompt": "Create a simple Python function that adds two numbers",
            "language": "python",
            "model": "claude"
        }
        
        success, response = self.run_test(
            "Generate Code without API Key",
            "POST",
            "generate-code",
            400,  # Should return 400 for missing API key
            data=code_gen_data
        )
        return success

    def test_get_available_agents(self):
        """Test getting available agents"""
        success, response = self.run_test(
            "Get Available Agents",
            "GET",
            "agents",
            200
        )
        
        if success:
            print(f"   Found {len(response)} agents")
            for agent in response:
                print(f"   - {agent.get('name', 'Unknown')}: {agent.get('capabilities', 'No capabilities')}")
        
        return success

    def test_analyze_request(self):
        """Test request analysis for agent selection"""
        # Test German code request
        german_request = {
            "message": "Erstelle eine Python Funktion für Fibonacci",
            "context": {}
        }
        
        success, response = self.run_test(
            "Analyze German Code Request",
            "POST",
            "agents/analyze",
            200,
            data=german_request
        )
        
        if success:
            print(f"   Language detected: {response.get('language_detected', {}).get('language', 'Unknown')}")
            print(f"   Best agent: {response.get('best_agent', 'None')}")
            print(f"   Requires agent: {response.get('requires_agent', False)}")
        
        return success

    def test_analyze_english_research_request(self):
        """Test request analysis for English research request"""
        english_request = {
            "message": "Research the latest developments in quantum computing and AI",
            "context": {}
        }
        
        success, response = self.run_test(
            "Analyze English Research Request",
            "POST",
            "agents/analyze",
            200,
            data=english_request
        )
        
        if success:
            print(f"   Language detected: {response.get('language_detected', {}).get('language', 'Unknown')}")
            print(f"   Best agent: {response.get('best_agent', 'None')}")
            print(f"   Requires agent: {response.get('requires_agent', False)}")
        
        return success

    def test_analyze_spanish_request(self):
        """Test request analysis for Spanish request"""
        spanish_request = {
            "message": "Analiza este código JavaScript y sugiere mejoras",
            "context": {}
        }
        
        success, response = self.run_test(
            "Analyze Spanish Code Request",
            "POST",
            "agents/analyze",
            200,
            data=spanish_request
        )
        
        if success:
            print(f"   Language detected: {response.get('language_detected', {}).get('language', 'Unknown')}")
            print(f"   Best agent: {response.get('best_agent', 'None')}")
            print(f"   Requires agent: {response.get('requires_agent', False)}")
        
        return success

    def test_analyze_french_request(self):
        """Test request analysis for French request"""
        french_request = {
            "message": "Recherche des informations sur l'intelligence artificielle",
            "context": {}
        }
        
        success, response = self.run_test(
            "Analyze French Research Request",
            "POST",
            "agents/analyze",
            200,
            data=french_request
        )
        
        if success:
            print(f"   Language detected: {response.get('language_detected', {}).get('language', 'Unknown')}")
            print(f"   Best agent: {response.get('best_agent', 'None')}")
            print(f"   Requires agent: {response.get('requires_agent', False)}")
        
        return success

    def test_chat_with_agent_german(self):
        """Test chat with agent processing (German)"""
        chat_data = {
            "message": "Erstelle eine Python Funktion für Fibonacci",
            "model": "claude",
            "use_agent": True,
            "context": {
                "language": "german"
            }
        }
        
        success, response = self.run_test(
            "Chat with Agent (German)",
            "POST",
            "chat",
            400,  # Will fail without API key, but should show agent processing
            data=chat_data
        )
        return success

    def test_chat_with_agent_english(self):
        """Test chat with agent processing (English)"""
        chat_data = {
            "message": "Generate a React component for user authentication",
            "model": "claude",
            "use_agent": True,
            "context": {
                "language": "english"
            }
        }
        
        success, response = self.run_test(
            "Chat with Agent (English)",
            "POST",
            "chat",
            400,  # Will fail without API key, but should show agent processing
            data=chat_data
        )
        return success

    def test_chat_without_agent(self):
        """Test chat without agent processing"""
        chat_data = {
            "message": "Hello, how are you?",
            "model": "claude",
            "use_agent": False
        }
        
        success, response = self.run_test(
            "Chat without Agent",
            "POST",
            "chat",
            400,  # Will fail without API key
            data=chat_data
        )
        return success

    def test_delete_file(self):
        """Test deleting a file"""
        if not self.file_id:
            print("❌ Skipping - No file ID available")
            return False
            
        success, response = self.run_test(
            "Delete File",
            "DELETE",
            f"files/{self.file_id}",
            200
        )
        return success

    def test_delete_project(self):
        """Test deleting a project"""
        if not self.project_id:
            print("❌ Skipping - No project ID available")
            return False
            
        success, response = self.run_test(
            "Delete Project",
            "DELETE",
            f"projects/{self.project_id}",
            200
        )
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Emergent Desktop API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Basic health and status tests
        self.test_health_check()
        self.test_api_keys_status()
        self.test_save_api_key()

        # Project management tests
        self.test_create_project()
        self.test_get_projects()
        self.test_get_project_by_id()
        self.test_update_project()

        # File management tests
        self.test_create_code_file()
        self.test_get_project_files()
        self.test_get_file_content()
        self.test_update_file()

        # Agent system tests
        self.test_get_available_agents()
        self.test_analyze_request()
        self.test_analyze_english_research_request()
        self.test_analyze_spanish_request()
        self.test_analyze_french_request()

        # AI functionality tests (without API keys)
        self.test_chat_without_api_key()
        self.test_generate_code_without_api_key()
        
        # Agent-enabled chat tests
        self.test_chat_with_agent_german()
        self.test_chat_with_agent_english()
        self.test_chat_without_agent()

        # Cleanup tests
        self.test_delete_file()
        self.test_delete_project()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = EmergentDesktopAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())