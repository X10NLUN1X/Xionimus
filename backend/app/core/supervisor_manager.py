"""
Supervisor Manager - Service Management & Monitoring
Emergent-Style Service Control
"""
import sys
import subprocess
if sys.platform == "win32":
    subprocess.CREATE_NO_WINDOW = 0x08000000
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

IS_WINDOWS = sys.platform == 'win32'

logger = logging.getLogger(__name__)

class SupervisorManager:
    """Manages services via supervisorctl"""
    
    SERVICES = ['backend', 'frontend', 'mongodb', 'code-server', 'mcp-server']
    
    def __init__(self, log_dir: str = None):
        # Use platform-specific log directory
        if log_dir is None:
            if IS_WINDOWS:
                log_dir = Path.home() / "logs" / "supervisor"
            else:
                log_dir = "/var/log/supervisor"
        self.log_dir = Path(log_dir)
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def execute_supervisorctl(self, command: str) -> Tuple[bool, str]:
        """
        Execute supervisorctl command (cross-platform)
        Returns (success, output)
        """
        try:
            # Build command based on platform
            if IS_WINDOWS:
                # On Windows, don't use sudo
                cmd = ['supervisorctl'] + command.split()
            else:
                # On Unix, use sudo
                cmd = ['sudo', 'supervisorctl'] + command.split()
            
            # Add Windows-specific flags to prevent console window
            kwargs = {
                'capture_output': True,
                'text': True,
                'timeout': 10
            }
            if IS_WINDOWS:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(cmd, **kwargs)
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            logger.error("Supervisorctl command timed out")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"Supervisorctl error: {e}")
            return False, str(e)
    
    def get_service_status(self, service: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of one or all services
        """
        command = f"status {service}" if service else "status"
        success, output = self.execute_supervisorctl(command)
        
        if not success:
            return {
                'success': False,
                'error': output,
                'timestamp': datetime.now().isoformat()
            }
        
        # Parse status output
        services = {}
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            # Format: service_name STATUS pid X, uptime Y
            parts = line.split()
            if len(parts) >= 2:
                service_name = parts[0]
                status = parts[1]
                
                # Extract PID if running
                pid = None
                uptime = None
                if 'pid' in line:
                    pid_match = re.search(r'pid (\d+)', line)
                    if pid_match:
                        pid = int(pid_match.group(1))
                
                if 'uptime' in line:
                    uptime_match = re.search(r'uptime (.+)$', line)
                    if uptime_match:
                        uptime = uptime_match.group(1).strip()
                
                services[service_name] = {
                    'status': status,
                    'pid': pid,
                    'uptime': uptime,
                    'running': status == 'RUNNING'
                }
        
        return {
            'success': True,
            'services': services,
            'timestamp': datetime.now().isoformat()
        }
    
    def restart_service(self, service: str) -> Dict[str, Any]:
        """
        Restart a specific service
        """
        if service not in self.SERVICES and service != 'all':
            return {
                'success': False,
                'error': f'Unknown service: {service}. Available: {", ".join(self.SERVICES)}',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"🔄 Restarting service: {service}")
        success, output = self.execute_supervisorctl(f"restart {service}")
        
        if success:
            logger.info(f"✅ Service restarted: {service}")
        else:
            logger.error(f"❌ Service restart failed: {service}")
        
        return {
            'success': success,
            'service': service,
            'output': output,
            'timestamp': datetime.now().isoformat()
        }
    
    def start_service(self, service: str) -> Dict[str, Any]:
        """
        Start a specific service
        """
        if service not in self.SERVICES:
            return {
                'success': False,
                'error': f'Unknown service: {service}',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"▶️ Starting service: {service}")
        success, output = self.execute_supervisorctl(f"start {service}")
        
        return {
            'success': success,
            'service': service,
            'output': output,
            'timestamp': datetime.now().isoformat()
        }
    
    def stop_service(self, service: str) -> Dict[str, Any]:
        """
        Stop a specific service
        """
        if service not in self.SERVICES:
            return {
                'success': False,
                'error': f'Unknown service: {service}',
                'timestamp': datetime.now().isoformat()
            }
        
        logger.info(f"⏸️ Stopping service: {service}")
        success, output = self.execute_supervisorctl(f"stop {service}")
        
        return {
            'success': success,
            'service': service,
            'output': output,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_service_logs(
        self, 
        service: str, 
        log_type: str = 'out',
        lines: int = 50,
        grep_pattern: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get service logs from supervisor log directory (cross-platform)
        log_type: 'out' or 'err'
        """
        try:
            log_file = self.log_dir / f"{service}.{log_type}.log"
            
            if not log_file.exists():
                return {
                    'success': False,
                    'error': f'Log file not found: {log_file}',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Pure Python implementation - works on all platforms
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Read all lines
                all_lines = f.readlines()
                
                # Get last N lines
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                # Apply grep pattern if provided
                if grep_pattern:
                    import re
                    pattern = re.compile(grep_pattern)
                    filtered_lines = [line for line in last_lines if pattern.search(line)]
                    log_content = ''.join(filtered_lines)
                else:
                    log_content = ''.join(last_lines)
            
            return {
                'success': True,
                'service': service,
                'log_type': log_type,
                'lines': lines,
                'content': log_content,
                'grep_pattern': grep_pattern,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_all_services_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of all services
        """
        status_result = self.get_service_status()
        
        if not status_result['success']:
            return status_result
        
        services_health = {}
        for service_name, service_info in status_result['services'].items():
            # Check if service should be running
            if service_name in self.SERVICES:
                is_healthy = service_info['running']
                
                # Get recent errors if not healthy
                recent_errors = None
                if not is_healthy:
                    error_logs = self.get_service_logs(
                        service_name,
                        log_type='err',
                        lines=10,
                        grep_pattern='ERROR|error|Error|CRITICAL|Failed'
                    )
                    if error_logs['success']:
                        recent_errors = error_logs['content']
                
                services_health[service_name] = {
                    'healthy': is_healthy,
                    'status': service_info['status'],
                    'pid': service_info['pid'],
                    'uptime': service_info['uptime'],
                    'recent_errors': recent_errors
                }
        
        # Overall health
        all_healthy = all(s['healthy'] for s in services_health.values())
        
        return {
            'success': True,
            'overall_healthy': all_healthy,
            'services': services_health,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_health_report(self, health_data: Dict[str, Any]) -> str:
        """
        Generate human-readable health report
        """
        if not health_data['success']:
            return f"❌ Failed to get health status: {health_data.get('error')}"
        
        lines = ["# 🏥 System Health Report\n"]
        
        overall = "✅ All services healthy" if health_data['overall_healthy'] else "⚠️ Some services need attention"
        lines.append(f"**Overall Status**: {overall}\n")
        
        lines.append("## Service Status\n")
        
        for service, info in health_data['services'].items():
            status_emoji = "✅" if info['healthy'] else "❌"
            lines.append(f"{status_emoji} **{service}**: {info['status']}")
            
            if info['pid']:
                lines.append(f"   - PID: {info['pid']}")
            if info['uptime']:
                lines.append(f"   - Uptime: {info['uptime']}")
            
            if info['recent_errors']:
                lines.append(f"   - Recent errors:\n```\n{info['recent_errors'][:200]}...\n```")
        
        return "\n".join(lines)


# Global instance
supervisor_manager = SupervisorManager()
