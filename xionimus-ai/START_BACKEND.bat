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

REM Wechsle ins Backend-Verzeichnis relativ zum Skript
cd /d "%~dp0backend"

if not exist "venv\" (
    echo [FEHLER] Virtuelle Umgebung nicht gefunden!
    echo Bitte fuehren Sie zuerst install-windows.bat aus.
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
