"""
Autonomous Tools Registry
Defines all tools as OpenAI function calling schemas for autonomous execution
"""
from typing import List, Dict, Any
import os
import subprocess
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AutonomousTools:
    """Registry of all autonomous tools with OpenAI function schemas"""
    
    @staticmethod
    def get_tool_schemas() -> List[Dict[str, Any]]:
        """
        Return all tool schemas in OpenAI function calling format
        Uses the new 'tools' parameter format (not deprecated 'functions')
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file from the filesystem",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Absolute path to the file to read, e.g. /app/backend/main.py"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write or overwrite content to a file. Creates parent directories if needed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Absolute path to the file to write, e.g. /app/backend/test.py"
                            },
                            "content": {
                                "type": "string",
                                "description": "Full content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_file",
                    "description": "Create a new file with content. Fails if file already exists.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Absolute path for the new file, e.g. /app/backend/new_file.py"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content for the new file"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List files and directories in a given path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Absolute path to the directory to list, e.g. /app/backend"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to list recursively (default: false)",
                                "default": False
                            }
                        },
                        "required": ["directory_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_in_files",
                    "description": "Search for a pattern in files using grep",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Search pattern (regex supported)"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in, e.g. /app/backend"
                            },
                            "file_extension": {
                                "type": "string",
                                "description": "Filter by file extension, e.g. '.py' or '.ts'",
                                "default": ""
                            }
                        },
                        "required": ["pattern", "directory"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_bash",
                    "description": "Execute a bash command. Use with caution. Avoid destructive commands.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Bash command to execute, e.g. 'ls -la /app'"
                            },
                            "working_directory": {
                                "type": "string",
                                "description": "Working directory for command execution (default: /app)",
                                "default": "/app"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "install_pip_package",
                    "description": "Install a Python package using pip",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "package_name": {
                                "type": "string",
                                "description": "Name of the package to install, e.g. 'requests' or 'requests==2.28.0'"
                            }
                        },
                        "required": ["package_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "install_npm_package",
                    "description": "Install a Node.js package using yarn (preferred) or npm",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "package_name": {
                                "type": "string",
                                "description": "Name of the package to install, e.g. 'axios' or 'axios@1.4.0'"
                            },
                            "dev": {
                                "type": "boolean",
                                "description": "Install as dev dependency (default: false)",
                                "default": False
                            }
                        },
                        "required": ["package_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "restart_service",
                    "description": "Restart a backend or frontend service using supervisorctl",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Service to restart: 'backend', 'frontend', or 'all'",
                                "enum": ["backend", "frontend", "all"]
                            }
                        },
                        "required": ["service_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_service_status",
                    "description": "Check status of backend/frontend services",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Service to check: 'backend', 'frontend', or 'all'",
                                "enum": ["backend", "frontend", "all"]
                            }
                        },
                        "required": ["service_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "git_status",
                    "description": "Get git status of the repository",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Repository directory (default: /app)",
                                "default": "/app"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "git_diff",
                    "description": "Show git diff of changes",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Specific file to diff (optional, shows all if not provided)"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Repository directory (default: /app)",
                                "default": "/app"
                            }
                        }
                    }
                }
            }
        ]
    
    @staticmethod
    def is_dangerous_command(command: str) -> tuple[bool, str]:
        """
        Check if a command is potentially dangerous
        Returns: (is_dangerous, reason)
        """
        dangerous_patterns = [
            (r"rm\s+-rf\s+/", "Recursive delete of root directory"),
            (r"rm\s+-rf\s+\*", "Recursive delete with wildcard"),
            (r"dd\s+if=", "Disk imaging/cloning command"),
            (r"mkfs\.", "Format filesystem command"),
            (r":(){ :|:& };:", "Fork bomb"),
            (r">/dev/sd", "Direct disk write"),
            (r"chmod\s+-R\s+777", "Recursive permission change to 777"),
            (r"chown\s+-R", "Recursive ownership change"),
            (r"shutdown", "System shutdown"),
            (r"reboot", "System reboot"),
            (r"init\s+0", "System halt"),
            (r"init\s+6", "System reboot"),
        ]
        
        import re
        for pattern, reason in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True, reason
        
        return False, ""
    
    @staticmethod
    def is_critical_file(file_path: str) -> bool:
        """Check if a file is critical and should have extra protection"""
        critical_files = [
            "/app/backend/.env",
            "/app/frontend/.env",
            "/app/backend/main.py",
            "/app/backend/server.py",
            "/.git/config",
            "/.emergent"
        ]
        
        critical_patterns = [
            ".git/",
            ".emergent/",
            "node_modules/",
            "venv/",
            "__pycache__/"
        ]
        
        # Exact match
        if file_path in critical_files:
            return True
        
        # Pattern match
        for pattern in critical_patterns:
            if pattern in file_path:
                return True
        
        return False