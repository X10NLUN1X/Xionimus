# 🎯 Windows Testing Protocol & Validation Plan

## Overview

This document provides a comprehensive testing protocol to ensure Xionimus AI runs stably and reliably on Windows 10/11 systems.

---

## 📋 PRE-TESTING CHECKLIST

### System Requirements Verification

```powershell
# Verify before starting
- [ ] Windows 10 (Build 19041+) or Windows 11
- [ ] Python 3.11+ installed and in PATH
- [ ] Node.js 18+ installed
- [ ] MongoDB Community Edition running as service
- [ ] Git for Windows installed
- [ ] Visual C++ Build Tools (for C/C++ compilation)
- [ ] At least 8GB RAM available
- [ ] 10GB free disk space
```

### Quick System Check

```powershell
# Run these commands to verify system readiness
python --version          # Should show 3.11+
node --version           # Should show 18+
npm --version            # Should be available
git --version            # Should be available
mongo --version          # Should show MongoDB version
```

---

## 🚀 PHASE 1: Initial Setup & Fixes

### Step 1: Clone Repository

```powershell
# Clone the project
git clone https://github.com/X10NLUN1X/Xionimus.git
cd Xionimus
```

### Step 2: Run Auto-Fixer

```powershell
# CRITICAL: Run this BEFORE installation
python Documents\xionimus_windows_fixer.py

# Check the output for:
# ✓ Fixes Applied: X
# ✗ Fixes Failed: Y (should be 0)
```

**Expected Output:**
```
================================================================================
XIONIMUS AI - WINDOWS COMPATIBILITY FIXES
================================================================================
✓ Fixes Applied: 9
  • sandbox_executor.py
  • Path issues in 2 files
  • Subprocess fixes in 8 files
  ...
```

### Step 3: Document Any Errors

If the fixer reports failures, note them here:
```
Error 1: [Description]
File: [File path]
Line: [Line number]
```

---

## 🔧 PHASE 2: Installation Validation

### Step 4: Run Windows Installation

```powershell
# Run the automated installer
install-windows.bat

# Monitor for errors during:
# - Python virtual environment creation
# - Backend dependencies installation
# - Frontend dependencies installation
# - MongoDB connection test
```

**Watch for These Errors:**
- `ERROR: Could not install packages`
- `Permission denied`
- `Command not found`
- `Network error`

### Step 5: Configure Environment

```powershell
# Edit backend/.env file
notepad backend\.env

# Add your API keys:
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-proj-...
# PERPLEXITY_API_KEY=pplx-...
# GITHUB_OAUTH_CLIENT_ID=...
# GITHUB_OAUTH_CLIENT_SECRET=...
```

**Verify Paths:**
```powershell
# Check that paths use Windows format
# Correct: C:\Users\YourName\Xionimus
# Incorrect: /c/Users/YourName/Xionimus
```

---

## 🧪 PHASE 3: Component Testing

### Step 6: Run Comprehensive Test Suite

```powershell
# Run the full test suite
python Documents\xionimus_windows_test_suite.py > test_results.log 2>&1

# Or run with real-time output:
python Documents\xionimus_windows_test_suite.py
```

**Test Categories (16 total):**
1. Environment Configuration
2. Backend Module Imports
3. Database Connectivity
4. API Endpoints
5. Agent System
6. Code Execution Sandbox
7. Frontend Build
8. WebSocket Communication
9. Authentication System
10. Session Management
11. GitHub Integration
12. Research Features
13. PDF Export
14. Performance Tests
15. Security Tests
16. Integration Tests

### Step 7: Review Test Results

```powershell
# Check the generated report
type test_results.log | findstr /C:"PASSED" /C:"FAILED"

# Or view the JSON report
type windows_test_report.json
```

**Success Criteria:**
- ✅ All CRITICAL tests must pass
- ⚠️ HIGH priority tests should pass
- ℹ️ MEDIUM/LOW priority can be addressed later

---

## 🔍 KEY AREAS TO MONITOR

### 1. Backend Startup Issues

**Common Errors to Watch For:**

```python
# Error 1: Resource module
ModuleNotFoundError: No module named 'resource'
# Fix: Already handled by fixer script

# Error 2: Fork not available
AttributeError: module 'os' has no attribute 'fork'
# Fix: Already handled by fixer script

# Error 3: Path errors
FileNotFoundError: [Errno 2] No such file or directory: '/tmp/...'
# Fix: Already handled by fixer script
```

**Quick Debug Commands:**

