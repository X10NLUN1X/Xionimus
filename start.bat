@echo off
title Xionimus AI
color 0A

echo.
echo ========================================================================
echo    Xionimus AI wird gestartet...
echo ========================================================================
echo.

REM Wechsle ins Hauptverzeichnis
cd /d "%~dp0"

REM Starte Backend
echo [1/3] Starte Backend...
start "Xionimus AI - Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

REM Warte 5 Sekunden
timeout /t 5 /nobreak >nul

REM Starte Frontend
echo [2/3] Starte Frontend...
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
echo Zwei neue Fenster sollten sich geoeffnet haben.
echo Warten auf Services...
echo.

REM [3/3] Warte auf Services und öffne Browser
echo [3/3] Browser wird automatisch geoeffnet...
timeout /t 10 /nobreak >nul

REM Öffne Browser automatisch
start http://localhost:3000

echo.
echo ========================================================================
echo    Browser geoeffnet! Xionimus AI ist bereit!
echo ========================================================================
echo.
echo Falls der Browser sich nicht geoeffnet hat, oeffne manuell:
echo     http://localhost:3000
echo.
echo Druecke eine beliebige Taste zum Beenden...
pause >nul
