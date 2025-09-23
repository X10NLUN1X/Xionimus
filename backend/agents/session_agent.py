import re
import json
import uuid
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
from datetime import datetime, timezone
from pathlib import Path
import zipfile
import os

class SessionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Session Agent",
            description="Specialized in session management, forking, and state preservation",
            capabilities=[
                AgentCapability.API_INTEGRATION
            ]
        )
        self.ai_model = "claude"  # Use Claude for session analysis and organization
        # Use relative path from backend directory for better Windows compatibility
        self.sessions_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        session_keywords = [
            'session', 'fork', 'save state', 'export session', 'import session',
            'backup', 'restore', 'snapshot', 'checkpoint', 'state management',
            'session management', 'preserve', 'continuation', 'resume',
            'sitzung', 'zustand', 'sichern', 'wiederherstellen'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in session_keywords if keyword in description_lower)
        confidence = min(matches / 2, 1.0)
        
        # Boost confidence for session-specific operations
        if any(term in description_lower for term in ['fork session', 'save session', 'export state']):
            confidence += 0.4
        
        # Boost if context suggests session operations
        if context.get('session_data') or context.get('project_state'):
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute session-related tasks"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing session operations")
            
            task_type = self._identify_session_task_type(task.description)
            
            await self.update_progress(task, 0.3, f"Executing {task_type}")
            
            if task_type == "fork":
                await self._handle_session_fork(task)
            elif task_type == "save":
                await self._handle_session_save(task)
            elif task_type == "load":
                await self._handle_session_load(task)
            elif task_type == "export":
                await self._handle_session_export(task)
            elif task_type == "import":
                await self._handle_session_import(task)
            elif task_type == "list":
                await self._handle_session_list(task)
            elif task_type == "snapshot":
                await self._handle_session_snapshot(task)
            else:
                await self._handle_general_session_task(task)
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Session operations completed")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"Session operation failed: {str(e)}"
            self.logger.error(f"Session agent error: {e}")
            
        return task
    
    def _identify_session_task_type(self, description: str) -> str:
        """Identify the type of session task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['fork', 'fork session', 'create fork']):
            return "fork"
        elif any(word in description_lower for word in ['save', 'save state', 'preserve', 'sichern']):
            return "save"
        elif any(word in description_lower for word in ['load', 'restore', 'resume', 'laden', 'wiederherstellen']):
            return "load"
        elif any(word in description_lower for word in ['export', 'download session', 'exportieren']):
            return "export"
        elif any(word in description_lower for word in ['import', 'upload session', 'importieren']):
            return "import"
        elif any(word in description_lower for word in ['list', 'show sessions', 'auflisten']):
            return "list"
        elif any(word in description_lower for word in ['snapshot', 'checkpoint', 'backup']):
            return "snapshot"
        else:
            return "general_session"
    
    async def _handle_session_fork(self, task: AgentTask):
        """Handle session forking - create a complete session package"""
        await self.update_progress(task, 0.5, "Creating session fork")
        
        # Get current session data
        projects = task.input_data.get('projects', [])
        messages = task.input_data.get('messages', [])
        files = task.input_data.get('files', [])
        settings = task.input_data.get('settings', {})
        agents_state = task.input_data.get('agents_state', {})
        
        fork_id = str(uuid.uuid4())
        fork_name = task.input_data.get('fork_name', f'Session_Fork_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        # Create fork directory
        fork_dir = self.sessions_dir / fork_id
        fork_dir.mkdir(exist_ok=True)
        
        # Create comprehensive session data
        session_data = {
            "fork_id": fork_id,
            "fork_name": fork_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "metadata": {
                "total_projects": len(projects),
                "total_messages": len(messages),
                "total_files": len(files),
                "session_duration": task.input_data.get('session_duration', 0),
                "user_agent": task.input_data.get('user_agent', 'Xionimus AI'),
                "language": task.input_data.get('language', 'german')
            },
            "projects": projects,
            "conversation_history": messages,
            "files": files,
            "settings": settings,
            "agents_state": agents_state,
            "instructions": {
                "how_to_restore": "Use the Session Agent to import this fork",
                "requirements": [
                    "Xionimus AI compatible system",
                    "Session Agent available",
                    "Project and file management capabilities"
                ],
                "included_data": [
                    "All project configurations",
                    "Complete conversation history",
                    "File references and metadata",
                    "Agent states and preferences",
                    "User settings and customizations"
                ]
            }
        }
        
        # Save session data as JSON
        session_file = fork_dir / "session_data.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
        
        # Create README for the fork
        readme_content = f"""# {fork_name}
## Xionimus AI Session Fork

Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Fork ID: {fork_id}

### Contents:
- **Projects**: {len(projects)} project(s)
- **Messages**: {len(messages)} conversation message(s)
- **Files**: {len(files)} file(s)
- **Settings**: User preferences and configurations
- **Agents**: AI agent states and configurations

### How to Restore:
1. Import this session using Xionimus AI Session Agent
2. Use the fork ID: `{fork_id}`
3. All projects, conversations, and files will be restored

### Compatibility:
- Requires Xionimus AI v1.0+
- Compatible with all agent systems
- Supports multi-language configurations

