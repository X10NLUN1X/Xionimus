@echo off
setlocal EnableDelayedExpansion
title Xionimus AI - Chat Fix (API Keys)
color 0B

echo.
echo ========================================================================
echo    XIONIMUS AI - CHAT FIX (API Keys automatisch laden)
echo ========================================================================
echo.
echo Problem: Chat funktioniert nicht - "Provider not configured"
echo Lösung: Backend laedt API Keys automatisch aus der Datenbank
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Python nicht gefunden!
    echo    Bitte Python installieren
    pause
    exit /b 1
)

echo ========================================================================
echo    SCHRITT 1: Fix installieren
echo ========================================================================
echo.

python FIX_API_KEYS_PERMANENT.py

if !errorlevel! neq 0 (
    echo.
    echo ❌ Fix fehlgeschlagen!
    echo    Siehe Fehlermeldungen oben
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    SCHRITT 2: API Keys pruefen
echo ========================================================================
echo.

python CHECK_API_KEYS.py

echo.
echo ========================================================================
echo    SCHRITT 3: Anweisungen
echo ========================================================================
echo.

REM Check if keys were found
python CHECK_API_KEYS.py 2>&1 | findstr "gefunden" >nul
if !errorlevel! equ 0 (
    echo ✅ API Keys gefunden in der Datenbank!
    echo.
    echo Naechster Schritt:
    echo   1. Backend NEU STARTEN (schliesse aktuelles Backend)
    echo   2. START.bat ausfuehren
    echo   3. Chat sollte jetzt funktionieren!
    echo.
) else (
    echo ⚠️  Keine API Keys in der Datenbank gefunden!
    echo.
    echo Bitte zuerst API Keys hinzufuegen:
    echo.
    echo   1. Backend starten: START.bat
    echo   2. Browser: http://localhost:3000
    echo   3. Settings (⚙️) oeffnen
    echo   4. API Keys eingeben:
    echo      • OpenAI: sk-proj-... oder sk-...
    echo      • Anthropic: sk-ant-api03-...
    echo      • Perplexity: pplx-...
    echo   5. "Save API Keys" klicken
    echo   6. Backend neu starten
    echo   7. Dieses Script nochmal ausfuehren
    echo.
)

echo ========================================================================
echo    ✅ FIX ABGESCHLOSSEN
echo ========================================================================
echo.
echo Was wurde gefixt:
echo   ✅ Backend laedt API Keys automatisch aus der Datenbank
echo   ✅ Chat funktioniert auch wenn Frontend keine Keys sendet
echo   ✅ Besseres Logging fuer Debugging
echo.
echo Tools installiert:
echo   • CHECK_API_KEYS.py - Zeigt gespeicherte Keys
echo   • SETUP_API_KEYS.bat - Setup-Assistent
echo.

pause
