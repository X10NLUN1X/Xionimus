"""
Auto-Setup Module
Automatically fixes common issues on startup
"""
import os
import sys
import subprocess
from pathlib import Path

def auto_install_dependencies():
    """Auto-install missing critical dependencies"""
    
    missing = []
    
    # Check tiktoken
    try:
        import tiktoken
    except ImportError:
        missing.append('tiktoken')
    
    # Check python-magic (different for Windows)
    try:
        import magic
    except (ImportError, OSError):
        if os.name == 'nt':  # Windows
            missing.append('python-magic-bin')
        else:
            missing.append('python-magic')
    
    if missing:
        print("=" * 70)
        print("🔧 AUTO-SETUP: Installing missing dependencies...")
        print("=" * 70)
        
        for package in missing:
            print(f"📦 Installing {package}...")
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package,
                    '--quiet', '--disable-pip-version-check'
                ])
                print(f"✅ {package} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Failed to install {package}: {e}")
                print(f"   Install manually: pip install {package}")
        
        print("=" * 70)
        print("✅ Auto-setup completed!")
        print("⚠️  Backend will continue with available features.")
        print("=" * 70)

def run_auto_setup():
    """Run all auto-setup routines"""
    
    # Only run in development mode
    if os.getenv('ENVIRONMENT', 'development') == 'development':
        try:
            auto_install_dependencies()
        except Exception as e:
            print(f"⚠️ Auto-setup failed: {e}")
            print("   Backend will continue with available features.")
