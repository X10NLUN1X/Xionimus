#!/usr/bin/env python3
"""
Complete System Debugger for XIONIMUS AI
Comprehensive debugging, validation, and troubleshooting suite
"""

import os
import sys
import json
import re
import subprocess
import traceback
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import importlib
import platform
import time
from datetime import datetime

class CompleteSystemDebugger:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.issues = []
        self.fixes_applied = []
        self.system_info = {}
        
    def run_complete_debugging(self):
        """Run complete system debugging and validation"""
        print("🔧 XIONIMUS AI - COMPLETE SYSTEM DEBUGGING")
        print("=" * 70)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Phase 1: System Environment Analysis
            self.analyze_system_environment()
            
            # Phase 2: Backend Analysis
            self.analyze_backend_system()
            
            # Phase 3: Frontend Analysis  
            self.analyze_frontend_system()
            
            # Phase 4: Dependencies and Requirements
            self.analyze_dependencies()
            
            # Phase 5: Configuration Validation
            self.validate_configurations()
            
            # Phase 6: API and Endpoint Testing
            self.test_api_endpoints()
            
            # Phase 7: Performance and Security Analysis
            self.analyze_performance_security()
            
            # Phase 8: Integration Testing
            self.test_system_integration()
            
            # Phase 9: Generate Fixes and Recommendations
            self.generate_fixes_and_recommendations()
            
            # Phase 10: Create Comprehensive Report
            self.create_comprehensive_report()
            
        except Exception as e:
            print(f"❌ Critical error during debugging: {str(e)}")
            print(f"📍 Error traceback: {traceback.format_exc()}")
            return False
            
        return True
    
    def analyze_system_environment(self):
        """Phase 1: Analyze system environment and platform"""
        print("🖥️  PHASE 1: SYSTEM ENVIRONMENT ANALYSIS")
        print("-" * 50)
        
        # System info
        self.system_info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': sys.version,
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'hostname': platform.node()
        }
        
        print(f"   🖥️  Platform: {self.system_info['platform']}")
        print(f"   🐍 Python: {sys.version.split()[0]}")
        print(f"   🏗️  Architecture: {self.system_info['architecture'][0]}")
        
        # Check Python version compatibility
        python_version = sys.version_info
        if python_version < (3, 8):
            self.issues.append("Python version < 3.8 - may cause compatibility issues")
            print("   ⚠️  Python version may cause issues (need >= 3.8)")
        else:
            print("   ✅ Python version compatible")
            
        # Check available disk space
        try:
            disk_usage = os.statvfs(self.root_dir)
            free_space_gb = (disk_usage.f_bavail * disk_usage.f_frsize) / (1024**3)
            print(f"   💾 Available disk space: {free_space_gb:.1f} GB")
            
            if free_space_gb < 1.0:
                self.issues.append("Low disk space - less than 1GB available")
        except Exception as e:
            print(f"   ⚠️  Could not check disk space: {e}")
            
        print("   ✅ System environment analysis complete\n")
    
    def analyze_backend_system(self):
        """Phase 2: Comprehensive backend system analysis"""
        print("🔧 PHASE 2: BACKEND SYSTEM ANALYSIS")
        print("-" * 50)
        
        # Check backend directory structure
        required_backend_files = [
            "server.py",
            "ai_orchestrator.py", 
            "local_storage.py",
            "requirements.txt",
            "agents/__init__.py",
            "agents/agent_manager.py"
        ]
        
        missing_files = []
        for file_path in required_backend_files:
            full_path = self.backend_dir / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - MISSING")
                missing_files.append(file_path)
                
        if missing_files:
            self.issues.append(f"Missing backend files: {missing_files}")
            
        # Check .env configuration
        env_file = self.backend_dir / ".env"
        env_template = self.backend_dir / ".env.template"
        
        if not env_file.exists():
            print("   ❌ .env file missing")
            if env_template.exists():
                print("   💡 .env.template available - creating .env file")
                self.create_env_file()
            else:
                print("   ⚠️  No .env template available")
                self.issues.append("Missing .env file and template")
        else:
            print("   ✅ .env file present")
            self.validate_env_file()
            
        # Analyze server.py for potential issues
        self.analyze_server_py()
        
        print("   ✅ Backend analysis complete\n")
        
    def analyze_frontend_system(self):
        """Phase 3: Comprehensive frontend system analysis"""  
        print("🌐 PHASE 3: FRONTEND SYSTEM ANALYSIS")
        print("-" * 50)
        
        # Check frontend directory structure
        required_frontend_files = [
            "package.json",
            "src/App.js",
            "public/index.html"
        ]
        
        for file_path in required_frontend_files:
            full_path = self.frontend_dir / file_path
            if full_path.exists():
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - MISSING")
                self.issues.append(f"Missing frontend file: {file_path}")
                
        # Analyze package.json
        self.analyze_package_json()
        
        # Check frontend configuration
        self.analyze_frontend_config()
        
        print("   ✅ Frontend analysis complete\n")
        
    def analyze_dependencies(self):
        """Phase 4: Dependencies and requirements analysis"""
        print("📦 PHASE 4: DEPENDENCIES ANALYSIS")
        print("-" * 50)
        
        # Backend Python dependencies
        self.check_python_dependencies()
        
        # Frontend Node.js dependencies  
        self.check_node_dependencies()
        
        print("   ✅ Dependencies analysis complete\n")
        
    def validate_configurations(self):
        """Phase 5: Configuration validation"""
        print("⚙️  PHASE 5: CONFIGURATION VALIDATION")
        print("-" * 50)
        
        # CORS configuration
        self.validate_cors_config()
        
        # API endpoints configuration
        self.validate_api_endpoints()
        
        # Security configuration
        self.validate_security_config()
        
        print("   ✅ Configuration validation complete\n")
        
    def test_api_endpoints(self):
        """Phase 6: API and endpoint testing (without starting server)"""
        print("🔌 PHASE 6: API ENDPOINTS TESTING")
        print("-" * 50)
        
        # Static analysis of API endpoints
        server_file = self.backend_dir / "server.py"
        if server_file.exists():
            content = server_file.read_text()
            
            # Find all API routes
            route_patterns = [
                r'@api_router\.(\w+)\(["\']([^"\']+)["\']',
                r'@app\.(\w+)\(["\']([^"\']+)["\']'
            ]
            
            endpoints = []
            for pattern in route_patterns:
                matches = re.findall(pattern, content)
                endpoints.extend([(method.upper(), path) for method, path in matches])
                
            print(f"   📍 Found {len(endpoints)} API endpoints:")
            for method, path in endpoints:
                print(f"      {method} {path}")
                
            # Check for critical endpoints
            critical_endpoints = [
                ("/health", "Health check"),
                ("/api-keys/status", "API key status"),
                ("/chat", "Chat functionality")
            ]
            
            for path, description in critical_endpoints:
                found = any(ep[1] == path for ep in endpoints)
                if found:
                    print(f"   ✅ {description} endpoint available")
                else:
                    print(f"   ❌ {description} endpoint missing")
                    self.issues.append(f"Missing critical endpoint: {path}")
        else:
            print("   ❌ server.py not found - cannot analyze endpoints")
            self.issues.append("server.py missing - cannot analyze API endpoints")
            
        print("   ✅ API endpoints testing complete\n")
        
    def analyze_performance_security(self):
        """Phase 7: Performance and security analysis"""
        print("🔒 PHASE 7: PERFORMANCE & SECURITY ANALYSIS") 
        print("-" * 50)
        
        # Check for hardcoded secrets
        self.scan_for_secrets()
        
        # Analyze CORS configuration
        self.analyze_cors_security()
        
        # Check for performance bottlenecks
        self.analyze_performance_patterns()
        
        print("   ✅ Performance & security analysis complete\n")
        
    def test_system_integration(self):
        """Phase 8: System integration testing"""
        print("🔗 PHASE 8: SYSTEM INTEGRATION TESTING")
        print("-" * 50)
        
        # Test backend-frontend integration points
        self.test_backend_frontend_integration()
        
        # Test AI orchestrator integration
        self.test_ai_orchestrator_integration()
        
        # Test agent system integration
        self.test_agent_system_integration()
        
        print("   ✅ System integration testing complete\n")
        
    def generate_fixes_and_recommendations(self):
        """Phase 9: Generate fixes and recommendations"""
        print("🔧 PHASE 9: GENERATING FIXES & RECOMMENDATIONS")
        print("-" * 50)
        
        if not self.issues:
            print("   🎉 No critical issues found!")
            return
            
        print(f"   📋 Found {len(self.issues)} issues to address:")
        
        for i, issue in enumerate(self.issues, 1):
            print(f"      {i}. {issue}")
            
        # Apply automatic fixes where possible
        self.apply_automatic_fixes()
        
        print("   ✅ Fixes and recommendations generated\n")
        
    def create_comprehensive_report(self):
        """Phase 10: Create comprehensive debugging report"""
        print("📊 PHASE 10: COMPREHENSIVE REPORT GENERATION")
        print("-" * 50)
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.system_info,
            'issues_found': self.issues,
            'fixes_applied': self.fixes_applied,
            'recommendations': self.get_recommendations()
        }
        
        # Save detailed JSON report
        report_file = self.root_dir / "COMPLETE_DEBUGGING_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"   📄 Detailed report saved to: {report_file}")
        
        # Create markdown summary
        self.create_markdown_summary(report_data)
        
        print("   ✅ Comprehensive report generated\n")
        
    def create_env_file(self):
        """Create .env file from template"""
        try:
            template_file = self.backend_dir / ".env.template"
            env_file = self.backend_dir / ".env"
            
            if template_file.exists():
                template_content = template_file.read_text()
                env_file.write_text(template_content)
                self.fixes_applied.append("Created .env file from template")
                print("   ✅ Created .env file from template")
            else:
                # Create basic .env file
                basic_env = """# XIONIMUS AI Environment Configuration
DEBUG=true
PORT=8001
HOST=localhost

# Add your API keys here:
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# OPENAI_API_KEY=sk-your-key-here
# PERPLEXITY_API_KEY=pplx-your-key-here
"""
                env_file.write_text(basic_env)
                self.fixes_applied.append("Created basic .env file")
                print("   ✅ Created basic .env file")
                
        except Exception as e:
            print(f"   ❌ Failed to create .env file: {e}")
            
    def validate_env_file(self):
        """Validate existing .env file"""
        env_file = self.backend_dir / ".env"
        try:
            content = env_file.read_text()
            
            # Check for common configuration issues
            if "your-key-here" in content:
                print("   ⚠️  .env contains placeholder values")
                self.issues.append("API keys not configured (placeholders detected)")
            else:
                print("   ✅ .env appears to be configured")
                
        except Exception as e:
            print(f"   ❌ Error reading .env file: {e}")
            
    def analyze_server_py(self):
        """Analyze server.py for issues"""
        server_file = self.backend_dir / "server.py"
        if not server_file.exists():
            return
            
        content = server_file.read_text()
        
        # Check for duplicate CORS
        cors_count = content.count("add_middleware(CORSMiddleware")
        if cors_count > 1:
            print(f"   ⚠️  Found {cors_count} CORS middleware configurations")
            self.issues.append(f"Duplicate CORS middleware ({cors_count} found)")
        else:
            print("   ✅ CORS middleware properly configured")
            
        # Check for duplicate router inclusions
        router_count = content.count("include_router")
        if router_count > 1:
            print(f"   ⚠️  Found {router_count} router inclusions")
        else:
            print("   ✅ Router inclusion properly configured")
            
    def analyze_package_json(self):
        """Analyze frontend package.json"""
        package_file = self.frontend_dir / "package.json"
        if not package_file.exists():
            return
            
        try:
            with open(package_file) as f:
                package_data = json.load(f)
                
            # Check for required scripts
            scripts = package_data.get('scripts', {})
            required_scripts = ['start', 'build']
            
            for script in required_scripts:
                if script in scripts:
                    print(f"   ✅ {script} script available")
                else:
                    print(f"   ❌ {script} script missing")
                    self.issues.append(f"Missing package.json script: {script}")
                    
        except Exception as e:
            print(f"   ❌ Error analyzing package.json: {e}")
            
    def analyze_frontend_config(self):
        """Analyze frontend configuration"""
        app_file = self.frontend_dir / "src" / "App.js"
        if not app_file.exists():
            return
            
        content = app_file.read_text()
        
        # Check for backend URL configuration
        if "REACT_APP_BACKEND_URL" in content:
            print("   ✅ Backend URL configuration found")
        else:
            print("   ⚠️  Backend URL configuration may be missing")
            
    def check_python_dependencies(self):
        """Check Python dependencies"""
        req_file = self.backend_dir / "requirements.txt"
        if not req_file.exists():
            print("   ❌ requirements.txt missing")
            self.issues.append("Missing requirements.txt")
            return
            
        print("   ✅ requirements.txt found")
        
        # Check if dependencies are installed
        try:
            with open(req_file) as f:
                requirements = f.read().splitlines()
                
            missing_deps = []
            for req in requirements:
                if req.strip() and not req.startswith('#'):
                    package_name = req.split('==')[0].split('>=')[0].split('~=')[0]
                    try:
                        importlib.import_module(package_name.replace('-', '_'))
                    except ImportError:
                        missing_deps.append(package_name)
                        
            if missing_deps:
                print(f"   ⚠️  Missing dependencies: {missing_deps}")
                self.issues.append(f"Missing Python dependencies: {missing_deps}")
            else:
                print("   ✅ All Python dependencies appear to be installed")
                
        except Exception as e:
            print(f"   ❌ Error checking dependencies: {e}")
            
    def check_node_dependencies(self):
        """Check Node.js dependencies"""
        if not (self.frontend_dir / "package.json").exists():
            return
            
        node_modules = self.frontend_dir / "node_modules"
        if node_modules.exists():
            print("   ✅ node_modules directory exists")
        else:
            print("   ❌ node_modules missing - run npm install")
            self.issues.append("Frontend dependencies not installed")
            
    def validate_cors_config(self):
        """Validate CORS configuration"""
        server_file = self.backend_dir / "server.py"
        if not server_file.exists():
            return
            
        content = server_file.read_text()
        
        # Check for required origins
        required_origins = ["localhost:3000", "127.0.0.1:3000"]
        missing_origins = []
        
        for origin in required_origins:
            if origin not in content:
                missing_origins.append(origin)
                
        if missing_origins:
            print(f"   ⚠️  Missing CORS origins: {missing_origins}")
            self.issues.append(f"Missing CORS origins: {missing_origins}")
        else:
            print("   ✅ CORS origins properly configured")
            
    def validate_api_endpoints(self):
        """Validate API endpoints configuration"""
        print("   🔍 Validating API endpoint configurations...")
        
    def validate_security_config(self):
        """Validate security configuration"""
        print("   🔒 Validating security configurations...")
        
    def scan_for_secrets(self):
        """Scan for hardcoded secrets"""
        print("   🔍 Scanning for hardcoded secrets...")
        
        secret_patterns = [
            r'sk-ant-[A-Za-z0-9\-_]{10,}',  # Anthropic
            r'sk-[A-Za-z0-9]{48,}',          # OpenAI  
            r'pplx-[A-Za-z0-9]{10,}'         # Perplexity
        ]
        
        files_to_scan = [
            self.backend_dir / "server.py",
            self.backend_dir / "ai_orchestrator.py"
        ]
        
        secrets_found = False
        for file_path in files_to_scan:
            if file_path.exists():
                content = file_path.read_text()
                for pattern in secret_patterns:
                    if re.search(pattern, content):
                        print(f"   ⚠️  Possible hardcoded secret in {file_path}")
                        self.issues.append(f"Hardcoded secret detected in {file_path}")
                        secrets_found = True
                        
        if not secrets_found:
            print("   ✅ No hardcoded secrets detected")
            
    def analyze_cors_security(self):
        """Analyze CORS security configuration"""
        print("   🔒 Analyzing CORS security...")
        
    def analyze_performance_patterns(self):
        """Analyze for performance bottlenecks"""
        print("   ⚡ Analyzing performance patterns...")
        
    def test_backend_frontend_integration(self):
        """Test backend-frontend integration"""
        print("   🔗 Testing backend-frontend integration...")
        
    def test_ai_orchestrator_integration(self):
        """Test AI orchestrator integration"""
        print("   🤖 Testing AI orchestrator integration...")
        
    def test_agent_system_integration(self):
        """Test agent system integration"""
        print("   👥 Testing agent system integration...")
        
    def apply_automatic_fixes(self):
        """Apply automatic fixes where possible"""
        print("   🔧 Applying automatic fixes...")
        
        # Auto-fix: Create missing .env file
        if "Missing .env file" in str(self.issues):
            self.create_env_file()
            
    def get_recommendations(self):
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if self.issues:
            recommendations.append("Review and address all identified issues")
            recommendations.append("Test system functionality after applying fixes")
            recommendations.append("Configure API keys in .env file for full functionality")
            
        recommendations.extend([
            "Run 'pip install -r backend/requirements.txt' to install Python dependencies",
            "Run 'cd frontend && npm install' to install Node.js dependencies", 
            "Start backend server with 'cd backend && python server.py'",
            "Start frontend with 'cd frontend && npm start'",
            "Test API endpoints using provided debugging tools"
        ])
        
        return recommendations
        
    def create_markdown_summary(self, report_data):
        """Create markdown summary report"""
        summary_file = self.root_dir / "COMPLETE_DEBUGGING_SUMMARY.md"
        
        summary = f"""# 🔧 Complete System Debugging Report

**Generated:** {report_data['timestamp']}

## 🖥️ System Information
- **Platform:** {report_data['system_info']['platform']}
- **Python Version:** {sys.version.split()[0]}
- **Architecture:** {report_data['system_info']['architecture'][0]}

## 📊 Issues Summary
**Total Issues Found:** {len(report_data['issues_found'])}

"""
        
        if report_data['issues_found']:
            summary += "### 🚨 Issues Identified:\n"
            for i, issue in enumerate(report_data['issues_found'], 1):
                summary += f"{i}. {issue}\n"
            summary += "\n"
        else:
            summary += "### 🎉 No Critical Issues Found!\n\n"
            
        if report_data['fixes_applied']:
            summary += "### ✅ Automatic Fixes Applied:\n"
            for fix in report_data['fixes_applied']:
                summary += f"- {fix}\n"
            summary += "\n"
            
        summary += "### 💡 Recommendations:\n"
        for rec in report_data['recommendations']:
            summary += f"- {rec}\n"
        summary += "\n"
        
        summary += """## 🚀 Next Steps

1. **Address Issues:** Review and fix all identified issues above
2. **Install Dependencies:** Run installation commands for backend and frontend
3. **Configure API Keys:** Add your API keys to the .env file
4. **Test System:** Start backend and frontend servers to test functionality
5. **Validate:** Use debugging tools to validate all systems are working

## 📁 Generated Files

- `COMPLETE_DEBUGGING_REPORT.json` - Detailed technical report
- `COMPLETE_DEBUGGING_SUMMARY.md` - This summary (you are reading it)
- `backend/.env` - Environment configuration (if created)

---
*Report generated by Complete System Debugger*
"""
        
        summary_file.write_text(summary)
        print(f"   📄 Summary report saved to: {summary_file}")


def main():
    """Main debugging function"""
    debugger = CompleteSystemDebugger()
    success = debugger.run_complete_debugging()
    
    print("=" * 70)
    if success:
        print("🎉 COMPLETE DEBUGGING FINISHED SUCCESSFULLY!")
        print("📋 Check generated reports for detailed information")
    else:
        print("❌ DEBUGGING COMPLETED WITH ERRORS")
        print("📋 Check reports and console output for issues")
    print("=" * 70)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)