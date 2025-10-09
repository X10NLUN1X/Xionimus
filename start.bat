@echo off
title Xionimus AI
color 0A

echo.
echo ========================================================================
echo    Xionimus AI wird gestartet...
echo ========================================================================
echo.

REM Wechsle ins Hauptverzeichnis
cd /d "%~dp0"

REM ========================================================================
REM SCHRITT 0: .env Setup pruefen und erstellen falls noetig
REM ========================================================================
echo [0/3] Pruefe .env Konfiguration...

if not exist "backend\.env" (
    echo.
    echo *** .env Datei nicht gefunden! ***
    echo Erstelle .env mit permanenten Keys...
    echo.
    
    REM Erstelle .env Datei mit PowerShell
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$envContent = @'^
# Xionimus AI Backend Configuration`n^
SECRET_KEY=4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307`n^
JWT_ALGORITHM=HS256`n^
JWT_EXPIRE_MINUTES=1440`n^
ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=`n^
DEBUG=true`n^
HOST=0.0.0.0`n^
PORT=8001`n^
LOG_LEVEL=INFO`n^
MONGO_URL=mongodb://localhost:27017/xionimus_ai`n^
REDIS_URL=redis://localhost:6379/0`n^
OPENAI_API_KEY=`n^
ANTHROPIC_API_KEY=`n^
PERPLEXITY_API_KEY=`n^
GITHUB_TOKEN=`n^
GITHUB_OAUTH_CLIENT_ID=Ov23liCIa2aVTC3ttGFf`n^
GITHUB_OAUTH_CLIENT_SECRET=acc1edb2b095606ee55182a4eb5daf0cda9ce46d`n^
GITHUB_OAUTH_CALLBACK_URL=http://localhost:3000/github/callback`n^
GITHUB_USE_PAT=false`n^
'@; $envContent | Out-File -FilePath 'backend\.env' -Encoding UTF8 -NoNewline; Write-Host '✅ .env erfolgreich erstellt!' -ForegroundColor Green"
    
    echo.
    echo ✅ .env Datei wurde erstellt mit permanenten Keys!
    echo ℹ️  Sie koennen API Keys spaeter in backend\.env hinzufuegen
    echo.
    timeout /t 3 /nobreak >nul
) else (
    echo ✅ .env Datei gefunden - wird verwendet
)

echo.

REM Starte Backend
echo [1/3] Starte Backend...
start "Xionimus AI - Backend" cmd /k "cd backend && venv\Scripts\activate.bat && python main.py"

REM Warte 5 Sekunden
timeout /t 5 /nobreak >nul

REM Starte Frontend
echo [2/3] Starte Frontend...
start "Xionimus AI - Frontend" cmd /k "cd frontend && yarn dev"

echo.
echo ========================================================================
echo    Xionimus AI wird gestartet!
echo ========================================================================
echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo API Docs: http://localhost:8001/docs
echo.
echo ========================================================================
echo.
echo Zwei neue Fenster sollten sich geoeffnet haben.
echo Warten auf Services...
echo.

REM [3/3] Warte auf Services und öffne Browser
echo [3/3] Browser wird automatisch geoeffnet...
timeout /t 10 /nobreak >nul

REM Öffne Browser automatisch
start http://localhost:3000

echo.
echo ========================================================================
echo    Browser geoeffnet! Xionimus AI ist bereit!
echo ========================================================================
echo.
echo Falls der Browser sich nicht geoeffnet hat, oeffne manuell:
echo     http://localhost:3000
echo.
echo ========================================================================
echo    WICHTIG: API Keys konfigurieren
echo ========================================================================
echo.
if not exist "backend\.env" (
    echo ⚠️  .env Datei wurde automatisch erstellt!
) else (
    echo ✅ .env Datei gefunden
)
echo.
echo Um AI Features zu nutzen, fuegen Sie Ihre API Keys hinzu:
echo   1. Oeffne: backend\.env
echo   2. Fuege Keys ein:
echo      OPENAI_API_KEY=sk-proj-ihr-key
echo      ANTHROPIC_API_KEY=sk-ant-ihr-key
echo   3. Backend neu starten
echo.
echo ========================================================================
echo.
echo Druecke eine beliebige Taste zum Beenden...
pause >nul
