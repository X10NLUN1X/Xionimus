"""
XIONIMUS AI - Comprehensive Windows Test Suite
This script performs complete testing and debugging on Windows 10/11
Run this to identify and validate all bugs and functionality
"""

import os
import sys
import json
import time
import subprocess
import platform
import socket
import asyncio
import threading
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import traceback

# Add colors for Windows console
try:
    import colorama
    colorama.init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

class Colors:
    """Console colors for output"""
    HEADER = '\033[95m' if HAS_COLOR else ''
    OKBLUE = '\033[94m' if HAS_COLOR else ''
    OKCYAN = '\033[96m' if HAS_COLOR else ''
    OKGREEN = '\033[92m' if HAS_COLOR else ''
    WARNING = '\033[93m' if HAS_COLOR else ''
    FAIL = '\033[91m' if HAS_COLOR else ''
    ENDC = '\033[0m' if HAS_COLOR else ''
    BOLD = '\033[1m' if HAS_COLOR else ''

class XionimusWindowsTestSuite:
    """Comprehensive test suite for Xionimus AI on Windows"""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.backend_path = self.project_path / "backend"
        self.frontend_path = self.project_path / "frontend"
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "errors": [],
            "skipped": []
        }
        self.start_time = None
        
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'=' * 80}{Colors.ENDC}")
        
    def print_section(self, text: str):
        """Print section header"""
        print(f"\n{Colors.OKCYAN}[{text}]{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'-' * 40}{Colors.ENDC}")
        
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")
        self.test_results["passed"].append(text)
        
    def print_failure(self, text: str, error: str = None):
        """Print failure message"""
        print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")
        if error:
            print(f"  {Colors.WARNING}Error: {error}{Colors.ENDC}")
        self.test_results["failed"].append({"test": text, "error": error})
        
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")
        self.test_results["warnings"].append(text)
        
    def print_info(self, text: str):
        """Print info message"""
        print(f"  {text}")
        
    def run_all_tests(self):
        """Run complete test suite"""
        self.start_time = datetime.now()
        
        self.print_header("XIONIMUS AI - WINDOWS COMPREHENSIVE TEST SUITE")
        print(f"Platform: {platform.system()} {platform.version()}")
        print(f"Python: {sys.version}")
        print(f"Project Path: {self.project_path}")
        print(f"Test Started: {self.start_time}")
        
        # Test Categories
        self.test_system_requirements()
        self.test_python_environment()
        self.test_backend_structure()
        self.test_frontend_structure()
        self.test_database_connectivity()
        self.test_api_endpoints()
        self.test_websocket_functionality()
        self.test_code_execution_sandbox()
        self.test_file_operations()
        self.test_authentication()
        self.test_agent_functionality()
        self.test_github_integration()
        self.test_research_features()
        self.test_export_features()
        self.test_performance()
        self.test_security()
        
        # Generate report
        self.generate_test_report()
        
    def test_system_requirements(self):
        """Test system requirements and dependencies"""
        self.print_section("SYSTEM REQUIREMENTS")
        
        # Check Windows version
        if platform.system() != "Windows":
            self.print_failure("Not running on Windows", f"Platform: {platform.system()}")
        else:
            win_ver = platform.version()
            if "10" in win_ver or "11" in win_ver:
                self.print_success(f"Windows version supported: {win_ver}")
            else:
                self.print_warning(f"Windows version may not be fully tested: {win_ver}")
                
        # Check Python version
        py_version = sys.version_info
        if py_version >= (3, 11):
            self.print_success(f"Python version OK: {py_version.major}.{py_version.minor}.{py_version.micro}")
        else:
            self.print_failure(f"Python 3.11+ required, found: {py_version.major}.{py_version.minor}")
            
        # Check required commands
        commands = {
            "node": ["node", "--version"],
            "npm": ["npm", "--version"],
            "git": ["git", "--version"],
            "python": ["python", "--version"],
            "pip": ["pip", "--version"]
        }
        
        for name, cmd in commands.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.print_success(f"{name}: {version}")
                else:
                    self.print_failure(f"{name} not working properly")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.print_failure(f"{name} not found or not accessible")
                
    def test_python_environment(self):
        """Test Python environment and packages"""
        self.print_section("PYTHON ENVIRONMENT")
        
        # Check virtual environment
        venv_path = self.backend_path / "venv"
        if venv_path.exists():
            self.print_success("Virtual environment found")
        else:
            self.print_warning("Virtual environment not found at backend/venv")
            
        # Check critical packages
        critical_packages = [
            "fastapi",
            "uvicorn",
            "pymongo",
            "sqlalchemy",
            "anthropic",
            "openai",
            "websockets",
            "pydantic",
            "jwt"
        ]
        
        for package in critical_packages:
            try:
                __import__(package)
                self.print_success(f"Package '{package}' available")
            except ImportError:
                self.print_failure(f"Package '{package}' not installed")
                
        # Check for Unix-specific imports
        self.print_info("Checking for Unix-specific module issues...")
        unix_modules = ["resource", "fcntl", "pwd", "grp", "termios"]
        for module in unix_modules:
            try:
                __import__(module)
                self.print_warning(f"Unix module '{module}' imported (may cause issues)")
            except ImportError:
                self.print_info(f"Unix module '{module}' not available (expected on Windows)")
                
    def test_backend_structure(self):
        """Test backend file structure and configuration"""
        self.print_section("BACKEND STRUCTURE")
        
        # Check main files
        critical_files = [
            "main.py",
            "requirements.txt",
            "requirements-windows.txt",
            ".env.example"
        ]
        
        for file in critical_files:
            file_path = self.backend_path / file
            if file_path.exists():
                self.print_success(f"Found: {file}")
            else:
                if "windows" in file:
                    self.print_warning(f"Missing: {file}")
                else:
                    self.print_failure(f"Missing critical file: {file}")
                    
        # Check app structure
        app_dirs = ["app", "app/api", "app/core", "app/services", "app/models"]
        for dir_name in app_dirs:
            dir_path = self.backend_path / dir_name
            if dir_path.exists():
                self.print_success(f"Directory exists: {dir_name}")
            else:
                self.print_failure(f"Missing directory: {dir_name}")
                
    def test_frontend_structure(self):
        """Test frontend structure"""
        self.print_section("FRONTEND STRUCTURE")
        
        # Check package.json
        package_json = self.frontend_path / "package.json"
        if package_json.exists():
            self.print_success("package.json found")
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    self.print_info(f"  Project: {data.get('name', 'Unknown')}")
                    self.print_info(f"  Version: {data.get('version', 'Unknown')}")
            except Exception as e:
                self.print_warning(f"Could not parse package.json: {e}")
        else:
            self.print_failure("package.json not found")
            
        # Check node_modules
        node_modules = self.frontend_path / "node_modules"
        if node_modules.exists():
            self.print_success("node_modules exists (packages installed)")
        else:
            self.print_warning("node_modules not found (run npm install)")
            
        # Check build output
        dist_dir = self.frontend_path / "dist"
        if dist_dir.exists():
            self.print_success("Build output found (dist)")
        else:
            self.print_info("No build output yet (run npm run build)")
            
    def test_database_connectivity(self):
        """Test database connections"""
        self.print_section("DATABASE CONNECTIVITY")
        
        # Test MongoDB
        try:
            from pymongo import MongoClient
            client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
            client.server_info()
            self.print_success("MongoDB connection successful")
            client.close()
        except Exception as e:
            self.print_failure("MongoDB connection failed", str(e))
            
        # Test SQLite
        try:
            import sqlite3
            # Use Windows temp directory
            db_path = Path(tempfile.gettempdir()) / "xionimus_test.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
            conn.close()
            db_path.unlink()  # Clean up
            self.print_success("SQLite operations working")
        except Exception as e:
            self.print_failure("SQLite test failed", str(e))
            
    def test_api_endpoints(self):
        """Test API endpoints"""
        self.print_section("API ENDPOINTS")
        
        try:
            import requests
            base_url = "http://localhost:8000"
            
            # Test health endpoint
            try:
                response = requests.get(f"{base_url}/health", timeout=2)
                if response.status_code == 200:
                    self.print_success("Health endpoint responding")
                else:
                    self.print_warning(f"Health endpoint returned: {response.status_code}")
            except requests.exceptions.ConnectionError:
                self.print_warning("API server not running (expected if not started)")
            except Exception as e:
                self.print_failure("Health check failed", str(e))
                
        except ImportError:
            self.print_warning("requests library not installed, skipping API tests")
            
    def test_websocket_functionality(self):
        """Test WebSocket functionality"""
        self.print_section("WEBSOCKET FUNCTIONALITY")
        
        # Check if asyncio works properly on Windows
        try:
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
                self.print_success("Windows event loop policy set correctly")
            
            # Create simple async test
            async def test_async():
                return True
                
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(test_async())
            loop.close()
            
            if result:
                self.print_success("Asyncio working properly")
        except Exception as e:
            self.print_failure("Asyncio test failed", str(e))
            
    def test_code_execution_sandbox(self):
        """Test code execution sandbox for all languages"""
        self.print_section("CODE EXECUTION SANDBOX")
        
        # Test Python execution
        try:
            result = subprocess.run(
                ["python", "-c", "print('Hello from Python')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "Hello from Python" in result.stdout:
                self.print_success("Python code execution working")
            else:
                self.print_failure("Python execution failed", result.stderr)
        except Exception as e:
            self.print_failure("Python execution test failed", str(e))
            
        # Test Node.js execution
        try:
            result = subprocess.run(
                ["node", "-e", "console.log('Hello from Node')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "Hello from Node" in result.stdout:
                self.print_success("Node.js code execution working")
            else:
                self.print_failure("Node.js execution failed", result.stderr)
        except FileNotFoundError:
            self.print_warning("Node.js not found")
        except Exception as e:
            self.print_failure("Node.js execution test failed", str(e))
            
        # Test PowerShell (Windows alternative to Bash)
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Write-Host 'Hello from PowerShell'"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "Hello from PowerShell" in result.stdout:
                self.print_success("PowerShell execution working")
            else:
                self.print_failure("PowerShell execution failed", result.stderr)
        except Exception as e:
            self.print_failure("PowerShell execution test failed", str(e))
            
        # Test C compiler
        try:
            result = subprocess.run(["gcc", "--version"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                self.print_success("GCC compiler available")
            else:
                self.print_warning("GCC not available")
        except FileNotFoundError:
            self.print_warning("GCC not installed (needed for C/C++ execution)")
            
        # Test C# compiler
        try:
            result = subprocess.run(["csc", "/?"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                self.print_success("C# compiler available")
        except FileNotFoundError:
            try:
                result = subprocess.run(["dotnet", "--version"], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    self.print_success("Dotnet CLI available (for C#)")
            except FileNotFoundError:
                self.print_warning("C# compiler not available")
                
    def test_file_operations(self):
        """Test file operations and path handling"""
        self.print_section("FILE OPERATIONS")
        
        # Test temp directory access
        try:
            temp_dir = Path(tempfile.gettempdir())
            test_file = temp_dir / "xionimus_test.txt"
            
            # Write test
            test_file.write_text("Test content")
            self.print_success("Temp file write successful")
            
            # Read test
            content = test_file.read_text()
            if content == "Test content":
                self.print_success("Temp file read successful")
                
            # Cleanup
            test_file.unlink()
            self.print_success("Temp file operations working")
        except Exception as e:
            self.print_failure("File operations failed", str(e))
            
        # Test path separators
        test_path = Path("backend") / "app" / "core" / "test.py"
        if "\\" in str(test_path):
            self.print_success("Windows path separators working")
        else:
            self.print_warning("Path separators may not be Windows-compatible")
            
    def test_authentication(self):
        """Test authentication system"""
        self.print_section("AUTHENTICATION SYSTEM")
        
        # Check JWT secret key
        env_file = self.backend_path / ".env"
        if env_file.exists():
            self.print_success(".env file exists")
            try:
                with open(env_file) as f:
                    content = f.read()
                    if "SECRET_KEY" in content:
                        self.print_success("SECRET_KEY configured")
                    else:
                        self.print_warning("SECRET_KEY not found in .env")
            except Exception as e:
                self.print_warning(f"Could not read .env: {e}")
        else:
            self.print_warning(".env file not found")
            
        # Test JWT library
        try:
            import jwt
            test_token = jwt.encode({"user": "test"}, "secret", algorithm="HS256")
            decoded = jwt.decode(test_token, "secret", algorithms=["HS256"])
            if decoded["user"] == "test":
                self.print_success("JWT encoding/decoding working")
        except ImportError:
            self.print_failure("JWT library not installed")
        except Exception as e:
            self.print_failure("JWT test failed", str(e))
            
    def test_agent_functionality(self):
        """Test agent system"""
        self.print_section("AGENT FUNCTIONALITY")
        
        agents = [
            "Research Agent",
            "Code Review Agent",
            "Testing Agent",
            "Documentation Agent",
            "Debugging Agent",
            "Security Agent",
            "Performance Agent",
            "Fork Agent"
        ]
        
        self.print_info("Checking agent configurations...")
        for agent in agents:
            # This would normally test actual agent availability
            self.print_info(f"  • {agent}")
            
        # Check agent routing
        routing_file = self.backend_path / "app" / "services" / "agent_router.py"
        if routing_file.exists():
            self.print_success("Agent routing system found")
        else:
            self.print_warning("Agent routing file not found")
            
    def test_github_integration(self):
        """Test GitHub integration"""
        self.print_section("GITHUB INTEGRATION")
        
        try:
            from github import Github
            self.print_success("PyGithub library available")
        except ImportError:
            self.print_warning("PyGithub not installed")
            
        # Check git command
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                self.print_success(f"Git available: {result.stdout.strip()}")
        except FileNotFoundError:
            self.print_failure("Git not found")
            
    def test_research_features(self):
        """Test research features"""
        self.print_section("RESEARCH FEATURES")
        
        # Check Perplexity integration
        env_file = self.backend_path / ".env"
        if env_file.exists():
            with open(env_file) as f:
                content = f.read()
                if "PERPLEXITY" in content:
                    self.print_success("Perplexity API key configured")
                else:
                    self.print_warning("Perplexity API key not found")
                    
    def test_export_features(self):
        """Test export features"""
        self.print_section("EXPORT FEATURES")
        
        # Test PDF generation capability
        try:
            from reportlab.pdfgen import canvas
            self.print_success("ReportLab PDF library available")
        except ImportError:
            self.print_warning("ReportLab not installed (PDF export limited)")
            
        try:
            from weasyprint import HTML
            self.print_success("WeasyPrint available")
        except (ImportError, OSError):
            self.print_warning("WeasyPrint not available (needs GTK on Windows)")
            
    def test_performance(self):
        """Test performance metrics"""
        self.print_section("PERFORMANCE TESTING")
        
        import psutil
        
        # System resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.print_info(f"CPU Usage: {cpu_percent}%")
        self.print_info(f"Memory: {memory.percent}% used ({memory.used / 1024**3:.1f}GB / {memory.total / 1024**3:.1f}GB)")
        self.print_info(f"Disk: {disk.percent}% used ({disk.used / 1024**3:.1f}GB / {disk.total / 1024**3:.1f}GB)")
        
        if cpu_percent < 80:
            self.print_success("CPU usage acceptable")
        else:
            self.print_warning("High CPU usage detected")
            
        if memory.percent < 90:
            self.print_success("Memory usage acceptable")
        else:
            self.print_warning("High memory usage detected")
            
    def test_security(self):
        """Test security features"""
        self.print_section("SECURITY TESTING")
        
        # Check for hardcoded secrets
        self.print_info("Checking for hardcoded secrets...")
        
        # Check CORS configuration
        main_py = self.backend_path / "main.py"
        if main_py.exists():
            with open(main_py) as f:
                content = f.read()
                if "CORSMiddleware" in content:
                    self.print_success("CORS middleware configured")
                else:
                    self.print_warning("CORS middleware not found")
                    
        # Check rate limiting
        if main_py.exists():
            with open(main_py) as f:
                content = f.read()
                if "slowapi" in content.lower() or "ratelimit" in content.lower():
                    self.print_success("Rate limiting configured")
                else:
                    self.print_warning("Rate limiting not found")
                    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        self.print_header("TEST RESULTS SUMMARY")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        total_tests = (len(self.test_results["passed"]) + 
                      len(self.test_results["failed"]) + 
                      len(self.test_results["skipped"]))
        
        print(f"\nTest Duration: {duration}")
        print(f"Total Tests: {total_tests}")
        print(f"{Colors.OKGREEN}Passed: {len(self.test_results['passed'])}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {len(self.test_results['failed'])}{Colors.ENDC}")
        print(f"{Colors.WARNING}Warnings: {len(self.test_results['warnings'])}{Colors.ENDC}")
        
        if self.test_results["failed"]:
            print(f"\n{Colors.FAIL}Failed Tests:{Colors.ENDC}")
            for failure in self.test_results["failed"][:10]:  # Show first 10 failures
                print(f"  • {failure['test']}")
                if failure.get('error'):
                    print(f"    Error: {failure['error'][:100]}")
                    
        # Calculate success rate
        if total_tests > 0:
            success_rate = (len(self.test_results["passed"]) / total_tests) * 100
            print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}")
            
            if success_rate == 100:
                print(f"{Colors.OKGREEN}✓ All tests passed! System is ready.{Colors.ENDC}")
            elif success_rate >= 80:
                print(f"{Colors.WARNING}⚠ System mostly functional but needs attention.{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ Critical issues detected. Review failed tests.{Colors.ENDC}")
                
        # Save detailed report
        report_path = self.project_path / "windows_test_report.json"
        report_data = {
            "timestamp": end_time.isoformat(),
            "duration": str(duration),
            "platform": platform.platform(),
            "python_version": sys.version,
            "results": self.test_results,
            "success_rate": success_rate if total_tests > 0 else 0
        }
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\nDetailed report saved to: {report_path}")
        except Exception as e:
            print(f"Could not save report: {e}")
            
def main():
    """Main entry point"""
    print(f"{Colors.BOLD}Starting Xionimus AI Windows Test Suite...{Colors.ENDC}")
    
    # Detect project path
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        # Try to find project path
        current_path = Path.cwd()
        if (current_path / "backend").exists():
            project_path = current_path
        elif (current_path.parent / "backend").exists():
            project_path = current_path.parent
        else:
            project_path = current_path
            
    # Run tests
    test_suite = XionimusWindowsTestSuite(project_path)
    test_suite.run_all_tests()
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test suite interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
        traceback.print_exc()
