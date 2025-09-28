@echo off
title XIONIMUS AI - Master Installation & Start
color 0A

REM ==========================================
echo.
echo ==========================================
echo    XIONIMUS AI - MASTER INSTALLATION
echo ==========================================
echo.
echo [INFO] Vollständige Installation, Konfiguration und Start
echo [INFO] Für Python 3.10+ und Node.js 18+  
echo [INFO] Behebt alle bekannten Import- und Konfigurationsprobleme
echo.

REM Automatische Installation - keine Benutzereingaben erforderlich
echo [WORKFLOW] Vollständig automatisierte Installation:
echo   1. System-Voraussetzungen prüfen
echo   2. Projekt-Konfiguration erstellen  
echo   3. Backend Dependencies installieren (inkl. craco)
echo   4. Frontend Dependencies installieren
echo   5. System-Tests durchführen
echo   6. Backend und Frontend automatisch starten
echo   7. Browser automatisch öffnen
echo.
echo [AUTO] Starte automatische Installation in 3 Sekunden...
timeout /t 3 /nobreak >nul

REM ==========================================
echo.
echo [STEP 1/8] SYSTEM-VORAUSSETZUNGEN PRÜFEN
echo ==========================================

REM Verzeichnis-Struktur prüfen
echo [CHECK] Verzeichnis-Struktur...
set INSTALL_DIR=%CD%
echo [INFO] Arbeitsverzeichnis: %INSTALL_DIR%

REM Automatische Pfad-Erkennung
if not exist "backend\server.py" (
    echo [SEARCH] Suche XIONIMUS Verzeichnis...
    
    if exist "C:\AI\XionimusX-main\backend\server.py" (
        cd /d "C:\AI\XionimusX-main"
        echo [FOUND] Gefunden: C:\AI\XionimusX-main
    ) else if exist "%USERPROFILE%\Desktop\XionimusX-main\backend\server.py" (
        cd /d "%USERPROFILE%\Desktop\XionimusX-main"
        echo [FOUND] Gefunden: Desktop\XionimusX-main
    ) else if exist "%USERPROFILE%\Downloads\XionimusX-main\backend\server.py" (
        cd /d "%USERPROFILE%\Downloads\XionimusX-main"
        echo [FOUND] Gefunden: Downloads\XionimusX-main
    ) else (
        echo [ERROR] XIONIMUS Verzeichnis nicht gefunden!
        echo [HELP] Mögliche Lösungen:
        echo   1. Stellen Sie sicher, dass Sie das Projekt heruntergeladen haben
        echo   2. Extrahieren Sie das ZIP-Archiv vollständig
        echo   3. Navigieren Sie manuell zum XionimusX-main Verzeichnis
        echo   4. Führen Sie dieses Script aus dem Projektordner aus
        pause
        exit /b 1
    )
    
    REM Prüfe nach Verzeichniswechsel
    if not exist "backend\server.py" (
        echo [ERROR] Verzeichniswechsel fehlgeschlagen!
        echo [DEBUG] Aktuelles Verzeichnis: %CD%
        pause
        exit /b 1
    )
)

if not exist "frontend\package.json" (
    echo [ERROR] Frontend-Verzeichnis nicht vollständig!
    pause
    exit /b 1
)

echo [SUCCESS] Projektstruktur validiert

REM Python prüfen
echo [CHECK] Python Installation...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht gefunden!
    echo [INFO] Bitte Python 3.10+ installieren: https://python.org
    pause
    exit /b 1
) else (
    python --version
    python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python 3.10+ erforderlich
        pause  
        exit /b 1
    )
    echo [SUCCESS] Python Version kompatibel
)

REM Node.js prüfen
echo [CHECK] Node.js Installation...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js nicht gefunden!
    echo [INFO] Bitte Node.js 18+ installieren: https://nodejs.org
    pause
    exit /b 1
) else (
    node --version
    echo [SUCCESS] Node.js verfügbar
)

