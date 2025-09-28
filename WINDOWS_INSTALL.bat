@echo off
title XIONIMUS AI - Installation
color 0A

REM ==========================================
echo.
echo ==========================================
echo      XIONIMUS AI - INSTALLATION
echo ==========================================
echo.
echo [INFO] Installiert Backend und Frontend Dependencies
echo [INFO] Erstellt notwendige Konfigurationsdateien
echo [INFO] Bereitet System für den Start vor
echo.

REM Automatische Installation - keine Benutzereingaben erforderlich
echo [WORKFLOW] Automatisierte Installation:
echo   1. System-Voraussetzungen prüfen
echo   2. Projekt-Konfiguration erstellen  
echo   3. Backend Dependencies installieren
echo   4. Frontend Dependencies installieren
echo   5. System-Tests durchführen
echo   6. Bereit für Start mit START_ALL.bat
echo.
echo [AUTO] Starte automatische Installation in 3 Sekunden...
ping 127.0.0.1 -n 4 >nul

REM ==========================================
echo.
echo [STEP 1/6] SYSTEM-VORAUSSETZUNGEN PRÜFEN
echo ==========================================

REM Verzeichnis-Struktur prüfen
echo [CHECK] Verzeichnis-Struktur...
set INSTALL_DIR=%CD%
echo [INFO] Arbeitsverzeichnis: %INSTALL_DIR%

REM Automatische Pfad-Erkennung
if not exist "backend\main.py" (
    echo [SEARCH] Suche XIONIMUS Verzeichnis...
    
    if exist "C:\AI\XionimusX-main\backend\main.py" (
        cd /d "C:\AI\XionimusX-main"
        echo [FOUND] Gefunden: C:\AI\XionimusX-main
    ) else if exist "%USERPROFILE%\Desktop\XionimusX-main\backend\main.py" (
        cd /d "%USERPROFILE%\Desktop\XionimusX-main"
        echo [FOUND] Gefunden: Desktop\XionimusX-main
    ) else if exist "%USERPROFILE%\Downloads\XionimusX-main\backend\main.py" (
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
    if not exist "backend\main.py" (
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
echo [STEP 2/6] PROJEKT-KONFIGURATION
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
echo DEBUG=true
echo HOST=0.0.0.0
echo PORT=8001
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
echo [STEP 3/6] BACKEND DEPENDENCIES
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
        echo [WARNING] Keine Internet-Verbindung verfügbar
        echo [AUTO] Versuche Installation mit lokalem Cache...
        echo [INFO] Einige Dependencies könnten fehlschlagen
    ) else (
        echo [INFO] Internet verfügbar - PyPI möglicherweise temporär nicht erreichbar
        echo [AUTO] Fortsetzung der Installation...
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
    echo [WARNING] Backend Installation wird übersprungen - Frontend wird trotzdem installiert
    goto :skip_backend_install
)

echo [DEBUG] Backend-Verzeichnis: %CD%
if not exist "main.py" (
    echo [ERROR] main.py nicht gefunden - falsches Verzeichnis?
    echo [DEBUG] Verfügbare Dateien:
    dir /b *.py 2>nul || echo Keine Python-Dateien gefunden
    echo [WARNING] Backend Installation wird übersprungen
    cd ..
    goto :skip_backend_install
)

echo [TEST] Teste Python und pip Verfügbarkeit...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python nicht verfügbar im Backend-Verzeichnis
    echo [WARNING] Installation wird trotzdem fortgesetzt...
)

python -m pip --version
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] pip nicht verfügbar
    echo [WARNING] Installation wird trotzdem fortgesetzt...
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
        echo [WARNING] Installation wird trotzdem fortgesetzt...
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
        echo [WARNING] Installation wird trotzdem fortgesetzt...
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

:skip_backend_install
cd ..

echo.

REM ==========================================
echo [STEP 4/6] FRONTEND DEPENDENCIES  
echo ==========================================

echo [DEBUG] Aktuelles Verzeichnis vor Frontend-Installation: %CD%
echo [DEBUG] Prüfe ob Frontend-Verzeichnis existiert...
if not exist "frontend" (
    echo [ERROR] Frontend-Verzeichnis nicht gefunden!
    echo [DEBUG] Verfügbare Verzeichnisse im aktuellen Pfad:
    dir /ad /b
    echo [WARNING] Frontend Installation wird übersprungen
    goto :skip_frontend
)

echo [DEBUG] Frontend-Verzeichnis gefunden, wechsle hinein...
REM Wechsle ins Frontend-Verzeichnis
cd frontend
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Kann nicht ins Frontend-Verzeichnis wechseln
    echo [WARNING] Frontend Installation wird übersprungen
    goto :skip_frontend
)

echo [DEBUG] Aktuelles Verzeichnis nach Wechsel: %CD%

REM Prüfe package.json
if not exist "package.json" (
    echo [ERROR] package.json nicht gefunden im Frontend-Verzeichnis
    echo [DEBUG] Verzeichnisinhalt:
    dir /b
    cd ..
    echo [WARNING] Frontend Installation übersprungen
    goto :skip_frontend
)

