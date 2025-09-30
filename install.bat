@echo off
REM Xionimus AI - Einfache Windows Installation
title Xionimus AI - Installation

echo.
echo ============================================================
echo    Xionimus AI - Installation (DEBUG MODE)
echo ============================================================
echo.

REM Ermittle Skript-Verzeichnis
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

echo [DEBUG] Skript-Datei: %~f0
echo [DEBUG] Skript-Verzeichnis: %~dp0
echo [DEBUG] ROOT_DIR: %ROOT_DIR%
echo [DEBUG] Aktuelles Verzeichnis: %CD%
echo.

REM Prüfe ob backend und frontend existieren
echo [DEBUG] Pruefe ob backend existiert...
if exist "%ROOT_DIR%\backend\" (
    echo [OK] backend gefunden: %ROOT_DIR%\backend\
) else (
    echo [FEHLER] backend NICHT gefunden!
    echo [DEBUG] Gesucht in: %ROOT_DIR%\backend\
    echo [DEBUG] Inhalt von ROOT_DIR:
    dir "%ROOT_DIR%" /B
    pause
    exit /b 1
)

echo [DEBUG] Pruefe ob frontend existiert...
if exist "%ROOT_DIR%\frontend\" (
    echo [OK] frontend gefunden: %ROOT_DIR%\frontend\
) else (
    echo [FEHLER] frontend NICHT gefunden!
    pause
    exit /b 1
)

echo.
echo [DEBUG] Druecken Sie eine Taste um fortzufahren...
pause

REM Prüfe Python
where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [FEHLER] Python nicht gefunden!
    echo Bitte installieren: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Prüfe Node
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [FEHLER] Node.js nicht gefunden!
    echo Bitte installieren: https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Python und Node.js gefunden
echo.

REM Backend Setup
echo [2/4] Backend wird eingerichtet...
cd /d "%ROOT_DIR%\backend"

if %errorLevel% neq 0 (
    echo [FEHLER] Konnte nicht ins backend Verzeichnis wechseln!
    echo Versuchter Pfad: %ROOT_DIR%\backend
    pause
    exit /b 1
)

echo Arbeite in: %CD%
echo.

if not exist "venv\" (
    echo Erstelle virtuelle Umgebung...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo [FEHLER] Konnte venv nicht erstellen!
        pause
        exit /b 1
    )
)

echo Aktiviere venv...
call venv\Scripts\activate.bat

if %errorLevel% neq 0 (
    echo [FEHLER] Konnte venv nicht aktivieren!
    echo Bitte pruefen Sie, ob backend\venv\Scripts\activate.bat existiert.
    pause
    exit /b 1
)

echo Installiere Python-Pakete...
python -m pip install --upgrade pip --quiet
pip install -r requirements-windows.txt

cd /d "%ROOT_DIR%"
echo [OK] Backend fertig
echo.

REM Frontend Setup
echo [3/4] Frontend wird eingerichtet...
cd /d "%ROOT_DIR%\frontend"

if %errorLevel% neq 0 (
    echo [FEHLER] Konnte nicht ins frontend Verzeichnis wechseln!
    pause
    exit /b 1
)

echo Arbeite in: %CD%
echo.

where yarn >nul 2>&1
if %errorLevel% neq 0 (
    echo Installiere Yarn...
    call npm install -g yarn
)

echo Installiere Node-Pakete...
call yarn install

cd /d "%ROOT_DIR%"
echo [OK] Frontend fertig
echo.

REM Start-Skript erstellen
echo [4/4] Start-Skript wird erstellt...
(
echo @echo off
echo title Xionimus AI
echo cd /d "%%~dp0"
echo start "Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"
echo timeout /t 3 /nobreak ^>nul
echo start "Frontend" cmd /k "cd frontend && yarn dev"
echo echo.
echo echo Xionimus AI wird gestartet...
echo echo Backend:  http://localhost:8001
echo echo Frontend: http://localhost:3000
echo echo.
) > "%ROOT_DIR%\start.bat"

echo [OK] Start-Skript erstellt
echo.
echo ============================================================
echo    Installation abgeschlossen!
echo ============================================================
echo.
echo Starten Sie Xionimus AI mit: start.bat
echo.
pause
