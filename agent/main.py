"""
Xionimus Autonomous Agent - Main Script
Monitors code directories and provides real-time analysis
"""

import asyncio
import logging
import os
import sys
import uuid
import argparse
from pathlib import Path
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from file_watcher import FileWatcher
from ws_client import XionimusWebSocketClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('xionimus_agent.log')
    ]
)
logger = logging.getLogger(__name__)


class XionimusAgent:
    """Main autonomous agent class"""
    
    def __init__(self, backend_url: str, watch_directories: List[str]):
        """
        Initialize Xionimus Agent
        
        Args:
            backend_url: Backend URL (e.g., http://localhost:8001)
            watch_directories: List of Windows directories to monitor
        """
        self.backend_url = backend_url
        self.watch_directories = watch_directories
        self.agent_id = str(uuid.uuid4())
        
        # Initialize components
        self.ws_client = XionimusWebSocketClient(backend_url, self.agent_id)
        self.file_watcher = FileWatcher(self._handle_file_change)
        
        # Register callbacks
        self.ws_client.on_connect(self._on_connected)
        self.ws_client.on_disconnect(self._on_disconnected)
        self.ws_client.on_message(self._on_message_received)
        
        self.running = False
        
    def _on_connected(self):
        """Callback when WebSocket connects"""
        logger.info("✅ Agent connected to backend")
        print("🟢 Xionimus Agent: CONNECTED")
        
    def _on_disconnected(self):
        """Callback when WebSocket disconnects"""
        logger.warning("❌ Agent disconnected from backend")
        print("🔴 Xionimus Agent: DISCONNECTED")
        
    def _on_message_received(self, data: dict):
        """Callback when message received from backend"""
        msg_type = data.get('type', 'unknown')
        logger.info(f"Received message: {msg_type}")
        
        if msg_type == 'analysis_result':
            self._handle_analysis_result(data)
        elif msg_type == 'suggestion':
            self._handle_suggestion(data)
        elif msg_type == 'error':
            self._handle_error(data)
            
    def _handle_analysis_result(self, data: dict):
        """Handle code analysis results from backend"""
        result = data.get('data', {})
        file_path = result.get('file_path', 'unknown')
        issues = result.get('issues', [])
        
        if issues:
            print(f"\n📊 Analysis for {file_path}:")
            for issue in issues:
                severity = issue.get('severity', 'info')
                message = issue.get('message', '')
                print(f"  {severity.upper()}: {message}")
        else:
            logger.debug(f"No issues found in {file_path}")
            
    def _handle_suggestion(self, data: dict):
        """Handle code suggestions from backend"""
        suggestion = data.get('data', {})
        title = suggestion.get('title', 'Suggestion')
        description = suggestion.get('description', '')
        
        print(f"\n💡 {title}")
        print(f"   {description}")
        
    def _handle_error(self, data: dict):
        """Handle error messages from backend"""
        error = data.get('data', {})
        message = error.get('message', 'Unknown error')
        logger.error(f"Backend error: {message}")
        print(f"\n❌ Error: {message}")
    
    def _handle_file_change(self, event_type: str, file_path: str):
        """
        Handle file system events
        
        Args:
            event_type: Type of event (created, modified, deleted)
            file_path: Path to the changed file
        """
        logger.info(f"File {event_type}: {file_path}")
        
        # Read file content for analysis (if not deleted)
        content = None
        if event_type != 'deleted':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
        
        # Send to backend via WebSocket
        asyncio.create_task(
            self.ws_client.send_file_event(event_type, file_path, content)
        )
    
    async def start(self):
        """Start the agent"""
        try:
            logger.info(f"Starting Xionimus Agent (ID: {self.agent_id})")
            print("=" * 60)
            print("🚀 Xionimus Autonomous Agent")
            print("=" * 60)
            print(f"Agent ID: {self.agent_id}")
            print(f"Backend: {self.backend_url}")
            print(f"Watching {len(self.watch_directories)} directories:")
            for directory in self.watch_directories:
                print(f"  📁 {directory}")
            print("=" * 60)
            
            # Add watch directories
            for directory in self.watch_directories:
                success = self.file_watcher.add_directory(directory)
                if not success:
                    logger.warning(f"Failed to add directory: {directory}")
            
            if not self.file_watcher.get_watched_directories():
                logger.error("No valid directories to watch. Exiting.")
                return
            
            # Start file watcher
            self.file_watcher.start()
            
            # Connect to backend
            await self.ws_client.connect()
            
            self.running = True
            
            # Keep running
            print("\n✅ Agent is running. Press Ctrl+C to stop.")
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopping agent...")
            await self.stop()
        except Exception as e:
            logger.error(f"Agent error: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        self.file_watcher.stop()
        await self.ws_client.disconnect()
        logger.info("Agent stopped")
        print("✅ Agent stopped successfully")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Xionimus Autonomous Agent')
    parser.add_argument(
        '--backend',
        default='http://localhost:8001',
        help='Backend URL (default: http://localhost:8001)'
    )
    parser.add_argument(
        '--directories',
        nargs='+',
        help='Directories to watch (Windows paths, e.g., C:\\Users\\YourName\\Projects)'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration file (JSON)'
    )
    
    args = parser.parse_args()
    
    # Get watch directories
    watch_dirs = []
    if args.config:
        # Load from config file
        import json
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                watch_dirs = config.get('watch_directories', [])
                backend_url = config.get('backend_url', args.backend)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return
    elif args.directories:
        watch_dirs = args.directories
        backend_url = args.backend
    else:
        print("❌ Error: No directories specified.")
        print("Usage:")
        print("  python main.py --directories C:\\Users\\YourName\\Projects")
        print("  python main.py --config config.json")
        return
    
    # Create and start agent
    agent = XionimusAgent(backend_url, watch_dirs)
    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
