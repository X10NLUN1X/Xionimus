@echo off
setlocal EnableDelayedExpansion
title Xionimus AI - API Keys Setup
color 0B

echo.
echo ========================================================================
echo    XIONIMUS AI - API KEYS SETUP
echo ========================================================================
echo.

cd /d "%~dp0"

echo Dieses Tool hilft dir, deine API Keys zu ueberpruefen und zu setzen.
echo.

REM Check Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Python nicht gefunden!
    pause
    exit /b 1
)

echo [1/2] Ueberpruefe gespeicherte API Keys...
echo.

python CHECK_API_KEYS.py

echo.
echo ========================================================================
echo    NAECHSTE SCHRITTE
echo ========================================================================
echo.

echo Falls keine Keys gefunden wurden:
echo.
echo   1. Backend starten: START.bat
echo   2. Browser: http://localhost:3000
echo   3. Settings (⚙️) oeffnen
echo   4. API Keys eingeben:
echo      - OpenAI: sk-...
echo      - Anthropic: sk-ant-...
echo      - Perplexity: pplx-...
echo   5. "Save API Keys" klicken
echo.

echo Nach dem Speichern:
echo   - Backend neu starten
echo   - CHECK_API_KEYS.py nochmal ausfuehren
echo   - Chat sollte funktionieren!
echo.

pause
