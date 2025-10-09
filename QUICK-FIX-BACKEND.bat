@echo off
echo.
echo ========================================================================
echo    QUICK FIX: Backend haengt - Redis/MongoDB deaktivieren
echo ========================================================================
echo.

cd /d "%~dp0"

echo Kopiere Windows-optimierte .env...
if exist "backend\.env.windows" (
    copy /Y "backend\.env.windows" "backend\.env" >nul 2>&1
) else (
    echo ❌ backend\.env.windows nicht gefunden!
    echo Erstelle manuell...
    (
        echo # Windows-optimiert ^(ohne MongoDB/Redis^)
        echo SECRET_KEY=4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307
        echo JWT_ALGORITHM=HS256
        echo JWT_EXPIRE_MINUTES=1440
        echo ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=
        echo DEBUG=true
        echo HOST=0.0.0.0
        echo PORT=8001
        echo LOG_LEVEL=INFO
        echo ANTHROPIC_API_KEY=
        echo OPENAI_API_KEY=
        echo PERPLEXITY_API_KEY=
        echo GITHUB_TOKEN=
        echo GITHUB_OAUTH_CLIENT_ID=Ov23liCIa2aVTC3ttGFf
        echo GITHUB_OAUTH_CLIENT_SECRET=acc1edb2b095606ee55182a4eb5daf0cda9ce46d
        echo GITHUB_OAUTH_CALLBACK_URL=http://localhost:3000/github/callback
        echo GITHUB_USE_PAT=false
    ) > "backend\.env"
)

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
