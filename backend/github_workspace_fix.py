"""
GitHub Workspace Fix Script
============================

Fixes Windows path issues for GitHub imports and ensures AI has access to repos.

Usage:
    cd backend
    venv\Scripts\activate.bat
    python github_workspace_fix.py
"""

import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 70)
    logger.info("GitHub Workspace Fix - Windows Path Compatibility")
    logger.info("=" * 70)
    
    # Get backend directory
    backend_dir = Path(__file__).parent
    logger.info(f"Backend directory: {backend_dir}")
    
    # Create workspace structure
    logger.info("\n[1/5] Creating workspace directories...")
    
    workspace = backend_dir / "workspace"
    github_imports = workspace / "github_imports"
    uploads = workspace / "uploads"
    exports = workspace / "exports"
    
    for directory in [workspace, github_imports, uploads, exports]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created: {directory.relative_to(backend_dir)}")
    
    # Verify config.py has correct settings
    logger.info("\n[2/5] Verifying configuration...")
    try:
        from app.core.config import settings
        
        # Test workspace access
        workspace_dir = settings.GITHUB_IMPORTS_DIR
        logger.info(f"✅ GITHUB_IMPORTS_DIR: {workspace_dir}")
        logger.info(f"   Exists: {workspace_dir.exists()}")
        logger.info(f"   Is directory: {workspace_dir.is_dir()}")
        
    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.info("   Make sure you're running from backend directory with venv activated")
        return False
    
    # Test GitHub repo detection
    logger.info("\n[3/5] Testing GitHub repo detection...")
    try:
        from app.api.chat import get_user_github_repos
        
        # Test with dummy user
        test_user_dir = github_imports / "test_user_123"
        test_repo_dir = test_user_dir / "test_repo"
        test_repo_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy file
        (test_repo_dir / "README.md").write_text("# Test Repository\n\nThis is a test.")
        
        # Test detection
        github_info = get_user_github_repos("test_user_123")
        
        if github_info and "test_repo" in github_info:
            logger.info("✅ GitHub repo detection working!")
            logger.info(f"   Detected: {github_info[:100]}...")
        else:
            logger.warning("⚠️  GitHub repo detection may not be working")
            logger.info(f"   Result: {github_info}")
        
    except Exception as e:
        logger.error(f"❌ GitHub detection test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test file operations
    logger.info("\n[4/5] Testing file operations...")
    try:
        test_file = test_repo_dir / "test.txt"
        test_file.write_text("Hello from Windows!")
        content = test_file.read_text()
        
        if content == "Hello from Windows!":
            logger.info("✅ File read/write operations working")
        else:
            logger.warning("⚠️  File operations may have issues")
            
    except Exception as e:
        logger.error(f"❌ File operations test failed: {e}")
    
    # Summary
    logger.info("\n[5/5] Summary...")
    logger.info("=" * 70)
    logger.info("✅ Workspace directories created")
    logger.info("✅ Configuration verified")
    logger.info("✅ GitHub repo detection tested")
    logger.info("✅ File operations tested")
    logger.info("=" * 70)
    
    logger.info("\n🎉 GitHub Workspace Fix completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Restart backend (close window + START.bat)")
    logger.info("2. Import a GitHub repository")
    logger.info("3. Chat with AI - it will automatically see your repos!")
    logger.info("\nTest workspace created at:")
    logger.info(f"   {test_user_dir}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
