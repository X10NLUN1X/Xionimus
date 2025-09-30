@echo off
REM ============================================================================
REM Xionimus AI - Windows Installation Script
REM Version: 2.0.0
REM Datum: 30. September 2025
REM ============================================================================

setlocal enabledelayedexpansion

color 0B
echo.
echo ========================================================================
echo    Xionimus AI - Windows Installation
echo    Version 2.0.0
echo ========================================================================
echo.

REM ============================================================================
REM 1. ADMIN-RECHTE PRÜFEN
REM ============================================================================
echo [1/8] Pruefe Administrator-Rechte...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Administrator-Rechte vorhanden
) else (
    echo [WARNUNG] Keine Administrator-Rechte. Einige Features koennen eingeschraenkt sein.
    echo            Empfohlen: Als Administrator ausfuehren
    echo.
    pause
)

REM ============================================================================
REM 2. PFAD-VALIDIERUNG
REM ============================================================================
echo.
echo [2/8] Validiere Projekt-Pfade...

REM Aktuelles Verzeichnis prüfen
set "PROJECT_ROOT=%CD%"
echo Projekt-Wurzel: %PROJECT_ROOT%

REM Prüfe ob wir im richtigen Verzeichnis sind
if not exist "%PROJECT_ROOT%\backend\" (
    echo [FEHLER] Backend-Verzeichnis nicht gefunden!
    echo          Bitte stellen Sie sicher, dass Sie das Skript aus dem
    echo          Xionimus AI Hauptverzeichnis ausfuehren.
    echo.
    echo Erwarteter Pfad: %PROJECT_ROOT%\backend\
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%\frontend\" (
    echo [FEHLER] Frontend-Verzeichnis nicht gefunden!
    pause
    exit /b 1
)

echo [OK] Projekt-Struktur validiert
echo      Backend:  %PROJECT_ROOT%\backend
echo      Frontend: %PROJECT_ROOT%\frontend

REM ============================================================================
REM 3. NODE.JS PRÜFUNG
REM ============================================================================
echo.
echo [3/8] Pruefe Node.js Installation...

where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [FEHLER] Node.js ist nicht installiert oder nicht im PATH!
    echo.
    echo Bitte installieren Sie Node.js v18 oder neuer:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node -v') do set NODE_VERSION=%%i
echo [OK] Node.js %NODE_VERSION% gefunden

REM ============================================================================
REM 4. PYTHON PRÜFUNG
REM ============================================================================
echo.
echo [4/8] Pruefe Python Installation...

where python >nul 2>&1
if %errorLevel% neq 0 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH!
    echo.
    echo Bitte installieren Sie Python 3.8 oder neuer:
    echo https://www.python.org/downloads/
    echo.
    echo WICHTIG: Bei Installation "Add Python to PATH" aktivieren!
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% gefunden

REM Python-Version prüfen (mindestens 3.8)
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if %errorLevel% neq 0 (
    echo [FEHLER] Python 3.8 oder neuer erforderlich!
    pause
    exit /b 1
)

REM ============================================================================
REM 5. GIT PRÜFUNG (OPTIONAL)
REM ============================================================================
echo.
echo [5/8] Pruefe Git Installation (optional)...

where git >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNUNG] Git ist nicht installiert.
    echo           Git wird fuer Updates und Versionskontrolle empfohlen.
    echo.
    echo Moechten Sie Git jetzt installieren? (j/n)
    set /p INSTALL_GIT="> "
    
    if /i "!INSTALL_GIT!"=="j" (
        echo Oeffne Git Download-Seite...
        start https://git-scm.com/download/win
        echo.
        echo Bitte installieren Sie Git und fuehren Sie dieses Skript erneut aus.
        pause
        exit /b 0
    ) else (
        echo [INFO] Ueberspringe Git-Installation
    )
) else (
    for /f "tokens=*" %%i in ('git --version') do set GIT_VERSION=%%i
    echo [OK] !GIT_VERSION! gefunden
)

REM ============================================================================
REM 6. BACKEND DEPENDENCIES INSTALLIEREN
REM ============================================================================
echo.
echo [6/8] Installiere Backend-Abhaengigkeiten...
echo      Dies kann einige Minuten dauern...
echo.

cd "%PROJECT_ROOT%\backend"

REM Virtuelle Umgebung erstellen
if not exist "venv\" (
    echo [INFO] Erstelle virtuelle Python-Umgebung...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo [FEHLER] Konnte virtuelle Umgebung nicht erstellen!
        pause
        exit /b 1
    )
    echo [OK] Virtuelle Umgebung erstellt
) else (
    echo [INFO] Virtuelle Umgebung existiert bereits
)

REM Aktiviere virtuelle Umgebung
echo [INFO] Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo [FEHLER] Konnte virtuelle Umgebung nicht aktivieren!
    pause
    exit /b 1
)

REM Upgrade pip
echo [INFO] Aktualisiere pip...
python -m pip install --upgrade pip --quiet

