"""
Alternative Windows-Compatible Uvicorn Server Launcher
======================================================

This launcher uses WindowsSelectorEventLoopPolicy as fallback
for situations where ProactorEventLoopPolicy doesn't work.

Usage:
    cd backend
    venv\Scripts\activate.bat
    python server_alternative.py
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

# CRITICAL: Use alternative event loop policy
if sys.platform == 'win32':
    logger.info("🪟 Windows detected - Applying ALTERNATIVE event loop policy")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    logger.info("✅ WindowsSelectorEventLoopPolicy applied (Fallback)")

# Now safe to import
import uvicorn
from main import app

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🚀 Xionimus AI Backend - Alternative Windows Launcher")
    logger.info("=" * 70)
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Python: {sys.version}")
    logger.info("Event Loop Policy: WindowsSelectorEventLoopPolicy (Alternative)")
    logger.info("=" * 70)
    
    # Use Config for more control
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8001,
        loop="asyncio",
        reload=False,
        workers=1,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    server.run()
