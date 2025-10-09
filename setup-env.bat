@echo off
title Xionimus AI - Environment Setup
color 0B

echo.
echo ========================================================================
echo    Xionimus AI - .env Konfigurationsdatei Setup
echo ========================================================================
echo.

cd /d "%~dp0"

REM Pruefe ob .env bereits existiert
if exist "backend\.env" (
    echo.
    echo ⚠️  WARNING: .env Datei existiert bereits!
    echo.
    echo Aktueller Speicherort: backend\.env
    echo.
    choice /C YN /M "Moechten Sie die bestehende .env ueberschreiben"
    if errorlevel 2 goto :cancelled
    if errorlevel 1 goto :create
) else (
    goto :create
)

:create
echo.
echo ========================================================================
echo    Erstelle .env Datei mit permanenten Security Keys...
echo ========================================================================
echo.

REM Erstelle .env mit PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$envContent = @'^
# ===================================`n^
# Xionimus AI Backend Configuration`n^
# ===================================`n^
# `n^
# WICHTIG: Diese Datei enthaelt SECRET_KEY und ENCRYPTION_KEY`n^
# Diese Keys sind PERMANENT und sollten NICHT geaendert werden`n^
# Halten Sie diese Datei sicher und committen Sie sie nie zu Git`n^
#`n^
`n^
# ===================================`n^
# SECURITY KEYS (PERMANENT - NICHT AENDERN!)`n^
# ===================================`n^
`n^
# JWT Secret Key - Signiert Authentication Tokens`n^
# KRITISCH: Aenderung macht alle User-Sessions ungueltig`n^
SECRET_KEY=4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307`n^
`n^
# JWT Configuration`n^
JWT_ALGORITHM=HS256`n^
JWT_EXPIRE_MINUTES=1440`n^
`n^
# Encryption Key - Verschluesselt API Keys in Datenbank`n^
# KRITISCH: Aenderung macht gespeicherte API Keys unleserlich`n^
ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=`n^
`n^
# ===================================`n^
# SERVER CONFIGURATION`n^
# ===================================`n^
`n^
DEBUG=true`n^
HOST=0.0.0.0`n^
PORT=8001`n^
LOG_LEVEL=INFO`n^
`n^
# ===================================`n^
# DATABASE CONFIGURATION`n^
# ===================================`n^
`n^
# MongoDB Connection URL`n^
MONGO_URL=mongodb://localhost:27017/xionimus_ai`n^
`n^
# Redis (optional - fuer Caching)`n^
REDIS_URL=redis://localhost:6379/0`n^
`n^
# ===================================`n^
# AI PROVIDER API KEYS (OPTIONAL)`n^
# ===================================`n^
# Fuegen Sie hier Ihre API Keys hinzu um AI Features zu aktivieren`n^
# Keys erhalten Sie von:`n^
#   - OpenAI: https://platform.openai.com/api-keys`n^
#   - Anthropic: https://console.anthropic.com/`n^
#   - Perplexity: https://www.perplexity.ai/settings/api`n^
`n^
OPENAI_API_KEY=`n^
ANTHROPIC_API_KEY=`n^
PERPLEXITY_API_KEY=`n^
GITHUB_TOKEN=`n^
`n^
# ===================================`n^
# GITHUB OAUTH (OPTIONAL)`n^
# ===================================`n^
`n^
GITHUB_OAUTH_CLIENT_ID=Ov23liCIa2aVTC3ttGFf`n^
GITHUB_OAUTH_CLIENT_SECRET=acc1edb2b095606ee55182a4eb5daf0cda9ce46d`n^
GITHUB_OAUTH_CALLBACK_URL=http://localhost:3000/github/callback`n^
GITHUB_USE_PAT=false`n^
'@; $envContent | Out-File -FilePath 'backend\.env' -Encoding UTF8 -NoNewline; if (Test-Path 'backend\.env') { Write-Host ''; Write-Host '✅ SUCCESS: .env Datei erfolgreich erstellt!' -ForegroundColor Green; Write-Host ''; Write-Host '📁 Speicherort: backend\.env' -ForegroundColor Cyan; $size = (Get-Item 'backend\.env').Length; Write-Host \"📊 Groesse: $size Bytes\" -ForegroundColor Cyan; Write-Host ''; Write-Host '🔑 Security Keys:' -ForegroundColor White; Write-Host '   ✅ SECRET_KEY: Gesetzt (64 Zeichen)' -ForegroundColor Green; Write-Host '   ✅ ENCRYPTION_KEY: Gesetzt (44 Zeichen)' -ForegroundColor Green; Write-Host ''; } else { Write-Host '❌ ERROR: Datei konnte nicht erstellt werden!' -ForegroundColor Red; }"

if exist "backend\.env" (
    echo.
    echo ========================================================================
    echo    NAECHSTE SCHRITTE
    echo ========================================================================
    echo.
    echo 1. [Optional] API Keys hinzufuegen:
    echo    - Oeffne: backend\.env
    echo    - Suche: OPENAI_API_KEY=
    echo    - Fuege ein: OPENAI_API_KEY=sk-proj-ihr-key
    echo    - Speichern
    echo.
    echo 2. Backend starten:
    echo    - Fuehre aus: start.bat
    echo    - ODER manuell: cd backend ^&^& python main.py
    echo.
    echo 3. Sie sollten NICHT mehr sehen:
    echo    ❌ AUTO-FIX: .env file not found
    echo.
    echo 4. Backend sollte starten mit:
    echo    ✅ Using existing .env configuration
    echo.
    echo ========================================================================
    echo.
    echo ✅ Setup abgeschlossen! Ihre .env ist bereit.
    echo.
) else (
    echo.
    echo ❌ FEHLER: .env Datei konnte nicht erstellt werden!
    echo.
    echo Bitte pruefen Sie:
    echo   - Schreibrechte im Verzeichnis
    echo   - backend\ Ordner existiert
    echo   - Keine Datei-Sperren auf .env
    echo.
)

goto :end

:cancelled
echo.
echo ❌ Abgebrochen. Bestehende .env Datei wurde NICHT veraendert.
echo.

:end
echo Druecke eine beliebige Taste zum Beenden...
pause >nul
