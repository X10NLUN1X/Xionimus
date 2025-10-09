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
    
    REM Check if .env.example exists and copy it
    if exist "backend\.env.example" (
        echo Copying backend\.env.example to backend\.env...
        copy "backend\.env.example" "backend\.env" >nul 2>&1
        
        if exist "backend\.env" (
            REM Update the placeholder keys with actual permanent keys
            echo Configuring permanent security keys...
            powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content 'backend\.env') -replace 'generate-your-secret-key-here-64-chars-hex', '4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307' -replace 'generate-your-encryption-key-here-fernet-format', '89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=' | Set-Content 'backend\.env'"
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
