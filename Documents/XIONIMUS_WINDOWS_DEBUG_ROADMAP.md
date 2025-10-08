# 🔧 XIONIMUS AI - WINDOWS 10/11 DEBUGGING & TESTING ROADMAP

**Project:** Xionimus AI - Multi-Agent AI Development Suite  
**Target Platform:** Windows 10/11 (No Linux Support)  
**Date:** October 8, 2025  
**Status:** Comprehensive Bug Analysis & Testing Plan

---

## 📊 EXECUTIVE SUMMARY

### Current State Analysis
- **Technology Stack:**
  - Backend: Python 3.11+ with FastAPI
  - Frontend: React 18 with TypeScript + Vite
  - Database: MongoDB + SQLite
  - AI Models: Claude, GPT, Perplexity integration
  - WebSocket: Real-time communication
  - Code Execution: Multi-language sandbox (7 languages)

### Critical Issues Identified
- **82 Critical Bugs** (mostly in dependencies)
- **325 Warnings** 
- **19 General Issues**
- **1 Major Incompatibility**

---

## 🔴 PHASE 1: CRITICAL BUG FIXES (Priority: URGENT)

### 1.1 Unix-Specific Module Issues

**Bug Category:** Platform Incompatibility  
**Files Affected:** 
- `backend/app/core/sandbox_executor.py`
- `backend/app/core/supervisor_manager.py`

**Issues:**
```python
# Current problematic code
import resource  # Unix-only module
resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
```

**Fix Required:**
```python
import sys
import platform

# Platform detection
IS_WINDOWS = sys.platform == 'win32'
HAS_RESOURCE = False

if not IS_WINDOWS:
    try:
        import resource
        HAS_RESOURCE = True
    except ImportError:
        pass

# Usage with platform check
if HAS_RESOURCE:
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
else:
    # Windows alternative: Use threading.Timer or subprocess timeout
    pass
```

### 1.2 Path Separator Issues

**Files to Fix:**
- All Python files using hardcoded `/` paths
- Configuration files with Unix paths

**Testing Checklist:**
- [ ] Replace `/tmp/` with `tempfile.gettempdir()`
- [ ] Use `pathlib.Path` for all file operations
- [ ] Replace hardcoded separators with `os.path.sep`
- [ ] Test path resolution on Windows

### 1.3 Subprocess & Process Management

**Critical Files:**
- `backend/app/core/sandbox_executor.py`
- `backend/app/core/code_executor.py`
- `backend/app/services/github_service.py`

**Issues to Fix:**
```python
# Unix-specific
subprocess.run(['ls', '-la'])  
subprocess.run('grep pattern file', shell=True)
os.fork()  # Not available on Windows
```

**Windows-Compatible Solutions:**
```python
# Cross-platform alternatives
subprocess.run(['cmd', '/c', 'dir'])  # Windows
subprocess.run(['powershell', '-Command', 'Get-ChildItem'])
# Use multiprocessing.Process instead of fork()
```

---

## 🟡 PHASE 2: DATABASE & STORAGE TESTING

### 2.1 MongoDB Connection Testing
```python
# Test MongoDB connection on Windows
def test_mongodb_windows():
    """Test MongoDB connectivity on Windows"""
    from pymongo import MongoClient
    
    # Windows MongoDB default path
    client = MongoClient('mongodb://localhost:27017/')
    
    # Test operations
    db = client.xionimus_test
    collection = db.test_collection
    
    # CRUD operations test
    test_doc = {"platform": "Windows", "test": True}
    insert_result = collection.insert_one(test_doc)
    assert insert_result.inserted_id
    
    # Cleanup
    collection.delete_one({"_id": insert_result.inserted_id})
    client.close()
```

### 2.2 SQLite Path Issues
- [ ] Fix relative path issues in SQLite connections
- [ ] Use absolute paths: `sqlite:///C:/xionimus/data.db`
- [ ] Test database migrations on Windows
- [ ] Verify file locking behavior

---

## 🟢 PHASE 3: API & NETWORK TESTING

### 3.1 CORS Configuration
**File:** `backend/main.py`

```python
# Ensure proper CORS for Windows development
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3.2 WebSocket Testing
```python
# Windows WebSocket test suite
async def test_websocket_windows():
    """Test WebSocket on Windows with proper error handling"""
    import asyncio
    
    # Set Windows event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )
    
    # Test WebSocket connection
    # Handle Windows-specific socket errors
