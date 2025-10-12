@echo off
setlocal EnableDelayedExpansion
title Xionimus AI - Comprehensive Workspace Fix
color 0B

echo.
echo ========================================================================
echo    XIONIMUS AI - WORKSPACE FIX
echo    Behebt: AI-Agent erkennt GitHub-Repositories nicht
echo ========================================================================
echo.

cd /d "%~dp0"

echo Problem:
echo   Repository werden nach /app/ statt in workspace/github_imports/ geklont
echo   AI-Agent findet importierte Dateien nicht
echo.
echo Loesung:
echo   1. Korrigiere Import-Pfade zu settings.GITHUB_IMPORTS_DIR
echo   2. Erstelle User-basierte Ordnerstruktur
echo   3. Konfiguriere AI-Agent (.cursorrules, .aider.conf.yml, etc.)
echo   4. Windows-Kompatibilitaet + Berechtigungen
echo.
pause

echo.
echo ========================================================================
echo    SCHRITT 1: PYTHON-FIX AUSFUEHREN
echo ========================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Python nicht gefunden!
    echo    Bitte installiere Python oder aktiviere das venv
    pause
    exit /b 1
)

REM Check if in venv
python -c "import sys; exit(0 if hasattr(sys, 'prefix') and sys.prefix != sys.base_prefix else 1)" >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️  Virtuelles Environment nicht aktiviert
    echo    Versuche venv zu aktivieren...
    
    if exist "backend\venv\Scripts\activate.bat" (
        call backend\venv\Scripts\activate.bat
        echo ✅ venv aktiviert
    ) else (
        echo ⚠️  venv nicht gefunden - verwende System-Python
    )
)

echo Fuehre Workspace-Fix aus...
echo.

python WORKSPACE_FIX_COMPREHENSIVE.py

if !errorlevel! neq 0 (
    echo.
    echo ❌ Fix fehlgeschlagen!
    echo    Siehe Fehlermeldungen oben
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo    SCHRITT 2: GIT KONFIGURATION
echo ========================================================================
echo.

REM Configure Git for Windows compatibility
git config --global core.longpaths true
if !errorlevel! equ 0 (
    echo ✅ Git longpaths aktiviert
) else (
    echo ⚠️  Git-Konfiguration fehlgeschlagen
)

git config --global core.autocrlf true
echo ✅ Git autocrlf aktiviert

git config --global core.fileMode false
echo ✅ Git fileMode deaktiviert (Windows-kompatibel)

echo.
echo ========================================================================
echo    SCHRITT 3: WORKSPACE-BERECHTIGUNGEN
echo ========================================================================
echo.

if exist "backend\workspace" (
    icacls "backend\workspace" /grant Everyone:(OI)(CI)F /T /Q >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ Workspace-Berechtigungen gesetzt
    ) else (
        echo ⚠️  Berechtigungen konnten nicht gesetzt werden
        echo    Wenn Import-Probleme auftreten, Script als Administrator ausfuehren
    )
) else (
    echo ⚠️  Workspace-Ordner nicht gefunden
)

echo.
echo ========================================================================
echo    ✅ FIX ABGESCHLOSSEN!
echo ========================================================================
echo.

echo Workspace-Struktur:
echo   backend\workspace\
echo   ├── github_imports\     ← GitHub Repos landen hier
echo   │   └── [user_id]\      ← Pro User ein Ordner
echo   │       └── [repo_name]\ ← Repository-Dateien
echo   ├── uploads\
echo   ├── exports\
echo   └── temp\
echo.

echo AI-Agent Konfiguration:
echo   ✅ .cursorrules erstellt (Cursor IDE)
echo   ✅ .cursor\rules\index.mdc erstellt (Cursor neu)
echo   ✅ .aider.conf.yml erstellt (Aider)
echo   ✅ .vscode\settings.json erstellt (VS Code)
echo.

echo Naechste Schritte:
echo   1. Backend neu starten:
echo      START.bat oder START-DEBUG.bat
echo.
echo   2. GitHub Repository importieren:
echo      → In UI: GitHub Import
echo      → Landet in: backend\workspace\github_imports\[user_id]\[repo_name]\
echo.
echo   3. AI-Agent oeffnen:
echo      → Cursor: Oeffne Projekt-Root (Xionimus-Ordner)
echo      → VS Code mit Copilot: code .
echo      → Agent erkennt automatisch alle Repos
echo.
echo   4. Optional - Alte Repos migrieren:
echo      python migrate_repos.py
echo.

echo ========================================================================
echo    Der AI-Agent hat jetzt vollen Zugriff auf importierte Repositories!
echo ========================================================================
echo.

echo Probleme?
echo   - Fuehre WORKSPACE-DIAGNOSE.bat aus
echo   - Checke Backend-Logs
echo   - Stelle sicher, dass Git installiert ist
echo.

pause
