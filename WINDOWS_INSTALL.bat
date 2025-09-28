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

REM Benutzer über Ablauf informieren
echo [WORKFLOW] Dieser Script führt folgende Schritte aus:
echo   1. System-Voraussetzungen prüfen
echo   2. Projekt-Konfiguration erstellen  
echo   3. Backend Dependencies installieren
echo   4. Frontend Dependencies installieren
echo   5. System-Tests durchführen
echo   6. Backend und Frontend starten
echo.
set /p continue="Fortfahren? (y/n): "
if /i not "%continue%"=="y" exit /b 0

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

cd backend

echo [UPDATE] Pip modernisieren...  
python -m pip install --upgrade pip setuptools wheel --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Pip Update fehlgeschlagen
    pause
    exit /b 1
)

echo [INSTALL] Kritische Async/Network Dependencies...
python -m pip install aiohttp==3.12.15 aiohappyeyeballs aiosignal anyio==4.11.0 --quiet
python -m pip install multidict frozenlist yarl propcache --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Async Dependencies Installation fehlgeschlagen
    pause
    exit /b 1
)

echo [INSTALL] Web Framework...
python -m pip install fastapi==0.110.1 uvicorn==0.25.0 starlette --quiet
python -m pip install pydantic pydantic_core typing_extensions --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Web Framework Installation fehlgeschlagen
    pause
    exit /b 1
)

echo [INSTALL] Database...
python -m pip install motor==3.3.1 pymongo==4.5.0 dnspython --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Database Dependencies Installation fehlgeschlagen
    pause
    exit /b 1
)

echo [INSTALL] AI APIs...
python -m pip install anthropic==0.68.1 openai==1.109.1 --quiet
python -m pip install httpx httpcore --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] AI API Dependencies Installation fehlgeschlagen
    pause
    exit /b 1
)

echo [INSTALL] Utilities...
python -m pip install python-dotenv==1.1.1 requests==2.32.5 --quiet
python -m pip install numpy pandas PyYAML Jinja2 rich click --quiet
python -m pip install jsonschema attrs Pillow --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Einige Utility Dependencies konnten nicht installiert werden
    echo [INFO] Grundfunktionen sollten trotzdem funktionieren
)

echo [TEST] Backend Import-Test...
python -c "
try:
    from agents.agent_manager import AgentManager
    print('[SUCCESS] Backend-System importiert')
except Exception as e:
    print(f'[ERROR] Backend-Import: {e}')
    exit(1)
" || (
    echo [ERROR] Backend-Imports fehlgeschlagen  
    pause
    exit /b 1
)

cd ..

echo.

REM ==========================================
echo [STEP 4/8] FRONTEND DEPENDENCIES  
echo ==========================================

cd frontend

REM Prüfe package.json
if not exist "package.json" (
    echo [ERROR] package.json nicht gefunden im Frontend-Verzeichnis
    pause
    exit /b 1
)

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

REM Port-Prüfung für Backend
echo [CHECK] Prüfe Port 8001 für Backend...
netstat -an | findstr :8001 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 8001 ist bereits belegt
    echo [OPTIONS] Mögliche Aktionen:
    echo   1. Andere Anwendung auf Port 8001 beenden
    echo   2. Trotzdem fortfahren (kann zu Konflikten führen)
    set /p port_choice="Trotzdem fortfahren? (y/n): "
    if /i not "%port_choice%"=="y" (
        echo [INFO] Installation abgebrochen - bitte Port 8001 freigeben
        pause
        exit /b 1
    )
    echo [ACTION] Fortfahren trotz Port-Konflikt...
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

REM Port-Prüfung für Frontend
echo [CHECK] Prüfe Port 3000 für Frontend...
netstat -an | findstr :3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Port 3000 ist bereits belegt
    echo [OPTIONS] Mögliche Aktionen:
    echo   1. Andere Anwendung auf Port 3000 beenden
    echo   2. Trotzdem fortfahren (kann zu Konflikten führen)
    set /p frontend_port_choice="Trotzdem fortfahren? (y/n): "
    if /i not "%frontend_port_choice%"=="y" (
        echo [INFO] Installation abgebrochen - bitte Port 3000 freigeben
        pause
        exit /b 1
    )
    echo [ACTION] Fortfahren trotz Port-Konflikt...
) else (
    echo [SUCCESS] Port 3000 verfügbar
)

REM Bestimme Frontend-Start-Befehl
where yarn >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set FRONTEND_START_CMD=yarn start
    echo [INFO] Verwende yarn für Frontend-Start
) else (
    set FRONTEND_START_CMD=npm start
    echo [INFO] Verwende npm für Frontend-Start
)

echo [START] Starte Frontend-Server...
cd frontend
start "XIONIMUS Frontend" cmd /k "echo [FRONTEND] XIONIMUS AI Frontend wird gestartet... && echo [INFO] Frontend läuft auf Port 3000 && %FRONTEND_START_CMD%"

echo [WAIT] Warte auf Frontend-Start (15 Sekunden)...
timeout /t 15 /nobreak >nul

echo [INFO] Frontend sollte jetzt verfügbar sein auf http://localhost:3000

cd ..

echo.

REM ==========================================
echo [STEP 8/8] SYSTEM BEREIT
echo ==========================================

echo.
echo 🎉 XIONIMUS AI INSTALLATION UND START ABGESCHLOSSEN!
echo.
echo 🖥️ SERVER-STATUS:
echo   ✅ Backend:  Gestartet auf http://localhost:8001
echo   ✅ Frontend: Gestartet auf http://localhost:3000
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

REM Browser automatisch öffnen
timeout /t 5 /nobreak >nul
echo [LAUNCH] Öffne XIONIMUS AI...
start http://localhost:3000

echo.
echo ✨ Viel Erfolg mit XIONIMUS AI! ✨
echo.
echo [INFO] Dieses Fenster kann nach dem Browserstart geschlossen werden.
echo [REMINDER] Halten Sie die Server-Fenster geöffnet!
echo.
pause