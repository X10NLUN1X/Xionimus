@echo off
echo.
echo ========================================================================
echo    WINDOWS FINAL FIX - Garantiert startfaehig
echo ========================================================================
echo.

cd /d "%~dp0"

echo [1/3] Loesche alte Konfigurationen...
if exist "backend\.env" del /Q "backend\.env"
if exist "backend\xionimus.db" del /Q "backend\xionimus.db"
echo ✅ Alte Dateien geloescht

echo.
echo [2/3] Erstelle optimale Windows .env...
(
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
echo ✅ Windows .env erstellt

echo.
echo [3/3] Verifiziere .env...
if exist "backend\.env" (
    echo ✅ backend\.env existiert
    for %%A in ("backend\.env") do echo    Groesse: %%~zA Bytes
) else (
    echo ❌ FEHLER: .env nicht erstellt!
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    ✅ WINDOWS FIX KOMPLETT!
echo ========================================================================
echo.
echo Naechste Schritte:
echo   1. START.bat ausfuehren
echo   2. Warten bis Browser oeffnet (kann 30 Sek dauern beim 1. Mal)
echo   3. Login: admin / admin123
echo.
pause
