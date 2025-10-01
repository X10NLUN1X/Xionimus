#!/usr/bin/env python3
"""
Auto Browser Opener für Xionimus AI
Öffnet automatisch den Browser nach Backend-Start
"""
import time
import sys
import webbrowser
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"
MAX_WAIT_TIME = 120  # 2 minutes
CHECK_INTERVAL = 2  # seconds

def print_banner():
    """Print startup banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║              🚀  XIONIMUS AI - AUTO STARTER  🚀               ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)
    logger.info("Starting Xionimus AI Auto Browser Opener...")

def check_backend_health():
    """Check if backend is ready"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def check_frontend_ready():
    """Check if frontend is ready"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def open_browser():
    """Open Xionimus AI in browser"""
    logger.info(f"🌐 Opening Xionimus AI in browser: {FRONTEND_URL}")
    try:
        webbrowser.open(FRONTEND_URL)
        logger.info("✅ Browser opened successfully!")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Could not open browser automatically: {e}")
        logger.info(f"📍 Please open manually: {FRONTEND_URL}")
        return False

def print_ready_message():
    """Print ready message with URL"""
    message = f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                                 ║
║                     ✅  XIONIMUS AI READY!  ✅                ║
║                                                                 ║
║  🌐 Frontend:  {FRONTEND_URL}                      ║
║  🔧 Backend:   {BACKEND_URL}                      ║
║                                                                 ║
║  💡 Tip: Auto-öffnet sich im Browser (falls lokal)            ║
║  📱 In Cloud: Öffne die URL manuell                            ║
║                                                                 ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(message)

def wait_for_services():
    """Wait for backend and frontend to be ready"""
    logger.info("⏳ Waiting for Xionimus AI services to start...")
    
    start_time = time.time()
    backend_ready = False
    frontend_ready = False
    
    while time.time() - start_time < MAX_WAIT_TIME:
        # Check backend
        if not backend_ready:
            if check_backend_health():
                logger.info("✅ Backend is ready!")
                backend_ready = True
        
        # Check frontend
        if not frontend_ready:
            if check_frontend_ready():
                logger.info("✅ Frontend is ready!")
                frontend_ready = True
        
        # Both ready?
        if backend_ready and frontend_ready:
            logger.info("🎉 All services ready!")
            return True
        
        # Status update
        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0 and elapsed > 0:  # Every 10 seconds
            status = []
            if not backend_ready:
                status.append("Backend: ⏳")
            if not frontend_ready:
                status.append("Frontend: ⏳")
            logger.info(f"Status ({elapsed}s): {', '.join(status)}")
        
        time.sleep(CHECK_INTERVAL)
    
    logger.error(f"❌ Timeout after {MAX_WAIT_TIME}s - Services not ready")
    return False

def main():
    """Main function"""
    print_banner()
    
    # Wait for services
    if wait_for_services():
        # Small delay to ensure everything is stable
        time.sleep(2)
        
        # Print ready message
        print_ready_message()
        
        # Try to open browser
        open_browser()
        
        logger.info("✅ Auto browser opener completed successfully!")
        return 0
    else:
        logger.error("❌ Services did not start in time")
        return 1

if __name__ == "__main__":
    sys.exit(main())