```powershell
# Check Python platform
cd backend
python -c "import sys; print(f'Platform: {sys.platform}')"
# Should output: Platform: win32

# Test imports
python -c "import app.core.sandbox_executor; print('✓ Sandbox OK')"
python -c "import app.core.base_agent; print('✓ Agents OK')"
python -c "import app.api.chat; print('✓ Chat OK')"

# Run backend with debug logging
$env:DEBUG="True"
python main.py
```

### 2. Agent Testing Matrix

Test each of the 8 specialized agents:

| Agent | Test Query | Expected Result | Status |
|-------|------------|-----------------|--------|
| **Research** | "Research quantum computing trends" | Perplexity response with citations | [ ] |
| **Code Review** | Submit Python code snippet | Quality score + security analysis | [ ] |
| **Testing** | "Generate tests for this function" | Unit test cases created | [ ] |
| **Documentation** | "Generate API docs" | Markdown documentation | [ ] |
| **Debugging** | Submit buggy code | Root cause + fix suggestions | [ ] |
| **Security** | "Scan for vulnerabilities" | Security issues identified | [ ] |
| **Performance** | "Optimize this code" | Performance suggestions | [ ] |
| **Fork** | "Create GitHub fork" | GitHub operations successful | [ ] |

**Test Script:**

```powershell
# Test each agent programmatically
python -c "
import requests
import json

BASE_URL = 'http://localhost:8001/api'
TOKEN = 'your_jwt_token_here'

agents_to_test = ['research', 'code_review', 'debugging', 'documentation']

for agent in agents_to_test:
    response = requests.post(
        f'{BASE_URL}/agents/{agent}',
        headers={'Authorization': f'Bearer {TOKEN}'},
        json={'query': 'Test query'}
    )
    print(f'{agent}: {response.status_code}')
"
```

### 3. Code Execution Sandbox

Test all 7 supported languages:

```powershell
# Create test file
$test_code = @'
{
  "python": "print('Hello Windows from Python')",
  "javascript": "console.log('Hello Windows from JS')",
  "powershell": "Write-Host 'Hello Windows from PowerShell'",
  "c": "#include <stdio.h>\nint main() { printf(\"Hello Windows from C\"); return 0; }",
  "cpp": "#include <iostream>\nint main() { std::cout << \"Hello Windows from C++\"; }",
  "csharp": "class Program { static void Main() { System.Console.WriteLine(\"Hello Windows from C#\"); }}",
  "perl": "print \"Hello Windows from Perl\""
}
'@

$test_code | Out-File -Encoding utf8 test_sandbox.json

# Test each language
python -c "
import json
with open('test_sandbox.json') as f:
    tests = json.load(f)
    for lang, code in tests.items():
        print(f'Testing {lang}...')
        # Test execution here
"
```

**Expected Results:**
- ✅ All languages execute successfully
- ✅ Output captured correctly
- ✅ Errors handled gracefully
- ✅ Timeouts work properly
- ✅ Resource limits enforced

### 4. WebSocket Stability

**Monitor WebSocket connection:**

```powershell
# Start backend and monitor logs
$env:DEBUG="True"
cd backend
python main.py

# In another terminal, test WebSocket
python -c "
import asyncio
import websockets

async def test_ws():
    uri = 'ws://localhost:8001/ws/chat'
    async with websockets.connect(uri) as ws:
        await ws.send('Hello')
        response = await ws.recv()
        print(f'Received: {response}')

asyncio.run(test_ws())
"
```

**Watch For:**
- ❌ "WebSocket connection reset"
- ❌ "ConnectionResetError"
- ❌ Frequent reconnection attempts
- ❌ Timeout errors

**Success Criteria:**
- ✅ Connection stable for 1+ hour
- ✅ Messages sent/received reliably
- ✅ Graceful reconnection on failure

---

## 📊 PERFORMANCE BENCHMARKS

### Test 1: Concurrent Users

```powershell
# Test 10 concurrent connections
python -c "
import asyncio
import aiohttp

async def test_concurrent():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(10):
            task = session.post(
                'http://localhost:8001/api/chat',
                json={'message': f'Test {i}'}
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        print(f'Completed {len(results)} concurrent requests')

asyncio.run(test_concurrent())
"
```

**Expected Results:**
- All requests complete successfully
- Average response time < 500ms
- No crashes or errors

### Test 2: Memory Usage Monitor

```powershell
# Monitor memory usage
while ($true) {
    Get-Process python | Select-Object Name, 
        @{Name='Memory(MB)';Expression={[math]::Round($_.WorkingSet / 1MB, 2)}},
        @{Name='CPU(%)';Expression={$_.CPU}}
    Start-Sleep -Seconds 5
}
```

