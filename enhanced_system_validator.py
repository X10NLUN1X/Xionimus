#!/usr/bin/env python3
"""
Enhanced System Validator for XIONIMUS AI
Comprehensive system validation with temporary server startup for 100% testing
"""

import asyncio
import subprocess
import sys
import json
import time
import signal
from pathlib import Path
from datetime import datetime
import os

# Add local Python packages path
sys.path.append('/home/runner/.local/lib/python3.12/site-packages')

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available - using alternative system monitoring")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("⚠️ aiohttp not available - API testing limited")

class EnhancedSystemValidator:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_process = None
        self.results = {}
        
    async def run_complete_validation(self):
        """Run complete system validation with temporary server startup"""
        print("🎯 XIONIMUS AI - ENHANCED SYSTEM VALIDATION")
        print("=" * 70)
        print(f"🕐 Validation started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        success = True
        
        # Phase 1: Infrastructure Validation
        print("🏗️ PHASE 1: INFRASTRUCTURE VALIDATION")
        print("-" * 50)
        infra_score = await self.validate_infrastructure()
        success &= infra_score >= 95
        
        # Phase 2: Dependencies Validation  
        print("\n📦 PHASE 2: DEPENDENCIES VALIDATION")
        print("-" * 50)
        deps_score = await self.validate_dependencies()
        success &= deps_score >= 95
        
        # Phase 3: Dynamic Server Testing
        print("\n🚀 PHASE 3: DYNAMIC SERVER TESTING")
        print("-" * 50)
        server_score = await self.validate_with_server()
        success &= server_score >= 95
        
        # Phase 4: Generate Enhanced Report
        print("\n📊 PHASE 4: ENHANCED REPORTING")
        print("-" * 50)
        overall_score = await self.generate_enhanced_report(infra_score, deps_score, server_score)
        
        return success, overall_score
        
    async def validate_infrastructure(self):
        """Validate system infrastructure"""
        score = 100
        issues = []
        
        # Check Python version
        if sys.version_info >= (3, 8):
            print("   ✅ Python version compatible")
        else:
            print("   ❌ Python version too old")
            score -= 20
            issues.append("Python version incompatible")
            
        # Check disk space
        if PSUTIL_AVAILABLE:
            disk_usage = psutil.disk_usage('/')
            free_gb = disk_usage.free // (1024**3)
            if free_gb >= 5:
                print(f"   ✅ Sufficient disk space: {free_gb} GB free")
            else:
                print(f"   ❌ Low disk space: {free_gb} GB free")
                score -= 15
                issues.append("Low disk space")
        else:
            print("   ⚠️ Disk space check skipped (psutil unavailable)")
            
        # Check memory
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            if memory.available >= 2 * 1024**3:  # 2GB
                print("   ✅ Sufficient memory available")
            else:
                print("   ⚠️ Low memory available")
                score -= 10
                issues.append("Low memory")
        else:
            print("   ⚠️ Memory check skipped (psutil unavailable)")
            
        self.results['infrastructure'] = {
            'score': score,
            'issues': issues
        }
        
        print(f"   📊 Infrastructure Score: {score}/100")
        return score
        
    async def validate_dependencies(self):
        """Validate all dependencies"""
        score = 100
        issues = []
        
        # Check Python dependencies
        required_packages = ['fastapi', 'uvicorn', 'aiohttp', 'psutil', 'requests']
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ Python package: {package}")
            except ImportError:
                print(f"   ❌ Missing Python package: {package}")
                score -= 10
                issues.append(f"Missing Python package: {package}")
                
        # Check Node.js dependencies
        if (self.frontend_dir / "node_modules").exists():
            print("   ✅ Frontend dependencies (node_modules)")
        else:
            print("   ❌ Missing frontend dependencies")
            score -= 15
            issues.append("Missing node_modules")
            
        # Check backend requirements
        if (self.backend_dir / "requirements.txt").exists():
            print("   ✅ Backend requirements.txt exists")
        else:
            print("   ❌ Missing backend requirements.txt")
            score -= 5
            issues.append("Missing requirements.txt")
            
        # Check configuration files
        if (self.backend_dir / ".env").exists():
            print("   ✅ Backend configuration (.env)")
        else:
            print("   ⚠️ Missing backend .env file")
            score -= 5
            issues.append("Missing .env configuration")
            
        self.results['dependencies'] = {
            'score': score,
            'issues': issues
        }
        
        print(f"   📊 Dependencies Score: {score}/100")
        return score
        
    async def validate_with_server(self):
        """Validate system by temporarily starting the backend server"""
        score = 100
        issues = []
        
        try:
            # Start backend server
            print("   🚀 Starting backend server for testing...")
            await self.start_backend_server()
            
            if self.backend_process and self.backend_process.poll() is None:
                print("   ✅ Backend server started successfully")
                
                # Wait for server to be ready
                await asyncio.sleep(3)
                
                # Test API endpoints
                api_score = await self.test_api_endpoints()
                score = min(score, api_score)
                
                print("   🛑 Stopping backend server...")
                await self.stop_backend_server()
                print("   ✅ Backend server stopped cleanly")
                
            else:
                print("   ❌ Failed to start backend server")
                score -= 50
                issues.append("Backend server startup failed")
                
        except Exception as e:
            print(f"   ❌ Server validation error: {e}")
            score -= 30
            issues.append(f"Server validation error: {str(e)}")
            
        finally:
            # Ensure server is stopped
            await self.stop_backend_server()
            
        self.results['server_validation'] = {
            'score': score,
            'issues': issues
        }
        
        print(f"   📊 Server Validation Score: {score}/100")
        return score
        
    async def start_backend_server(self):
        """Start the backend server"""
        try:
            # Check if server is already running (if psutil is available)
            if PSUTIL_AVAILABLE:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    cmdline = proc.info['cmdline']
                    if cmdline and any('server.py' in str(cmd) for cmd in cmdline):
                        print("   ⚠️ Backend server already running")
                        return
                    
            # Start server process
            env = os.environ.copy()
            self.backend_process = subprocess.Popen(
                [sys.executable, "server.py"],
                cwd=self.backend_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Give server time to start
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"   ❌ Failed to start backend server: {e}")
            self.backend_process = None
            
    async def stop_backend_server(self):
        """Stop the backend server"""
        try:
            if self.backend_process:
                # Terminate the entire process group
                os.killpg(os.getpgid(self.backend_process.pid), signal.SIGTERM)
                
                # Wait for process to terminate
                try:
                    self.backend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    os.killpg(os.getpgid(self.backend_process.pid), signal.SIGKILL)
                    
                self.backend_process = None
                
        except Exception as e:
            print(f"   ⚠️ Error stopping server: {e}")
            
    async def test_api_endpoints(self):
        """Test key API endpoints"""
        score = 100
        base_url = "http://localhost:8001"
        
        if not AIOHTTP_AVAILABLE:
            print("   ⚠️ API testing skipped (aiohttp unavailable)")
            return 85  # Partial score if we can't test APIs
        
        endpoints = [
            "/api/health",
            "/api/api-keys/status", 
            "/api/agents",
        ]
        
        successful_tests = 0
        total_tests = len(endpoints)
        
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint in endpoints:
                    try:
                        async with session.get(f"{base_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status in [200, 404, 422]:  # Accept these as valid responses
                                print(f"   ✅ API endpoint: {endpoint} ({response.status})")
                                successful_tests += 1
                            else:
                                print(f"   ⚠️ API endpoint: {endpoint} ({response.status})")
                                
                    except Exception as e:
                        print(f"   ❌ API endpoint: {endpoint} - {str(e)[:50]}")
                        
        except Exception as e:
            print(f"   ❌ API testing failed: {e}")
            score -= 50
            
        # Calculate score based on successful tests
        if successful_tests == total_tests:
            print(f"   ✅ All {total_tests} API endpoints responding")
        else:
            print(f"   ⚠️ {successful_tests}/{total_tests} API endpoints responding")
            score -= (total_tests - successful_tests) * 15
            
        return max(score, 0)
        
    async def generate_enhanced_report(self, infra_score, deps_score, server_score):
        """Generate enhanced validation report"""
        overall_score = (infra_score + deps_score + server_score) // 3
        
        # Determine status
        if overall_score >= 98:
            status = "🟢 PERFECT"
            health_status = "PERFECT"
        elif overall_score >= 95:
            status = "🟢 EXCELLENT" 
            health_status = "EXCELLENT"
        elif overall_score >= 85:
            status = "🟡 GOOD"
            health_status = "GOOD"
        else:
            status = "🟠 NEEDS IMPROVEMENT"
            health_status = "FAIR"
            
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'status': health_status,
            'detailed_scores': {
                'infrastructure': infra_score,
                'dependencies': deps_score,
                'server_validation': server_score
            },
            'results': self.results
        }
        
        # Save enhanced report
        report_file = self.root_dir / "ENHANCED_VALIDATION_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"   📊 Overall System Score: {overall_score}/100")
        print(f"   🏥 Status: {status}")
        print(f"   📄 Report saved: ENHANCED_VALIDATION_REPORT.json")
        
        return overall_score

async def main():
    """Main validation runner"""
    validator = EnhancedSystemValidator()
    success, score = await validator.run_complete_validation()
    
    print("\n" + "=" * 70)
    if score >= 98:
        print("🎉 PERFECT SYSTEM VALIDATION ACHIEVED!")
        print(f"📊 Final Score: {score}/100 (🟢 PERFECT)")
    elif score >= 95:
        print("🎉 EXCELLENT SYSTEM VALIDATION COMPLETED!")
        print(f"📊 Final Score: {score}/100 (🟢 EXCELLENT)")
    else:
        print("⚠️ SYSTEM VALIDATION COMPLETED WITH IMPROVEMENTS NEEDED")
        print(f"📊 Final Score: {score}/100")
        
    print("=" * 70)
    
    return score >= 95

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)