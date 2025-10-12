"""
Windows-Compatible Uvicorn Server Launcher
==========================================

This launcher fixes common Windows + Python asyncio issues by:
1. Setting the correct event loop policy for Windows
2. Using stable Uvicorn configuration
3. Importing the app after event loop setup

Usage:
    cd backend
    venv\\Scripts\\activate.bat
    python server_launcher.py
"""

import sys
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CRITICAL: Fix Windows Event Loop BEFORE any other imports
if sys.platform == 'win32':
    logger.info("🪟 Windows detected - Applying event loop policy fix")
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    logger.info("✅ WindowsProactorEventLoopPolicy applied")

# Now safe to import FastAPI app and Uvicorn
import uvicorn
from main import app

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🚀 Xionimus AI Backend - Windows Launcher")
    logger.info("=" * 70)
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Python: {sys.version}")
    logger.info("Event Loop Policy: WindowsProactorEventLoopPolicy")
    logger.info("=" * 70)
    
    # Windows-optimized Uvicorn configuration
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable auto-reload for stability
        workers=1,     # Single worker for Windows
        loop="asyncio",
        log_level="info",
        access_log=True
    )
