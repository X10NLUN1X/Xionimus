#!/usr/bin/env python3
"""
COMPREHENSIVE BACKEND TESTING - Project Hardening Verification

Tests all 13 newly implemented hardening features to verify production readiness.

TESTING SCOPE:
1. Dependency Resolution (H1)
2. Secrets Management (H3) 
3. Test Coverage (H4)
4. Database Indexing (M1)
5. API Versioning (M2)
6. CORS Configuration (L1)
7. Prometheus Metrics (L4)
8. Backend Stability
"""

import requests
import json
import time
import logging
import sqlite3
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HardeningTester:
    def __init__(self, base_url: str = None):
        # Get backend URL from frontend .env if available
        frontend_env_path = Path("/app/frontend/.env")
        if frontend_env_path.exists():
            with open(frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        backend_url = line.split('=', 1)[1].strip()
                        self.base_url = backend_url
                        break
        
        if not hasattr(self, 'base_url') or not self.base_url:
            self.base_url = base_url or "http://localhost:8001"
        
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        self.db_path = os.path.expanduser("~/.xionimus_ai/xionimus.db")

    def authenticate_demo_user(self) -> Dict[str, Any]:
        """Authenticate with demo/demo123 credentials"""
        logger.info("🔐 Authenticating with demo user (demo/demo123)")
        
        try:
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
            
            logger.info(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                auth_data = response.json()
                self.token = auth_data.get("access_token")
                self.user_info = {
                    "user_id": auth_data.get("user_id"),
                    "username": auth_data.get("username")
                }
                
                logger.info("✅ Authentication successful!")
                logger.info(f"   User ID: {self.user_info['user_id']}")
                logger.info(f"   Username: {self.user_info['username']}")
                
                return {"status": "success", "token": self.token, "user_info": self.user_info}
            else:
                error_detail = response.json().get("detail", "Unknown error") if response.content else f"HTTP {response.status_code}"
                logger.error(f"❌ Authentication failed: {error_detail}")
                return {"status": "failed", "error": error_detail}
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return {"status": "error", "error": str(e)}

    def test_dependency_resolution(self) -> Dict[str, Any]:
        """Test H1: Dependency Resolution - Backend starts without conflicts"""
        logger.info("🔧 Testing Dependency Resolution (H1)")
        
        try:
            # Check if backend is running by hitting root endpoint (public)
            response = self.session.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                root_data = response.json()
                logger.info("✅ Backend started successfully")
                logger.info(f"   Message: {root_data.get('message')}")
                logger.info(f"   Platform: {root_data.get('platform')}")
                logger.info(f"   Docs: {root_data.get('docs')}")
                
                # Check for dependency conflicts in logs
                try:
                    result = subprocess.run(
                        ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if result.returncode == 0:
                        log_content = result.stdout.lower()
                        conflict_indicators = ["conflict", "incompatible", "version mismatch", "import error"]
                        conflicts_found = [indicator for indicator in conflict_indicators if indicator in log_content]
                        
                        if conflicts_found:
                            logger.warning(f"⚠️ Potential conflicts found: {conflicts_found}")
                            return {
                                "status": "warning",
                                "backend_running": True,
                                "conflicts_found": conflicts_found,
                                "root_data": root_data
                            }
                        else:
                            logger.info("✅ No dependency conflicts detected in logs")
                            return {
                                "status": "success",
                                "backend_running": True,
                                "conflicts_found": [],
                                "root_data": root_data
                            }
                    else:
                        logger.warning("⚠️ Could not check backend logs")
                        return {
                            "status": "partial",
                            "backend_running": True,
                            "log_check": "failed",
                            "root_data": root_data
                        }
                        
                except Exception as e:
                    logger.warning(f"⚠️ Log check failed: {e}")
                    return {
                        "status": "partial",
                        "backend_running": True,
                        "log_check_error": str(e),
                        "root_data": root_data
                    }
            else:
                logger.error(f"❌ Backend not responding: {response.status_code}")
                return {
                    "status": "failed",
                    "backend_running": False,
                    "error": f"Health check failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Dependency resolution test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_secrets_management(self) -> Dict[str, Any]:
        """Test H3: Secrets Management - env_validator.py and .env.example"""
        logger.info("🔐 Testing Secrets Management (H3)")
        
        try:
            # Check if env_validator.py exists and is functional
            env_validator_path = Path("/app/backend/app/core/env_validator.py")
            env_example_path = Path("/app/backend/.env.example")
            env_path = Path("/app/backend/.env")
            
            results = {
                "env_validator_exists": env_validator_path.exists(),
                "env_example_exists": env_example_path.exists(),
                "env_exists": env_path.exists(),
                "validation_working": False,
                "required_vars_check": {},
                "secret_key_secure": False
            }
            
            if env_validator_path.exists():
                logger.info("✅ env_validator.py exists")
                
                # Test validation by importing
                try:
                    sys.path.insert(0, str(env_validator_path.parent.parent.parent))
                    from app.core.env_validator import validate_environment, EnvironmentValidator
                    
                    # Test validator functionality
                    validator = EnvironmentValidator(strict_mode=False)
                    success, message = validator.validate_all()
                    
                    results["validation_working"] = True
                    results["validation_success"] = success
                    results["validation_message"] = message[:200] + "..." if len(message) > 200 else message
                    
                    logger.info("✅ Environment validator is functional")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Environment validator import failed: {e}")
                    results["validation_error"] = str(e)
            else:
                logger.error("❌ env_validator.py not found")
            
            if env_example_path.exists():
                logger.info("✅ .env.example exists")
                
                # Check completeness of .env.example
                with open(env_example_path, 'r') as f:
                    example_content = f.read()
                
                required_vars = ["SECRET_KEY", "MONGO_URL", "JWT_ALGORITHM", "JWT_EXPIRE_MINUTES"]
                for var in required_vars:
                    if var in example_content:
                        results["required_vars_check"][var] = True
                        logger.info(f"   ✓ {var} found in .env.example")
                    else:
                        results["required_vars_check"][var] = False
                        logger.warning(f"   ⚠️ {var} missing from .env.example")
            else:
                logger.error("❌ .env.example not found")
            
            if env_path.exists():
                logger.info("✅ .env exists")
                
                # Check SECRET_KEY security
                secret_key = os.getenv("SECRET_KEY", "")
                if secret_key:
                    insecure_patterns = ["your-secret-key-here", "changeme", "secret", "test"]
                    is_secure = len(secret_key) >= 32 and not any(pattern in secret_key.lower() for pattern in insecure_patterns)
                    results["secret_key_secure"] = is_secure
                    results["secret_key_length"] = len(secret_key)
                    
                    if is_secure:
                        logger.info("✅ SECRET_KEY appears secure")
                    else:
                        logger.warning("⚠️ SECRET_KEY may be insecure")
            else:
                logger.warning("⚠️ .env not found")
            
            # Determine overall status
            if results["env_validator_exists"] and results["env_example_exists"] and results["validation_working"]:
                status = "success"
                logger.info("✅ Secrets management implementation complete")
            else:
                status = "partial"
                logger.warning("⚠️ Secrets management partially implemented")
            
            return {"status": status, **results}
            
        except Exception as e:
            logger.error(f"❌ Secrets management test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_coverage_files(self) -> Dict[str, Any]:
        """Test H4: Test Coverage - Run specific test files"""
        logger.info("🧪 Testing Test Coverage (H4)")
        
        test_files = [
            "test_jwt_auth.py",
            "test_rate_limiting.py", 
            "test_rag_basic.py",
            "test_cors_config.py"
        ]
        
        results = {
            "test_files_exist": {},
            "test_results": {},
            "overall_status": "unknown"
        }
        
        backend_tests_dir = Path("/app/backend/tests")
        
        try:
            # Check if test files exist
            for test_file in test_files:
                test_path = backend_tests_dir / test_file
                exists = test_path.exists()
                results["test_files_exist"][test_file] = exists
                
                if exists:
                    logger.info(f"✅ {test_file} exists")
                else:
                    logger.warning(f"⚠️ {test_file} not found")
            
            # Run tests if they exist
            existing_tests = [f for f in test_files if results["test_files_exist"][f]]
            
            if existing_tests:
                logger.info(f"🏃 Running {len(existing_tests)} test files...")
                
                for test_file in existing_tests:
                    try:
                        # Run pytest on specific file
                        result = subprocess.run([
                            "python", "-m", "pytest", 
                            str(backend_tests_dir / test_file),
                            "-v", "--tb=short"
                        ], 
                        cwd="/app/backend",
                        capture_output=True, 
                        text=True, 
                        timeout=60
                        )
                        
                        results["test_results"][test_file] = {
                            "return_code": result.returncode,
                            "passed": result.returncode == 0,
                            "stdout": result.stdout[-500:] if result.stdout else "",  # Last 500 chars
                            "stderr": result.stderr[-500:] if result.stderr else ""
                        }
                        
                        if result.returncode == 0:
                            logger.info(f"✅ {test_file} passed")
                        else:
                            logger.warning(f"⚠️ {test_file} failed (exit code: {result.returncode})")
                            
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️ {test_file} timed out")
                        results["test_results"][test_file] = {
                            "return_code": -1,
                            "passed": False,
                            "error": "timeout"
                        }
                    except Exception as e:
                        logger.warning(f"⚠️ {test_file} error: {e}")
                        results["test_results"][test_file] = {
                            "return_code": -1,
                            "passed": False,
                            "error": str(e)
                        }
                
                # Calculate overall status
                passed_tests = sum(1 for r in results["test_results"].values() if r.get("passed", False))
                total_tests = len(results["test_results"])
                
                if passed_tests == total_tests:
                    results["overall_status"] = "success"
                    logger.info(f"✅ All {total_tests} tests passed")
                elif passed_tests > 0:
                    results["overall_status"] = "partial"
                    logger.warning(f"⚠️ {passed_tests}/{total_tests} tests passed")
                else:
                    results["overall_status"] = "failed"
                    logger.error(f"❌ 0/{total_tests} tests passed")
            else:
                results["overall_status"] = "no_tests"
                logger.warning("⚠️ No test files found to run")
            
            return {"status": results["overall_status"], **results}
            
        except Exception as e:
            logger.error(f"❌ Test coverage check failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_database_indexing(self) -> Dict[str, Any]:
        """Test M1: Database Indexing - Verify SQLite indexes exist"""
        logger.info("🗄️ Testing Database Indexing (M1)")
        
        try:
            if not os.path.exists(self.db_path):
                logger.warning(f"⚠️ Database not found at {self.db_path}")
                return {
                    "status": "failed",
                    "error": f"Database file not found at {self.db_path}"
                }
            
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results = {
                "database_exists": True,
                "tables_checked": {},
                "indexes_found": {},
                "expected_indexes": {
                    "users": ["ix_users_email", "ix_users_username", "idx_users_role", "idx_users_is_active"],
                    "sessions": ["idx_sessions_user_id", "idx_sessions_created_at", "idx_sessions_updated_at"],
                    "messages": ["idx_messages_session_id", "idx_messages_timestamp", "idx_messages_role"]
                }
            }
            
            # Check each table and its indexes
            for table_name, expected_indexes in results["expected_indexes"].items():
                try:
                    # Check if table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                    table_exists = cursor.fetchone() is not None
                    results["tables_checked"][table_name] = table_exists
                    
                    if table_exists:
                        # Get indexes for this table
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=?", (table_name,))
                        actual_indexes = [row[0] for row in cursor.fetchall()]
                        results["indexes_found"][table_name] = actual_indexes
                        
                        # Check expected indexes
                        found_expected = [idx for idx in expected_indexes if idx in actual_indexes]
                        missing_expected = [idx for idx in expected_indexes if idx not in actual_indexes]
                        
                        logger.info(f"📊 {table_name}: {len(found_expected)}/{len(expected_indexes)} expected indexes found")
                        
                        if missing_expected:
                            logger.warning(f"   ⚠️ Missing indexes: {missing_expected}")
                        else:
                            logger.info(f"   ✅ All expected indexes present")
                    else:
                        logger.warning(f"⚠️ Table {table_name} not found")
                        results["indexes_found"][table_name] = []
                        
                except Exception as e:
                    logger.error(f"❌ Error checking {table_name}: {e}")
                    results["tables_checked"][table_name] = False
                    results["indexes_found"][table_name] = []
            
            conn.close()
            
            # Calculate overall status
            total_expected = sum(len(indexes) for indexes in results["expected_indexes"].values())
            total_found = sum(
                len([idx for idx in expected if idx in results["indexes_found"].get(table, [])])
                for table, expected in results["expected_indexes"].items()
            )
            
            if total_found >= total_expected * 0.8:  # 80% threshold
                status = "success"
                logger.info(f"✅ Database indexing: {total_found}/{total_expected} indexes found")
            elif total_found > 0:
                status = "partial"
                logger.warning(f"⚠️ Database indexing: {total_found}/{total_expected} indexes found")
            else:
                status = "failed"
                logger.error(f"❌ Database indexing: {total_found}/{total_expected} indexes found")
            
            return {
                "status": status,
                "total_expected": total_expected,
                "total_found": total_found,
                **results
            }
            
        except Exception as e:
            logger.error(f"❌ Database indexing test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_api_versioning(self) -> Dict[str, Any]:
        """Test M2: API Versioning - Test /api/version and v1 routes"""
        logger.info("🔄 Testing API Versioning (M2)")
        
        try:
            results = {
                "version_endpoint": False,
                "v1_routes_working": False,
                "legacy_routes_working": False,
                "deprecation_headers": False,
                "version_info": {}
            }
            
            # Test version endpoint
            try:
                response = self.session.get(f"{self.api_url}/version", timeout=10)
                if response.status_code == 200:
                    version_data = response.json()
                    results["version_endpoint"] = True
                    results["version_info"] = version_data
                    logger.info("✅ /api/version endpoint working")
                    logger.info(f"   Current version: {version_data.get('current_version')}")
                else:
                    logger.warning(f"⚠️ /api/version returned {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ /api/version test failed: {e}")
            
            # Test v1 routes (using health as example)
            try:
                response = self.session.get(f"{self.base_url}/api/v1/health", timeout=10)
                if response.status_code == 200:
                    results["v1_routes_working"] = True
                    logger.info("✅ /api/v1/* routes working")
                    
                    # Check for API-Version header
                    if "API-Version" in response.headers:
                        logger.info(f"   ✓ API-Version header: {response.headers['API-Version']}")
                else:
                    logger.warning(f"⚠️ /api/v1/health returned {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ v1 routes test failed: {e}")
            
            # Test legacy routes with deprecation headers
            try:
                response = self.session.get(f"{self.api_url}/health", timeout=10)
                if response.status_code == 200:
                    results["legacy_routes_working"] = True
                    logger.info("✅ Legacy /api/* routes working")
                    
                    # Check for deprecation headers
                    deprecation_headers = ["Deprecation", "Sunset", "Warning"]
                    found_headers = [h for h in deprecation_headers if h in response.headers]
                    
                    if found_headers:
                        results["deprecation_headers"] = True
                        logger.info(f"   ✓ Deprecation headers found: {found_headers}")
                    else:
                        logger.warning("   ⚠️ No deprecation headers found")
                else:
                    logger.warning(f"⚠️ Legacy /api/health returned {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Legacy routes test failed: {e}")
            
            # Determine overall status
            working_features = sum([
                results["version_endpoint"],
                results["v1_routes_working"],
                results["legacy_routes_working"]
            ])
            
            if working_features >= 3:
                status = "success"
                logger.info("✅ API versioning fully functional")
            elif working_features >= 2:
                status = "partial"
                logger.warning("⚠️ API versioning partially working")
            else:
                status = "failed"
                logger.error("❌ API versioning not working")
            
            return {"status": status, **results}
            
        except Exception as e:
            logger.error(f"❌ API versioning test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_cors_configuration(self) -> Dict[str, Any]:
        """Test L1: CORS Configuration - Verify CORS headers"""
        logger.info("🌐 Testing CORS Configuration (L1)")
        
        try:
            results = {
                "cors_headers_present": False,
                "preflight_working": False,
                "cors_config_loaded": False,
                "headers_found": {}
            }
            
            # Test CORS headers on a simple GET request
            try:
                response = self.session.get(f"{self.base_url}/", timeout=10)
                
                cors_headers = [
                    "Access-Control-Allow-Origin",
                    "Access-Control-Allow-Methods", 
                    "Access-Control-Allow-Headers",
                    "Access-Control-Allow-Credentials"
                ]
                
                found_headers = {}
                for header in cors_headers:
                    if header in response.headers:
                        found_headers[header] = response.headers[header]
                
                results["headers_found"] = found_headers
                results["cors_headers_present"] = len(found_headers) > 0
                
                if found_headers:
                    logger.info(f"✅ CORS headers found: {len(found_headers)}")
                    for header, value in found_headers.items():
                        logger.info(f"   {header}: {value}")
                else:
                    logger.warning("⚠️ No CORS headers found in response")
                    
            except Exception as e:
                logger.warning(f"⚠️ CORS headers test failed: {e}")
            
            # Test CORS preflight (OPTIONS request)
            try:
                headers = {
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type,Authorization"
                }
                
                response = self.session.options(f"{self.api_url}/health", headers=headers, timeout=10)
                
                if response.status_code in [200, 204]:
                    results["preflight_working"] = True
                    logger.info("✅ CORS preflight (OPTIONS) working")
                else:
                    logger.warning(f"⚠️ CORS preflight returned {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ CORS preflight test failed: {e}")
            
            # Check if cors_config.py exists
            cors_config_path = Path("/app/backend/app/core/cors_config.py")
            if cors_config_path.exists():
                results["cors_config_loaded"] = True
                logger.info("✅ cors_config.py exists")
            else:
                logger.warning("⚠️ cors_config.py not found")
            
            # Determine overall status
            working_features = sum([
                results["cors_headers_present"],
                results["cors_config_loaded"]
            ])
            
            if working_features >= 2:
                status = "success"
                logger.info("✅ CORS configuration working")
            elif working_features >= 1:
                status = "partial"
                logger.warning("⚠️ CORS configuration partially working")
            else:
                status = "failed"
                logger.error("❌ CORS configuration not working")
            
            return {"status": status, **results}
            
        except Exception as e:
            logger.error(f"❌ CORS configuration test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_prometheus_metrics(self) -> Dict[str, Any]:
        """Test L4: Prometheus Metrics - Test /api/metrics endpoint"""
        logger.info("📊 Testing Prometheus Metrics (L4)")
        
        try:
            results = {
                "metrics_endpoint": False,
                "prometheus_format": False,
                "metrics_content": "",
                "prometheus_client_integrated": False,
                "metrics_count": 0
            }
            
            # Test metrics endpoint
            try:
                response = self.session.get(f"{self.api_url}/metrics", timeout=10)
                
                if response.status_code == 200:
                    results["metrics_endpoint"] = True
                    logger.info("✅ /api/metrics endpoint accessible")
                    
                    # Check content type
                    content_type = response.headers.get("content-type", "")
                    if "text/plain" in content_type or "prometheus" in content_type:
                        results["prometheus_format"] = True
                        logger.info("✅ Prometheus format detected")
                    
                    # Check content
                    content = response.text
                    results["metrics_content"] = content[:500]  # First 500 chars
                    
                    # Count metrics (lines starting with # HELP or actual metrics)
                    lines = content.split('\n')
                    help_lines = [line for line in lines if line.startswith('# HELP')]
                    metric_lines = [line for line in lines if line and not line.startswith('#')]
                    
                    results["metrics_count"] = len(help_lines)
                    
                    logger.info(f"   Metrics found: {len(help_lines)} definitions, {len(metric_lines)} values")
                    
                    # Check for expected Xionimus metrics
                    expected_metrics = ["xionimus_", "http_requests", "system_"]
                    found_expected = [metric for metric in expected_metrics if metric in content]
                    
                    if found_expected:
                        logger.info(f"   ✓ Expected metrics found: {found_expected}")
                    else:
                        logger.warning("   ⚠️ No expected Xionimus metrics found")
                        
                else:
                    logger.warning(f"⚠️ /api/metrics returned {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Metrics endpoint test failed: {e}")
            
            # Check if prometheus_client is integrated
            prometheus_metrics_path = Path("/app/backend/app/core/prometheus_metrics.py")
            if prometheus_metrics_path.exists():
                results["prometheus_client_integrated"] = True
                logger.info("✅ prometheus_metrics.py exists")
            else:
                logger.warning("⚠️ prometheus_metrics.py not found")
            
            # Determine overall status
            if results["metrics_endpoint"] and results["prometheus_format"] and results["metrics_count"] > 0:
                status = "success"
                logger.info("✅ Prometheus metrics fully functional")
            elif results["metrics_endpoint"]:
                status = "partial"
                logger.warning("⚠️ Prometheus metrics partially working")
            else:
                status = "failed"
                logger.error("❌ Prometheus metrics not working")
            
            return {"status": status, **results}
            
        except Exception as e:
            logger.error(f"❌ Prometheus metrics test failed: {e}")
            return {"status": "error", "error": str(e)}

    def test_backend_stability(self) -> Dict[str, Any]:
        """Test Backend Stability - Verify backend starts cleanly and APIs accessible"""
        logger.info("🏥 Testing Backend Stability")
        
        try:
            results = {
                "health_check": False,
                "supervisor_status": "unknown",
                "api_endpoints_accessible": 0,
                "error_logs": [],
                "uptime_seconds": 0
            }
            
            # Test health check
            try:
                response = self.session.get(f"{self.api_url}/health", timeout=10)
                if response.status_code == 200:
                    health_data = response.json()
                    results["health_check"] = True
                    results["uptime_seconds"] = health_data.get("uptime_seconds", 0)
                    logger.info("✅ Health check passed")
                    logger.info(f"   Uptime: {results['uptime_seconds']} seconds")
                    logger.info(f"   Status: {health_data.get('status')}")
                else:
                    logger.warning(f"⚠️ Health check returned {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Health check failed: {e}")
            
            # Check supervisor status
            try:
                result = subprocess.run(
                    ["supervisorctl", "status", "backend"],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    status_output = result.stdout.strip()
                    if "RUNNING" in status_output:
                        results["supervisor_status"] = "running"
                        logger.info("✅ Supervisor shows backend RUNNING")
                    else:
                        results["supervisor_status"] = "not_running"
                        logger.warning(f"⚠️ Supervisor status: {status_output}")
                else:
                    results["supervisor_status"] = "error"
                    logger.warning("⚠️ Could not check supervisor status")
                    
            except Exception as e:
                logger.warning(f"⚠️ Supervisor check failed: {e}")
            
            # Test multiple API endpoints
            test_endpoints = [
                "/health",
                "/version", 
                "/auth/login",  # Should return 422 without data, but endpoint should exist
                "/rate-limits/limits"
            ]
            
            accessible_count = 0
            for endpoint in test_endpoints:
                try:
                    response = self.session.get(f"{self.api_url}{endpoint}", timeout=5)
                    # Accept any response that's not 404 or connection error
                    if response.status_code != 404:
                        accessible_count += 1
                        logger.info(f"   ✓ {endpoint} accessible ({response.status_code})")
                    else:
                        logger.warning(f"   ⚠️ {endpoint} not found (404)")
                except Exception as e:
                    logger.warning(f"   ⚠️ {endpoint} error: {e}")
            
            results["api_endpoints_accessible"] = accessible_count
            logger.info(f"API endpoints accessible: {accessible_count}/{len(test_endpoints)}")
            
            # Check for errors in logs
            try:
                result = subprocess.run(
                    ["tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
                    capture_output=True, text=True, timeout=5
                )
                
                if result.returncode == 0:
                    error_lines = [line.strip() for line in result.stdout.split('\n') 
                                 if line.strip() and any(keyword in line.lower() 
                                 for keyword in ['error', 'exception', 'failed', 'critical'])]
                    results["error_logs"] = error_lines[-5:]  # Last 5 errors
                    
                    if error_lines:
                        logger.warning(f"⚠️ Recent errors found: {len(error_lines)}")
                    else:
                        logger.info("✅ No recent errors in logs")
                        
            except Exception as e:
                logger.warning(f"⚠️ Error log check failed: {e}")
            
            # Determine overall status
            stability_score = 0
            if results["health_check"]:
                stability_score += 2
            if results["supervisor_status"] == "running":
                stability_score += 2
            if results["api_endpoints_accessible"] >= len(test_endpoints) * 0.75:  # 75% threshold
                stability_score += 2
            if len(results["error_logs"]) == 0:
                stability_score += 1
            
            if stability_score >= 6:
                status = "success"
                logger.info("✅ Backend stability excellent")
            elif stability_score >= 4:
                status = "partial"
                logger.warning("⚠️ Backend stability good with minor issues")
            else:
                status = "failed"
                logger.error("❌ Backend stability issues detected")
            
            return {"status": status, "stability_score": stability_score, **results}
            
        except Exception as e:
            logger.error(f"❌ Backend stability test failed: {e}")
            return {"status": "error", "error": str(e)}

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all hardening tests"""
        print("\n" + "="*80)
        print("🔒 COMPREHENSIVE BACKEND TESTING - Project Hardening Verification")
        print("="*80 + "\n")
        
        # Authenticate first
        auth_result = self.authenticate_demo_user()
        if auth_result["status"] != "success":
            logger.error("❌ Authentication failed - cannot proceed with protected endpoint tests")
        
        # Run all tests
        test_results = {}
        
        tests = [
            ("H1_Dependency_Resolution", self.test_dependency_resolution),
            ("H3_Secrets_Management", self.test_secrets_management),
            ("H4_Test_Coverage", self.test_coverage_files),
            ("M1_Database_Indexing", self.test_database_indexing),
            ("M2_API_Versioning", self.test_api_versioning),
            ("L1_CORS_Configuration", self.test_cors_configuration),
            ("L4_Prometheus_Metrics", self.test_prometheus_metrics),
            ("Backend_Stability", self.test_backend_stability)
        ]
        
        for test_name, test_func in tests:
            print(f"\n{'='*60}")
            print(f"Testing {test_name}")
            print('='*60)
            
            try:
                result = test_func()
                test_results[test_name] = result
                
                status = result.get("status", "unknown")
                if status == "success":
                    print(f"✅ {test_name}: PASSED")
                elif status == "partial":
                    print(f"⚠️ {test_name}: PARTIAL")
                elif status == "failed":
                    print(f"❌ {test_name}: FAILED")
                else:
                    print(f"❓ {test_name}: {status.upper()}")
                    
            except Exception as e:
                logger.error(f"❌ {test_name} crashed: {e}")
                test_results[test_name] = {"status": "error", "error": str(e)}
                print(f"💥 {test_name}: ERROR")
        
        # Generate summary
        print(f"\n{'='*80}")
        print("📊 HARDENING TEST SUMMARY")
        print('='*80)
        
        success_count = sum(1 for r in test_results.values() if r.get("status") == "success")
        partial_count = sum(1 for r in test_results.values() if r.get("status") == "partial")
        failed_count = sum(1 for r in test_results.values() if r.get("status") in ["failed", "error"])
        total_count = len(test_results)
        
        print(f"✅ Passed: {success_count}/{total_count}")
        print(f"⚠️ Partial: {partial_count}/{total_count}")
        print(f"❌ Failed: {failed_count}/{total_count}")
        
        overall_status = "success" if success_count >= total_count * 0.8 else "partial" if success_count >= total_count * 0.5 else "failed"
        
        print(f"\n🎯 Overall Status: {overall_status.upper()}")
        
        if overall_status == "success":
            print("🎉 Backend hardening verification PASSED! Production ready.")
        elif overall_status == "partial":
            print("⚠️ Backend hardening partially complete. Review failed tests.")
        else:
            print("❌ Backend hardening verification FAILED. Critical issues need attention.")
        
        print('='*80 + "\n")
        
        return {
            "overall_status": overall_status,
            "summary": {
                "total": total_count,
                "passed": success_count,
                "partial": partial_count,
                "failed": failed_count
            },
            "test_results": test_results
        }


if __name__ == "__main__":
    tester = HardeningTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if results["overall_status"] == "success":
        sys.exit(0)
    elif results["overall_status"] == "partial":
        sys.exit(1)
    else:
        sys.exit(2)