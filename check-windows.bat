@echo off
:: ============================================================
:: Xionimus AI - Windows System Check & Diagnostics
:: ============================================================
:: Prüft alle Voraussetzungen und findet potenzielle Probleme
:: ============================================================

title Xionimus AI - System Check

echo.
echo ========================================================
echo  Xionimus AI - Windows Systemprüfung
echo ========================================================
echo.

set ERROR_COUNT=0
set WARNING_COUNT=0

:: ============================================================
:: Python Check
:: ============================================================
echo [1/10] Python prüfen...
python --version >nul 2>&1
if errorlevel 1 (
    echo    [FEHLER] Python nicht gefunden!
    echo    [INFO] Installiere Python 3.11+ von https://www.python.org/downloads/
    set /a ERROR_COUNT+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo    [OK] Python gefunden: %PYTHON_VERSION%
    
    :: Prüfe Python-Version (mindestens 3.11)
    for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
        if %%a LSS 3 (
            echo    [FEHLER] Python Version zu alt! Benötigt: 3.11+
            set /a ERROR_COUNT+=1
        ) else if %%a EQU 3 (
            if %%b LSS 11 (
                echo    [WARNUNG] Python 3.11+ empfohlen, aktuell: %PYTHON_VERSION%
                set /a WARNING_COUNT+=1
            )
        )
    )
)

:: ============================================================
:: Node.js Check
:: ============================================================
echo.
echo [2/10] Node.js prüfen...
node --version >nul 2>&1
if errorlevel 1 (
    echo    [FEHLER] Node.js nicht gefunden!
    echo    [INFO] Installiere Node.js 18+ von https://nodejs.org/
    set /a ERROR_COUNT+=1
) else (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo    [OK] Node.js gefunden: %NODE_VERSION%
)

:: ============================================================
:: Yarn Check
:: ============================================================
echo.
echo [3/10] Yarn prüfen...
yarn --version >nul 2>&1
if errorlevel 1 (
    echo    [WARNUNG] Yarn nicht gefunden
    echo    [INFO] Wird automatisch installiert mit: npm install -g yarn
    set /a WARNING_COUNT+=1
) else (
    for /f "tokens=1" %%i in ('yarn --version 2^>^&1') do set YARN_VERSION=%%i
    echo    [OK] Yarn gefunden: %YARN_VERSION%
)

:: ============================================================
:: MongoDB Check
:: ============================================================
echo.
echo [4/10] MongoDB prüfen...
mongosh --version >nul 2>&1
if errorlevel 1 (
    echo    [WARNUNG] MongoDB Shell nicht gefunden
    echo    [INFO] Installiere von https://www.mongodb.com/try/download/community
    set /a WARNING_COUNT+=1
) else (
    for /f "tokens=2" %%i in ('mongosh --version 2^>^&1') do set MONGO_VERSION=%%i
    echo    [OK] MongoDB Shell gefunden: %MONGO_VERSION%
)

:: Prüfe MongoDB Service
sc query MongoDB >nul 2>&1
if errorlevel 1 (
    echo    [WARNUNG] MongoDB Service nicht installiert
    set /a WARNING_COUNT+=1
) else (
    sc query MongoDB | find "RUNNING" >nul 2>&1
    if errorlevel 1 (
        echo    [WARNUNG] MongoDB Service läuft nicht
        echo    [INFO] Starte mit: net start MongoDB
        set /a WARNING_COUNT+=1
    ) else (
        echo    [OK] MongoDB Service läuft
    )
)

:: ============================================================
:: Git Check
:: ============================================================
echo.
echo [5/10] Git prüfen...
git --version >nul 2>&1
if errorlevel 1 (
    echo    [WARNUNG] Git nicht gefunden
    echo    [INFO] Installiere von https://git-scm.com/download/win
    set /a WARNING_COUNT+=1
) else (
    for /f "tokens=3" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
    echo    [OK] Git gefunden: %GIT_VERSION%
)