**Watch For:**
- Memory leaks (constantly increasing memory)
- Excessive CPU usage (>80% sustained)
- Process crashes

### Test 3: Response Time Test

```powershell
# Measure API response times
$times = @()
for ($i=1; $i -le 100; $i++) {
    $start = Get-Date
    Invoke-RestMethod -Uri "http://localhost:8001/api/health" -Method GET
    $end = Get-Date
    $times += ($end - $start).TotalMilliseconds
}

$avg = ($times | Measure-Object -Average).Average
Write-Host "Average response time: $avg ms"
```

**Success Criteria:**
- Average response time < 500ms
- 95th percentile < 1000ms
- No timeouts

---

## 🚨 COMMON WINDOWS-SPECIFIC ISSUES

### Issue 1: Path Length Limit

**Symptom:** `OSError: [WinError 206] The filename or extension is too long`

**Solution:**
```powershell
# Enable long paths (Run as Administrator)
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" `
    -Value 1 `
    -PropertyType DWORD `
    -Force

# Restart computer
Restart-Computer
```

### Issue 2: Permission Denied

**Symptom:** `PermissionError: [WinError 5] Access is denied`

**Solutions:**
```powershell
# Option 1: Run as Administrator
# Right-click Command Prompt → "Run as administrator"

# Option 2: Use user directory
# Install to: C:\Users\YourName\Xionimus
# NOT: C:\Program Files\Xionimus

# Option 3: Set folder permissions
icacls "C:\path\to\Xionimus" /grant Everyone:(OI)(CI)F /T
```

### Issue 3: Port Already in Use

**Symptom:** `OSError: [WinError 10048] Only one usage of each socket address`

**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# Kill the process using the port
taskkill /PID <process_id> /F

# Or change port in .env file
```

### Issue 4: Antivirus Blocking

**Symptom:** Random failures, especially with file operations

**Solution:**
```powershell
# Add Windows Defender exclusions (Run as Administrator)
Add-MpPreference -ExclusionPath "C:\path\to\Xionimus"
Add-MpPreference -ExclusionProcess "python.exe"
Add-MpPreference -ExclusionProcess "node.exe"
```

### Issue 5: SSL Certificate Issues

**Symptom:** `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Solution:**
```powershell
# Option 1: Install certificates
pip install --upgrade certifi

# Option 2: Disable SSL verification (development only!)
$env:PYTHONHTTPSVERIFY="0"

# Option 3: Use HTTP locally (backend/.env)
# Change URLs from https:// to http://
```

### Issue 6: MongoDB Service Not Running

**Symptom:** `pymongo.errors.ServerSelectionTimeoutError: localhost:27017`

**Solution:**
```powershell
# Check MongoDB service status
Get-Service MongoDB

# Start MongoDB service
net start MongoDB

# If not installed as service, run manually:
& "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath C:\data\db
```

---

## 📝 DATA TO COLLECT FOR DEBUGGING

When issues occur, collect this information:

### 1. System Information

```powershell
# Save system info
systeminfo > system_info.txt
python --version >> system_info.txt
node --version >> system_info.txt
npm --version >> system_info.txt
git --version >> system_info.txt

# Save installed packages
pip list > pip_packages.txt
npm list -g --depth=0 > npm_packages.txt
```

### 2. Error Logs

```powershell
# Backend logs
Get-Content backend\logs\*.log | Out-File all_backend_logs.txt

# Test results
Get-Content test_results.log
Get-Content windows_test_report.json

# Console output with errors
# Copy from terminal or redirect output
```

### 3. Failure Context

Document:
- ✍️ Exact error message and full stack trace
- ⏱️ When the error occurred
- 🔄 What action triggered the error
- 📊 Whether it's consistent or intermittent
- 🔍 Any patterns noticed
- 💻 System state (CPU, memory usage)

**Template:**
```
ERROR REPORT
============
Date/Time: [timestamp]
Component: [backend/frontend/agent/etc]
Action: [what you were doing]
Error: [full error message]
Stack Trace: [full stack trace]
Reproducible: [yes/no/sometimes]
System Load: [CPU%, Memory%]
```

---

## 🔄 ITERATIVE DEBUGGING PROCESS

```
┌──────────────┐
│  1. Run Test │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ 2. Identify Issue│
└──────┬───────────┘
       │
       ▼
┌──────────────┐
│ 3. Apply Fix │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  4. Re-test  │
└──────┬───────┘
       │
       ▼
