"""
Streaming Chat API with WebSocket
Real-time AI response streaming for better UX

FIXED VERSION - With /activate command handler and proper active_project handling
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Set
import json
import asyncio
import logging
from datetime import datetime, timezone

from ..core.ai_manager import AIManager
from ..core.database import get_db_session as get_database

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# 🆕 COMMAND HANDLER FOR /activate AND OTHER SLASH COMMANDS
# ============================================================================

async def handle_command(
    user_message: str,
    session_id: str,
    user_id: str,
    websocket: WebSocket,
    manager: 'ConnectionManager'
) -> bool:
    """
    Handle slash commands like /activate, /help, etc.
    
    Returns:
        bool: True if command was handled, False otherwise
    """
    message = user_message.strip()
    
    if not message.startswith("/"):
        return False
    
    # Parse command and arguments
    parts = message.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Handle /activate command
    if command == "/activate":
        if not args:
            await manager.send_message({
                "type": "error",
                "message": "⚠️ Usage: /activate <project_name>",
                "details": "Example: /activate Xionimus",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, session_id)
            return True
        
        project_name = args.strip()
        
        # Update session with active project
        db = get_database()
        try:
            from ..models.session_models import Session
            
            session = db.query(Session).filter(Session.id == session_id).first()
            
            if session:
                # Verify project exists in workspace
                import os
                from pathlib import Path
                home_dir = Path.home()
                github_imports_dir = home_dir / ".xionimus_ai" / "github_imports"
                repo_path = github_imports_dir / user_id / project_name
                
                if repo_path.exists():
                    session.active_project = project_name
                    session.updated_at = datetime.now(timezone.utc)
                    db.commit()
                    
                    await manager.send_message({
                        "type": "command_response",
                        "message": f"✅ Active project set to: **{project_name}**",
                        "details": f"Repository path: {repo_path}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, session_id)
                    logger.info(f"✅ Active project set via /activate: {project_name}")
                else:
                    await manager.send_message({
                        "type": "error",
                        "message": f"❌ Project '{project_name}' not found",
                        "details": f"Expected path: {repo_path}\n\nPlease import the repository first.",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }, session_id)
            else:
                await manager.send_message({
                    "type": "error",
                    "message": "❌ Session not found",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
        
        except Exception as e:
            logger.error(f"Error handling /activate command: {e}")
            await manager.send_message({
                "type": "error",
                "message": "❌ Failed to activate project",
                "details": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, session_id)
        finally:
            db.close()
        
        return True
    
    # Handle /help command
    elif command == "/help":
        help_text = """
**Available Commands:**

• `/activate <project_name>` - Set active project for the current session
  Example: `/activate Xionimus`

• `/help` - Show this help message