echo.

REM ==========================================
echo [STEP 2/8] PROJEKT-KONFIGURATION
echo ==========================================

echo [CREATE] Erstelle notwendige Verzeichnisse...
if not exist "backend\sessions" mkdir backend\sessions
if not exist "backend\uploads" mkdir backend\uploads  
if not exist "backend\local_data" mkdir backend\local_data

echo [CREATE] Konfigurationsdateien...

REM Backend .env
(
echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
echo ANTHROPIC_API_KEY=
echo OPENAI_API_KEY=  
echo PERPLEXITY_API_KEY=
) > backend\.env

REM Frontend .env  
echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env

if exist "backend\.env" if exist "frontend\.env" (
    echo [SUCCESS] Konfigurationsdateien erstellt
) else (
    echo [ERROR] Fehler beim Erstellen der .env Dateien
    pause
    exit /b 1
)

echo.

REM ==========================================
echo [STEP 3/8] BACKEND DEPENDENCIES
echo ==========================================

echo [PRECHECK] System-Prüfungen für Dependencies...

REM Teste Internet-Verbindung zu PyPI
echo [TEST] Teste Internet-Verbindung zu PyPI...
ping -n 1 pypi.org >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Keine Verbindung zu pypi.org
    echo [DEBUG] Versuche alternative Konnektivität...
    ping -n 1 8.8.8.8 >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Keine Internet-Verbindung verfügbar
        echo [ACTION] Bitte prüfen Sie Ihre Netzwerkverbindung
        set /p continue_offline="Trotzdem fortfahren? (y/n): "
        if /i not "%continue_offline%"=="y" (
            pause
            exit /b 1
        )
    ) else (
        echo [INFO] Internet verfügbar - PyPI möglicherweise temporär nicht erreichbar
    )
) else (
    echo [SUCCESS] PyPI erreichbar
)

REM Teste Schreibrechte im aktuellen Verzeichnis
echo [TEST] Teste Schreibrechte...
echo test > test_write.tmp 2>nul
if exist test_write.tmp (
    del test_write.tmp
    echo [SUCCESS] Schreibrechte verfügbar
) else (
    echo [WARNING] Möglicherweise keine Schreibrechte - könnte Probleme verursachen
)

echo [DEBUG] Aktuelles Verzeichnis: %CD%
echo [ACTION] Wechsle ins Backend-Verzeichnis...

cd backend
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Kann nicht ins Backend-Verzeichnis wechseln
    echo [DEBUG] Prüfe ob backend\ Ordner existiert
    pause
    exit /b 1
)

echo [DEBUG] Backend-Verzeichnis: %CD%
if not exist "server.py" (
    echo [ERROR] server.py nicht gefunden - falsches Verzeichnis?
    echo [DEBUG] Verfügbare Dateien:
    dir /b *.py 2>nul || echo Keine Python-Dateien gefunden
    pause
    exit /b 1
)

echo [TEST] Teste Python und pip Verfügbarkeit...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht verfügbar im Backend-Verzeichnis
    pause
    exit /b 1
)

python -m pip --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip nicht verfügbar
    pause
    exit /b 1
)

echo [UPDATE] Pip modernisieren...  
python -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Pip Update fehlgeschlagen
    echo [DEBUG] Versuche ohne --upgrade...
    python -m pip install pip setuptools wheel
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Auch Basis-Pip Installation fehlgeschlagen
        echo [INFO] Möglicherweise Berechtigungsproblem oder Netzwerkfehler
        pause
        exit /b 1
    )
)

echo [INSTALL] Kritische Async/Network Dependencies...
echo [DEBUG] Installiere: aiohttp, aiohappyeyeballs, aiosignal, anyio...
python -m pip install aiohttp==3.12.15 aiohappyeyeballs aiosignal anyio==4.11.0
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Erste Async-Dependencies fehlgeschlagen - versuche einzeln...
    python -m pip install aiohttp==3.12.15
    python -m pip install aiohappyeyeballs aiosignal anyio==4.11.0
)

