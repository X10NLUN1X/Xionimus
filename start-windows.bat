@echo off
echo ==========================================
echo Starting Xionimus AI on Windows
echo ==========================================

REM Start MongoDB (if installed as service, it should already be running)
echo Checking MongoDB...
mongo --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: MongoDB not found. Some features may not work.
)

REM Start Backend
echo.
echo Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start Frontend
echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo Xionimus AI is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ==========================================
echo Press any key to open in browser...
pause >nul
start http://localhost:3000
