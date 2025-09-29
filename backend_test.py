#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Development Environment
Tests all workspace and file upload endpoints
"""

import requests
import json
import os
import tempfile
from pathlib import Path
import time
import uuid

# Use local backend URL for testing
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api"

print(f"🧪 Testing Backend APIs at: {API_BASE}")
print("=" * 60)

class BackendTester:
    def __init__(self):
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, f"Version: {data.get('version', 'N/A')}")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unhealthy status: {data}")
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_workspace_tree(self):
        """Test workspace tree endpoint"""
        try:
            # Test root directory
            response = requests.get(f"{API_BASE}/workspace/tree", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Workspace Tree (root)", True, f"Found {len(data)} items")
                else:
                    self.log_test("Workspace Tree (root)", False, "Response is not a list")
                    return False
            else:
                self.log_test("Workspace Tree (root)", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Test with path parameter
            response = requests.get(f"{API_BASE}/workspace/tree?path=test", timeout=10)
            # This might return 404 if test directory doesn't exist, which is acceptable
            if response.status_code in [200, 404]:
                self.log_test("Workspace Tree (with path)", True, f"HTTP {response.status_code}")
            else:
                self.log_test("Workspace Tree (with path)", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Workspace Tree", False, f"Connection error: {str(e)}")
            return False
    
    def test_workspace_file_operations(self):
        """Test workspace file operations (create, read, delete)"""
        test_file_path = f"test_file_{uuid.uuid4().hex[:8]}.txt"
        test_content = "This is a test file content for API testing."
        
        try:
            # Test file creation/saving
            save_data = {"content": test_content}
            response = requests.post(
                f"{API_BASE}/workspace/file/{test_file_path}",
                json=save_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "saved":
                    self.log_test("Workspace File Save", True, f"Saved {data.get('size', 0)} bytes")
                else:
                    self.log_test("Workspace File Save", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Workspace File Save", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Test file reading
            response = requests.get(f"{API_BASE}/workspace/file/{test_file_path}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("content") == test_content:
                    self.log_test("Workspace File Read", True, f"Content matches ({data.get('size', 0)} bytes)")
                else:
                    self.log_test("Workspace File Read", False, "Content mismatch")
                    return False
            else:
                self.log_test("Workspace File Read", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Test file deletion
            response = requests.delete(f"{API_BASE}/workspace/file/{test_file_path}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "deleted":
                    self.log_test("Workspace File Delete", True, "File deleted successfully")
                else:
                    self.log_test("Workspace File Delete", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Workspace File Delete", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Workspace File Operations", False, f"Connection error: {str(e)}")
            return False
    
    def test_workspace_directory_creation(self):
        """Test workspace directory creation"""
        test_dir_path = f"test_dir_{uuid.uuid4().hex[:8]}"
        
        try:
            create_data = {"path": test_dir_path}
            response = requests.post(
                f"{API_BASE}/workspace/directory",
                json=create_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "created":
                    self.log_test("Workspace Directory Create", True, f"Created directory: {test_dir_path}")
                    
                    # Clean up - try to delete the directory
                    try:
                        requests.delete(f"{API_BASE}/workspace/file/{test_dir_path}", timeout=5)
                    except:
                        pass  # Ignore cleanup errors
                    
                    return True
                else:
                    self.log_test("Workspace Directory Create", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Workspace Directory Create", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Workspace Directory Create", False, f"Connection error: {str(e)}")
            return False
    
    def test_file_upload(self):
        """Test file upload endpoint"""
        try:
            # Create a test file
            test_content = b"This is a test file for upload testing. " * 100  # ~4KB file
            test_filename = f"test_upload_{uuid.uuid4().hex[:8]}.txt"
            
            files = {
                'file': (test_filename, test_content, 'text/plain')
            }
            data = {
                'description': 'Test file upload'
            }
            
            response = requests.post(
                f"{API_BASE}/files/upload",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                upload_data = response.json()
                if upload_data.get("status") == "uploaded":
                    file_id = upload_data.get("file_id")
                    self.log_test("File Upload", True, f"Uploaded {upload_data.get('size', 0)} bytes, ID: {file_id}")
                    
                    # Test file deletion
                    if file_id:
                        delete_response = requests.delete(f"{API_BASE}/files/{file_id}", timeout=10)
                        if delete_response.status_code == 200:
                            self.log_test("File Delete", True, "File deleted successfully")
                        else:
                            self.log_test("File Delete", False, f"HTTP {delete_response.status_code}")
                    
                    return True
                else:
                    self.log_test("File Upload", False, f"Unexpected response: {upload_data}")
                    return False
            else:
                self.log_test("File Upload", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("File Upload", False, f"Connection error: {str(e)}")
            return False
    
    def test_file_list(self):
        """Test file listing endpoint"""
        try:
            response = requests.get(f"{API_BASE}/files/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("File List", True, f"Found {len(data)} files")
                    return True
                else:
                    self.log_test("File List", False, "Response is not a list")
                    return False
            else:
                self.log_test("File List", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("File List", False, f"Connection error: {str(e)}")
            return False
    
    def test_large_file_upload(self):
        """Test large file upload (within 250MB limit)"""
        try:
            # Create a 5MB test file
            test_content = b"A" * (5 * 1024 * 1024)  # 5MB
            test_filename = f"large_test_{uuid.uuid4().hex[:8]}.bin"
            
            files = {
                'file': (test_filename, test_content, 'application/octet-stream')
            }
            data = {
                'description': 'Large file upload test (5MB)'
            }
            
            response = requests.post(
                f"{API_BASE}/files/upload",
                files=files,
                data=data,
                timeout=60  # Longer timeout for large file
            )
            
            if response.status_code == 200:
                upload_data = response.json()
                if upload_data.get("status") == "uploaded":
                    file_id = upload_data.get("file_id")
                    self.log_test("Large File Upload (5MB)", True, f"Uploaded {upload_data.get('size', 0)} bytes")
                    
                    # Clean up
                    if file_id:
                        try:
                            requests.delete(f"{API_BASE}/files/{file_id}", timeout=10)
                        except:
                            pass  # Ignore cleanup errors
                    
                    return True
                else:
                    self.log_test("Large File Upload (5MB)", False, f"Unexpected response: {upload_data}")
                    return False
            else:
                self.log_test("Large File Upload (5MB)", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Large File Upload (5MB)", False, f"Connection error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests...")
        print()
        
        # Test health endpoint first
        if not self.test_health_endpoint():
            print("\n❌ Backend health check failed. Stopping tests.")
            return False
        
        print()
        
        # Test workspace endpoints
        print("📁 Testing Workspace APIs...")
        self.test_workspace_tree()
        self.test_workspace_file_operations()
        self.test_workspace_directory_creation()
        
        print()
        
        # Test file upload endpoints
        print("📤 Testing File Upload APIs...")
        self.test_file_list()
        self.test_file_upload()
        self.test_large_file_upload()
        
        print()
        print("=" * 60)
        
        # Summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {failed_tests}")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All backend tests passed!")
        exit(0)
    else:
        print(f"\n💥 {len(tester.failed_tests)} test(s) failed!")
        exit(1)