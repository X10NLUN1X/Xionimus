@echo off
title Xionimus AI - Startup
color 0B

echo.
echo ========================================================================
echo    XIONIMUS AI - Automated Startup System
echo ========================================================================
echo.

cd /d "%~dp0"

REM ========================================================================
REM   STEP 1: Check Prerequisites
REM ========================================================================

echo [1/8] Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js not found!
    echo.
    echo Please install Node.js from:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js found: 
node --version
echo.

REM ========================================================================
REM   STEP 2: Create/Validate .env File
REM ========================================================================

echo [2/8] Checking environment configuration...
echo.

if not exist "backend\.env" (
    echo ⚠️  .env file not found. Creating now...
    echo.
    
    REM Create .env file with permanent keys
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$envContent = @'^
# ===================================`n^
# Xionimus AI Backend Configuration`n^
# ===================================`n^
# `n^
# IMPORTANT: This file contains SECRET_KEY and ENCRYPTION_KEY`n^
# These keys are PERMANENT and should NEVER be changed`n^
# Keep this file secure and never commit it to Git`n^
#`n^
`n^
# ===================================`n^
# SECURITY KEYS (PERMANENT - DO NOT CHANGE!)`n^
# ===================================`n^
`n^
# JWT Secret Key - Signs Authentication Tokens`n^
# CRITICAL: Changing this invalidates all user sessions`n^
SECRET_KEY=4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307`n^
`n^
# JWT Configuration`n^
JWT_ALGORITHM=HS256`n^
JWT_EXPIRE_MINUTES=1440`n^
`n^
# Encryption Key - Encrypts API Keys in Database`n^
# CRITICAL: Changing this makes stored API Keys unreadable`n^
ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=`n^
`n^
# ===================================`n^
# SERVER CONFIGURATION`n^
# ===================================`n^
`n^
DEBUG=true`n^
HOST=0.0.0.0`n^
PORT=8001`n^
LOG_LEVEL=INFO`n^
`n^
# ===================================`n^
# DATABASE CONFIGURATION`n^
# ===================================`n^
`n^
# MongoDB Connection URL`n^
MONGO_URL=mongodb://localhost:27017/xionimus_ai`n^
`n^
# Redis (optional - for caching)`n^
REDIS_URL=redis://localhost:6379/0`n^
`n^
# ===================================`n^
# AI PROVIDER API KEYS (OPTIONAL)`n^
# ===================================`n^
# Add your API Keys here to enable AI features`n^
# Get keys from:`n^
#   - OpenAI: https://platform.openai.com/api-keys`n^
#   - Anthropic: https://console.anthropic.com/`n^
#   - Perplexity: https://www.perplexity.ai/settings/api`n^
`n^
OPENAI_API_KEY=`n^
ANTHROPIC_API_KEY=`n^
PERPLEXITY_API_KEY=`n^
GITHUB_TOKEN=`n^
`n^
# ===================================`n^
# GITHUB OAUTH (OPTIONAL)`n^
# ===================================`n^
`n^
GITHUB_OAUTH_CLIENT_ID=Ov23liCIa2aVTC3ttGFf`n^
GITHUB_OAUTH_CLIENT_SECRET=acc1edb2b095606ee55182a4eb5daf0cda9ce46d`n^
GITHUB_OAUTH_CALLBACK_URL=http://localhost:3000/github/callback`n^
GITHUB_USE_PAT=false`n^
'@; $envContent | Out-File -FilePath 'backend\.env' -Encoding UTF8 -NoNewline"
    
    if exist "backend\.env" (
        echo ✅ .env file created successfully!
    ) else (
        echo ❌ ERROR: Failed to create .env file!
        echo.
        echo Please check:
        echo   - Write permissions in directory
        echo   - backend\ folder exists
        echo.
        pause
        exit /b 1
    )
) else (
    echo ✅ .env file exists
)
echo.

REM ========================================================================
REM   STEP 3: Setup Backend Environment
REM ========================================================================

echo [3/8] Setting up backend environment...
echo.

cd backend

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment!
        echo.
        pause
        cd ..
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ ERROR: Failed to activate virtual environment!
    echo.
    pause
    cd ..
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM ========================================================================
REM   STEP 4: Install Backend Dependencies
REM ========================================================================

echo [4/8] Installing backend dependencies...
echo.

pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some packages may have failed to install.
    echo Continuing anyway...
) else (
    echo ✅ Backend dependencies installed
)
echo.

cd ..

REM ========================================================================
REM   STEP 5: Install Frontend Dependencies
REM ========================================================================

echo [5/8] Installing frontend dependencies...
echo.

cd frontend

REM Check if yarn is available
call yarn --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Yarn not found, using npm instead...
    call npm install
) else (
    call yarn install
)

if errorlevel 1 (
    echo ❌ ERROR: Failed to install frontend dependencies!
    echo.
    pause
    cd ..
    exit /b 1
)

echo ✅ Frontend dependencies installed
echo.

cd ..

REM ========================================================================
REM   STEP 6: Start Backend Server
REM ========================================================================

echo [6/8] Starting backend server...
echo.

cd backend

REM Start backend in new window
start "Xionimus Backend" cmd /k "call venv\Scripts\activate.bat && python server.py"

echo ✅ Backend starting on http://localhost:8001
echo    (Check backend window for status)
echo.

cd ..

REM Wait for backend to initialize
echo Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

REM ========================================================================
REM   STEP 7: Start Frontend Server
REM ========================================================================

echo [7/8] Starting frontend server...
echo.

cd frontend

REM Start frontend in new window
start "Xionimus Frontend" cmd /k "yarn dev"

echo ✅ Frontend starting on http://localhost:3000
echo    (Check frontend window for status)
echo.

cd ..

REM ========================================================================
REM   STEP 8: Open Browser
REM ========================================================================

echo [8/8] Opening browser...
echo.

REM Wait for frontend to be ready
timeout /t 5 /nobreak >nul

REM Open browser
start http://localhost:3000

echo ✅ Browser opened!
echo.

REM ========================================================================
REM   SUCCESS
REM ========================================================================

echo ========================================================================
echo    ✅ XIONIMUS AI STARTED SUCCESSFULLY!
echo ========================================================================
echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo Docs:     http://localhost:8001/docs
echo.
echo ========================================================================
echo    FIRST TIME SETUP (Important!)
echo ========================================================================
echo.
echo If this is your FIRST time starting Xionimus:
echo.
echo 1. Clear browser cache:
echo    - Press F12
echo    - Go to Application ^> Clear storage
echo    - Click "Clear site data"
echo    - OR: Press Ctrl+Shift+R
echo.
echo 2. Login with:
echo    - Username: admin
echo    - Password: admin123
echo.
echo ========================================================================
echo    OPTIONAL: Add API Keys
echo ========================================================================
echo.
echo To enable AI chat features:
echo.
echo 1. Open: backend\.env
echo 2. Add your API keys:
echo    OPENAI_API_KEY=sk-proj-your-key
echo    ANTHROPIC_API_KEY=sk-ant-your-key
echo 3. Save and close backend window
echo 4. Run START.bat again
echo.
echo ========================================================================
echo.
echo This window can be closed.
echo The application will continue running in the backend and frontend windows.
echo.
echo To stop: Close the backend and frontend windows.
echo.
pause
