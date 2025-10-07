@echo off
REM Xionimus AI - Windows Installation
title Xionimus AI - Installation

echo.
echo ============================================================
echo    Xionimus AI - Installation
echo ============================================================
echo.

REM Ermittle Skript-Verzeichnis
set "ROOT_DIR=%~dp0"
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

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

echo [1/3] Python und Node.js gefunden
echo.

REM ============================================================
REM BACKEND SETUP
REM ============================================================
echo [2/3] Backend wird eingerichtet...
cd /d "%ROOT_DIR%\backend"

REM Lösche alten venv (könnte von Linux sein)
if exist "venv\" (
    echo    - Loesche alten venv Ordner...
    rmdir /s /q venv
)

REM Erstelle neuen Windows-venv
echo    - Erstelle virtuelle Umgebung...
python -m venv venv
if %errorLevel% neq 0 (
    echo [FEHLER] Konnte venv nicht erstellen!
    pause
    exit /b 1
)

REM Aktiviere venv
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo [FEHLER] Konnte venv nicht aktivieren!
    pause
    exit /b 1
)

REM Installiere Pakete
echo    - Installiere Python-Pakete (kann 5-10 Min dauern)...
python -m pip install --upgrade pip --quiet

REM Verwende Windows-spezifische Requirements (ohne uvloop)
if exist "requirements-windows.txt" (
    echo    - Verwende requirements-windows.txt (Windows-kompatibel)
    pip install -r requirements-windows.txt
) else (
    echo    - Verwende requirements.txt
    pip install -r requirements.txt
)

if %errorLevel% neq 0 (
    echo [WARNUNG] Installation mit Fehlern - versuche wichtige Pakete einzeln...
)

REM Explizite Installation wichtiger Pakete
echo    - Installiere sse-starlette explizit...
pip install sse-starlette==2.1.3

echo    - Installiere python-magic-bin fuer Windows...
pip install python-magic-bin

echo    - Installiere weasyprint und reportlab...
pip install reportlab==4.4.4
pip install weasyprint==66.0

if %errorLevel% neq 0 (
    echo [FEHLER] Installation fehlgeschlagen!
    pause
    exit /b 1
)

echo [OK] Backend fertig
echo.

REM ============================================================
REM FRONTEND SETUP
REM ============================================================
echo [3/3] Frontend wird eingerichtet...
cd /d "%ROOT_DIR%\frontend"

REM Prüfe Yarn
where yarn >nul 2>&1
if %errorLevel% neq 0 (
    echo    - Installiere Yarn...
    call npm install -g yarn --silent
)

REM Installiere Pakete
echo    - Installiere Node-Pakete...
call yarn install

if %errorLevel% neq 0 (
    echo [FEHLER] Frontend-Installation fehlgeschlagen!
    pause
    exit /b 1
)

echo [OK] Frontend fertig
echo.

REM ============================================================
REM ERSTELLE START-SKRIPT
REM ============================================================
cd /d "%ROOT_DIR%"

echo @echo off > start.bat
echo title Xionimus AI >> start.bat
echo cd /d "%%~dp0" >> start.bat
echo start "Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py" >> start.bat
echo timeout /t 3 /nobreak ^>nul >> start.bat
echo start "Frontend" cmd /k "cd frontend && yarn dev" >> start.bat
echo echo. >> start.bat
echo echo Xionimus AI wird gestartet... >> start.bat
echo echo Backend:  http://localhost:8001 >> start.bat
echo echo Frontend: http://localhost:3000 >> start.bat

echo.
echo ============================================================
echo    Installation erfolgreich!
echo ============================================================
echo.
echo Starten Sie Xionimus AI mit: start.bat
echo.
pause
