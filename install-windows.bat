@echo off
setlocal enabledelayedexpansion

:: =============================================================================
:: Emergent-Next Windows Installation Script
:: =============================================================================
:: Automatic installation script for Windows environments
:: =============================================================================

echo.
echo ================================================================================
echo EMERGENT-NEXT WINDOWS INSTALLATION
echo ================================================================================
echo.

:: Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] This script should be run as Administrator for best results.
    echo [WARNING] Some features may not work without admin privileges.
    echo.
)

:: Check for required tools
echo [INFO] Checking system requirements...

:: Check for Node.js
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo [ERROR] Please install Node.js 18+ from: https://nodejs.org/
    pause
    exit /b 1
) else (
    echo [SUCCESS] Node.js is installed
)

:: Check for Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo [ERROR] Please install Python 3.10+ from: https://python.org/
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python is installed
)

:: Check for Git
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Git is not installed. Some features may not work.
) else (
    echo [SUCCESS] Git is installed
)

echo.
echo [INFO] Installing dependencies...

:: Install Yarn globally if not present
call yarn --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Installing Yarn...
    call npm install -g yarn
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to install Yarn
        pause
        exit /b 1
    )
    echo [SUCCESS] Yarn installed
) else (
    echo [SUCCESS] Yarn is already installed
)

:: Navigate to project directory
cd /d "%~dp0emergent-next"
if %errorLevel% neq 0 (
    echo [ERROR] emergent-next directory not found
    pause
    exit /b 1
)

:: Install Backend Dependencies
echo.
echo [INFO] Installing Python backend dependencies...
cd backend

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Backend dependencies installed

:: Install Frontend Dependencies
echo.
echo [INFO] Installing frontend dependencies...
cd ..\frontend

:: Remove conflicting files
if exist "package-lock.json" del "package-lock.json"
if exist "node_modules" rmdir /s /q "node_modules" 2>nul

:: Install with Yarn
call yarn install
if %errorLevel% neq 0 (
    echo [ERROR] Failed to install frontend dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Frontend dependencies installed

:: Create environment files
echo.
echo [INFO] Creating environment configuration...

:: Backend .env
if not exist "..\backend\.env" (
    echo [INFO] Creating backend .env file...
    (
        echo # MongoDB Configuration
        echo MONGO_URL=mongodb://localhost:27017/emergent_next
        echo.
        echo # AI API Keys
        echo OPENAI_API_KEY=
        echo ANTHROPIC_API_KEY=
        echo PERPLEXITY_API_KEY=
        echo.
        echo # Application Settings
        echo DEBUG=true
        echo HOST=0.0.0.0
        echo PORT=8002
        echo LOG_LEVEL=INFO
        echo.
        echo # Security
        echo SECRET_KEY=emergent-secret-key-change-in-production
        echo JWT_ALGORITHM=HS256
        echo JWT_EXPIRE_MINUTES=1440
        echo.
        echo # File Upload ^(250MB limit^)
        echo MAX_FILE_SIZE=262144000
        echo UPLOAD_DIR=uploads
        echo WORKSPACE_DIR=workspace
    ) > ..\backend\.env
    echo [SUCCESS] Backend .env file created
)

:: Frontend .env
if not exist ".env" (
    echo [INFO] Creating frontend .env file...
    echo VITE_BACKEND_URL=http://localhost:8002 > .env
    echo [SUCCESS] Frontend .env file created
)

:: Create startup scripts
echo.
echo [INFO] Creating startup scripts...

cd ..

:: Backend startup script
(
    echo @echo off
    echo echo Starting Emergent-Next Backend...
    echo cd backend
    echo call venv\Scripts\activate.bat
    echo python main.py
    echo pause
) > start-backend.bat

:: Frontend startup script
(
    echo @echo off
    echo echo Starting Emergent-Next Frontend...
    echo cd frontend
    echo yarn dev
    echo pause
) > start-frontend.bat

:: Combined startup script
(
    echo @echo off
    echo echo Starting Emergent-Next Development Environment...
    echo echo.
    echo echo [INFO] Starting Backend ^(Port 8002^)...
    echo start /B cmd /C "cd backend && call venv\Scripts\activate.bat && python main.py > backend.log 2>&1"
    echo echo [INFO] Waiting for backend to start...
    echo timeout /t 5 /nobreak > nul
    echo echo [INFO] Starting Frontend ^(Port 3000^)...
    echo start /B cmd /C "cd frontend && yarn dev > frontend.log 2>&1"
    echo echo.
    echo echo ================================================================================
    echo echo EMERGENT-NEXT STARTED SUCCESSFULLY
    echo echo ================================================================================
    echo echo Frontend: http://localhost:3000
    echo echo Backend:  http://localhost:8002
    echo echo API Docs: http://localhost:8002/docs
    echo echo.
    echo echo Press any key to stop services...
    echo pause > nul
    echo echo.
    echo echo [INFO] Stopping services...
    echo taskkill /F /IM python.exe 2>nul
    echo taskkill /F /IM node.exe 2>nul
    echo echo [INFO] Services stopped
    echo pause
) > start-all.bat

echo [SUCCESS] Startup scripts created

:: Final instructions
echo.
echo ================================================================================
echo INSTALLATION COMPLETED SUCCESSFULLY!
echo ================================================================================
echo.
echo [SUCCESS] All dependencies have been installed successfully!
echo.
echo Next steps:
echo 1. Configure AI API keys in: emergent-next\backend\.env
echo 2. Install MongoDB: https://www.mongodb.com/try/download/community
echo 3. Start the application: double-click start-all.bat
echo 4. Access the application at: http://localhost:3000
echo.
echo Available scripts:
echo - start-all.bat      - Start both backend and frontend
echo - start-backend.bat  - Start only backend
echo - start-frontend.bat - Start only frontend
echo.
echo [INFO] Press any key to exit...
pause > nul