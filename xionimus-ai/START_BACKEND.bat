@echo off
REM ============================================================================
REM Xionimus AI - Backend Starter (Windows)
REM Version: 2.0.0
REM Mit automatischem Dependency-Check
REM ============================================================================

setlocal enabledelayedexpansion

color 0B
title Xionimus AI - Backend

echo.
echo ========================================================================
echo    Xionimus AI Backend
echo ========================================================================
echo.

cd /d "%~dp0backend"

if not exist "venv\" (
    echo [FEHLER] Virtuelle Umgebung nicht gefunden!
    echo Bitte fuehren Sie zuerst install-windows.bat aus.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [INFO] Pruefe Python-Abhaengigkeiten...

python -c "import fastapi, uvicorn, pypdf, PIL, chromadb" 2>nul
if %errorLevel% neq 0 (
    echo [FEHLER] Kritische Module fehlen!
    echo Installiere fehlende Pakete...
    
    if exist "requirements-windows.txt" (
        pip install -r requirements-windows.txt
    ) else (
        findstr /v /i "uvloop" requirements.txt ^> requirements-temp.txt
        pip install -r requirements-temp.txt
        del requirements-temp.txt
    )
)

echo [OK] Alle Abhaengigkeiten vorhanden
echo.
echo Starte Backend auf http://localhost:8001
echo.

python main.py

pause
