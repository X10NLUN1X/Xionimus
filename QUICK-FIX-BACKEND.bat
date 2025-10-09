@echo off
echo.
echo ========================================================================
echo    QUICK FIX: Backend haengt - Redis/MongoDB deaktivieren
echo ========================================================================
echo.

cd /d "%~dp0"

echo Erstelle Windows-optimierte .env...
(
    echo # ===================================
    echo # Xionimus AI Backend Configuration
    echo # Windows-optimiert ^(ohne MongoDB/Redis^)
    echo # ===================================
    echo.
    echo # SECURITY KEYS ^(PERMANENT - DO NOT CHANGE!^)
    echo SECRET_KEY=4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307
    echo JWT_ALGORITHM=HS256
    echo JWT_EXPIRE_MINUTES=1440
    echo.
    echo # Encryption Key for API Keys
    echo ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=
    echo.
    echo # SERVER CONFIGURATION
    echo DEBUG=true
    echo HOST=0.0.0.0
    echo PORT=8001
    echo LOG_LEVEL=INFO
    echo.
    echo # DATABASE CONFIGURATION - SQLite wird verwendet
    echo # MONGO_URL nicht gesetzt = SQLite wird verwendet
    echo.
    echo # Redis Configuration - DEAKTIVIERT fuer Windows
    echo # REDIS_URL nicht gesetzt = Redis wird uebersprungen
    echo.
    echo # AI PROVIDER API KEYS ^(Add via Settings UI after login^)
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    echo GITHUB_TOKEN=
    echo.
    echo # GITHUB OAUTH CONFIGURATION
    echo GITHUB_OAUTH_CLIENT_ID=Ov23liCIa2aVTC3ttGFf
    echo GITHUB_OAUTH_CLIENT_SECRET=acc1edb2b095606ee55182a4eb5daf0cda9ce46d
    echo GITHUB_OAUTH_CALLBACK_URL=http://localhost:3000/github/callback
    echo GITHUB_USE_PAT=false
) > "backend\.env"

if exist "backend\.env" (
    echo ✅ Windows-optimierte .env erstellt!
    echo.
    echo Aenderungen:
    echo   - SQLite statt MongoDB ^(automatisch^)
    echo   - Redis deaktiviert
    echo   - Keine haengenden Verbindungen mehr
    echo.
    echo.
    echo Jetzt koennen Sie:
    echo   1. Das Backend-Fenster schliessen ^(falls noch offen^)
    echo   2. START.bat erneut ausfuehren
    echo.
) else (
    echo ❌ Fehler beim Erstellen der .env!
)

echo.
pause
