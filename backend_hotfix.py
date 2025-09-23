#!/usr/bin/env python3
"""Emergency hotfix for XIONIMUS AI backend - Updated with all critical fixes applied"""

import os
import sys
from pathlib import Path

def verify_fixes():
    """Verify that all critical fixes have been applied"""
    
    backend_dir = Path(__file__).parent / "backend"
    
    print("🔍 Verifying all critical fixes are applied...")
    
    # Verify Claude model names are correct
    agent_files = ['agents/code_agent.py', 'agents/data_agent.py', 'agents/writing_agent.py']
    correct_model = "claude-3-5-sonnet-20241022"
    incorrect_model = "claude-sonnet-4-20250514"
    
    model_fixes_ok = True
    for file_path in agent_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            content = full_path.read_text()
            if incorrect_model in content:
                print(f"❌ {file_path} still has incorrect model name")
                model_fixes_ok = False
            elif correct_model in content:
                print(f"✅ {file_path} has correct model name")
            else:
                print(f"⚠️ {file_path} model name unclear")
    
    # Verify API validation improvements
    server_path = backend_dir / 'server.py'
    api_validation_ok = False
    if server_path.exists():
        content = server_path.read_text()
        if "configured_keys = []" in content and "startswith('sk-ant-')" in content:
            print("✅ API key validation improved")
            api_validation_ok = True
        else:
            print("❌ API key validation not improved")
    
    # Verify path resolution fixes
    path_fixes_ok = True
    for agent_file in ['agents/file_agent.py', 'agents/session_agent.py']:
        full_path = backend_dir / agent_file
        if full_path.exists():
            content = full_path.read_text()
            if "Path.cwd()" in content:
                print(f"❌ {agent_file} still uses Path.cwd()")
                path_fixes_ok = False
            elif "os.path.dirname(os.path.dirname(__file__))" in content:
                print(f"✅ {agent_file} path resolution fixed")
            else:
                print(f"⚠️ {agent_file} path resolution unclear")
    
    # Verify MongoDB retry logic
    mongodb_fixes_ok = False
    if server_path.exists():
        content = server_path.read_text()
        if "get_mongodb_client" in content and "serverSelectionTimeoutMS" in content:
            print("✅ MongoDB retry logic added")
            mongodb_fixes_ok = True
        else:
            print("❌ MongoDB retry logic not found")
    
    # Verify error handling improvements
    error_handling_ok = False
    if server_path.exists():
        content = server_path.read_text()
        if "anthropic.APIError" in content and "openai.APIError" in content:
            print("✅ Improved error handling added")
            error_handling_ok = True
        else:
            print("❌ Improved error handling not found")
    
    # Verify CORS improvements
    cors_fixes_ok = False
    if server_path.exists():
        content = server_path.read_text()
        if "ALLOWED_ORIGINS = [" in content:
            print("✅ CORS configuration improved")
            cors_fixes_ok = True
        else:
            print("❌ CORS configuration not improved")
    
    all_fixes_ok = all([
        model_fixes_ok, 
        api_validation_ok, 
        path_fixes_ok, 
        mongodb_fixes_ok,
        error_handling_ok,
        cors_fixes_ok
    ])
    
    return all_fixes_ok

def create_safe_env():
    """Create a safe .env file with correct defaults"""
    
    backend_dir = Path(__file__).parent / "backend"
    env_path = backend_dir / '.env'
    
    # Create backend directory if it doesn't exist
    backend_dir.mkdir(exist_ok=True)
    
    if not env_path.exists():
        env_content = """# XIONIMUS AI Backend Configuration
MONGO_URL="mongodb://localhost:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="http://localhost:3000,http://localhost:3001"

# Add your API keys here (replace with actual values):
# PERPLEXITY_API_KEY=pplx-your_key_here
# ANTHROPIC_API_KEY=sk-ant-your_key_here
# OPENAI_API_KEY=sk-your_key_here

# Security Configuration
# ENCRYPTION_KEY=your_encryption_key_here_for_future_use
"""
        env_path.write_text(env_content)
        print("✅ Created .env file with safe defaults")
        return True
    else:
        print("ℹ️ .env file already exists")
        return True

def validate_backend_startup():
    """Test that the backend can import without errors"""
    
    print("\n🧪 Testing backend import and startup...")
    
    backend_dir = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
    try:
        # Test imports
        print("  Importing agents...")
        from agents.code_agent import CodeAgent
        from agents.data_agent import DataAgent
        from agents.writing_agent import WritingAgent
        from agents.agent_manager import AgentManager
        print("  ✅ Agent imports successful")
        
        # Test agent instantiation
        print("  Testing agent instantiation...")
        code_agent = CodeAgent()
        data_agent = DataAgent()
        writing_agent = WritingAgent()
        print("  ✅ Agent instantiation successful")
        
        # Test agent manager
        print("  Testing agent manager...")
        manager = AgentManager()
        available_agents = manager.get_available_agents()
        print(f"  ✅ Agent manager created with {len(available_agents)} agents")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Backend startup test failed: {e}")
        return False

def main():
    """Apply hotfixes and verify system"""
    print("🚀 XIONIMUS AI Hotfix Verification Tool")
    print("=" * 50)
    
    # Verify all fixes are applied
    fixes_ok = verify_fixes()
    
    # Create safe environment
    env_ok = create_safe_env()
    
    # Test backend startup
    startup_ok = validate_backend_startup()
    
    print("\n📊 Hotfix Verification Summary:")
    print("=" * 50)
    print(f"Critical Fixes Applied: {'✅ YES' if fixes_ok else '❌ NO'}")
    print(f"Environment Setup:      {'✅ YES' if env_ok else '❌ NO'}")
    print(f"Backend Startup Test:   {'✅ YES' if startup_ok else '❌ NO'}")
    print("=" * 50)
    
    if all([fixes_ok, env_ok, startup_ok]):
        print("🎉 All hotfixes verified successfully!")
        print("\n📋 Next Steps:")
        print("1. Ensure MongoDB is running (mongodb://localhost:27017)")
        print("2. Add your API keys to backend/.env file:")
        print("   - ANTHROPIC_API_KEY=sk-ant-your_key_here")
        print("   - PERPLEXITY_API_KEY=pplx-your_key_here")
        print("   - OPENAI_API_KEY=sk-your_key_here")
        print("3. Start the backend: cd backend && python -m uvicorn server:app --reload")
        print("4. Start the frontend: cd frontend && npm start")
        return True
    else:
        print("❌ Some issues need attention before starting the system")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)