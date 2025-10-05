"""
Autonomous Execution Engine
Handles OpenAI function calling workflow and tool execution
"""
from typing import Dict, Any, Optional, List, AsyncGenerator
import os
import subprocess
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import asyncio

from .autonomous_tools import AutonomousTools

logger = logging.getLogger(__name__)

class AutonomousExecutionEngine:
    """
    Core engine for autonomous AI tool execution
    Handles function calling workflow with OpenAI
    """
    
    def __init__(self, state_manager=None):
        self.tools = AutonomousTools()
        self.state_manager = state_manager
        self.execution_count = 0
        self.max_executions = 100  # Prevent infinite loops
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single tool and return the result
        
        Returns:
            {
                "success": bool,
                "result": str,
                "error": Optional[str],
                "execution_time": float
            }
        """
        start_time = datetime.now(timezone.utc)
        
        # Check execution limit
        self.execution_count += 1
        if self.execution_count > self.max_executions:
            return {
                "success": False,
                "result": "",
                "error": f"Execution limit reached ({self.max_executions} actions). Session reset required.",
                "execution_time": 0
            }
        
        logger.info(f"🔧 Executing tool: {tool_name} with args: {arguments}")
        
        try:
            # Route to appropriate handler
            if tool_name == "read_file":
                result = await self._read_file(**arguments)
            elif tool_name == "write_file":
                result = await self._write_file(**arguments)
            elif tool_name == "create_file":
                result = await self._create_file(**arguments)
            elif tool_name == "list_directory":
                result = await self._list_directory(**arguments)
            elif tool_name == "search_in_files":
                result = await self._search_in_files(**arguments)
            elif tool_name == "execute_bash":
                result = await self._execute_bash(**arguments)
            elif tool_name == "install_pip_package":
                result = await self._install_pip_package(**arguments)
            elif tool_name == "install_npm_package":
                result = await self._install_npm_package(**arguments)
            elif tool_name == "restart_service":
                result = await self._restart_service(**arguments)
            elif tool_name == "check_service_status":
                result = await self._check_service_status(**arguments)
            elif tool_name == "git_status":
                result = await self._git_status(**arguments)
            elif tool_name == "git_diff":
                result = await self._git_diff(**arguments)
            else:
                result = {
                    "success": False,
                    "result": "",
                    "error": f"Unknown tool: {tool_name}"
                }
            
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            logger.info(f"✅ Tool execution complete: {tool_name} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool execution failed: {tool_name} - {str(e)}")
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            return {
                "success": False,
                "result": "",
                "error": str(e),
                "execution_time": execution_time
            }
    
    # ============ File Operations ============
    
    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file contents"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "result": "", "error": f"File not found: {file_path}"}
            
            if not path.is_file():
                return {"success": False, "result": "", "error": f"Not a file: {file_path}"}
            
            content = path.read_text(encoding='utf-8')
            return {
                "success": True,
                "result": f"File: {file_path}\n{'='*60}\n{content}",
                "error": None
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    async def _write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to file (overwrite)"""
        try:
            # Check if critical file
            if self.tools.is_critical_file(file_path):
                logger.warning(f"⚠️ Modifying critical file: {file_path}")
            
            # Create checkpoint before writing
            if self.state_manager:
                await self.state_manager.create_checkpoint(file_path, "write_file")
            
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "result": f"✅ File written: {file_path} ({len(content)} bytes)",
                "error": None
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    async def _create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Create new file (fails if exists)"""
        try:
            path = Path(file_path)
            if path.exists():
                return {"success": False, "result": "", "error": f"File already exists: {file_path}"}
            
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "result": f"✅ File created: {file_path} ({len(content)} bytes)",
                "error": None
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    async def _list_directory(self, directory_path: str, recursive: bool = False) -> Dict[str, Any]:
        """List directory contents"""
        try:
            path = Path(directory_path)
            if not path.exists():
                return {"success": False, "result": "", "error": f"Directory not found: {directory_path}"}
            
            if not path.is_dir():
                return {"success": False, "result": "", "error": f"Not a directory: {directory_path}"}
            
            if recursive:
                items = [str(p.relative_to(path)) for p in path.rglob('*')]
            else:
                items = [p.name for p in path.iterdir()]
            
            result = f"Directory: {directory_path}\n{'='*60}\n"
            result += "\n".join(sorted(items))
            
            return {
                "success": True,
                "result": result,
                "error": None
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    async def _search_in_files(self, pattern: str, directory: str, file_extension: str = "") -> Dict[str, Any]:
        """Search for pattern in files using grep"""
        try:
            cmd = ["grep", "-r", "-n", pattern, directory]
            if file_extension:
                cmd.extend(["--include", f"*{file_extension}"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": f"Search results for '{pattern}' in {directory}:\n{'='*60}\n{result.stdout}",
                    "error": None
                }
            elif result.returncode == 1:
                return {
                    "success": True,
                    "result": f"No matches found for '{pattern}' in {directory}",
                    "error": None
                }
            else:
                return {"success": False, "result": "", "error": result.stderr}
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    # ============ Code Execution ============
    
    async def _execute_bash(self, command: str, working_directory: str = "/app") -> Dict[str, Any]:
        """Execute bash command"""
        try:
            # Check for dangerous commands
            is_dangerous, reason = self.tools.is_dangerous_command(command)
            if is_dangerous:
                return {
                    "success": False,
                    "result": "",
                    "error": f"🚫 Dangerous command blocked: {reason}"
                }
            
            logger.info(f"🖥️ Executing: {command} in {working_directory}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=working_directory,
                timeout=60
            )
            
            output = result.stdout + result.stderr
            
            return {
                "success": result.returncode == 0,
                "result": f"Command: {command}\nExit code: {result.returncode}\n{'='*60}\n{output}",
                "error": None if result.returncode == 0 else result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "result": "", "error": "Command timeout (60s limit)"}
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    # ============ Package Management ============
    
    async def _install_pip_package(self, package_name: str) -> Dict[str, Any]:
        """Install Python package"""
        try:
            logger.info(f"📦 Installing pip package: {package_name}")
            
            result = subprocess.run(
                ["pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            return {
                "success": result.returncode == 0,
                "result": f"✅ Installed {package_name}\n{result.stdout}",
                "error": None if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    async def _install_npm_package(self, package_name: str, dev: bool = False) -> Dict[str, Any]:
        """Install Node.js package using yarn"""
        try:
            logger.info(f"📦 Installing npm package: {package_name} (dev={dev})")
            
            cmd = ["yarn", "add", package_name]
            if dev:
                cmd.append("-D")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd="/app/frontend",
                timeout=300  # 5 minutes
            )
            
            return {
                "success": result.returncode == 0,
                "result": f"✅ Installed {package_name}\n{result.stdout}",
                "error": None if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    # ============ Service Control ============
    
    async def _restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart service using supervisorctl"""
        try:
            logger.info(f"🔄 Restarting service: {service_name}")
            
            result = subprocess.run(
                ["sudo", "supervisorctl", "restart", service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "result": f"✅ Service restarted: {service_name}\n{result.stdout}",
                "error": None if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    async def _check_service_status(self, service_name: str) -> Dict[str, Any]:
        """Check service status"""
        try:
            result = subprocess.run(
                ["sudo", "supervisorctl", "status", service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": True,
                "result": f"Service status: {service_name}\n{'='*60}\n{result.stdout}",
                "error": None
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    # ============ Git Operations ============
    
    async def _git_status(self, directory: str = "/app") -> Dict[str, Any]:
        """Get git status"""
        try:
            result = subprocess.run(
                ["git", "status"],
                capture_output=True,
                text=True,
                cwd=directory,
                timeout=10
            )
            
            return {
                "success": True,
                "result": f"Git status in {directory}:\n{'='*60}\n{result.stdout}",
                "error": None
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}
    
    async def _git_diff(self, file_path: str = None, directory: str = "/app") -> Dict[str, Any]:
        """Show git diff"""
        try:
            cmd = ["git", "diff"]
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=directory,
                timeout=10
            )
            
            return {
                "success": True,
                "result": f"Git diff in {directory}:\n{'='*60}\n{result.stdout if result.stdout else 'No changes'}",
                "error": None
            }
        except Exception as e:
            return {"success": False, "result": "", "error": str(e)}