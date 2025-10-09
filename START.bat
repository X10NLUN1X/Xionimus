@echo off
setlocal EnableDelayedExpansion
title Xionimus AI - Startup
color 0B

echo.
echo ========================================================================
echo    XIONIMUS AI - Automated Startup System
echo ========================================================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

REM Verify we're in the right directory
if not exist "backend" (
    echo ❌ ERROR: backend directory not found!
    echo Current directory: %CD%
    echo.
    echo Please ensure you're running this script from the Xionimus AI root directory.
    echo.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ ERROR: frontend directory not found!
    echo Current directory: %CD%
    echo.
    echo Please ensure you're running this script from the Xionimus AI root directory.
    echo.
    pause
    exit /b 1
)

echo ✅ Directory structure verified
echo.

REM ========================================================================
REM   STEP 1: Check Prerequisites
REM ========================================================================

echo [1/8] Checking prerequisites...
echo.

REM Check Python
echo Checking for Python...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ❌ ERROR: Python not found or not in PATH!
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python found: !PYTHON_VERSION!

REM Check Node.js
echo Checking for Node.js...
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ❌ ERROR: Node.js not found or not in PATH!
    echo.
    echo Please install Node.js from:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo ✅ Node.js found: !NODE_VERSION!
echo.

REM ========================================================================
REM   STEP 2: Create/Validate .env File
REM ========================================================================

echo [2/8] Checking environment configuration...
echo.

if not exist "backend\.env" (
    echo ⚠️  .env file not found. Creating now...
    echo.
    
    REM Check if .env.example exists and copy it
    if exist "backend\.env.example" (
        echo Copying and configuring .env file...
        copy "backend\.env.example" "backend\.env" >nul 2>&1
        
        if exist "backend\.env" (
            REM Create a temporary PowerShell script for replacement
            echo $content = Get-Content 'backend\.env' -Raw > temp_replace.ps1
            echo $content = $content -replace 'generate-your-secret-key-here-64-chars-hex', '4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307' >> temp_replace.ps1
            echo $content = $content -replace 'generate-your-encryption-key-here-fernet-format', '89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=' >> temp_replace.ps1
            echo $content ^| Set-Content 'backend\.env' -NoNewline >> temp_replace.ps1
            
            REM Run the PowerShell script
            powershell -NoProfile -ExecutionPolicy Bypass -File temp_replace.ps1
            
            REM Clean up
            del temp_replace.ps1 >nul 2>&1
            
            echo ✅ .env file created and configured!
        ) else (
            echo ❌ ERROR: Failed to copy .env.example!
            pause
            exit /b 1
        )
    ) else (
        echo ❌ ERROR: backend\.env.example not found!
        echo.
        echo Please ensure backend\.env.example exists.
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
    if !errorlevel! neq 0 (
        echo ❌ ERROR: Failed to create virtual environment!
        echo.
        echo Please check:
        echo   - Python is properly installed
        echo   - You have write permissions
        echo   - Enough disk space available
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
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ❌ ERROR: venv\Scripts\activate.bat not found!
    echo Virtual environment may be corrupted.
    echo.
    echo Try deleting the venv folder and run START.bat again.
    echo.
    pause
    cd ..
    exit /b 1
)
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
if !errorlevel! neq 0 (
    echo ⚠️  Yarn not found, using npm instead...
    call npm install
    if !errorlevel! neq 0 (
        echo ❌ ERROR: npm install failed!
        echo.
        echo Please check:
        echo   - Node.js is properly installed
        echo   - Internet connection is available
        echo   - No firewall blocking npm
        echo.
        pause
        cd ..
        exit /b 1
    )
) else (
    call yarn install
    if !errorlevel! neq 0 (
        echo ❌ ERROR: yarn install failed!
        echo.
        echo Please check:
        echo   - Internet connection is available
        echo   - No firewall blocking yarn
        echo.
        pause
        cd ..
        exit /b 1
    )
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
echo 1. Login to the application (admin / admin123)
echo 2. Go to Settings or Profile section
echo 3. Enter your API keys in the UI:
echo    - OpenAI API Key
echo    - Anthropic API Key
echo    - Perplexity API Key (optional)
echo.
echo Keys are securely encrypted and stored in the database.
echo.
echo ========================================================================
echo.
echo This window can be closed.
echo The application will continue running in the backend and frontend windows.
echo.
echo To stop: Close the backend and frontend windows.
echo.
pause
