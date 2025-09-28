@echo off
title XIONIMUS AI - Auto-Find and Install
color 0D
echo.
echo ==========================================
echo    XIONIMUS AI - AUTO FIND AND INSTALL
echo ==========================================
echo.
echo [INFO] Sucht automatisch das XIONIMUS Verzeichnis und installiert
echo.

REM Häufige Pfade durchsuchen
echo [SEARCH] Suche XIONIMUS Verzeichnis...

set FOUND_PATH=

REM Pfad 1: C:\AI\XionimusX-main
if exist "C:\AI\XionimusX-main\backend\server.py" (
    set FOUND_PATH=C:\AI\XionimusX-main
    echo [FOUND] ✅ C:\AI\XionimusX-main
    goto :install
)

REM Pfad 2: Desktop
if exist "C:\Users\%USERNAME%\Desktop\XionimusX-main\backend\server.py" (
    set FOUND_PATH=C:\Users\%USERNAME%\Desktop\XionimusX-main
    echo [FOUND] ✅ Desktop\XionimusX-main
    goto :install
)

REM Pfad 3: Downloads
if exist "C:\Users\%USERNAME%\Downloads\XionimusX-main\backend\server.py" (
    set FOUND_PATH=C:\Users\%USERNAME%\Downloads\XionimusX-main
    echo [FOUND] ✅ Downloads\XionimusX-main
    goto :install
)

REM Pfad 4: Dokumente
if exist "C:\Users\%USERNAME%\Documents\XionimusX-main\backend\server.py" (
    set FOUND_PATH=C:\Users\%USERNAME%\Documents\XionimusX-main
    echo [FOUND] ✅ Documents\XionimusX-main
    goto :install
)

REM Pfad 5: Laufwerk C:\ Root
if exist "C:\XionimusX-main\backend\server.py" (
    set FOUND_PATH=C:\XionimusX-main
    echo [FOUND] ✅ C:\XionimusX-main
    goto :install
)

REM Nicht gefunden
echo [ERROR] ❌ XIONIMUS Verzeichnis nicht gefunden!
echo.
echo [INFO] Durchsuchte Pfade:
echo   - C:\AI\XionimusX-main
echo   - %USERPROFILE%\Desktop\XionimusX-main
echo   - %USERPROFILE%\Downloads\XionimusX-main
echo   - %USERPROFILE%\Documents\XionimusX-main
echo   - C:\XionimusX-main
echo.
echo [FIX] Bitte manuell:
echo   1. Finden Sie Ihr XionimusX-main Verzeichnis
echo   2. Öffnen Sie es im Explorer
echo   3. Doppelklicken Sie auf WINDOWS_INSTALL.bat
echo.
pause
exit /b 1

:install
echo [SUCCESS] XIONIMUS gefunden in: %FOUND_PATH%
echo [INFO] Wechsle ins Verzeichnis und starte Installation...
echo.

cd /d "%FOUND_PATH%"

REM Prüfe ob WINDOWS_INSTALL.bat existiert
if exist "WINDOWS_INSTALL.bat" (
    echo [EXECUTE] Starte WINDOWS_INSTALL.bat...
    call WINDOWS_INSTALL.bat
) else (
    echo [ERROR] WINDOWS_INSTALL.bat nicht gefunden in %FOUND_PATH%
    echo [FIX] Erstelle minimale Installation...
    
    REM Minimale Installation direkt hier
    echo [INSTALL] Minimale Dependencies...
    
    REM .env Dateien erstellen
    (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    ) > backend\.env
    
    echo REACT_APP_BACKEND_URL=http://localhost:8001 > frontend\.env
    
    REM Backend Dependencies
    cd backend
    pip install aiohttp==3.12.15 fastapi==0.110.1 uvicorn==0.25.0 --quiet
    pip install motor==3.3.1 pymongo==4.5.0 anthropic==0.68.1 openai==1.109.1 --quiet
    pip install python-dotenv==1.1.1 requests==2.32.5 --quiet
    cd ..
    
    REM Frontend Dependencies  
    cd frontend
    npm install --silent
    cd ..
    
    echo [SUCCESS] Minimale Installation abgeschlossen!
    echo [START] Backend: START_BACKEND.bat
    echo [START] Frontend: START_FRONTEND.bat
)

pause