#!/usr/bin/env python3
"""
Phase 5 Research History & PDF Export Testing
Comprehensive test suite for MongoDB-based research history and PDF export functionality
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

class Phase5ResearchHistoryTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "http://localhost:8001"  # Using internal URL for testing
        self.api_base = f"{self.base_url}/api"
        self.headers = {"Content-Type": "application/json"}
        self.auth_token = None
        self.test_research_ids = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def authenticate(self) -> bool:
        """Test 1: Authentication Setup - Login with demo/demo123"""
        self.log("🔐 Testing Authentication Setup...")
        
        try:
            login_data = {
                "username": "demo",
                "password": "demo123"
            }
            
            response = requests.post(
                f"{self.api_base}/auth/login",
                json=login_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.headers["Authorization"] = f"Bearer {self.auth_token}"
                    self.log("✅ Authentication successful - JWT token obtained")
                    return True
                else:
                    self.log("❌ Authentication failed - No access token in response", "ERROR")
                    return False
            else:
                self.log(f"❌ Authentication failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {str(e)}", "ERROR")
            return False
    
    def test_save_research(self) -> bool:
        """Test 2: Save Research (POST /api/research/save)"""
        self.log("💾 Testing Save Research...")
        
        try:
            research_data = {
                "query": "What is FastAPI?",
                "result": {
                    "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints. It was created by Sebastian Ramirez and is built on top of Starlette for the web parts and Pydantic for the data parts. FastAPI provides automatic API documentation, data validation, serialization, and async support out of the box.",
                    "citations": ["https://fastapi.tiangolo.com", "https://github.com/tiangolo/fastapi"],
                    "sources_count": 2,
                    "related_questions": ["How does FastAPI compare to Flask?", "What are FastAPI's main features?"],
                    "model_used": "gpt-4"
                },
                "duration_seconds": 5.2,
                "token_usage": {
                    "input_tokens": 150,
                    "output_tokens": 300,
                    "total_tokens": 450
                }
            }
            
            response = requests.post(
                f"{self.api_base}/research/save",
                json=research_data,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "user_id", "timestamp", "query", "result"]
                
                if all(field in data for field in required_fields):
                    research_id = data["id"]
                    self.test_research_ids.append(research_id)
                    
                    # Verify data integrity
                    if (data["query"] == research_data["query"] and
                        data["result"]["content"] == research_data["result"]["content"] and
                        data["result"]["sources_count"] == research_data["result"]["sources_count"] and
                        data["is_favorite"] == False):
                        
                        self.log(f"✅ Save Research successful - ID: {research_id[:8]}...")
                        return True
                    else:
                        self.log("❌ Save Research failed - Data integrity check failed", "ERROR")
                        return False
                else:
                    self.log(f"❌ Save Research failed - Missing required fields: {required_fields}", "ERROR")
                    return False
            else:
                self.log(f"❌ Save Research failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Save Research error: {str(e)}", "ERROR")
            return False
    
    def test_get_research_history(self) -> bool:
        """Test 3: Get Research History (GET /api/research/history)"""
        self.log("📚 Testing Get Research History...")
        
        try:
            # Test with default parameters
            response = requests.get(
                f"{self.api_base}/research/history",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    if len(data) > 0:
                        # Verify structure of first item
                        item = data[0]
                        required_fields = ["id", "user_id", "timestamp", "query", "result"]
                        
                        if all(field in item for field in required_fields):
                            self.log(f"✅ Get Research History successful - Found {len(data)} items")
                            return True
                        else:
                            self.log(f"❌ Get Research History failed - Missing fields in items: {required_fields}", "ERROR")
                            return False
                    else:
                        self.log("✅ Get Research History successful - Empty history (expected for new user)")
                        return True
                else:
                    self.log("❌ Get Research History failed - Response is not an array", "ERROR")
                    return False
            else:
                self.log(f"❌ Get Research History failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Get Research History error: {str(e)}", "ERROR")
            return False
    
    def test_toggle_favorite(self) -> bool:
        """Test 4: Toggle Favorite (PATCH /api/research/history/{id}/favorite)"""
        self.log("⭐ Testing Toggle Favorite...")
        
        if not self.test_research_ids:
            self.log("❌ Toggle Favorite failed - No research IDs available for testing", "ERROR")
            return False
        
        try:
            research_id = self.test_research_ids[0]
            
            # Toggle to favorite
            response = requests.patch(
                f"{self.api_base}/research/history/{research_id}/favorite",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "is_favorite" in data and data["is_favorite"] == True:
                    self.log("✅ Toggle Favorite to True successful")
                    
                    # Toggle back to false
                    response2 = requests.patch(
                        f"{self.api_base}/research/history/{research_id}/favorite",
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        if "is_favorite" in data2 and data2["is_favorite"] == False:
                            self.log("✅ Toggle Favorite to False successful")
                            return True
                        else:
                            self.log("❌ Toggle Favorite to False failed - Incorrect response", "ERROR")
                            return False
                    else:
                        self.log(f"❌ Toggle Favorite to False failed - Status: {response2.status_code}", "ERROR")
                        return False
                else:
                    self.log("❌ Toggle Favorite to True failed - Incorrect response", "ERROR")
                    return False
            else:
                self.log(f"❌ Toggle Favorite failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Toggle Favorite error: {str(e)}", "ERROR")
            return False
    
    def test_delete_research(self) -> bool:
        """Test 5: Delete Research (DELETE /api/research/history/{id})"""
        self.log("🗑️ Testing Delete Research...")
        
        if not self.test_research_ids:
            self.log("❌ Delete Research failed - No research IDs available for testing", "ERROR")
            return False
        
        try:
            research_id = self.test_research_ids[0]
            
            response = requests.delete(
                f"{self.api_base}/research/history/{research_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "deleted successfully" in data["message"]:
                    self.log("✅ Delete Research successful")
                    
                    # Verify deletion by trying to get history
                    verify_response = requests.get(
                        f"{self.api_base}/research/history",
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if verify_response.status_code == 200:
                        history_data = verify_response.json()
                        deleted_item_exists = any(item["id"] == research_id for item in history_data)
                        
                        if not deleted_item_exists:
                            self.log("✅ Delete Research verification successful - Item no longer in history")
                            # Remove from our test list
                            self.test_research_ids.remove(research_id)
                            return True
                        else:
                            self.log("❌ Delete Research verification failed - Item still in history", "ERROR")
                            return False
                    else:
                        self.log("⚠️ Delete Research successful but verification failed", "WARNING")
                        return True
                else:
                    self.log("❌ Delete Research failed - Incorrect response message", "ERROR")
                    return False
            else:
                self.log(f"❌ Delete Research failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Delete Research error: {str(e)}", "ERROR")
            return False
    
    def test_pdf_export_single(self) -> bool:
        """Test 6: PDF Export - Single (GET /api/research/history/{id}/export-pdf)"""
        self.log("📄 Testing PDF Export - Single...")
        
        # Create a new research item for PDF testing
        if not self.create_test_research_for_pdf():
            return False
        
        try:
            research_id = self.test_research_ids[-1]  # Use the latest created item
            
            response = requests.get(
                f"{self.api_base}/research/history/{research_id}/export-pdf",
                headers=self.headers,
                timeout=20
            )
            
            if response.status_code == 200:
                # Check Content-Type
                content_type = response.headers.get("Content-Type", "")
                if "application/pdf" in content_type:
                    self.log("✅ PDF Export Single - Correct Content-Type")
                    
                    # Check Content-Disposition
                    content_disposition = response.headers.get("Content-Disposition", "")
                    if "attachment" in content_disposition and "filename=" in content_disposition:
                        self.log("✅ PDF Export Single - Correct Content-Disposition header")
                        
                        # Check PDF content size
                        pdf_size = len(response.content)
                        if pdf_size > 1000:  # PDF should be at least 1KB
                            self.log(f"✅ PDF Export Single successful - PDF size: {pdf_size} bytes")
                            return True
                        else:
                            self.log(f"❌ PDF Export Single failed - PDF too small: {pdf_size} bytes", "ERROR")
                            return False
                    else:
                        self.log("❌ PDF Export Single failed - Missing or incorrect Content-Disposition header", "ERROR")
                        return False
                else:
                    self.log(f"❌ PDF Export Single failed - Incorrect Content-Type: {content_type}", "ERROR")
                    return False
            else:
                self.log(f"❌ PDF Export Single failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ PDF Export Single error: {str(e)}", "ERROR")
            return False
    
    def test_pdf_export_bulk(self) -> bool:
        """Test 7: PDF Export - Bulk (POST /api/research/export-bulk-pdf)"""
        self.log("📄 Testing PDF Export - Bulk...")
        
        # Create additional research items for bulk testing
        if not self.create_multiple_test_research():
            return False
        
        try:
            # Use the last 2-3 research IDs for bulk export
            research_ids = self.test_research_ids[-3:] if len(self.test_research_ids) >= 3 else self.test_research_ids
            
            bulk_request = {
                "research_ids": research_ids,
                "title": "Test Bulk Export",
                "include_sources": True,
                "include_metadata": True
            }
            
            response = requests.post(
                f"{self.api_base}/research/export-bulk-pdf",
                json=bulk_request,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                # Check Content-Type
                content_type = response.headers.get("Content-Type", "")
                if "application/pdf" in content_type:
                    self.log("✅ PDF Export Bulk - Correct Content-Type")
                    
                    # Check Content-Disposition with timestamp
                    content_disposition = response.headers.get("Content-Disposition", "")
                    if ("attachment" in content_disposition and 
                        "filename=" in content_disposition and
                        "research-export-" in content_disposition):
                        self.log("✅ PDF Export Bulk - Correct Content-Disposition with timestamp")
                        
                        # Check PDF content size
                        pdf_size = len(response.content)
                        if pdf_size > 2000:  # Bulk PDF should be larger
                            self.log(f"✅ PDF Export Bulk successful - PDF size: {pdf_size} bytes")
                            return True
                        else:
                            self.log(f"❌ PDF Export Bulk failed - PDF too small: {pdf_size} bytes", "ERROR")
                            return False
                    else:
                        self.log("❌ PDF Export Bulk failed - Missing or incorrect Content-Disposition header", "ERROR")
                        return False
                else:
                    self.log(f"❌ PDF Export Bulk failed - Incorrect Content-Type: {content_type}", "ERROR")
                    return False
            else:
                self.log(f"❌ PDF Export Bulk failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ PDF Export Bulk error: {str(e)}", "ERROR")
            return False
    
    def test_research_stats(self) -> bool:
        """Test 8: Research Stats (GET /api/research/stats)"""
        self.log("📊 Testing Research Stats...")
        
        try:
            response = requests.get(
                f"{self.api_base}/research/stats",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_queries", "favorites", "total_sources", "total_tokens", "average_sources_per_query"]
                
                if all(field in data for field in required_fields):
                    # Verify all values are numbers
                    if all(isinstance(data[field], (int, float)) for field in required_fields):
                        # Verify reasonable values
                        if (data["total_queries"] >= 0 and 
                            data["favorites"] >= 0 and
                            data["total_sources"] >= 0 and
                            data["total_tokens"] >= 0 and
                            data["average_sources_per_query"] >= 0):
                            
                            self.log(f"✅ Research Stats successful - Queries: {data['total_queries']}, Favorites: {data['favorites']}, Sources: {data['total_sources']}")
                            return True
                        else:
                            self.log("❌ Research Stats failed - Unreasonable values", "ERROR")
                            return False
                    else:
                        self.log("❌ Research Stats failed - Non-numeric values", "ERROR")
                        return False
                else:
                    self.log(f"❌ Research Stats failed - Missing required fields: {required_fields}", "ERROR")
                    return False
            else:
                self.log(f"❌ Research Stats failed - Status: {response.status_code}, Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Research Stats error: {str(e)}", "ERROR")
            return False
    
    def test_mongodb_connection(self) -> bool:
        """Test 9: MongoDB Connection verification"""
        self.log("🍃 Testing MongoDB Connection...")
        
        try:
            # Check backend logs for MongoDB connection messages
            # We'll use the health endpoint to verify overall system health
            response = requests.get(
                f"{self.api_base}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if system is healthy
                if data.get("status") in ["healthy", "limited"]:
                    self.log("✅ Backend health check passed")
                    
                    # Try to save a research item to verify MongoDB is working
                    test_save_result = self.create_test_research_for_mongodb()
                    if test_save_result:
                        self.log("✅ MongoDB Connection verified - Research save successful")
                        return True
                    else:
                        self.log("❌ MongoDB Connection failed - Cannot save research", "ERROR")
                        return False
                else:
                    self.log(f"❌ Backend health check failed - Status: {data.get('status')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Backend health check failed - Status: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ MongoDB Connection test error: {str(e)}", "ERROR")
            return False
    
    def test_error_handling(self) -> bool:
        """Test 10: Error Handling"""
        self.log("🚨 Testing Error Handling...")
        
        try:
            # Test 1: Unauthorized access (no Bearer token)
            headers_no_auth = {"Content-Type": "application/json"}
            response = requests.get(
                f"{self.api_base}/research/history",
                headers=headers_no_auth,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log("✅ Error Handling - Unauthorized access returns 401")
            else:
                self.log(f"❌ Error Handling - Unauthorized access should return 401, got {response.status_code}", "ERROR")
                return False
            
            # Test 2: Invalid research_id (should return 404)
            invalid_id = "invalid_research_id_12345"
            response = requests.get(
                f"{self.api_base}/research/history/{invalid_id}/export-pdf",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 404:
                self.log("✅ Error Handling - Invalid research_id returns 404")
            else:
                self.log(f"❌ Error Handling - Invalid research_id should return 404, got {response.status_code}", "ERROR")
                return False
            
            # Test 3: Malformed request body (should return 422)
            malformed_data = {
                "query": "Test",
                "result": "This should be an object, not a string"  # Invalid structure
            }
            
            response = requests.post(
                f"{self.api_base}/research/save",
                json=malformed_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 422:
                self.log("✅ Error Handling - Malformed request returns 422")
                return True
            else:
                self.log(f"❌ Error Handling - Malformed request should return 422, got {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Error Handling test error: {str(e)}", "ERROR")
            return False
    
    def create_test_research_for_pdf(self) -> bool:
        """Helper: Create a research item for PDF testing"""
        research_data = {
            "query": "How does machine learning work?",
            "result": {
                "content": "Machine learning is a subset of artificial intelligence (AI) that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves.",
                "citations": ["https://www.ibm.com/cloud/learn/machine-learning", "https://www.coursera.org/learn/machine-learning"],
                "sources_count": 2,
                "related_questions": ["What are the types of machine learning?", "How is machine learning used in business?"],
                "model_used": "claude-3-sonnet"
            },
            "duration_seconds": 3.8,
            "token_usage": {
                "input_tokens": 120,
                "output_tokens": 280,
                "total_tokens": 400
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/research/save",
                json=research_data,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_research_ids.append(data["id"])
                return True
            return False
        except:
            return False
    
    def create_multiple_test_research(self) -> bool:
        """Helper: Create multiple research items for bulk testing"""
        research_items = [
            {
                "query": "What is Python programming?",
                "result": {
                    "content": "Python is a high-level, interpreted programming language with dynamic semantics. Its high-level built-in data structures, combined with dynamic typing and dynamic binding, make it very attractive for Rapid Application Development.",
                    "citations": ["https://www.python.org/doc/essays/blurb/", "https://docs.python.org/3/tutorial/"],
                    "sources_count": 2,
                    "model_used": "gpt-4"
                },
                "duration_seconds": 2.5
            },
            {
                "query": "What is cloud computing?",
                "result": {
                    "content": "Cloud computing is the delivery of computing services—including servers, storage, databases, networking, software, analytics, and intelligence—over the Internet ('the cloud') to offer faster innovation, flexible resources, and economies of scale.",
                    "citations": ["https://azure.microsoft.com/en-us/overview/what-is-cloud-computing/", "https://aws.amazon.com/what-is-cloud-computing/"],
                    "sources_count": 2,
                    "model_used": "claude-3-haiku"
                },
                "duration_seconds": 4.1
            }
        ]
        
        success_count = 0
        for item in research_items:
            try:
                response = requests.post(
                    f"{self.api_base}/research/save",
                    json=item,
                    headers=self.headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.test_research_ids.append(data["id"])
                    success_count += 1
            except:
                continue
        
        return success_count >= 2
    
    def create_test_research_for_mongodb(self) -> bool:
        """Helper: Create a research item to test MongoDB connection"""
        research_data = {
            "query": "MongoDB connection test",
            "result": {
                "content": "This is a test research item to verify MongoDB connectivity.",
                "citations": ["https://test.example.com"],
                "sources_count": 1
            },
            "duration_seconds": 1.0
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/research/save",
                json=research_data,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_research_ids.append(data["id"])
                return True
            return False
        except:
            return False
    
    def cleanup_test_data(self):
        """Clean up test research items"""
        self.log("🧹 Cleaning up test data...")
        
        for research_id in self.test_research_ids:
            try:
                requests.delete(
                    f"{self.api_base}/research/history/{research_id}",
                    headers=self.headers,
                    timeout=10
                )
            except:
                pass  # Ignore cleanup errors
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all Phase 5 tests"""
        self.log("🚀 Starting Phase 5 Research History & PDF Export Testing...")
        self.log("=" * 60)
        
        tests = [
            ("Authentication Setup", self.authenticate),
            ("Save Research", self.test_save_research),
            ("Get Research History", self.test_get_research_history),
            ("Toggle Favorite", self.test_toggle_favorite),
            ("Delete Research", self.test_delete_research),
            ("PDF Export - Single", self.test_pdf_export_single),
            ("PDF Export - Bulk", self.test_pdf_export_bulk),
            ("Research Stats", self.test_research_stats),
            ("MongoDB Connection", self.test_mongodb_connection),
            ("Error Handling", self.test_error_handling)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- Testing: {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                self.log(f"❌ {test_name} failed with exception: {str(e)}", "ERROR")
                results[test_name] = False
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log("📊 PHASE 5 TESTING SUMMARY")
        self.log("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} {test_name}")
        
        success_rate = (passed / total) * 100
        self.log(f"\n🎯 Overall Success Rate: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.log("🎉 Phase 5 Research History & PDF Export is WORKING!")
        elif success_rate >= 60:
            self.log("⚠️ Phase 5 has some issues but core functionality works")
        else:
            self.log("❌ Phase 5 has significant issues requiring attention")
        
        return results


if __name__ == "__main__":
    tester = Phase5ResearchHistoryTester()
    results = tester.run_all_tests()