```

### 3.3 API Endpoint Testing Matrix

| Endpoint | Method | Windows Test | Status |
|----------|--------|-------------|--------|
| `/health` | GET | Basic connectivity | 🔄 |
| `/auth/login` | POST | JWT generation | 🔄 |
| `/agents/*` | ALL | Agent routing | 🔄 |
| `/sandbox/execute` | POST | Code execution | 🔄 |
| `/research/*` | POST | Perplexity integration | 🔄 |
| `/github/*` | ALL | GitHub operations | 🔄 |
| `/ws/agent` | WS | WebSocket stability | 🔄 |

---

## 🔵 PHASE 4: CODE EXECUTION SANDBOX

### 4.1 Windows Sandbox Implementation

**Current Issues:**
- Resource limits not available (no `resource` module)
- Process isolation different on Windows
- Signal handling limitations

**Windows-Safe Implementation:**
```python
import subprocess
import threading
import psutil
import os

class WindowsSandboxExecutor:
    def __init__(self):
        self.timeout = 10  # seconds
        self.memory_limit = 512 * 1024 * 1024  # 512MB
        
    def execute_code(self, language, code):
        """Execute code safely on Windows"""
        
        # Language-specific commands for Windows
        commands = {
            'python': ['python', '-c', code],
            'javascript': ['node', '-e', code],
            'bash': ['powershell', '-Command', code],  # PowerShell instead
            'c': self._compile_and_run_c,
            'cpp': self._compile_and_run_cpp,
            'csharp': ['csc', '/nologo', '-'],  # C# compiler
            'perl': ['perl', '-e', code]
        }
        
        # Use subprocess with timeout
        try:
            result = subprocess.run(
                commands[language],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                creationflags=subprocess.CREATE_NO_WINDOW  # Windows-specific
            )
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return None, "Execution timeout"
```

### 4.2 Language-Specific Testing

**Test Matrix:**

| Language | Windows Command | Test Case | Status |
|----------|----------------|-----------|---------|
| Python | `python -c` | Hello World | 🔄 |
| JavaScript | `node -e` | Console.log | 🔄 |
| PowerShell | `powershell -Command` | Write-Host | 🔄 |
| C | `gcc` + execute | Basic program | 🔄 |
| C++ | `g++` + execute | STL usage | 🔄 |
| C# | `csc` or `dotnet` | Console app | 🔄 |
| Perl | `perl -e` | Print statement | 🔄 |

---

## 🟣 PHASE 5: FRONTEND TESTING

### 5.1 Build Process
```bash
# Windows build commands
cd frontend
npm install  # or yarn install
npm run build  # Vite build for production
npm run dev    # Development server
```

### 5.2 Path Resolution Issues
- [ ] Fix relative imports in TypeScript
- [ ] Verify asset loading on Windows
- [ ] Test hot module replacement (HMR)
- [ ] Check WebSocket connection to backend

### 5.3 Environment Variables
```javascript
// Windows-safe environment variable handling
const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace('http', 'ws') + '/ws';
```

---

## 🟠 PHASE 6: INTEGRATION TESTING

### 6.1 End-to-End Test Suite
```python
# Comprehensive Windows E2E test
import pytest
import asyncio
import sys

class TestWindowsIntegration:
    @pytest.fixture
    def setup_windows_env(self):
        """Setup Windows test environment"""
        if sys.platform != 'win32':
            pytest.skip("Windows-only test")
        
        # Set event loop policy
        asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy()
        )
        
    def test_full_workflow(self, setup_windows_env):
        """Test complete user workflow on Windows"""
        # 1. Start backend
        # 2. Start frontend
        # 3. Login
        # 4. Create chat
        # 5. Test each agent
        # 6. Execute code in sandbox
        # 7. GitHub operations
        # 8. Export/Import
        pass
```

### 6.2 Performance Testing
- [ ] Memory usage monitoring
- [ ] CPU usage under load
- [ ] WebSocket stability (1000+ messages)
- [ ] Concurrent user testing
- [ ] Database query performance

---

## 🔴 PHASE 7: SECURITY TESTING

### 7.1 Windows-Specific Security
```python
# Security checks for Windows
def security_audit_windows():
    checks = {
        "file_permissions": check_file_permissions_windows(),
        "api_key_storage": verify_encrypted_storage(),
        "sandbox_isolation": test_sandbox_escape_prevention(),
        "path_traversal": test_path_traversal_protection(),
        "dll_injection": test_dll_injection_prevention(),
    }
    return checks
```

### 7.2 Vulnerability Testing
- [ ] SQL Injection tests
- [ ] XSS prevention
- [ ] CSRF token validation
- [ ] JWT token security
- [ ] Rate limiting effectiveness
- [ ] File upload restrictions

---

## 🟢 PHASE 8: DEPLOYMENT READINESS

### 8.1 Windows Installer Creation
```batch
@echo off
REM Windows installer script
echo Installing Xionimus AI...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.11+ required
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js 18+ required
    exit /b 1
)

REM Install backend
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements-windows.txt

REM Install frontend
cd ../frontend
npm install
npm run build

echo Installation complete!
```

### 8.2 Service Configuration
```python
# Windows service setup
import win32serviceutil
import win32service

class XionimusWindowsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "XionimusAI"
    _svc_display_name_ = "Xionimus AI Service"
    
    def SvcDoRun(self):
        # Start FastAPI server
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000)
```

---

## 📋 TESTING CHECKLIST

### Pre-Testing Setup
- [ ] Windows 10/11 clean environment
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] MongoDB installed and running
- [ ] Git for Windows installed
- [ ] Visual C++ Build Tools (for compilations)

### Critical Path Testing
- [ ] Fresh installation from GitHub
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] User registration/login works
- [ ] All 8 agents respond correctly
- [ ] Code execution in all 7 languages
- [ ] WebSocket maintains connection
- [ ] File upload/download works
- [ ] PDF export functions (if WeasyPrint available)
- [ ] GitHub integration works
- [ ] MongoDB persistence verified
- [ ] Session management stable

### Regression Testing
- [ ] Previous bugs remain fixed
- [ ] No new errors in console
- [ ] Performance acceptable
- [ ] Memory leaks checked
- [ ] Error handling robust

---

## 🎯 SUCCESS CRITERIA

### Functionality (100% Required)
- ✅ All core features work on Windows 10/11
- ✅ No crashes during normal operation
- ✅ All APIs respond correctly
- ✅ WebSocket stable for 1+ hour
- ✅ Code execution works for all languages

### Performance Targets
- Response time: <500ms for API calls
- Memory usage: <1GB for backend
- CPU usage: <20% idle, <80% active
- Concurrent users: 10+ supported
- WebSocket latency: <100ms

### Reliability Metrics
- Uptime: 99.9% over 24 hours
- Error rate: <0.1% of requests
- Recovery time: <5 seconds after crash
- Data integrity: 100% maintained

---

## 🚀 FINAL DEPLOYMENT VALIDATION

### Production Readiness Checklist
1. [ ] All critical bugs fixed
2. [ ] All tests passing (100%)
3. [ ] Documentation updated
4. [ ] Installation guide verified
5. [ ] Performance benchmarks met
6. [ ] Security audit passed
7. [ ] Backup/restore tested
8. [ ] Monitoring configured
9. [ ] Error logging active
10. [ ] Rollback plan ready

### Sign-Off Requirements
- [ ] Developer testing complete
- [ ] QA testing passed
- [ ] User acceptance testing done
- [ ] Performance testing satisfactory
- [ ] Security review approved

---

## 📝 NOTES & RECOMMENDATIONS

### Known Limitations on Windows
1. **Resource Limits**: Cannot use Unix `resource` module - use alternatives
2. **Signal Handling**: Limited to Windows-compatible signals
3. **File Locking**: Different behavior than Unix
4. **Path Length**: Max 260 characters (unless long paths enabled)
5. **Process Management**: No fork(), use multiprocessing

### Best Practices
1. Always use `pathlib.Path` for file operations
2. Set Windows event loop policy for asyncio
3. Handle Windows-specific exceptions
4. Test with both forward and backslashes
5. Use cross-platform libraries when possible

### Recommended Tools
- **Testing**: pytest with Windows markers
- **Monitoring**: Windows Performance Monitor
- **Logging**: Windows Event Log integration
- **Deployment**: NSSM for service management
- **Installer**: NSIS or WiX for MSI creation

---

**Document Version:** 1.0  
**Last Updated:** October 8, 2025  
**Next Review:** After Phase 1 completion

---

## IMMEDIATE ACTION ITEMS

1. **Fix critical platform incompatibilities** (Week 1)
2. **Update subprocess commands for Windows** (Week 1)
3. **Test all code execution languages** (Week 2)
4. **Verify WebSocket stability** (Week 2)
5. **Complete integration testing** (Week 3)
6. **Security audit** (Week 3)
7. **Performance optimization** (Week 4)
8. **Final validation** (Week 4)

**Target Completion: 4 weeks for 100% Windows compatibility**
