@echo off
REM ============================================================================
REM Xionimus AI - Backend Starter (Windows)
REM Version: 2.1.0
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

REM Ermittle Skript-Verzeichnis
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo [INFO] Skript-Verzeichnis: %SCRIPT_DIR%

REM Prüfe ob wir bereits im Backend-Verzeichnis sind
if exist "venv\" (
    echo [INFO] Bereits im Backend-Verzeichnis
    set "BACKEND_DIR=%CD%"
) else if exist "%SCRIPT_DIR%\backend\venv\" (
    echo [INFO] Wechsle ins Backend-Verzeichnis...
    cd /d "%SCRIPT_DIR%\backend"
    set "BACKEND_DIR=%SCRIPT_DIR%\backend"
) else (
    echo [FEHLER] Virtuelle Umgebung nicht gefunden!
    echo.
    echo Gesucht in:
    echo   - Aktuell: %CD%\venv
    echo   - Alternativ: %SCRIPT_DIR%\backend\venv
    echo.
    echo Bitte fuehren Sie zuerst install-windows.bat aus.
    echo.
    pause
    exit /b 1
)

echo [INFO] Backend-Verzeichnis: %BACKEND_DIR%

if not exist "venv\" (
    echo [FEHLER] Virtuelle Umgebung konnte nicht gefunden werden!
    echo Bitte fuehren Sie install-windows.bat aus.
    pause
    exit /b 1
)

echo [INFO] Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat

if %errorLevel% neq 0 (
    echo [FEHLER] Konnte virtuelle Umgebung nicht aktivieren!
    pause
    exit /b 1
)

echo [INFO] Pruefe kritische Python-Abhaengigkeiten...

REM Prüfe jedes Modul einzeln für bessere Fehlermeldungen
python -c "import fastapi" 2>nul
if %errorLevel% neq 0 (
    echo [FEHLER] fastapi fehlt! Installiere Abhaengigkeiten...
    goto :INSTALL_DEPS
)

python -c "import uvicorn" 2>nul
if %errorLevel% neq 0 (
    echo [FEHLER] uvicorn fehlt! Installiere Abhaengigkeiten...
    goto :INSTALL_DEPS
)

python -c "import pypdf" 2>nul
if %errorLevel% neq 0 (
    echo [FEHLER] pypdf fehlt! Installiere Abhaengigkeiten...
    goto :INSTALL_DEPS
)

python -c "import PIL" 2>nul
if %errorLevel% neq 0 (
    echo [FEHLER] Pillow fehlt! Installiere Abhaengigkeiten...
    goto :INSTALL_DEPS
)

python -c "import chromadb" 2>nul
if %errorLevel% neq 0 (
    echo [FEHLER] chromadb fehlt! Installiere Abhaengigkeiten...
    goto :INSTALL_DEPS
)

echo [OK] Alle Abhaengigkeiten vorhanden
goto :START_SERVER

:INSTALL_DEPS
echo.
echo [INFO] Installiere fehlende Python-Pakete...
echo        Dies kann einige Minuten dauern...
echo.

if exist "requirements-windows.txt" (
    echo [INFO] Verwende requirements-windows.txt
    pip install -r requirements-windows.txt --no-cache-dir
) else (
    echo [INFO] Filtere Linux-spezifische Pakete...
    findstr /v /i "uvloop" requirements.txt > requirements-temp.txt
    pip install -r requirements-temp.txt --no-cache-dir
    del requirements-temp.txt
)

if %errorLevel% neq 0 (
    echo.
    echo [FEHLER] Installation fehlgeschlagen!
    echo         Bitte pruefen Sie die Fehlermeldungen oben.
    echo         Mögliche Lösungen:
    echo         1. Stellen Sie sicher, dass Python korrekt installiert ist
    echo         2. Pruefen Sie Ihre Internetverbindung
    echo         3. Fuehren Sie das Skript mit Administrator-Rechten aus
    echo.
    pause
    exit /b 1
)

echo [OK] Installation erfolgreich
echo.

:START_SERVER
echo ========================================================================
echo    Starte Backend auf http://localhost:8001
echo    API Docs: http://localhost:8001/docs
echo ========================================================================
echo.

python main.py

if %errorLevel% neq 0 (
    echo.
    echo [FEHLER] Backend konnte nicht gestartet werden!
    echo         Pruefen Sie die Fehlermeldungen oben.
    echo.
)

pause
