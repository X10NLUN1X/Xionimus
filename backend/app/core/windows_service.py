"""
Windows Service Management
Provides Windows-compatible service control without supervisor
"""

import sys
import subprocess
import logging
import psutil
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

IS_WINDOWS = sys.platform == 'win32'


class WindowsServiceManager:
    """
    Manage application services on Windows
    
    Since supervisor doesn't work on Windows, this provides
    alternative service management using Windows native tools
    """
    
    SERVICES = {
        'backend': {
            'command': ['python', '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8001'],
            'cwd': Path(__file__).parent.parent.parent,
            'name': 'Xionimus Backend'
        },
        'frontend': {
            'command': ['yarn', 'dev'],
            'cwd': Path(__file__).parent.parent.parent.parent / 'frontend',
            'name': 'Xionimus Frontend'
        }
    }
    
    @classmethod
    def start_service(cls, service_name: str) -> Dict[str, Any]:
        """
        Start a service on Windows
        
        Args:
            service_name: Name of service to start
            
        Returns:
            Dict with success status and message
        """
        if service_name not in cls.SERVICES:
            return {
                'success': False,
                'error': f'Unknown service: {service_name}'
            }
        
        service = cls.SERVICES[service_name]
        
        try:
            # Check if already running
            if cls.is_service_running(service_name):
                return {
                    'success': True,
                    'message': f'{service["name"]} is already running',
                    'status': 'running'
                }
            
            # Start the service
            process = subprocess.Popen(
                service['command'],
                cwd=service['cwd'],
                creationflags=subprocess.CREATE_NEW_CONSOLE if IS_WINDOWS else 0,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Started {service['name']} (PID: {process.pid})")
            
            return {
                'success': True,
                'message': f'{service["name"]} started successfully',
                'pid': process.pid,
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Failed to start {service['name']}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def stop_service(cls, service_name: str) -> Dict[str, Any]:
        """
        Stop a service on Windows
        
        Args:
            service_name: Name of service to stop
            
        Returns:
            Dict with success status and message
        """
        if service_name not in cls.SERVICES:
            return {
                'success': False,
                'error': f'Unknown service: {service_name}'
            }
        
        service = cls.SERVICES[service_name]
        
        try:
            # Find and kill processes
            killed = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if any(cmd in cmdline for cmd in service['command']):
                        proc.terminate()
                        proc.wait(timeout=5)
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed > 0:
                return {
                    'success': True,
                    'message': f'Stopped {killed} {service["name"]} process(es)',
                    'status': 'stopped'
                }
            else:
                return {
                    'success': True,
                    'message': f'{service["name"]} was not running',
                    'status': 'not_running'
                }
                
        except Exception as e:
            logger.error(f"Failed to stop {service['name']}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def is_service_running(cls, service_name: str) -> bool:
        """
        Check if a service is running
        
        Args:
            service_name: Name of service to check
            
        Returns:
            bool: True if running, False otherwise
        """
        if service_name not in cls.SERVICES:
            return False
        
        service = cls.SERVICES[service_name]
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if any(cmd in cmdline for cmd in service['command']):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return False
        except Exception:
            return False
    
    @classmethod
    def get_service_status(cls, service_name: str = None) -> Dict[str, Any]:
        """
        Get status of service(s)
        
        Args:
            service_name: Optional service name. If None, returns all services
            
        Returns:
            Dict with service status information
        """
        if service_name:
            services_to_check = {service_name: cls.SERVICES[service_name]}
        else:
            services_to_check = cls.SERVICES
        
        status = {}
        for name, service in services_to_check.items():
            running = cls.is_service_running(name)
            status[name] = {
                'name': service['name'],
                'running': running,
                'status': 'running' if running else 'stopped'
            }
        
        return status


def get_service_manager():
    """
    Get appropriate service manager for the platform
    
    Returns:
        Service manager instance
    """
    if IS_WINDOWS:
        return WindowsServiceManager()
    else:
        # On Unix, use supervisor
        from app.core.supervisor_manager import SupervisorManager
        return SupervisorManager()