@echo off
title XIONIMUS AI - Python 3.13 Complete Installation
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - PYTHON 3.13 COMPLETE
echo ==========================================
echo.
echo [INFO] Vollständige Installation für Python 3.13.2032.0
echo [INFO] Installiert alle Features und Optimierungen
echo.

REM Verzeichnis prüfen
if not exist "backend" (
    echo [ERROR] backend\ Verzeichnis nicht gefunden!
    echo [INFO] Bitte im XIONIMUS Hauptverzeichnis ausführen
    pause
    exit /b 1
)

echo [STEP 1/5] PYTHON 3.13 REQUIREMENTS ERSTELLEN
echo [CREATE] Erstelle requirements_python313.txt...

REM Python 3.13 Requirements erstellen
(
echo # XIONIMUS AI - Python 3.13 Complete Requirements
echo.
echo # Web Framework
echo fastapi==0.115.6
echo uvicorn[standard]==0.32.1
echo starlette==0.41.3
echo.
echo # Data Models
echo pydantic==2.10.3
echo pydantic_core==2.27.1
echo typing_extensions==4.12.2
echo.
echo # Database
echo motor==3.6.0
echo pymongo==4.10.1
echo dnspython==2.8.0
echo.
echo # AI APIs
echo anthropic==0.40.0
echo openai==1.57.4
echo httpx==0.28.1
echo httpcore==1.0.7
echo.
echo # Data Processing ^(Python 3.13 latest^)
echo numpy==2.2.1
echo pandas==2.2.3
echo.
echo # Async and Network ^(CRITICAL^)
echo aiohttp==3.11.10
echo aiohappyeyeballs==2.4.4
echo aiosignal==1.4.0
echo anyio==4.7.0
echo multidict==6.1.0
echo frozenlist==1.5.0
echo yarl==1.18.3
echo propcache==0.3.0
echo.
echo # Authentication
echo passlib[bcrypt]==1.7.4
echo python-jose[cryptography]==3.3.0
echo cryptography==44.0.0
echo PyJWT==2.10.1
echo python-multipart==0.0.20
echo.
echo # Utilities
echo python-dotenv==1.1.1
echo click==8.2.1
echo tqdm==4.67.1
echo requests==2.32.3
echo urllib3==2.3.0
echo certifi==2024.12.14
echo charset-normalizer==3.4.1
echo idna==3.10
echo.
echo # File Processing
echo pillow==11.0.0
echo PyYAML==6.0.2
echo.
echo # JSON and Data Validation
echo jsonschema==4.23.0
echo attrs==24.3.0
echo annotated-types==0.7.0
echo.
echo # Development
echo rich==13.9.4
echo Jinja2==3.1.4
echo MarkupSafe==3.0.2
) > backend\requirements_python313.txt

echo [SUCCESS] requirements_python313.txt erstellt
echo.

echo [STEP 2/5] PIP AKTUALISIEREN
echo [UPDATE] Aktualisiere pip für Python 3.13...
python -m pip install --upgrade pip setuptools wheel

echo.
echo [STEP 3/5] DEPENDENCIES INSTALLIEREN
echo [INSTALL] Installiere Python 3.13 optimierte Dependencies...
cd backend

REM Kritische Dependencies zuerst
echo [INSTALL] Kritische Dependencies...
python -m pip install aiohttp fastapi uvicorn motor pymongo

REM AI APIs
echo [INSTALL] AI API Clients...
python -m pip install anthropic openai httpx

REM Vollständige Requirements
echo [INSTALL] Alle Requirements...
python -m pip install -r requirements_python313.txt

if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Einige Packages konnten nicht installiert werden
    echo [INFO] Versuche Fallback-Installation...
    
    REM Fallback mit wichtigsten Packages
    python -m pip install aiohttp aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache
    python -m pip install fastapi uvicorn starlette pydantic typing_extensions
    python -m pip install motor pymongo dnspython
    python -m pip install anthropic openai httpx httpcore
    python -m pip install numpy pandas python-dotenv click requests
    
    echo [INFO] Fallback-Installation abgeschlossen
) else (
    echo [SUCCESS] Alle Dependencies erfolgreich installiert
)

cd ..
echo.

echo [STEP 4/5] .ENV DATEIEN ERSTELLEN
echo [CREATE] Erstelle/Prüfe .env Dateien...

REM Backend .env
if not exist "backend\.env" (
    (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    ) > backend\.env
    echo [SUCCESS] backend\.env erstellt
) else (
    echo [INFO] backend\.env bereits vorhanden
)

REM Frontend .env  
if not exist "frontend\.env" (
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
    echo [SUCCESS] frontend\.env erstellt
) else (
    echo [INFO] frontend\.env bereits vorhanden
)

echo.
echo [STEP 5/5] SYSTEM TEST
echo [TEST] Teste kritische Imports...

python -c "import aiohttp; print('[✅] aiohttp - OK')" 2>nul || echo [❌] aiohttp - FEHLT
python -c "import fastapi; print('[✅] fastapi - OK')" 2>nul || echo [❌] fastapi - FEHLT
python -c "import motor; print('[✅] motor - OK')" 2>nul || echo [❌] motor - FEHLT
python -c "import anthropic; print('[✅] anthropic - OK')" 2>nul || echo [❌] anthropic - FEHLT
python -c "import numpy; print('[✅] numpy - OK')" 2>nul || echo [❌] numpy - FEHLT

echo.
echo ==========================================
echo    PYTHON 3.13 INSTALLATION COMPLETE
echo ==========================================
echo.
echo [SUCCESS] XIONIMUS AI bereit für Python 3.13!
echo.
echo [INFO] System starten:
echo   1. Backend: cd backend ^&^& python server.py
echo   2. Frontend: cd frontend ^&^& yarn start  
echo   3. Browser: http://localhost:3000
echo.
echo [INFO] Optimierungen für Python 3.13:
echo   ✅ numpy 2.2.1 ^(neueste Version^)
echo   ✅ pandas 2.2.3 ^(beste Performance^)
echo   ✅ aiohttp 3.11.10 ^(async optimiert^)
echo   ✅ fastapi 0.115.6 ^(neueste Features^)
echo.
echo [CONFIG] API Keys konfigurieren in Web-Oberfläche:
echo   http://localhost:3000 → API Configuration
echo.
pause