**Tips:**
- Use `/activate` to switch between imported repositories
- Make sure to import a repository first via the GitHub integration
"""
        await manager.send_message({
            "type": "command_response",
            "message": help_text,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, session_id)
        return True
    
    # Unknown command
    else:
        await manager.send_message({
            "type": "error",
            "message": f"❌ Unknown command: {command}",
            "details": "Type `/help` to see available commands",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, session_id)
        return True


# ============================================================================
# 🆕 NEUE FUNKTIONEN FÜR REPOSITORY STRUKTUR SCANNING
# ============================================================================

def scan_repository_structure(repo_path: str, max_files: int = 2500) -> dict:
    """
    Scannt die Verzeichnisstruktur eines Repositories und erstellt
    eine strukturierte Übersicht für den AI-Agent.
    
    Args:
        repo_path: Pfad zum Repository
        max_files: Maximale Anzahl an Dateien (um zu große Strukturen zu vermeiden)
        
    Returns:
        Dict mit Verzeichnisstruktur und Statistiken
    """
    import os
    
    try:
        if not os.path.exists(repo_path):
            logger.warning(f"Repository path does not exist: {repo_path}")
            return {
                "error": "Repository not found",
                "path": repo_path
            }
        
        file_tree = []
        directories = set()
        file_extensions = {}
        total_files = 0
        total_size = 0
        
        # Ignore patterns
        ignore_dirs = {
            '.git', 'node_modules', '__pycache__', 'venv', '.venv',
            'build', 'dist', '.next', '.cache', 'coverage',
            '.pytest_cache', '.mypy_cache', 'eggs', '.eggs'
        }
        ignore_files = {
            '.DS_Store', 'Thumbs.db', '.gitignore', '.dockerignore'
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            
            # Get relative path
            rel_root = os.path.relpath(root, repo_path)
            if rel_root != '.':
                directories.add(rel_root)
            
            # Process files
            for filename in files:
                if filename in ignore_files or filename.startswith('.'):
                    continue
                
                total_files += 1
                if total_files > max_files:
                    logger.warning(f"Reached max_files limit ({max_files}). Stopping scan.")
                    break
                
                # Get file info
                filepath = os.path.join(root, filename)
                try:
                    file_size = os.path.getsize(filepath)
                    total_size += file_size
                except OSError:
                    file_size = 0
                
                # Track extension
                _, ext = os.path.splitext(filename)
                if ext:
                    file_extensions[ext] = file_extensions.get(ext, 0) + 1
                
                # Build relative path
                if rel_root == '.':
                    rel_path = filename
                else:
                    rel_path = os.path.join(rel_root, filename)
                
                file_tree.append({
                    "path": rel_path.replace('\\', '/'),  # Normalize path separators
                    "size": file_size,
                    "ext": ext
                })
            
            if total_files > max_files:
                break
        
        # Sort files for better readability
        file_tree.sort(key=lambda x: x["path"])
        directories = sorted(directories)
        
        # Create summary
        summary = {
            "total_files": total_files,
            "total_directories": len(directories),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": dict(sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)[:10])
        }
        
        return {
            "success": True,
            "path": repo_path,
            "directories": list(directories),
            "files": file_tree,
            "summary": summary,
            "truncated": total_files >= max_files
        }
        
    except Exception as e:
        logger.error(f"Error scanning repository structure: {e}", exc_info=True)
        return {
            "error": str(e),
            "path": repo_path
        }


def format_repository_context(repo_structure: dict, project_name: str) -> str:
    """
    Formatiert die Repository-Struktur als lesbaren Text für die System Message.
    """
    import os
    
    if "error" in repo_structure:
        return f"⚠️ Unable to load repository structure: {repo_structure['error']}"
    
    lines = [
        f"📁 **Repository: {project_name}**",
        "",
        f"**Summary:**",
        f"- Total Files: {repo_structure['summary']['total_files']}",
        f"- Total Directories: {repo_structure['summary']['total_directories']}",
        f"- Total Size: {repo_structure['summary']['total_size_mb']} MB",
        ""
    ]
    
    # File types
    if repo_structure['summary']['file_types']:
        lines.append("**File Types:**")
        for ext, count in repo_structure['summary']['file_types'].items():
            lines.append(f"  - {ext}: {count} files")
        lines.append("")
    
    # Directory structure
    if repo_structure['directories']:
        lines.append("**Directories:**")
        lines.append("```")
        for directory in repo_structure['directories'][:50]:  # Limit to 50 directories
            lines.append(f"  {directory}")
        if len(repo_structure['directories']) > 50:
            lines.append(f"  ... and {len(repo_structure['directories']) - 50} more directories")
        lines.append("```")
        lines.append("")
    
    # File listing (grouped by directory)
    if repo_structure['files']:
        lines.append("**Files:**")
        lines.append("```")
        
        # Group files by directory
        current_dir = None
        file_count = 0
        max_files_display = 200
        
        for file_info in repo_structure['files']:
            if file_count >= max_files_display:
                remaining = len(repo_structure['files']) - file_count
                lines.append(f"... and {remaining} more files")
                break
            
            file_path = file_info['path']
            dir_part = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            
            # New directory?
            if dir_part != current_dir:
                if current_dir is not None:
                    lines.append("")
                current_dir = dir_part
                if dir_part:
                    lines.append(f"{dir_part}/")
                    lines.append(f"  ├── {file_name}")
                else:
                    lines.append(f"├── {file_name}")
            else:
                if dir_part:
                    lines.append(f"  ├── {file_name}")
                else:
                    lines.append(f"├── {file_name}")
            
            file_count += 1
        
        lines.append("```")
        
        if repo_structure.get('truncated'):
            lines.append("")
            lines.append("⚠️ *Note: File listing truncated due to size limits*")
    
    return "\n".join(lines)


# ============================================================================
# CONNECTION MANAGER (UNVERÄNDERT)
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        logger.info(f"✅ WebSocket connected: {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"❌ WebSocket disconnected: {session_id}")
    
    async def send_message(self, message: dict, session_id: str):
        """Send message to all connections in a session"""
        if session_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected sockets
            for conn in disconnected:
                self.disconnect(conn, session_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming chat with Keep-Alive
    
    Expected message format:
    {
        "type": "chat",
        "content": "user message",
        "provider": "anthropic",
        "model": "claude-sonnet-4",
        "ultra_thinking": false,
        "api_keys": {...}
    }
    
    Keep-Alive: Automatic ping every 30 seconds to prevent connection drops
    """
    # Check origin header for CORS (WebSocket doesn't use CORS middleware)
    # Note: WebSocket headers are case-sensitive, check both cases
    origin = websocket.headers.get("Origin", "") or websocket.headers.get("origin", "")
    logger.info(f"WebSocket connection attempt - Origin: '{origin}', Headers: {dict(websocket.headers)}")
    
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5173",
    ]
    
    # Allow connections from allowed origins or when origin is empty (same-origin)
    if origin and origin not in allowed_origins:
        logger.warning(f"WebSocket connection rejected: Invalid origin '{origin}' not in {allowed_origins}")
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    
    logger.info(f"WebSocket origin check passed for origin: '{origin}'")
    
    # Accept WebSocket connection
    try:
        await manager.connect(websocket, session_id)
    except Exception as e:
        logger.error(f"Failed to accept WebSocket: {e}")
        return
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
                continue
            
            if message_data.get("type") != "chat":
                continue
            
            # Extract message details
            user_message = message_data.get("content", "")
            provider = message_data.get("provider", "openai")
            model = message_data.get("model", "gpt-4o-mini")
            ultra_thinking = message_data.get("ultra_thinking", False)
            api_keys = message_data.get("api_keys", {})
            conversation_history = message_data.get("messages", [])
            
            # Debug logging for API keys
            logger.info(f"🔍 WebSocket received - Provider: {provider}, Model: {model}")
            logger.info(f"🔍 API keys received from frontend: {list(api_keys.keys())}")
            logger.info(f"🔍 API key for {provider}: {'✅ Present' if api_keys.get(provider) else '❌ Missing'}")
            
            # CRITICAL FIX: Determine user_id FIRST, then load API keys and project context
            user_id = None
            project_context = None
            
            db = get_database()
            try:
                from ..models.session_models import Session
                from ..models.user_models import User
                from ..core.config import settings
                import os
                
                # STEP 1: Try to get user_id from session
                session_obj = db.query(Session).filter(Session.id == session_id).first()
                
                if session_obj and session_obj.user_id:
                    user_id = session_obj.user_id
                    logger.info(f"🔍 User ID from session: {user_id}")
                    
                    # Load active project from session
                    if session_obj.active_project:
                        # Build correct Windows path to the repository
                        github_imports_dir = settings.GITHUB_IMPORTS_DIR
                        repo_path = os.path.join(str(github_imports_dir), str(user_id), session_obj.active_project)
                        
                        # Check if directory exists
                        if os.path.exists(repo_path):
                            # ===================================================================
                            # 🆕 FIX: SCAN REPOSITORY STRUCTURE
                            # ===================================================================
                            logger.info(f"📂 Scanning repository structure: {repo_path}")
                            repo_structure = scan_repository_structure(repo_path, max_files=1000)
                            
                            if repo_structure.get("success"):
                                # Format repository structure for System Message
                                repo_context_text = format_repository_context(repo_structure, session_obj.active_project)
                                
                                project_context = {
                                    "project_name": session_obj.active_project,
                                    "branch": session_obj.active_project_branch or "main",
                                    "working_directory": repo_path,
                                    "repository_structure": repo_structure,  # Raw structure data
                                    "repository_context": repo_context_text   # Formatted text for System Message
                                }
                                
                                logger.info(f"✅ Active project from session: {session_obj.active_project}")
                                logger.info(f"✅ Repository path: {repo_path}")
                                logger.info(f"✅ Repository contains {repo_structure['summary']['total_files']} files in {repo_structure['summary']['total_directories']} directories")
                                logger.info(f"✅ Repository structure scanned successfully!")
                            else:
                                # Fallback if scan fails
                                project_context = {
                                    "project_name": session_obj.active_project,
                                    "branch": session_obj.active_project_branch or "main",
                                    "working_directory": repo_path
                                }
                                logger.warning(f"⚠️ Repository scan failed, using basic context")
                            # ===================================================================
                            # END FIX
                            # ===================================================================
                        else:
                            logger.error(f"❌ Repository directory not found: {repo_path}")
                            logger.warning(f"⚠️ Project '{session_obj.active_project}' may need to be re-imported")
                
                # STEP 2: If no user_id, use first available user (demo mode)
                if not user_id:
                    logger.warning(f"⚠️ No user_id in session, using first available user (demo mode)")
                    first_user = db.query(User).first()
                    
                    if first_user:
                        user_id = first_user.id
                        logger.info(f"✅ Using first user: {user_id}")
                
                # STEP 3: Now load API keys for this user_id if missing from frontend
                if user_id and not api_keys.get(provider):
                    logger.warning(f"⚠️ API key for {provider} not sent from frontend - loading from database")
                    try:
                        from ..models.api_key_models import UserApiKey
                        from ..core.encryption import encryption_manager
                        
                        # Load all stored API keys for this user
                        user_api_keys = db.query(UserApiKey).filter(
                            UserApiKey.user_id == user_id,
                            UserApiKey.is_active == True
                        ).all()
                        
                        # Decrypt and add to api_keys dict
                        loaded_count = 0
                        for key_record in user_api_keys:
                            try:
                                decrypted_key = encryption_manager.decrypt(key_record.encrypted_key)
                                api_keys[key_record.provider] = decrypted_key
                                loaded_count += 1
                                logger.info(f"✅ Loaded {key_record.provider} API key from database")
                            except Exception as decrypt_error:
                                logger.error(f"❌ Failed to decrypt {key_record.provider} key: {decrypt_error}")
                        
                        if loaded_count > 0:
                            logger.info(f"✅ Successfully loaded {loaded_count} API key(s) from database for user {user_id}")
                        else:
                            logger.warning(f"⚠️ No API keys found in database for user {user_id}")
                    
                    except Exception as e:
                        logger.error(f"❌ Failed to load API keys: {e}")
                        import traceback
                        traceback.print_exc()
                
                # FINAL: Logging
                if project_context:
                    logger.info(f"✅ Active project loaded for user {user_id}: {project_context['project_name']}")
                    logger.info(f"✅ Working directory: {project_context['working_directory']}")
                    if 'repository_context' in project_context:
                        logger.info(f"✅ Repository structure included in context")
                else:
                    logger.warning(f"⚠️ No active project set for session {session_id}")
            
            except Exception as e:
                logger.error(f"❌ Failed to load user context: {e}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
            
            # ============================================================================
            # 🆕 CHECK FOR SLASH COMMANDS FIRST
            # ============================================================================
            if user_message.strip().startswith("/"):
                command_handled = await handle_command(
                    user_message=user_message,
                    session_id=session_id,
                    user_id=user_id,
                    websocket=websocket,
                    manager=manager
                )
                
                if command_handled:
                    continue  # Skip normal AI processing for commands
            # ============================================================================
            
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Send acknowledgment
            await manager.send_message({
                "type": "start",
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, session_id)
            
            try:
                # Initialize AI Manager
                ai_manager = AIManager()
                
                # Stream AI response
                full_response = ""
                chunk_count = 0
                
                # Pass api_keys and project_context to stream_response
                async for chunk in ai_manager.stream_response(
                    provider=provider,
                    model=model,
                    messages=conversation_history,
                    ultra_thinking=ultra_thinking,
                    api_keys=api_keys,
                    project_context=project_context
                ):
                    chunk_count += 1
                    chunk_text = chunk.get("content", "")
                    full_response += chunk_text
                    
                    # Send chunk to client
                    await manager.send_message({
                        "type": "chunk",
                        "content": chunk_text,
                        "chunk_id": chunk_count
                    }, session_id)
                    
                    # Small delay to prevent overwhelming client
                    await asyncio.sleep(0.01)
                
                # Send completion message
                # Get token usage stats
                from ..core.token_tracker import token_tracker
                token_stats = token_tracker.get_usage_stats()
                
                await manager.send_message({
                    "type": "complete",
                    "full_content": full_response,
                    "model": model,
                    "provider": provider,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "token_usage": token_stats  # NEW: Include token usage
                }, session_id)
                
                # Save to SQLite
                db = get_database()
                
                try:
                    from ..models.session_models import Message, Session
                    import uuid
                    
                    # Check if session exists, create if not
                    session = db.query(Session).filter(Session.id == session_id).first()
                    if not session:
                        # Create session if it doesn't exist
                        new_session = Session(
                            id=session_id,
                            name="Chat Session",
                            user_id=None  # Will be set later if authenticated
                        )
                        db.add(new_session)
                        db.commit()
                    
                    # Save user message
                    user_msg = Message(
                        id=f"msg_{uuid.uuid4().hex[:16]}",
                        session_id=session_id,
                        role="user",
                        content=user_message,
                        provider=provider,
                        model=model
                    )
                    db.add(user_msg)
                    
                    # Save assistant message
                    assistant_msg = Message(
                        id=f"msg_{uuid.uuid4().hex[:16]}",
                        session_id=session_id,
                        role="assistant",
                        content=full_response,
                        provider=provider,
                        model=model
                    )
                    db.add(assistant_msg)
                    
                    db.commit()
                    logger.info(f"✅ Messages saved to database")
                    
                except Exception as e:
                    logger.error(f"❌ Error saving messages to database: {e}")
                    db.rollback()
                finally:
                    if "db" in locals() and db is not None:
                        db.close()
                
                logger.info(f"✅ Streaming complete: {chunk_count} chunks, {len(full_response)} chars")
                
            except ValueError as e:
                # Handle configuration errors (missing API keys)
                error_message = str(e)
                logger.warning(f"⚠️ Configuration error: {error_message}")
                
                # Send user-friendly error message
                await manager.send_message({
                    "type": "error",
                    "message": "⚠️ API Key Not Configured",
                    "details": f"{error_message}\n\n🔑 Please configure your API keys:\n1. Click on Settings (⚙️)\n2. Scroll to 'AI Provider API Keys'\n3. Add your API key for {provider}\n4. Click 'Save API Keys'\n5. Return to chat and try again",
                    "action_required": "configure_api_keys",
                    "provider": provider,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                await manager.send_message({
                    "type": "error",
                    "message": "An error occurred while processing your message",
                    "details": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"Client disconnected: {session_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)


@router.get("/stream/status")
async def get_stream_status():
    """Get streaming service status"""
    return {
        "status": "active",
        "active_sessions": len(manager.active_connections),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values())
    }