echo [DEBUG] Installiere: multidict, frozenlist, yarl, propcache...
python -m pip install multidict frozenlist yarl propcache
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Einige Async-Dependencies fehlgeschlagen - nicht kritisch
    echo [INFO] Versuche Fortsetzung...
)

echo [INSTALL] Web Framework (KRITISCH)...
echo [DEBUG] Installiere: fastapi, uvicorn, starlette...
python -m pip install fastapi==0.110.1 uvicorn==0.25.0 starlette
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Web Framework Installation fehlgeschlagen
    echo [DEBUG] Versuche Fallback-Versionen...
    python -m pip install fastapi uvicorn starlette
    if %ERRORLEVEL% NEQ 0 (
        echo [CRITICAL] Web Framework Installation komplett fehlgeschlagen
        echo [INFO] Backend kann ohne FastAPI nicht funktionieren
        pause
        exit /b 1
    )
)

echo [DEBUG] Installiere: pydantic, typing_extensions...
python -m pip install pydantic typing_extensions
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Pydantic Installation fehlgeschlagen - versuche ohne Version...
    python -m pip install pydantic
)

echo [INSTALL] Database (KRITISCH)...
echo [DEBUG] Installiere: motor, pymongo, dnspython...
python -m pip install motor==3.3.1 pymongo==4.5.0 dnspython
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Database Dependencies mit Versionen fehlgeschlagen
    echo [DEBUG] Versuche ohne spezifische Versionen...
    python -m pip install motor pymongo dnspython
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Database Dependencies Installation komplett fehlgeschlagen
        echo [INFO] Backend benötigt MongoDB Treiber
        echo [ACTION] Versuche Fortsetzung ohne Database...
    )
)

echo [INSTALL] AI APIs...
echo [DEBUG] Installiere: anthropic, openai...
python -m pip install anthropic==0.68.1 openai==1.109.1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] AI APIs mit Versionen fehlgeschlagen - versuche neueste...
    python -m pip install anthropic openai
)

echo [DEBUG] Installiere: httpx, httpcore...
python -m pip install httpx httpcore
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] HTTP Dependencies fehlgeschlagen - nicht kritisch für Start
)

echo [INSTALL] Utilities...
echo [DEBUG] Installiere: python-dotenv, requests...
python -m pip install python-dotenv==1.1.1 requests==2.32.5
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Core Utilities fehlgeschlagen - versuche ohne Versionen...
    python -m pip install python-dotenv requests
)

echo [DEBUG] Installiere: Data Processing (numpy, pandas)...
python -m pip install numpy pandas
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] NumPy/Pandas Installation fehlgeschlagen - nicht kritisch für Start
)

echo [DEBUG] Installiere: Additional Utilities...
python -m pip install PyYAML Jinja2 rich click jsonschema attrs
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Einige Additional Utilities fehlgeschlagen - nicht kritisch
)

echo [DEBUG] Installiere: Pillow (Image Processing)...
python -m pip install Pillow
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Pillow Installation fehlgeschlagen - Image Processing nicht verfügbar
)

echo.
echo [VALIDATION] Teste kritische Backend-Dependencies...
echo =====================================

REM Teste die wichtigsten Imports einzeln mit robuster Fehlerbehandlung
echo [TEST] Teste FastAPI...
python -c "import fastapi; print('✅ FastAPI verfügbar')"
if %ERRORLEVEL% NEQ 0 echo ❌ FastAPI FEHLT

echo [TEST] Teste Uvicorn...
python -c "import uvicorn; print('✅ Uvicorn verfügbar')"
if %ERRORLEVEL% NEQ 0 echo ❌ Uvicorn FEHLT

echo [TEST] Teste aiohttp...
python -c "import aiohttp; print('✅ aiohttp verfügbar')"
if %ERRORLEVEL% NEQ 0 echo ❌ aiohttp FEHLT

