@echo off
title Xionimus AI - Complete Platform
echo Starting Xionimus AI Platform...
echo Backend + Frontend services starting simultaneously

start "Xionimus AI Backend" START_BACKEND.bat
timeout /t 3 /nobreak > nul
start "Xionimus AI Frontend" START_FRONTEND.bat

echo.
echo ================================================================
echo  Xionimus AI Platform is starting...
echo  Backend: http://localhost:8001
echo  Frontend: http://localhost:3000 (or next available port)
echo  Docs: http://localhost:8001/docs
echo ================================================================
echo.
echo Press any key to exit...
pause > nul
