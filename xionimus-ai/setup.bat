@echo off
REM #############################################
REM Xionimus AI - One-Click Setup Script (Windows)
REM Version: 1.0.0
REM #############################################

setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════╗
echo ║   Xionimus AI - Setup Script v1.0.0   ║
echo ╚════════════════════════════════════════╝
echo.

REM Check Node.js
echo [Step 1/6] Checking prerequisites...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+ first.
    echo Visit: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo [OK] Node.js !NODE_VERSION! installed

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] !PYTHON_VERSION! installed

REM Check Yarn
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Yarn not found. Installing...
    call npm install -g yarn
)
echo [OK] Yarn installed
echo.

REM Install backend dependencies
echo [Step 2/6] Installing backend dependencies...
cd backend
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
)
call venv\Scripts\activate
pip install -r requirements.txt --quiet
echo [OK] Backend dependencies installed
cd ..
echo.

REM Install frontend dependencies
echo [Step 3/6] Installing frontend dependencies...
cd frontend
call yarn install --silent
echo [OK] Frontend dependencies installed
cd ..
echo.

REM Setup database
echo [Step 4/6] Setting up SQLite database...
if not exist "%USERPROFILE%\.xionimus_ai" mkdir "%USERPROFILE%\.xionimus_ai"
echo [OK] Database directory created
echo.

REM Configure environment
echo [Step 5/6] Checking environment configuration...
if not exist "backend\.env" (
    echo [WARN] .env file not found. Creating default...
    (
        echo # Xionimus AI Configuration
        echo DATABASE_URL=%USERPROFILE%\.xionimus_ai\xionimus.db
        echo UPLOAD_DIR=%USERPROFILE%\.xionimus_ai\uploads
        echo.
        echo # AI Provider API Keys ^(Optional - configure in Settings UI^)
        echo OPENAI_API_KEY=
        echo ANTHROPIC_API_KEY=
        echo PERPLEXITY_API_KEY=
        echo.
        echo # Server Configuration
        echo BACKEND_PORT=8001
        echo FRONTEND_PORT=3000
    ) > backend\.env
    echo [OK] Created default .env file
) else (
    echo [OK] Environment configuration found
)
echo.

REM Display completion
echo [Step 6/6] Setup complete!
echo.
echo ════════════════════════════════════════
echo [SUCCESS] Xionimus AI is ready to run!
echo ════════════════════════════════════════
echo.
echo To start the application:
echo.
echo   Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo   Frontend: cd frontend ^&^& yarn dev
echo.
echo ════════════════════════════════════════
echo.
echo Configure AI Provider API keys:
echo   • Open http://localhost:3000
echo   • Navigate to Settings
echo   • Add your OpenAI, Anthropic, or Perplexity API keys
echo.
echo ════════════════════════════════════════
echo.
echo [SUCCESS] Happy coding with Xionimus AI! 🚀
echo.
pause