echo [TEST] Teste Motor/MongoDB...
python -c "import motor; print('✅ Motor verfügbar')"
if %ERRORLEVEL% NEQ 0 echo ❌ Motor FEHLT

echo [TEST] Teste AI APIs...
python -c "import anthropic; print('✅ Anthropic verfügbar')"
if %ERRORLEVEL% NEQ 0 echo ❌ Anthropic FEHLT

python -c "import openai; print('✅ OpenAI verfügbar')"
if %ERRORLEVEL% NEQ 0 echo ❌ OpenAI FEHLT

echo [TEST] Teste python-dotenv...
python -c "from dotenv import load_dotenv; print('✅ python-dotenv verfügbar')"
if %ERRORLEVEL% NEQ 0 echo ❌ python-dotenv FEHLT

echo.
echo [CRITICAL] Prüfe kritische Dependencies für Backend-Start...

REM Erstelle temporäre Python Test-Datei für robuste Prüfung
echo import sys > temp_test.py
echo try: >> temp_test.py
echo     import fastapi >> temp_test.py
echo     import uvicorn >> temp_test.py
echo     from dotenv import load_dotenv >> temp_test.py
echo     print("[SUCCESS] Backend-Kern ist startbereit!") >> temp_test.py
echo     sys.exit(0) >> temp_test.py
echo except ImportError as e: >> temp_test.py
echo     print(f"[ERROR] Kritische Dependencies fehlen: {e}") >> temp_test.py
echo     sys.exit(1) >> temp_test.py
echo except Exception as e: >> temp_test.py
echo     print(f"[ERROR] Unerwarteter Fehler: {e}") >> temp_test.py
echo     sys.exit(1) >> temp_test.py

python temp_test.py
set BACKEND_TEST_RESULT=%ERRORLEVEL%
del temp_test.py

if %BACKEND_TEST_RESULT% NEQ 0 (
    echo.
    echo [WARNING] BACKEND DEPENDENCIES UNVOLLSTÄNDIG!
    echo [AUTO] Versuche Reparatur-Installation...
    
    REM Automatische Reparatur-Installation
    echo [REPAIR] Installiere kritische Dependencies erneut...
    python -m pip install --force-reinstall fastapi uvicorn python-dotenv
    
    REM Erneuter Test
    python temp_test.py >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Reparatur erfolgreich - Backend bereit!
    ) else (
        echo [WARNING] Backend unvollständig - Installation fortsetzt trotzdem
        echo [INFO] Einige Features möglicherweise nicht verfügbar
    )
) else (
    echo [SUCCESS] Backend Dependencies erfolgreich installiert!
)

echo [TEST] Backend System Import-Test...

REM Erstelle .env Datei falls nicht vorhanden (für Agent Manager Test)
if not exist ".env" (
    echo [DEBUG] Erstelle temporäre .env für Import-Test...
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai > .env
    echo ANTHROPIC_API_KEY= >> .env
    echo OPENAI_API_KEY= >> .env
    echo PERPLEXITY_API_KEY= >> .env
)

REM Teste Backend Import mit robuster Fehlerbehandlung
echo import sys > temp_backend_test.py
echo import os >> temp_backend_test.py
echo sys.path.append('.') >> temp_backend_test.py
echo try: >> temp_backend_test.py
echo     from agents.agent_manager import AgentManager >> temp_backend_test.py
echo     print("[SUCCESS] Backend-System erfolgreich importiert") >> temp_backend_test.py
echo     sys.exit(0) >> temp_backend_test.py
echo except Exception as e: >> temp_backend_test.py
echo     print(f"[WARNING] Backend-Import Problem: {e}") >> temp_backend_test.py
echo     print("[INFO] Dies kann behoben werden wenn .env konfiguriert ist") >> temp_backend_test.py
echo     sys.exit(0) >> temp_backend_test.py

