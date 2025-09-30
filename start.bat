@echo off
title Xionimus AI
start "Backend" /D "%~dp0backend" cmd /k "venv\Scripts\activate.bat && python main.py"
timeout /t 3 /nobreak >nul
start "Frontend" /D "%~dp0frontend" cmd /k "yarn dev"
echo.
echo Xionimus AI wird gestartet...
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo.