:: ============================================================
:: Virtual Environment Check
:: ============================================================
echo.
echo [6/10] Backend Virtual Environment prüfen...
if exist "backend\venv\" (
    echo    [OK] Virtual Environment existiert
    
    :: Prüfe ob es ein Windows venv ist
    if exist "backend\venv\Scripts\activate.bat" (
        echo    [OK] Windows venv erkannt
    ) else (
        echo    [WARNUNG] Kein Windows venv - möglicherweise von Linux
        echo    [INFO] Lösche und erstelle neu mit install.bat
        set /a WARNING_COUNT+=1
    )
) else (
    echo    [INFO] Virtual Environment nicht vorhanden
    echo    [INFO] Wird mit install.bat erstellt
)

:: ============================================================
:: Dependencies Check
:: ============================================================
echo.
echo [7/10] Backend Dependencies prüfen...
if exist "backend\venv\Scripts\python.exe" (
    echo    [INFO] Prüfe installierte Packages...
    
    backend\venv\Scripts\python.exe -c "import fastapi" >nul 2>&1
    if errorlevel 1 (
        echo    [WARNUNG] FastAPI nicht installiert
        set /a WARNING_COUNT+=1
    ) else (
        echo    [OK] FastAPI installiert
    )
    
    backend\venv\Scripts\python.exe -c "import anthropic" >nul 2>&1
    if errorlevel 1 (
        echo    [WARNUNG] Anthropic SDK nicht installiert
        set /a WARNING_COUNT+=1
    ) else (
        echo    [OK] Anthropic SDK installiert
    )
    
    backend\venv\Scripts\python.exe -c "import openai" >nul 2>&1
    if errorlevel 1 (
        echo    [WARNUNG] OpenAI SDK nicht installiert
        set /a WARNING_COUNT+=1
    ) else (
        echo    [OK] OpenAI SDK installiert
    )
    
    :: Prüfe sse-starlette (bekanntes Problem)
    backend\venv\Scripts\python.exe -c "import sse_starlette" >nul 2>&1
    if errorlevel 1 (
        echo    [FEHLER] sse-starlette nicht installiert
        echo    [INFO] Installiere mit: pip install sse-starlette==2.1.3
        set /a ERROR_COUNT+=1
    ) else (
        echo    [OK] sse-starlette installiert
    )
    
    :: Prüfe WeasyPrint (optional auf Windows)
    backend\venv\Scripts\python.exe -c "import weasyprint" >nul 2>&1
    if errorlevel 1 (
        echo    [INFO] WeasyPrint nicht verfügbar (optional auf Windows)
        echo    [INFO] PDF-Export benötigt GTK: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
    ) else (
        echo    [OK] WeasyPrint installiert (PDF-Export verfügbar)
    )
) else (
    echo    [INFO] Virtual Environment noch nicht initialisiert
)

:: ============================================================
:: Frontend Dependencies Check
:: ============================================================
echo.
echo [8/10] Frontend Dependencies prüfen...
if exist "frontend\node_modules\" (
    echo    [OK] node_modules Ordner existiert
    
    if exist "frontend\node_modules\react\" (
        echo    [OK] React installiert
    ) else (
        echo    [WARNUNG] React nicht gefunden
        set /a WARNING_COUNT+=1
    )
) else (
    echo    [INFO] node_modules nicht vorhanden
    echo    [INFO] Wird mit install.bat erstellt
)