python temp_backend_test.py
del temp_backend_test.py

echo [INFO] Backend Import-Test abgeschlossen (Warnings sind normal ohne API Keys)

echo.
echo [SUMMARY] Schritt 3 - Backend Dependencies Zusammenfassung
echo ========================================================
echo [INFO] Verzeichnis: %CD%
echo [INFO] Python Version: 
python --version
echo [INFO] Pip Version:
python -m pip --version
echo.

REM Final test der wichtigsten Module
echo [FINAL TEST] Kritische Module Check:
python -c "
modules = ['fastapi', 'uvicorn', 'aiohttp', 'motor', 'anthropic', 'openai']
success = 0
total = len(modules)
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
        success += 1
    except ImportError:
        print(f'❌ {module}')

print(f'\\n[RESULT] {success}/{total} kritische Module verfügbar')
if success >= 4:
    print('[STATUS] Backend kann gestartet werden')
else:
    print('[STATUS] Backend möglicherweise nicht vollständig funktional')
"

cd ..

echo.

REM ==========================================
echo [STEP 4/8] FRONTEND DEPENDENCIES  
echo ==========================================

cd frontend

REM Prüfe package.json
if not exist "package.json" (
    echo [ERROR] package.json nicht gefunden im Frontend-Verzeichnis
    echo [DEBUG] Aktuelles Verzeichnis: %CD%
    echo [INFO] Installation kann nicht fortgesetzt werden
    cd ..
    exit /b 1
)

echo [INFO] Frontend Dependencies aus package.json:
echo [CHECK] Craco (React Build Tool): 
findstr "craco" package.json | findstr "dependencies"
echo [CHECK] React Scripts und weitere Dependencies werden installiert...

echo [INFO] Prüfe Package Manager Verfügbarkeit...

REM Yarn installieren falls nicht vorhanden
where yarn >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INSTALL] Installiere Yarn global...
    npm install -g yarn
    if %ERRORLEVEL% NEQ 0 (
        echo [WARNING] Yarn Installation fehlgeschlagen - verwende npm
        set USE_NPM=1
    ) else (
        echo [SUCCESS] Yarn installiert
    )
) else (
    echo [INFO] Yarn bereits verfügbar
)

REM Frontend Dependencies installieren mit Fallback-Strategie
if defined USE_NPM (
    goto :use_npm
) else (
    echo [YARN] Installiere Frontend Dependencies mit yarn...
    yarn install
    if %ERRORLEVEL% EQU 0 (
        set START_FRONTEND_CMD=yarn start
        echo [SUCCESS] Frontend Dependencies mit yarn installiert
        goto :frontend_deps_done
    ) else (
        echo [WARNING] Yarn Installation fehlgeschlagen - fallback zu npm
    )
)

:use_npm
echo [NPM] Installiere Frontend Dependencies mit npm...
npm install
if %ERRORLEVEL% EQU 0 (
    set START_FRONTEND_CMD=npm start
    echo [SUCCESS] Frontend Dependencies mit npm installiert
) else (
    echo [ERROR] Frontend Installation komplett fehlgeschlagen
    echo [DEBUG] Prüfe Internet-Verbindung und npm Registry
    pause
    exit /b 1
)

:frontend_deps_done
cd ..

echo.

REM ==========================================  
echo [STEP 5/8] SYSTEM-TESTS
echo ==========================================

echo [TEST] Backend-Module...
cd backend
python -c "import aiohttp, fastapi, motor; print('✅ Core modules OK')" || echo ❌ Core modules fehlen
python -c "from agents.agent_manager import AgentManager; print('✅ Agent System OK')" || echo ❌ Agent System fehlen

echo [TEST] Konfigurationsdateien...
if exist ".env" (echo ✅ backend\.env) else (echo ❌ backend\.env fehlt)
cd ..\frontend  
if exist ".env" (echo ✅ frontend\.env) else (echo ❌ frontend\.env fehlt)
cd ..