REM Windows-spezifische requirements.txt erstellen
echo [INFO] Erstelle Windows-kompatible requirements.txt...
if exist "requirements-windows.txt" (
    echo [INFO] Verwende requirements-windows.txt
    pip install -r requirements-windows.txt
) else (
    echo [INFO] Filtere Linux-only Pakete aus requirements.txt...
    
    REM Erstelle temporäre requirements ohne uvloop
    findstr /v /i "uvloop" requirements.txt > requirements-temp.txt
    
    REM Installiere gefilterte requirements
    pip install -r requirements-temp.txt
    
    REM Aufräumen
    del requirements-temp.txt
)

if %errorLevel% neq 0 (
    echo [FEHLER] Installation der Python-Pakete fehlgeschlagen!
    echo          Pruefen Sie die Fehlermeldungen oben.
    pause
    exit /b 1
)

echo [OK] Backend-Abhaengigkeiten installiert

REM Deaktiviere venv für weitere Schritte
deactivate 2>nul

cd "%PROJECT_ROOT%"

REM ============================================================================
REM 7. FRONTEND DEPENDENCIES INSTALLIEREN
REM ============================================================================
echo.
echo [7/8] Installiere Frontend-Abhaengigkeiten...
echo      Dies kann einige Minuten dauern...
echo.

cd "%PROJECT_ROOT%\frontend"

REM Prüfe ob Yarn installiert ist
where yarn >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Yarn nicht gefunden, installiere Yarn global...
    call npm install -g yarn
    if %errorLevel% neq 0 (
        echo [FEHLER] Yarn-Installation fehlgeschlagen!
        echo          Versuche npm stattdessen...
        
        REM Fallback auf npm
        call npm install
        if %errorLevel% neq 0 (
            echo [FEHLER] Auch npm install ist fehlgeschlagen!
            pause
            exit /b 1
        )
        echo [OK] Frontend-Abhaengigkeiten mit npm installiert
        cd "%PROJECT_ROOT%"
        goto :SKIP_YARN
    )
)

REM Installiere mit Yarn
call yarn install
if %errorLevel% neq 0 (
    echo [FEHLER] Frontend-Installation fehlgeschlagen!
    pause
    exit /b 1
)

echo [OK] Frontend-Abhaengigkeiten installiert

:SKIP_YARN
cd "%PROJECT_ROOT%"

REM ============================================================================
REM 8. ERSTELLE START-SKRIPTE
REM ============================================================================
echo.
echo [8/8] Erstelle Start-Skripte...

REM Backend-Start-Skript
echo @echo off > START_BACKEND.bat
echo REM Xionimus AI Backend Starter >> START_BACKEND.bat
echo cd /d "%%~dp0backend" >> START_BACKEND.bat
echo call venv\Scripts\activate.bat >> START_BACKEND.bat
echo python main.py >> START_BACKEND.bat
echo pause >> START_BACKEND.bat

REM Frontend-Start-Skript
echo @echo off > START_FRONTEND.bat
echo REM Xionimus AI Frontend Starter >> START_FRONTEND.bat
echo cd /d "%%~dp0frontend" >> START_FRONTEND.bat
echo call yarn dev >> START_FRONTEND.bat
echo pause >> START_FRONTEND.bat

REM Beide-Start-Skript
echo @echo off > START_ALL.bat
echo REM Xionimus AI - Starte Backend und Frontend >> START_ALL.bat
echo start "Xionimus AI Backend" START_BACKEND.bat >> START_ALL.bat
echo timeout /t 5 /nobreak ^> nul >> START_ALL.bat
echo start "Xionimus AI Frontend" START_FRONTEND.bat >> START_ALL.bat
echo echo. >> START_ALL.bat
echo echo ======================================================================== >> START_ALL.bat
echo echo    Xionimus AI wird gestartet... >> START_ALL.bat
echo echo    Backend:  http://localhost:8001 >> START_ALL.bat
echo echo    Frontend: http://localhost:3000 >> START_ALL.bat
echo echo ======================================================================== >> START_ALL.bat

echo [OK] Start-Skripte erstellt:
echo      - START_BACKEND.bat
echo      - START_FRONTEND.bat
echo      - START_ALL.bat

REM ============================================================================
REM FERTIG!
REM ============================================================================
echo.
echo ========================================================================
echo    Installation erfolgreich abgeschlossen!
echo ========================================================================
echo.
echo Naechste Schritte:
echo.
echo 1. Starten Sie Xionimus AI mit: START_ALL.bat
echo    Oder einzeln:
echo    - Backend:  START_BACKEND.bat
echo    - Frontend: START_FRONTEND.bat
echo.
echo 2. Oeffnen Sie http://localhost:3000 in Ihrem Browser
echo.
echo 3. Konfigurieren Sie Ihre API-Schluessel unter Einstellungen
echo    (OpenAI, Anthropic, Perplexity)
echo.
echo ========================================================================
echo.
pause
