@echo off
echo ==========================================
echo Xionimus AI - Windows Installation
echo ==========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo Installing Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-windows.txt

echo.
echo Installing Frontend...
cd ..\frontend
call npm install

echo.
echo ==========================================
echo Installation Complete!
echo Run 'start-windows.bat' to start the application
echo ==========================================
pause