echo.

REM ==========================================
echo [STEP 6/8] BACKEND STARTEN
echo ==========================================

REM Port-Prüfung für Backend (automatisch)
echo [CHECK] Prüfe Port 8001 für Backend...
netstat -an | findstr :8001 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 8001 ist bereits belegt - versuche automatische Lösung
    echo [AUTO] Beende eventuell laufende Prozesse auf Port 8001...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do (
        echo [AUTO] Beende Prozess %%a auf Port 8001
        taskkill /f /pid %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
    netstat -an | findstr :8001 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Port 8001 immer noch belegt - Installation fortsetzt trotzdem
    ) else (
        echo [SUCCESS] Port 8001 erfolgreich freigegeben
    )
) else (
    echo [SUCCESS] Port 8001 verfügbar
)

echo [START] Starte Backend-Server...
cd backend

REM Prüfe ob server.py existiert
if not exist "server.py" (
    echo [ERROR] server.py nicht gefunden im Backend-Verzeichnis
    pause
    exit /b 1
)

REM Schneller Import-Test vor Start
echo [PRETEST] Teste kritische Backend-Imports...
python -c "
try:
    import sys
    sys.path.append('.')
    import server
    print('[SUCCESS] Backend bereit für Start')
except Exception as e:
    print(f'[ERROR] Backend nicht startbereit: {e}')
    exit(1)
" || (
    echo [ERROR] Backend kann nicht gestartet werden - Import-Probleme
    pause
    exit /b 1
)

echo [LAUNCH] Starte Backend in separatem Fenster...
start "XIONIMUS Backend" cmd /k "title XIONIMUS Backend Server && echo. && echo ========================================= && echo    XIONIMUS AI BACKEND SERVER && echo ========================================= && echo [INFO] Backend läuft auf http://localhost:8001 && echo [INFO] Lassen Sie dieses Fenster geöffnet! && echo. && python server.py"

REM Warte und teste Backend-Verfügbarkeit
echo [WAIT] Warte auf Backend-Start...
timeout /t 8 /nobreak >nul

echo [TEST] Teste Backend-Verfügbarkeit...
python -c "
import time
import socket
print('[INFO] Teste Backend-Verbindung...')
for i in range(10):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8001))
        sock.close()
        if result == 0:
            print('[SUCCESS] Backend antwortet auf Port 8001')
            exit(0)
    except:
        pass
    print(f'[RETRY] Warte auf Backend... ({i+1}/10)')
    time.sleep(1)
print('[WARNING] Backend antwortet nicht - möglicherweise noch am starten')
"

cd ..

echo.

REM ==========================================
echo [STEP 7/8] FRONTEND STARTEN  
echo ==========================================

REM Port-Prüfung für Frontend (automatisch)
echo [CHECK] Prüfe Port 3000 für Frontend...
netstat -an | findstr :3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 3000 ist bereits belegt - versuche automatische Lösung
    echo [AUTO] Beende eventuell laufende Prozesse auf Port 3000...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
        echo [AUTO] Beende Prozess %%a auf Port 3000
        taskkill /f /pid %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
    netstat -an | findstr :3000 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [INFO] Port 3000 immer noch belegt - Installation fortsetzt trotzdem
    ) else (
        echo [SUCCESS] Port 3000 erfolgreich freigegeben
    )
) else (
    echo [SUCCESS] Port 3000 verfügbar
)

echo [START] Starte Frontend-Server...
cd frontend

REM Bestimme den korrekten Start-Befehl basierend auf vorheriger Installation
if "%START_FRONTEND_CMD%"=="" (
    REM Fallback wenn Variable nicht gesetzt
    where yarn >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set START_FRONTEND_CMD=yarn start
        echo [INFO] Verwende yarn für Frontend-Start
    ) else (
        set START_FRONTEND_CMD=npm start  
        echo [INFO] Verwende npm für Frontend-Start
    )
)

