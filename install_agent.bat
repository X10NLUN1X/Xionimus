@echo off
REM Xionimus Agent Installer for Windows
echo ================================================
echo Xionimus Autonomous Agent - Windows Installation
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Python found
python --version

echo.
echo [2/4] Installing dependencies...
cd agent
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Creating configuration file...
if not exist config.json (
    copy config.example.json config.json
    echo Created config.json from template
    echo.
    echo IMPORTANT: Edit config.json and update:
    echo   - backend_url (your Xionimus backend URL)
    echo   - watch_directories (your project directories)
) else (
    echo config.json already exists
)

echo.
echo [4/4] Installation complete!
echo.
echo ================================================
echo Next Steps:
echo ================================================
echo 1. Edit agent\config.json with your settings
echo 2. Run: python agent\main.py --config agent\config.json
echo 3. Configure directories in web UI: http://your-backend/agent
echo ================================================
echo.
pause
