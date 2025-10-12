@echo off
title XIONIMUS - ALL-IN-ONE FIX
color 0A

echo.
echo ========================================
echo   XIONIMUS ALL-IN-ONE FIX
echo ========================================
echo.
echo Dieser Fix loest:
echo   [1] API Keys gehen verloren
echo   [2] Agent hat keinen Repo-Zugriff
echo.
echo ========================================
echo.

REM Pruefe ob Python installiert ist
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH!
    echo.
    pause
    exit /b 1
)

REM Fuehre den Fix aus
echo [INFO] Starte ALL-IN-ONE Fix...
echo.
python ALL_IN_ONE_FIX.py

REM Pruefe Exit-Code
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   FIX ERFOLGREICH ANGEWENDET!
    echo ========================================
    echo.
    echo Naechste Schritte:
    echo   1. Backend neu starten: START.bat
    echo   2. Repository NEU importieren in der UI
    echo   3. In der UI das Projekt aktivieren
    echo   4. Chat sollte jetzt Zugriff haben!
    echo.
) else (
    echo.
    echo ========================================
    echo   FIX FEHLGESCHLAGEN!
    echo ========================================
    echo.
    echo Siehe Fehler oben fuer Details.
    echo.
)

pause
