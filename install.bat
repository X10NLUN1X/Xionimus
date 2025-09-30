@echo off
REM Xionimus AI - Einfache Windows Installation
title Xionimus AI - Installation

echo.
echo ============================================================
echo    Xionimus AI - Installation
echo ============================================================
echo.

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
cd /d "%~dp0backend"

if not exist "venv\" (
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements-windows.txt --quiet

cd /d "%~dp0"
echo [OK] Backend fertig
echo.

REM Frontend Setup
echo [3/4] Frontend wird eingerichtet...
cd /d "%~dp0frontend"

where yarn >nul 2>&1
if %errorLevel% neq 0 (
    call npm install -g yarn
)

call yarn install --silent

cd /d "%~dp0"
echo [OK] Frontend fertig
echo.

REM Start-Skript erstellen
echo [4/4] Start-Skript wird erstellt...
(
echo @echo off
echo title Xionimus AI
echo start "Backend" /D "%~dp0backend" cmd /k "venv\Scripts\activate.bat && python main.py"
echo timeout /t 3 /nobreak ^>nul
echo start "Frontend" /D "%~dp0frontend" cmd /k "yarn dev"
echo echo.
echo echo Xionimus AI wird gestartet...
echo echo Backend:  http://localhost:8001
echo echo Frontend: http://localhost:3000
echo echo.
) > start.bat

echo [OK] Start-Skript erstellt
echo.
echo ============================================================
echo    Installation abgeschlossen!
echo ============================================================
echo.
echo Starten Sie Xionimus AI mit: start.bat
echo.
pause