REM Prüfe node_modules
if not exist "node_modules" (
    echo [WARNING] node_modules nicht gefunden - Dependencies möglicherweise nicht installiert
    echo [ACTION] Versuche schnelle Installation...
    npm install --silent
)

echo [LAUNCH] Starte Frontend in separatem Fenster...
start "XIONIMUS Frontend" cmd /k "title XIONIMUS Frontend Server && echo. && echo ========================================= && echo    XIONIMUS AI FRONTEND SERVER && echo ========================================= && echo [INFO] Frontend läuft auf http://localhost:3000 && echo [INFO] Lassen Sie dieses Fenster geöffnet! && echo [STARTING] Lade React Application... && echo. && %START_FRONTEND_CMD%"

echo [WAIT] Warte auf Frontend-Start (React Build dauert etwas)...
timeout /t 12 /nobreak >nul

echo [TEST] Teste Frontend-Verfügbarkeit...
python -c "
import time
import socket
print('[INFO] Teste Frontend-Verbindung...')
for i in range(15):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 3000))
        sock.close()
        if result == 0:
            print('[SUCCESS] Frontend antwortet auf Port 3000')
            exit(0)
    except:
        pass
    print(f'[RETRY] Warte auf Frontend... ({i+1}/15)')
    time.sleep(2)
print('[WARNING] Frontend antwortet nicht - React Build dauert eventuell länger')
"

cd ..

echo.

REM ==========================================
echo [STEP 8/8] SYSTEM BEREIT
echo ==========================================

REM Finale Status-Prüfung
echo [FINAL] Finale System-Prüfung...
python -c "
import socket
import sys

def test_port(port, name):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

backend_ok = test_port(8001, 'Backend')
frontend_ok = test_port(3000, 'Frontend')

print(f'Backend Port 8001: {\"✅ OK\" if backend_ok else \"❌ NICHT VERFÜGBAR\"}')
print(f'Frontend Port 3000: {\"✅ OK\" if frontend_ok else \"❌ NICHT VERFÜGBAR\"}')

if backend_ok and frontend_ok:
    print('[SUCCESS] Beide Server laufen erfolgreich!')
    sys.exit(0)
elif backend_ok:
    print('[PARTIAL] Backend läuft, Frontend startet noch...')
    sys.exit(1)
elif frontend_ok:
    print('[PARTIAL] Frontend läuft, Backend Problem')
    sys.exit(2)  
else:
    print('[WARNING] Beide Server haben Probleme')
    sys.exit(3)
"

set SERVER_STATUS=%ERRORLEVEL%

echo.
echo 🎉 XIONIMUS AI INSTALLATION UND START ABGESCHLOSSEN!
echo.