:: ============================================================
:: Configuration Check
:: ============================================================
echo.
echo [9/10] Konfigurationsdateien prüfen...
if exist "backend\.env" (
    echo    [OK] backend\.env existiert
    
    :: Prüfe ob API Keys vorhanden sind
    findstr /C:"ANTHROPIC_API_KEY=" backend\.env | findstr /V "ANTHROPIC_API_KEY=$" >nul 2>&1
    if errorlevel 1 (
        echo    [WARNUNG] ANTHROPIC_API_KEY nicht gesetzt
        set /a WARNING_COUNT+=1
    ) else (
        echo    [OK] ANTHROPIC_API_KEY gesetzt
    )
    
    findstr /C:"OPENAI_API_KEY=" backend\.env | findstr /V "OPENAI_API_KEY=$" >nul 2>&1
    if errorlevel 1 (
        echo    [WARNUNG] OPENAI_API_KEY nicht gesetzt
        set /a WARNING_COUNT+=1
    ) else (
        echo    [OK] OPENAI_API_KEY gesetzt
    )
) else (
    echo    [INFO] backend\.env nicht vorhanden
    echo    [INFO] Wird beim ersten Start automatisch erstellt
)

if exist "frontend\.env" (
    echo    [OK] frontend\.env existiert
) else (
    echo    [INFO] frontend\.env nicht vorhanden (optional)
)

:: ============================================================
:: Port Check
:: ============================================================
echo.
echo [10/10] Port-Verfügbarkeit prüfen...

:: Prüfe Port 8001 (Backend)
netstat -ano | findstr ":8001" >nul 2>&1
if errorlevel 1 (
    echo    [OK] Port 8001 (Backend) ist frei
) else (
    echo    [WARNUNG] Port 8001 (Backend) ist bereits belegt
    echo    [INFO] Finde Prozess mit: netstat -ano ^| findstr :8001
    set /a WARNING_COUNT+=1
)

:: Prüfe Port 3000 (Frontend)
netstat -ano | findstr ":3000" >nul 2>&1
if errorlevel 1 (
    echo    [OK] Port 3000 (Frontend) ist frei
) else (
    echo    [WARNUNG] Port 3000 (Frontend) ist bereits belegt
    echo    [INFO] Finde Prozess mit: netstat -ano ^| findstr :3000
    set /a WARNING_COUNT+=1
)

:: Prüfe Port 27017 (MongoDB)
netstat -ano | findstr ":27017" >nul 2>&1
if errorlevel 1 (
    echo    [WARNUNG] Port 27017 (MongoDB) ist frei
    echo    [INFO] MongoDB läuft möglicherweise nicht
    set /a WARNING_COUNT+=1
) else (
    echo    [OK] Port 27017 (MongoDB) ist in Verwendung
)

:: ============================================================
:: Zusammenfassung
:: ============================================================
echo.
echo ========================================================
echo  Systemprüfung abgeschlossen
echo ========================================================
echo.
echo Fehler:     %ERROR_COUNT%
echo Warnungen:  %WARNING_COUNT%
echo.

if %ERROR_COUNT% GTR 0 (
    echo [AKTION ERFORDERLICH] Bitte behebe die Fehler vor der Installation
    echo.
    echo Nächste Schritte:
    echo 1. Installiere fehlende Software
    echo 2. Führe check-windows.bat erneut aus
    echo 3. Führe install.bat aus
) else if %WARNING_COUNT% GTR 0 (
    echo [EMPFOHLEN] Einige Warnungen sollten behoben werden
    echo.
    echo Du kannst fortfahren mit:
    echo - install.bat ^(Installation^)
    echo.
    echo Oder zuerst Warnungen beheben für beste Ergebnisse
) else (
    echo [BEREIT] System ist bereit für die Installation!
    echo.
    echo Nächste Schritte:
    echo 1. Führe install.bat aus
    echo 2. Füge API-Keys zu backend\.env hinzu
    echo 3. Führe start.bat aus
)

echo.
echo ========================================================
echo  Detaillierte Diagnose
echo ========================================================
echo.
echo System-Informationen:
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"
echo.
echo Freier Speicherplatz:
for /f "tokens=3" %%a in ('dir %SystemDrive%\ ^| find "bytes free"') do set FREE_SPACE=%%a
echo %SystemDrive%\ - %FREE_SPACE% bytes frei
echo.
echo Prozessor:
wmic cpu get name | findstr /V "Name"
echo.

pause