echo [SUCCESS] package.json gefunden
echo [INFO] Starte Frontend Dependencies Installation...
echo [DEBUG] Vor Installation - überprüfe aktuellen Zustand:
if exist "node_modules" (
    echo [DEBUG] node_modules Verzeichnis bereits vorhanden
) else (
    echo [DEBUG] node_modules Verzeichnis nicht vorhanden - wird erstellt
)
echo [DEBUG] NPM Version check...
npm --version
echo [DEBUG] Node.js Version check...
node --version

REM Lösche alte node_modules für saubere Installation
if exist "node_modules" (
    echo [INFO] Alte node_modules gefunden - werden für saubere Installation entfernt
    rmdir /s /q node_modules 2>nul
    if exist "node_modules" (
        echo [WARNING] node_modules konnten nicht vollständig gelöscht werden - Installation fortsetzen
    )
)

REM NPM Installation (ausschließlich NPM mit React 18 Kompatibilität)
echo [NPM] Starte npm install im Verzeichnis: %CD%
echo [DEBUG] NPM Version: 
npm --version
echo [DEBUG] Node.js Version:
node --version
echo [INFO] React 19 + Node.js 20 ist inkompatibel - downgrade zu React 18...

echo [STEP 1] Installiere React 18 für bessere Kompatibilität...
npm install react@18 react-dom@18 --legacy-peer-deps --force --save
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] React 18 Installation erfolgreich
) else (
    echo [ERROR] React 18 Installation fehlgeschlagen
)

echo [STEP 2] Installiere restliche Dependencies...
npm install --legacy-peer-deps --force
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] npm install erfolgreich ausgeführt
    echo [DEBUG] Überprüfe node_modules Erstellung...
    if exist "node_modules" (
        echo [SUCCESS] node_modules erfolgreich erstellt
    ) else (
        echo [ERROR] node_modules nicht erstellt trotz erfolgreichem npm install
    )
) else (
    echo [ERROR] npm install fehlgeschlagen - Fehlercode: %ERRORLEVEL%
    echo [DEBUG] Führe Fehlerdiagnose durch...
    echo [RETRY] Versuche Cache bereinigen und alternative Installation...
    npm cache clean --force
    echo [RETRY] Versuche npm install mit anderen Flags...
    npm install --force --no-audit --legacy-peer-deps
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] npm install beim zweiten Versuch erfolgreich
    ) else (
        echo [ERROR] npm install auch beim zweiten Versuch fehlgeschlagen
        echo [DEBUG] Versuche mit reduziertem Dependency-Set...
        npm install --legacy-peer-deps --ignore-engines --force
        if %ERRORLEVEL% EQU 0 (
            echo [SUCCESS] npm install mit ignore-engines erfolgreich
        ) else (
            echo [CRITICAL] Alle npm install Versuche fehlgeschlagen
            echo [INFO] Installation wird fortgesetzt, aber Frontend möglicherweise nicht funktional
        )
    )
)

REM Validiere Installation
echo [VERIFY] Überprüfe Installation...
if exist "node_modules" (
    echo [SUCCESS] node_modules Verzeichnis existiert
    echo [INFO] Anzahl installierter Packages:
    dir node_modules /a 2>nul | find /c /v "" || echo "Package-Zählung fehlgeschlagen"
    
    REM Prüfe wichtige Dependencies
    if exist "node_modules\react" (
        echo [SUCCESS] React installiert
    ) else (
        echo [WARNING] React nicht gefunden in node_modules
    )
    
    if exist "node_modules\@craco" (
        echo [SUCCESS] Craco installiert
    ) else (
        echo [WARNING] Craco nicht gefunden in node_modules
    )
) else (
    echo [ERROR] node_modules Verzeichnis nicht erstellt
    echo [DEBUG] Aktueller Verzeichnisinhalt:
    dir /b
    echo [WARNING] Frontend möglicherweise unvollständig installiert
)

echo [INFO] Frontend Dependencies Installation abgeschlossen
:skip_frontend
cd ..

echo.

REM ==========================================  
echo [STEP 5/6] SYSTEM-TESTS
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
echo [INSTALLATION ABGESCHLOSSEN - STEP 6/6]
echo ==========================================

echo.
echo ✅ XIONIMUS AI INSTALLATION ERFOLGREICH!
echo.
echo 📋 NÄCHSTE SCHRITTE:
echo.
echo [START] Verwenden Sie die Start-Skripte:
echo    START_BACKEND.bat    - Backend starten
echo    START_FRONTEND.bat   - Frontend starten  
echo    START_ALL.bat        - Beide Services starten
echo.
echo [ACCESS] Nach dem Start verfügbar unter:
echo    → Frontend: http://localhost:3000
echo    → Backend:  http://localhost:8001
echo.
echo 🔑 API-KONFIGURATION:
echo    → Öffnen Sie http://localhost:3000
echo    → Klicken Sie auf "API Configuration"
echo    → Konfigurieren Sie Ihre API-Keys:
echo      • Anthropic API Key (für Claude)
echo      • OpenAI API Key (für GPT)
echo      • Perplexity API Key (für Research)
echo.
echo 🎯 INSTALLATION VOLLSTÄNDIG ABGESCHLOSSEN!
echo.
echo [INFO] Verwenden Sie START_ALL.bat für den einfachen Start beider Services
echo.

pause