@echo off
chcp 65001 >nul
title PSEONIMUS - STATUS CHECK
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║          🔍 PSEONIMUS STATUS-CHECK TEST-SUITE 🔍            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ FEHLER: Python ist nicht installiert oder nicht in PATH
    echo.
    echo Bitte installiere Python von: https://www.python.org/downloads/
    echo Achte darauf "Add Python to PATH" anzuhaken!
    echo.
    pause
    exit /b 1
)

echo Python gefunden ✓
echo.
echo Starte Status-Check...
echo.

REM Führe die Test-Suite aus
python STATUS_CHECK.py

echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo Drücke eine beliebige Taste zum Beenden...
pause >nul
