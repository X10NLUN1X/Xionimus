@echo off
title Xionimus AI

echo.
echo ========================================================================
echo    Xionimus AI wird gestartet...
echo ========================================================================
echo.

REM Wechsle ins Hauptverzeichnis
cd /d "%~dp0"

REM Starte Backend
echo [1/2] Starte Backend...
start "Xionimus AI - Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

REM Warte 5 Sekunden
timeout /t 5 /nobreak >nul

REM Starte Frontend
echo [2/2] Starte Frontend...
start "Xionimus AI - Frontend" cmd /k "cd frontend && yarn dev"

echo.
echo ========================================================================
echo    Xionimus AI wird gestartet!
echo ========================================================================
echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo API Docs: http://localhost:8001/docs
echo.
echo ========================================================================
echo.
echo Zwei neue Fenster sollten sich geöffnet haben.
echo Warten Sie 10-15 Sekunden, dann öffnen Sie:
echo.
echo     http://localhost:3000
echo.
echo ========================================================================
