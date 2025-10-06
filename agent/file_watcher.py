"""
File Watcher Service for Windows
Monitors specified directories for file changes and triggers analysis
"""

import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from typing import List, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CodeFileHandler(FileSystemEventHandler):
    """Handles file system events for code files"""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.html', '.css', '.md'}
    
    # Debounce settings (to avoid duplicate events)
    DEBOUNCE_SECONDS = 2
    
    def __init__(self, on_file_change: Callable):
        """
        Initialize the file handler
        
        Args:
            on_file_change: Callback function to call when a file changes
                            Signature: on_file_change(event_type, file_path)
        """
        super().__init__()
        self.on_file_change = on_file_change
        self.last_modified = {}
        
    def _should_process(self, file_path: str) -> bool:
        """Check if file should be processed"""
        # Check extension
        ext = Path(file_path).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            return False
            
        # Check if in node_modules, .git, or other ignored directories
        path_parts = Path(file_path).parts
        ignored_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.next', 'dist', 'build'}
        if any(ignored_dir in path_parts for ignored_dir in ignored_dirs):
            return False
            
        # Debounce - ignore if file was modified very recently
        current_time = time.time()
        last_time = self.last_modified.get(file_path, 0)
        if current_time - last_time < self.DEBOUNCE_SECONDS:
            return False
            
        self.last_modified[file_path] = current_time
        return True
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        if self._should_process(file_path):
            logger.info(f"File modified: {file_path}")
            self.on_file_change("modified", file_path)
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        if self._should_process(file_path):
            logger.info(f"File created: {file_path}")
            self.on_file_change("created", file_path)
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        # Don't check extension for deleted files
        logger.info(f"File deleted: {file_path}")
        self.on_file_change("deleted", file_path)


class FileWatcher:
    """Main file watcher class"""
    
    def __init__(self, on_file_change: Callable):
        """
        Initialize the file watcher
        
        Args:
            on_file_change: Callback function for file changes
        """
        self.on_file_change = on_file_change
        self.observers = []
        self.watched_directories = []
        
    def add_directory(self, directory_path: str):
        """
        Add a directory to watch
        
        Args:
            directory_path: Windows path to watch (e.g., C:\\Users\\username\\Projects)
        """
        # Normalize Windows path
        directory_path = os.path.normpath(directory_path)
        
        if not os.path.exists(directory_path):
            logger.warning(f"Directory does not exist: {directory_path}")
            return False
            
        if not os.path.isdir(directory_path):
            logger.warning(f"Path is not a directory: {directory_path}")
            return False
        
        # Create observer for this directory
        event_handler = CodeFileHandler(self.on_file_change)
        observer = Observer()
        observer.schedule(event_handler, directory_path, recursive=True)
        
        self.observers.append(observer)
        self.watched_directories.append(directory_path)
        
        logger.info(f"Added watch directory: {directory_path}")
        return True
    
    def start(self):
        """Start watching all directories"""
        if not self.observers:
            logger.warning("No directories to watch")
            return False
            
        for observer in self.observers:
            observer.start()
            
        logger.info(f"File watcher started. Monitoring {len(self.watched_directories)} directories.")
        return True
    
    def stop(self):
        """Stop watching all directories"""
        for observer in self.observers:
            observer.stop()
            observer.join()
            
        logger.info("File watcher stopped")
    
    def is_running(self) -> bool:
        """Check if watcher is running"""
        return any(observer.is_alive() for observer in self.observers)
    
    def get_watched_directories(self) -> List[str]:
        """Get list of watched directories"""
        return self.watched_directories.copy()


if __name__ == "__main__":
    # Test the file watcher
    def test_callback(event_type, file_path):
        print(f"Event: {event_type} - File: {file_path}")
    
    watcher = FileWatcher(test_callback)
    
    # Test with a sample directory (will need to be configured)
    # watcher.add_directory("C:\\Users\\YourUsername\\Projects")
    
    print("File watcher test mode. Press Ctrl+C to exit.")
    print("Configure watch directories in production.")
