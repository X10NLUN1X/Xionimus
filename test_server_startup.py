#!/usr/bin/env python3
"""
Minimal backend server startup for testing
Uses only essential imports to avoid dependency issues
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def check_essential_modules():
    """Check if essential modules are available"""
    required_modules = ['fastapi', 'uvicorn']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} is available")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} is missing")
    
    if missing_modules:
        print(f"\n🚨 Missing required modules: {', '.join(missing_modules)}")
        print("Please install with: pip install " + " ".join(missing_modules))
        return False
    
    return True

def test_server_import():
    """Test if the server module can be imported"""
    try:
        print("\n🔄 Testing server import...")
        
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Import the server module
        import server
        print("✅ Server module imported successfully")
        
        # Check if the app is properly configured
        if hasattr(server, 'app'):
            print("✅ FastAPI app is configured")
            return True
        else:
            print("❌ FastAPI app not found in server module")
            return False
            
    except Exception as e:
        print(f"❌ Server import failed: {str(e)}")
        return False

def start_server_test():
    """Start the server for testing"""
    try:
        print("\n🚀 Starting server...")
        import uvicorn
        from server import app
        
        # Start server with minimal configuration
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8001, 
            log_level="info",
            access_log=False
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Server startup failed: {str(e)}")
        return False

def main():
    """Main function to test server startup"""
    print("🔧 XIONIMUS AI - Backend Server Test")
    print("=" * 40)
    
    # Step 1: Check essential modules
    if not check_essential_modules():
        return False
    
    # Step 2: Test server import
    if not test_server_import():
        return False
    
    # Step 3: Offer to start server
    print("\n✅ All tests passed - Server is ready to start")
    response = input("\n🤔 Start the server? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        start_server_test()
    else:
        print("ℹ️  Server not started. Run this script again with 'y' to start.")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)