┌───────────────────┐
│ 5. Document Issue │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ 6. Update Scripts │
└───────────────────┘
```

**Best Practices:**
1. Test one component at a time
2. Document every fix applied
3. Re-run full test suite after fixes
4. Keep original error logs
5. Track fix success rate

---

## 📞 WHEN TO REPORT ISSUES

### Critical Blockers (Report Immediately)

- 🔴 Application won't start
- 🔴 Complete data loss
- 🔴 Security vulnerabilities
- 🔴 Crashes on startup

**Report With:**
- Full error logs
- System information
- Steps to reproduce
- Screenshots if applicable

### Feature Failures (Report After Initial Debugging)

- 🟡 Specific agents not working
- 🟡 Code execution failures
- 🟡 WebSocket disconnections
- 🟡 Database errors

**Report With:**
- Which feature failed
- Test results
- Any patterns observed
- Attempted solutions

### Performance Issues (Report After Benchmarking)

- 🟢 Slow response times
- 🟢 High memory usage
- 🟢 CPU spikes
- 🟢 Long loading times

**Report With:**
- Performance metrics
- Load conditions
- Resource usage graphs
- Comparison to Linux

---

## 🎯 VALIDATION CHECKLIST

Before considering production-ready on Windows:

### Core Functionality
- [ ] Backend starts without errors
- [ ] Frontend builds and loads
- [ ] Database connection established
- [ ] Authentication system works
- [ ] Session management functional

### Agent System
- [ ] All 8 agents respond correctly
- [ ] Research agent returns citations
- [ ] Code review provides analysis
- [ ] Debugging generates fixes
- [ ] Documentation creates docs
- [ ] Testing generates test cases
- [ ] Security identifies issues
- [ ] Performance gives suggestions
- [ ] Fork agent works with GitHub

### Code Execution
- [ ] Python execution works
- [ ] JavaScript execution works
- [ ] PowerShell execution works
- [ ] C compilation works
- [ ] C++ compilation works
- [ ] C# compilation works
- [ ] Perl execution works

### Stability
- [ ] WebSocket stable for 1+ hour
- [ ] No memory leaks after 24 hours
- [ ] Can handle 10+ concurrent users
- [ ] No crashes in 100 operations
- [ ] Graceful error handling

### Integration
- [ ] GitHub OAuth works
- [ ] GitHub import/export works
- [ ] API keys save correctly
- [ ] Research history persists
- [ ] PDF export functional

### Performance
- [ ] API response < 500ms average
- [ ] Memory usage < 2GB
- [ ] CPU usage < 50% idle
- [ ] No timeout errors
- [ ] Fast frontend loading

---

## 💡 OPTIMIZATION TIPS

### 1. Enable Windows Long Paths

```powershell
# Run as Administrator
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
    -Name "LongPathsEnabled" `
    -Value 1 `
    -PropertyType DWORD `
    -Force

# Restart required
Restart-Computer
```

### 2. Optimize Python for Windows

```powershell
# Set encoding
[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "User")

# Optimize pip
pip config set global.cache-dir "%LOCALAPPDATA%\pip\Cache"

# Use faster package resolver
pip install --upgrade pip
```

### 3. Configure Windows Defender

```powershell
# Run as Administrator
# Add exclusions for better performance
Add-MpPreference -ExclusionPath "C:\Users\YourName\Xionimus"
Add-MpPreference -ExclusionProcess "python.exe"
Add-MpPreference -ExclusionProcess "node.exe"
Add-MpPreference -ExclusionExtension ".py"
Add-MpPreference -ExclusionExtension ".js"
```

### 4. Optimize MongoDB

```powershell
# Edit MongoDB config (C:\Program Files\MongoDB\Server\7.0\bin\mongod.cfg)
storage:
  dbPath: C:\data\db
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2  # Adjust based on RAM

# Restart MongoDB
net stop MongoDB
net start MongoDB
```

### 5. Node.js Optimization

```powershell
# Increase max memory
$env:NODE_OPTIONS="--max-old-space-size=4096"

# Use faster package manager
npm install -g yarn
yarn install  # Instead of npm install
```

---

## 🚀 READY FOR TESTING

I'm ready to investigate any issues that arise during Windows testing!

**To Get Help:**

1. Run the tests and collect error logs
2. Gather system information
3. Document the issue using the template above
4. Provide screenshots if applicable
5. Share the collected data

**I will provide:**
- Targeted fixes for Windows-specific issues
- Updated scripts if needed
- Performance optimization suggestions
- Alternative approaches when needed

**Let's make Xionimus AI 100% Windows-compatible!** 🎯

---

**Document Version:** 1.0  
**Last Updated:** October 8, 2025  
**Status:** Ready for Windows 10/11 Testing
