@echo off
REM Xionimus AI - Einfache Windows Installation
title Xionimus AI - Installation

echo.
echo ============================================================
echo    Xionimus AI - Installation
echo ============================================================
echo.

REM Ermittle Skript-Verzeichnis
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

echo Projekt-Verzeichnis: %ROOT_DIR%
echo.

REM Prüfe ob backend und frontend existieren
if not exist "%ROOT_DIR%\backend\" (
    echo [FEHLER] backend Ordner nicht gefunden!
    echo Bitte stellen Sie sicher, dass Sie das Skript im Hauptverzeichnis ausfuehren.
    echo Erwartet: %ROOT_DIR%\backend\
    pause
    exit /b 1
)

if not exist "%ROOT_DIR%\frontend\" (
    echo [FEHLER] frontend Ordner nicht gefunden!
    pause
    exit /b 1
)

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

if not exist "venv\" (
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements-windows.txt --quiet

cd /d "%ROOT_DIR%"
echo [OK] Backend fertig
echo.

REM Frontend Setup
echo [3/4] Frontend wird eingerichtet...
cd /d "%ROOT_DIR%\frontend"

where yarn >nul 2>&1
if %errorLevel% neq 0 (
    call npm install -g yarn
)

call yarn install --silent

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
