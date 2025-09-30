@echo off
REM Xionimus AI - Backend Starter (Windows)

title Xionimus AI - Backend

echo.
echo ========================================================================
echo    Xionimus AI Backend
echo ========================================================================
echo.

REM Wechsle ins Backend-Verzeichnis
cd /d "%~dp0backend"

if not exist "venv\" (
    echo [FEHLER] Virtuelle Umgebung nicht gefunden!
    echo.
    echo Bitte fuehren Sie zuerst install-windows.bat aus:
    echo   1. Oeffnen Sie eine Eingabeaufforderung
    echo   2. Gehen Sie zum xionimus-ai Verzeichnis
    echo   3. Fuehren Sie aus: install-windows.bat
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starte Backend auf http://localhost:8001
echo API Dokumentation: http://localhost:8001/docs
echo.

python main.py

pause