Generated by Xionimus AI Session Agent
"""
        
        readme_file = fork_dir / "README.md"
        readme_file.write_text(readme_content, encoding='utf-8')
        
        # Create archive for easy distribution
        archive_path = self.sessions_dir / f"{fork_name}_{fork_id[:8]}.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in fork_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(fork_dir)
                    zipf.write(file_path, arcname)
        
        task.result = {
            "type": "session_fork",
            "fork_id": fork_id,
            "fork_name": fork_name,
            "fork_directory": str(fork_dir),
            "archive_path": str(archive_path),
            "archive_size": archive_path.stat().st_size,
            "session_data": session_data["metadata"],
            "restoration_instructions": session_data["instructions"],
            "created_at": session_data["created_at"]
        }
    
    async def _handle_session_save(self, task: AgentTask):
        """Handle session saving"""
        await self.update_progress(task, 0.5, "Saving session state")
        
        session_id = task.input_data.get('session_id', str(uuid.uuid4()))
        session_name = task.input_data.get('session_name', f'Session_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        session_data = {
            "session_id": session_id,
            "session_name": session_name,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "projects": task.input_data.get('projects', []),
            "messages": task.input_data.get('messages', []),
            "files": task.input_data.get('files', []),
            "settings": task.input_data.get('settings', {}),
            "current_state": task.input_data.get('current_state', {})
        }
        
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
        
        task.result = {
            "type": "session_save",
            "session_id": session_id,
            "session_name": session_name,
            "session_file": str(session_file),
            "saved_at": session_data["saved_at"],
            "data_size": session_file.stat().st_size
        }
    
    async def _handle_session_load(self, task: AgentTask):
        """Handle session loading"""
        await self.update_progress(task, 0.5, "Loading session state")
        
        session_id = task.input_data.get('session_id')
        if not session_id:
            raise Exception("Session ID required for loading")
        
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            raise Exception(f"Session {session_id} not found")
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        task.result = {
            "type": "session_load",
            "session_data": session_data,
            "loaded_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _handle_session_export(self, task: AgentTask):
        """Handle session export"""
        await self.update_progress(task, 0.5, "Exporting session")
        
        session_id = task.input_data.get('session_id')
        export_format = task.input_data.get('format', 'zip')
        
        if not session_id:
            raise Exception("Session ID required for export")
        
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            raise Exception(f"Session {session_id} not found")
        
        if export_format == 'zip':
            export_path = self.sessions_dir / f"export_{session_id}.zip"
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(session_file, session_file.name)
        else:
            export_path = session_file
        
        task.result = {
            "type": "session_export",
            "session_id": session_id,
            "export_path": str(export_path),
            "export_format": export_format,
            "export_size": export_path.stat().st_size
        }
    
    async def _handle_session_import(self, task: AgentTask):
        """Handle session import"""
        await self.update_progress(task, 0.5, "Importing session")
        
        import_data = task.input_data.get('import_data')
        if not import_data:
            raise Exception("Import data required")
        
        # Parse import data
        if isinstance(import_data, str):
            session_data = json.loads(import_data)
        else:
            session_data = import_data
        
        session_id = session_data.get('session_id', str(uuid.uuid4()))
        
        # Save imported session
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
        
        task.result = {
            "type": "session_import",
            "session_id": session_id,
            "imported_at": datetime.now(timezone.utc).isoformat(),
            "session_data": session_data
        }
    
    async def _handle_session_list(self, task: AgentTask):
        """Handle session listing"""
        await self.update_progress(task, 0.5, "Listing sessions")
        
        sessions = []
        
        for session_file in self.sessions_dir.glob('*.json'):
            if session_file.name.startswith('export_'):
                continue
                
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    "session_id": session_data.get('session_id', session_file.stem),
                    "session_name": session_data.get('session_name', 'Unnamed Session'),
                    "created_at": session_data.get('saved_at', 'Unknown'),
                    "file_size": session_file.stat().st_size,
                    "projects_count": len(session_data.get('projects', [])),
                    "messages_count": len(session_data.get('messages', []))
                })
            except:
                continue
        
        task.result = {
            "type": "session_list",
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
    
    async def _handle_session_snapshot(self, task: AgentTask):
        """Handle session snapshot creation"""
        await self.update_progress(task, 0.5, "Creating session snapshot")
        
        snapshot_id = str(uuid.uuid4())
        snapshot_name = task.input_data.get('snapshot_name', f'Snapshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        snapshot_data = {
            "snapshot_id": snapshot_id,
            "snapshot_name": snapshot_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "current_state": task.input_data.get('current_state', {}),
            "quick_restore": True,
            "snapshot_type": "checkpoint"
        }
        
        snapshot_file = self.sessions_dir / f"snapshot_{snapshot_id}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, indent=2, ensure_ascii=False, default=str)
        
        task.result = {
            "type": "session_snapshot",
            "snapshot_id": snapshot_id,
            "snapshot_name": snapshot_name,
            "snapshot_file": str(snapshot_file),
            "created_at": snapshot_data["created_at"]
        }
    
    async def _handle_general_session_task(self, task: AgentTask):
        """Handle general session tasks"""
        await self.update_progress(task, 0.5, "Processing general session task")
        
        task.result = {
            "type": "general_session",
            "message": "General session task processed",
            "description": task.description,
            "suggestions": [
                "Use 'fork session' to create a complete session backup",
                "Use 'save session' to preserve current state",
                "Use 'load session' to restore a previous state",
                "Use 'list sessions' to see all saved sessions"
            ]
        }