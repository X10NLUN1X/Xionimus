#!/usr/bin/env python3
"""
System Health Monitor for XIONIMUS AI
Real-time monitoring and diagnostics dashboard
"""

import sys
sys.path.append('/home/runner/.local/lib/python3.12/site-packages')

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available - system monitoring features limited")

import os
import json
import time
from pathlib import Path
from datetime import datetime
import subprocess

class SystemHealthMonitor:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        
    def run_health_monitoring(self):
        """Run comprehensive system health monitoring"""
        print("🏥 XIONIMUS AI - SYSTEM HEALTH MONITORING")
        print("=" * 60)
        print(f"🕐 Monitoring started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # System Resources
        self.monitor_system_resources()
        
        # Process Monitoring
        self.monitor_processes()
        
        # Disk Space
        self.monitor_disk_space()
        
        # Network Status
        self.monitor_network_status()
        
        # Dependencies Status
        self.monitor_dependencies()
        
        # Configuration Status
        self.monitor_configurations()
        
        # Generate Health Score
        self.generate_health_score()
        
    def monitor_system_resources(self):
        """Monitor system resources usage"""
        print("💾 SYSTEM RESOURCES")
        print("-" * 30)
        
        if not PSUTIL_AVAILABLE:
            print("   ⚠️  System monitoring requires psutil")
            print("   💡 Install with: pip install psutil")
            return
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        print(f"   🖥️  CPU Usage: {cpu_percent:.1f}% ({cpu_count} cores)")
        
        if cpu_percent < 50:
            print("   ✅ CPU usage is normal")
        elif cpu_percent < 80:
            print("   ⚠️  CPU usage is elevated")  
        else:
            print("   ❌ CPU usage is high")
            
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        print(f"   🧠 Memory Usage: {memory_percent:.1f}% ({memory_available_gb:.1f}GB available)")
        
        if memory_percent < 70:
            print("   ✅ Memory usage is normal")
        elif memory_percent < 85:
            print("   ⚠️  Memory usage is elevated")
        else:
            print("   ❌ Memory usage is high")
            
        print()
        
    def monitor_processes(self):
        """Monitor XIONIMUS AI related processes"""
        print("🔄 PROCESS MONITORING")  
        print("-" * 30)
        
        if not PSUTIL_AVAILABLE:
            print("   ⚠️  psutil not available - using basic process monitoring")
            self.monitor_processes_basic()
            return
        
        # Look for backend server process
        backend_running = False
        frontend_running = False
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    if 'server.py' in cmdline or 'uvicorn' in cmdline:
                        print(f"   ✅ Backend server running (PID: {proc.info['pid']})")
                        backend_running = True
                        
                        # Get process stats
                        p = psutil.Process(proc.info['pid'])
                        cpu = p.cpu_percent()
                        memory = p.memory_info().rss / (1024**2)  # MB
                        print(f"      📊 CPU: {cpu:.1f}%, Memory: {memory:.1f}MB")
                        
                    if 'npm' in cmdline and 'start' in cmdline:
                        print(f"   ✅ Frontend running (PID: {proc.info['pid']})")
                        frontend_running = True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"   ⚠️  Error monitoring processes: {e}")
            self.monitor_processes_basic()
            return
                
        if not backend_running:
            print("   ❌ Backend server not running")
            
        if not frontend_running:
            print("   ❌ Frontend not running")
            
        print()
        
    def monitor_processes_basic(self):
        """Fallback process monitoring without psutil"""
        print("   🔍 Using basic process monitoring...")
        
        try:
            # Check for Python processes that might be our backend
            result = subprocess.run(['pgrep', '-f', 'server.py'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        print(f"   ✅ Backend server process found (PID: {pid})")
            else:
                print("   ❌ Backend server not running")
                
            # Check for Node.js processes
            result = subprocess.run(['pgrep', '-f', 'npm.*start'], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        print(f"   ✅ Frontend process found (PID: {pid})")
            else:
                print("   ❌ Frontend not running")
                
        except Exception as e:
            print(f"   ⚠️  Basic process monitoring error: {e}")
        
    def monitor_disk_space(self):
        """Monitor disk space usage"""
        print("💿 DISK SPACE MONITORING")
        print("-" * 30)
        
        if not PSUTIL_AVAILABLE:
            print("   ⚠️  Disk monitoring requires psutil")
            print("   💡 Using basic disk space check...")
            try:
                result = subprocess.run(['df', '-h', str(self.root_dir)], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 4:
                            print(f"   💾 Disk Usage: {parts[4]} used")
                            print(f"   🆓 Available: {parts[3]}")
                else:
                    print("   ⚠️  Cannot check disk space")
            except Exception as e:
                print(f"   ❌ Disk space check failed: {e}")
            return
        
        # Get disk usage for current directory
        disk_usage = psutil.disk_usage(self.root_dir)
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        used_percent = (used_gb / total_gb) * 100
        
        print(f"   💾 Total Space: {total_gb:.1f}GB")
        print(f"   📊 Used: {used_gb:.1f}GB ({used_percent:.1f}%)")
        print(f"   🆓 Free: {free_gb:.1f}GB")
        
        if free_gb > 5.0:
            print("   ✅ Sufficient disk space")
        elif free_gb > 1.0:
            print("   ⚠️  Disk space getting low")
        else:
            print("   ❌ Critical: Low disk space")
            
        # Check specific directories
        if (self.backend_dir / "local_data").exists():
            try:
                local_data_size = sum(f.stat().st_size for f in (self.backend_dir / "local_data").rglob('*') if f.is_file())
                local_data_mb = local_data_size / (1024**2)
                print(f"   📂 Local data storage: {local_data_mb:.1f}MB")
            except Exception as e:
                print(f"   ⚠️  Could not check local data size: {e}")
                
        print()
        
    def monitor_network_status(self):
        """Monitor network connectivity"""
        print("🌐 NETWORK STATUS")
        print("-" * 30)
        
        if not PSUTIL_AVAILABLE:
            print("   ⚠️  Network monitoring requires psutil")
            print("   🔍 Using basic network check...")
            
            # Basic port checks using netstat
            try:
                result = subprocess.run(['netstat', '-ln'], capture_output=True, text=True)
                if result.returncode == 0:
                    output = result.stdout
                    backend_port_used = ':8001' in output
                    frontend_port_used = ':3000' in output
                    print(f"   🔌 Port 8001 (Backend): {'In use' if backend_port_used else 'Available'}")
                    print(f"   🔌 Port 3000 (Frontend): {'In use' if frontend_port_used else 'Available'}")
                else:
                    print("   ⚠️  Cannot check port usage")
            except Exception as e:
                print(f"   ❌ Port check failed: {e}")
        else:
            # Check network interfaces
            network_stats = psutil.net_if_stats()
            active_interfaces = [name for name, stats in network_stats.items() if stats.isup]
            print(f"   🔗 Active network interfaces: {len(active_interfaces)}")
            
            # Check if ports are in use
            connections = psutil.net_connections(kind='inet')
            
            backend_port_used = any(conn.laddr.port == 8001 for conn in connections if conn.laddr)
            frontend_port_used = any(conn.laddr.port == 3000 for conn in connections if conn.laddr)
            
            print(f"   🔌 Port 8001 (Backend): {'In use' if backend_port_used else 'Available'}")
            print(f"   🔌 Port 3000 (Frontend): {'In use' if frontend_port_used else 'Available'}")
        
        # Basic connectivity test
        try:
            import urllib.request
            urllib.request.urlopen('https://www.google.com', timeout=5)
            print("   ✅ Internet connectivity available")
        except:
            print("   ❌ No internet connectivity")
            
        print()
        
    def monitor_dependencies(self):
        """Monitor dependencies status"""
        print("📦 DEPENDENCIES STATUS")
        print("-" * 30)
        
        # Python dependencies
        req_file = self.backend_dir / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file) as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    
                print(f"   🐍 Python requirements: {len(requirements)} packages")
                
                # Check a few critical packages
                critical_packages = ['fastapi', 'uvicorn', 'openai', 'anthropic']
                missing_critical = []
                
                for package in critical_packages:
                    try:
                        __import__(package.replace('-', '_'))
                    except ImportError:
                        missing_critical.append(package)
                        
                if not missing_critical:
                    print("   ✅ Critical Python packages installed")
                else:
                    print(f"   ❌ Missing critical packages: {missing_critical}")
                    
            except Exception as e:
                print(f"   ❌ Error checking Python dependencies: {e}")
        else:
            print("   ❌ requirements.txt not found")
            
        # Node.js dependencies
        package_json = self.frontend_dir / "package.json"
        node_modules = self.frontend_dir / "node_modules"
        
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    dependencies = package_data.get('dependencies', {})
                    dev_dependencies = package_data.get('devDependencies', {})
                    total_deps = len(dependencies) + len(dev_dependencies)
                    print(f"   📦 Node.js packages: {total_deps} defined")
                    
                if node_modules.exists():
                    installed_packages = len(list(node_modules.iterdir()))
                    print(f"   ✅ Node.js packages installed: {installed_packages}")
                else:
                    print("   ❌ node_modules directory missing")
                    
            except Exception as e:
                print(f"   ❌ Error checking Node.js dependencies: {e}")
        else:
            print("   ❌ package.json not found")
            
        print()
        
    def monitor_configurations(self):
        """Monitor configuration files status"""
        print("⚙️  CONFIGURATION STATUS")
        print("-" * 30)
        
        # Backend configuration
        env_file = self.backend_dir / ".env"
        env_template = self.backend_dir / ".env.template"
        
        if env_file.exists():
            print("   ✅ .env file exists")
            try:
                with open(env_file) as f:
                    env_content = f.read()
                    
                # Check for configured API keys
                api_keys_configured = 0
                if 'ANTHROPIC_API_KEY=' in env_content and 'sk-ant-' in env_content:
                    api_keys_configured += 1
                if 'OPENAI_API_KEY=' in env_content and ('sk-' in env_content and 'sk-ant-' not in env_content):
                    api_keys_configured += 1
                if 'PERPLEXITY_API_KEY=' in env_content and 'pplx-' in env_content:
                    api_keys_configured += 1
                    
                print(f"   🔑 API keys configured: {api_keys_configured}/3")
                
                if api_keys_configured == 0:
                    print("   ⚠️  No API keys configured - AI features will be limited")
                elif api_keys_configured < 3:
                    print("   ⚠️  Partial API key configuration")
                else:
                    print("   ✅ All major API keys configured")
                    
            except Exception as e:
                print(f"   ❌ Error reading .env file: {e}")
        else:
            print("   ❌ .env file missing")
            if env_template.exists():
                print("   💡 .env.template available for configuration")
                
        # Frontend configuration
        app_js = self.frontend_dir / "src" / "App.js"
        if app_js.exists():
            print("   ✅ Frontend App.js exists")
            try:
                with open(app_js) as f:
                    content = f.read()
                    if 'REACT_APP_BACKEND_URL' in content:
                        print("   ✅ Backend URL configuration found")
                    else:
                        print("   ⚠️  Backend URL configuration may be missing")
            except Exception as e:
                print(f"   ❌ Error reading App.js: {e}")
        else:
            print("   ❌ Frontend App.js missing")
            
        print()
        
    def generate_health_score(self):
        """Generate overall system health score"""
        print("🏥 SYSTEM HEALTH SCORE")
        print("-" * 30)
        
        # This is a simplified scoring system
        score = 100
        issues = []
        
        if not PSUTIL_AVAILABLE:
            print("   ⚠️  Health scoring requires psutil for accurate metrics")
            score = 70  # Base score when psutil not available
            issues.append("psutil not available - limited system monitoring")
        else:
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 80:
                score -= 15
                issues.append("High CPU usage")
            elif cpu_percent > 50:
                score -= 5
                issues.append("Elevated CPU usage")
                
            # Check Memory
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                score -= 15
                issues.append("High memory usage")
            elif memory_percent > 70:
                score -= 5
                issues.append("Elevated memory usage")
                
            # Check disk space
            free_gb = psutil.disk_usage(self.root_dir).free / (1024**3)
            if free_gb < 1.0:
                score -= 20
                issues.append("Critical disk space")
            elif free_gb < 5.0:
                score -= 10
                issues.append("Low disk space")
        
        # Check configurations
        if not (self.backend_dir / ".env").exists():
            score -= 15
            issues.append("Missing .env file")
            
        if not (self.frontend_dir / "node_modules").exists():
            score -= 10
            issues.append("Missing node_modules")
            
        # Determine health status
        if score >= 90:
            health_status = "🟢 EXCELLENT"
            recommendation = "System is running optimally"
        elif score >= 75:
            health_status = "🟡 GOOD"
            recommendation = "System is healthy with minor issues"
        elif score >= 50:
            health_status = "🟠 FAIR"
            recommendation = "System has some issues that should be addressed"
        else:
            health_status = "🔴 POOR"
            recommendation = "System has significant issues requiring immediate attention"
            
        print(f"   📊 Overall Health Score: {score}/100")
        print(f"   🏥 Status: {health_status}")
        print(f"   💡 Recommendation: {recommendation}")
        
        if issues:
            print("   ⚠️  Issues detected:")
            for issue in issues:
                print(f"      • {issue}")
        else:
            print("   ✅ No critical issues detected")
            
        # Save health report
        health_data = {
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'status': health_status.split(' ')[1],
            'issues': issues,
            'recommendation': recommendation
        }
        
        health_file = self.root_dir / "SYSTEM_HEALTH_REPORT.json"
        with open(health_file, 'w') as f:
            json.dump(health_data, f, indent=2)
            
        print(f"   📄 Health report saved to: {health_file}")
        print()
        
        return health_data


def main():
    """Main health monitoring function"""
    monitor = SystemHealthMonitor()
    health_data = monitor.run_health_monitoring()
    
    print("=" * 60)
    print("🎯 SYSTEM HEALTH MONITORING COMPLETE")
    print("=" * 60)
    
    return health_data

if __name__ == "__main__":
    main()