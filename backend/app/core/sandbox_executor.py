"""
Secure Code Execution Engine - Subprocess-based Sandbox
Provides safe, isolated code execution without Docker
"""
import subprocess
import tempfile
import os
import signal
import time
import logging
import uuid
import resource
from typing import Dict, Any, Optional, List
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class SandboxExecutor:
    """
    Secure code executor using subprocess with resource limits
    """
    
    # Supported languages and their execution commands
    LANGUAGE_CONFIGS = {
        "python": {
            "extension": ".py",
            "command": ["python3", "-u"],  # -u for unbuffered output
            "timeout": 30,
            "memory_limit_mb": 256,
            "compiled": False
        },
        "javascript": {
            "extension": ".js",
            "command": ["node", "--max-old-space-size=512"],  # Node.js needs more memory + explicit heap size
            "timeout": 30,
            "memory_limit_mb": 512,  # Increased to 512MB for Node.js
            "compiled": False
        },
        "bash": {
            "extension": ".sh",
            "command": ["bash"],
            "timeout": 30,
            "memory_limit_mb": 128,
            "compiled": False
        },
        "cpp": {
            "extension": ".cpp",
            "compile_command": ["g++", "-std=c++17", "-O2", "-o"],
            "command": [],  # Will be set to compiled binary path
            "timeout": 30,
            "memory_limit_mb": 512,
            "compiled": True
        },
        "c": {
            "extension": ".c",
            "compile_command": ["gcc", "-std=c11", "-O2", "-o"],
            "command": [],  # Will be set to compiled binary path
            "timeout": 30,
            "memory_limit_mb": 512,
            "compiled": True
        },
        "csharp": {
            "extension": ".cs",
            "compile_command": ["mcs", "-out:"],
            "command": ["mono"],  # mono program.exe
            "timeout": 30,
            "memory_limit_mb": 512,
            "compiled": True
        },
        "perl": {
            "extension": ".pl",
            "command": ["perl"],
            "timeout": 30,
            "memory_limit_mb": 256,
            "compiled": False
        }
    }
    
    def __init__(self):
        self.workspace_dir = Path("/tmp/xionimus_sandbox")
        self.workspace_dir.mkdir(exist_ok=True)
        logger.info(f"✅ Sandbox workspace: {self.workspace_dir}")
    
    def execute_code(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
        stdin_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code in a secure subprocess
        
        Args:
            code: Source code to execute
            language: Programming language (python, javascript, bash)
            timeout: Max execution time in seconds
            stdin_input: Optional stdin input
            
        Returns:
            Dict with stdout, stderr, exit_code, execution_time
        """
        # Validate language
        if language not in self.LANGUAGE_CONFIGS:
            return {
                "success": False,
                "error": f"Unsupported language: {language}",
                "supported_languages": list(self.LANGUAGE_CONFIGS.keys())
            }
        
        config = self.LANGUAGE_CONFIGS[language]
        timeout = timeout or config["timeout"]
        
        # Create temporary execution directory
        execution_id = str(uuid.uuid4())[:8]
        exec_dir = self.workspace_dir / execution_id
        exec_dir.mkdir(exist_ok=True)
        
        try:
            # Write code to temporary file
            code_file = exec_dir / f"code{config['extension']}"
            code_file.write_text(code)
            
            # Make bash scripts executable
            if language == "bash":
                os.chmod(code_file, 0o755)
            
            # Build command
            cmd = config["command"] + [str(code_file)]
            
            logger.info(f"🚀 Executing {language} code (ID: {execution_id})")
            logger.info(f"   Command: {' '.join(cmd)}")
            logger.info(f"   Timeout: {timeout}s")
            logger.info(f"   Memory limit: {config['memory_limit_mb']}MB")
            
            # Execute with resource limits
            start_time = time.time()
            
            result = self._execute_with_limits(
                cmd=cmd,
                timeout=timeout,
                memory_limit_mb=config["memory_limit_mb"],
                stdin_input=stdin_input,
                cwd=exec_dir
            )
            
            execution_time = time.time() - start_time
            
            logger.info(f"✅ Execution complete (ID: {execution_id})")
            logger.info(f"   Exit code: {result['exit_code']}")
            logger.info(f"   Time: {execution_time:.2f}s")
            logger.info(f"   Stdout length: {len(result['stdout'])} chars")
            logger.info(f"   Stderr length: {len(result['stderr'])} chars")
            
            return {
                "success": result["exit_code"] == 0,
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "execution_time": round(execution_time, 3),
                "language": language,
                "execution_id": execution_id,
                "timeout_occurred": result.get("timeout_occurred", False)
            }
            
        except Exception as e:
            logger.error(f"❌ Execution failed (ID: {execution_id}): {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_id": execution_id
            }
        finally:
            # Cleanup temporary directory
            try:
                shutil.rmtree(exec_dir)
                logger.debug(f"🗑️ Cleaned up execution directory: {execution_id}")
            except Exception as e:
                logger.warning(f"⚠️ Cleanup failed for {execution_id}: {e}")
    
    def _execute_with_limits(
        self,
        cmd: List[str],
        timeout: int,
        memory_limit_mb: int,
        stdin_input: Optional[str],
        cwd: Path
    ) -> Dict[str, Any]:
        """
        Execute command with resource limits
        """
        # Setup resource limits (works on Unix-like systems)
        def set_limits():
            try:
                # Set memory limit (in bytes)
                memory_bytes = memory_limit_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
                
                # Set CPU time limit
                resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
                
                # Disable core dumps
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                
                # Limit number of processes
                resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))
            except Exception as e:
                logger.warning(f"⚠️ Could not set resource limits: {e}")
        
        try:
            # Execute subprocess with timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE if stdin_input else None,
                cwd=cwd,
                preexec_fn=set_limits,  # Apply resource limits
                text=True
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(
                    input=stdin_input,
                    timeout=timeout
                )
                
                return {
                    "stdout": stdout,
                    "stderr": stderr,
                    "exit_code": process.returncode,
                    "timeout_occurred": False
                }
                
            except subprocess.TimeoutExpired:
                # Kill process if timeout
                process.kill()
                process.wait()
                
                return {
                    "stdout": "",
                    "stderr": f"Execution timeout ({timeout}s exceeded)",
                    "exit_code": -1,
                    "timeout_occurred": True
                }
                
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": -1,
                "timeout_occurred": False
            }
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """Get list of supported languages with metadata"""
        return [
            {
                "language": lang,
                "extension": config["extension"],
                "timeout": config["timeout"],
                "memory_limit_mb": config["memory_limit_mb"]
            }
            for lang, config in self.LANGUAGE_CONFIGS.items()
        ]

# Global instance
sandbox_executor = SandboxExecutor()