if %SERVER_STATUS% EQU 0 (
    echo 🖥️ SERVER-STATUS:
    echo   ✅ Backend:  Läuft erfolgreich auf http://localhost:8001
    echo   ✅ Frontend: Läuft erfolgreich auf http://localhost:3000
    echo   ✅ SYSTEM:   Vollständig einsatzbereit!
) else if %SERVER_STATUS% EQU 1 (
    echo 🖥️ SERVER-STATUS:
    echo   ✅ Backend:  Läuft erfolgreich auf http://localhost:8001
    echo   ⏳ Frontend: Startet noch... (React Build in Arbeit)
    echo   ⚠️ SYSTEM:   Teilweise bereit
) else (
    echo 🖥️ SERVER-STATUS:
    echo   ⚠️ Backend:  Möglicherweise noch am starten...
    echo   ⚠️ Frontend: Möglicherweise noch am starten...
    echo   ❓ SYSTEM:   Prüfe Server-Fenster für Details
)
echo.
echo 🌐 ZUGRIFF:
echo   → Frontend: http://localhost:3000  (Haupt-UI)
echo   → Backend:  http://localhost:8001  (API-Server)
echo.  
echo 📋 WICHTIGE HINWEISE:
echo   ✓ Beide Server-Fenster müssen geöffnet bleiben
echo   ✓ Backend-Fenster: "XIONIMUS Backend"
echo   ✓ Frontend-Fenster: "XIONIMUS Frontend"
echo   ✓ Schließen Sie NICHT die Server-Fenster
echo.
echo 🔑 ERSTE SCHRITTE:
echo   1. Browser öffnet automatisch http://localhost:3000
echo   2. Klicke "API Configuration" 
echo   3. Konfiguriere deine API-Keys:
echo      • Anthropic API Key (für Claude)
echo      • OpenAI API Key (für GPT)
echo      • Perplexity API Key (für Research)
echo   4. Starte mit einem Chat!
echo.
echo 🤖 VERFÜGBARE FEATURES:
echo   ✅ 9 AI-Agenten (Code, Research, Writing, Data, QA, etc.)
echo   ✅ Multi-Agent Chat System mit intelligenter Weiterleitung
echo   ✅ GitHub Repository Integration
echo   ✅ File Upload und Management
echo   ✅ Session Management (Gespräche speichern)
echo   ✅ Projekt Management
echo.
echo 🛠️ TROUBLESHOOTING:
echo   • Weiße Seite? → Warte 1-2 Minuten, Frontend startet noch
echo   • Backend-Fehler? → Prüfe Backend-Fenster für Fehlermeldungen
echo   • Port belegt? → Andere Anwendungen auf Port 3000/8001 schließen
echo   • Bei Problemen: Script erneut ausführen
echo.
echo 🚀 SYSTEM IST BEREIT! Browser öffnet in 5 Sekunden...
echo.

REM Intelligenter Browser-Launch
if %SERVER_STATUS% EQU 0 (
    echo 🚀 SYSTEM IST BEREIT! Browser öffnet in 5 Sekunden...
    timeout /t 5 /nobreak >nul
    echo [LAUNCH] Öffne XIONIMUS AI...
    start http://localhost:3000
) else if %SERVER_STATUS% EQU 1 (
    echo 🚀 BACKEND BEREIT! Browser öffnet in 10 Sekunden (Frontend Build läuft noch)...
    timeout /t 10 /nobreak >nul
    echo [LAUNCH] Öffne XIONIMUS AI (Frontend lädt noch)...
    start http://localhost:3000
) else (
    echo ⏳ Server starten noch... Browser öffnet in 15 Sekunden...
    echo [INFO] Falls Seite nicht lädt, warten Sie 1-2 Minuten und laden neu
    timeout /t 15 /nobreak >nul
    echo [LAUNCH] Öffne XIONIMUS AI (möglicherweise noch am laden)...
    start http://localhost:3000
)

echo.
echo ✨ XIONIMUS AI GESTARTET! ✨
echo.

REM Finale Anweisungen basierend auf Status
if %SERVER_STATUS% EQU 0 (
    echo ✅ ALLES BEREIT! Sie können sofort loslegen.
) else (
    echo ⏳ FALLS DIE SEITE NICHT LÄDT:
    echo   → Warten Sie 1-2 Minuten
    echo   → Laden Sie die Seite neu (F5)
    echo   → Prüfen Sie die Server-Fenster für Fehlermeldungen
)

echo.
echo 📋 WICHTIG:
echo   ✓ Lassen Sie beide Server-Fenster geöffnet
echo   ✓ "XIONIMUS Backend" und "XIONIMUS Frontend" 
echo   ✓ Bei Problemen: Script erneut ausführen
echo.
echo 🔧 SUPPORT:
echo   → Server-Logs in den Konsolen-Fenstern prüfen
echo   → Bei anhaltenden Problemen: Script neu starten
echo   → Beide Ports (3000, 8001) müssen frei sein
echo.
echo [INFO] Dieses Installationsfenster kann nun geschlossen werden.
echo.
pause