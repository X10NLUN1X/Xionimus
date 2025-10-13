@echo off
REM ============================================================================
REM XIONIMUS - Repository Structure Fix - DIAGNOSE
REM ============================================================================
REM 
REM Dieses Skript prüft warum der Agent die Repository-Struktur nicht sieht
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo   XIONIMUS - Repository Structure Fix - DIAGNOSE
echo ================================================================================
echo.

REM Prüfe ob wir im richtigen Verzeichnis sind
if not exist "backend\app\api\chat_stream.py" (
    echo [FEHLER] chat_stream.py nicht gefunden!
    echo.
    echo Bitte dieses Skript in C:\AI\Xionimus\ ausführen
    echo.
    pause
    exit /b 1
)

echo [1/5] Prüfe ob Fix installiert ist...
echo.

REM Suche nach der neuen Funktion scan_repository_structure
findstr /C:"def scan_repository_structure" backend\app\api\chat_stream.py >nul 2>&1
if %errorlevel% equ 0 (
    echo       [OK] Fix ist installiert - scan_repository_structure() gefunden
    set FIX_INSTALLED=1
) else (
    echo       [FEHLER] Fix ist NICHT installiert!
    echo       Die Funktion scan_repository_structure() wurde nicht gefunden.
    echo.
    echo       LÖSUNG:
    echo       1. Führe INSTALL_REPO_STRUCTURE_FIX.bat aus
    echo       2. Oder kopiere chat_stream_REPOSITORY_STRUCTURE_FIX.py manuell
    echo.
    set FIX_INSTALLED=0
)

echo.
echo [2/5] Prüfe workspace Verzeichnis...
echo.

REM Prüfe ob workspace existiert
if exist "backend\workspace\" (
    echo       [OK] workspace\ Verzeichnis existiert
    
    REM Prüfe github_imports
    if exist "backend\workspace\github_imports\" (
        echo       [OK] workspace\github_imports\ Verzeichnis existiert
        
        REM Liste User-IDs
        echo.
        echo       Gefundene User-IDs:
        for /d %%D in (backend\workspace\github_imports\*) do (
            echo       - %%~nxD
            set FOUND_USER=1
            
            REM Liste Repositories für diese User-ID
            for /d %%R in (%%D\*) do (
                echo         └─> Repository: %%~nxR
                set FOUND_REPO=1
            )
        )
        
        if not defined FOUND_USER (
            echo       [WARNUNG] Keine User-Verzeichnisse gefunden!
            echo       Repository muss importiert werden.
        )
    ) else (
        echo       [FEHLER] workspace\github_imports\ existiert nicht!
        echo       Repository muss importiert werden.
    )
) else (
    echo       [FEHLER] workspace\ Verzeichnis existiert nicht!
    echo       Backend wurde möglicherweise noch nie gestartet.
)

echo.
echo [3/5] Prüfe Datenbank (Sessions)...
echo.

REM Prüfe ob SQLite DB existiert
if exist "backend\xionimus.db" (
    echo       [OK] Datenbank gefunden: backend\xionimus.db
    
    REM Versuche Sessions auszulesen (benötigt sqlite3)
    where sqlite3 >nul 2>&1
    if %errorlevel% equ 0 (
        echo.
        echo       Letzte 5 Sessions:
        sqlite3 backend\xionimus.db "SELECT id, name, active_project FROM sessions ORDER BY updated_at DESC LIMIT 5" 2>nul
    ) else (
        echo       [INFO] sqlite3 nicht installiert - kann Sessions nicht auslesen
    )
) else (
    echo       [FEHLER] Datenbank nicht gefunden!
    echo       Backend muss mindestens einmal gestartet worden sein.
)

echo.
echo [4/5] Prüfe Backend Logs...
echo.

REM Suche nach typischen Log-Zeilen
echo       Suche nach Repository-Scan Logs...

REM Hinweis: Logs sind nur verfügbar wenn Backend läuft
echo       [INFO] Prüfe Backend-Terminal für folgende Zeilen:
echo.
echo       ✅ Sollte vorhanden sein:
echo          - "User ID from session: ..."
echo          - "Active project from session: ..."
echo          - "Scanning repository structure: ..."
echo          - "Repository contains X files in Y directories"
echo          - "Repository structure scanned successfully!"
echo.
echo       ❌ Wenn diese Zeilen fehlen:
echo          - Session hat kein active_project gesetzt
echo          - Repository-Pfad existiert nicht
echo          - Fix ist nicht installiert

echo.
echo [5/5] Zusammenfassung...
echo.

REM Erstelle Zusammenfassung
echo ================================================================================
echo   DIAGNOSE ERGEBNIS
echo ================================================================================
echo.

if !FIX_INSTALLED! equ 1 (
    echo [OK] Fix ist installiert
) else (
    echo [FEHLER] Fix ist NICHT installiert
    echo         AKTION: Führe INSTALL_REPO_STRUCTURE_FIX.bat aus
)

if defined FOUND_REPO (
    echo [OK] Repository gefunden im workspace
) else (
    echo [FEHLER] Kein Repository im workspace gefunden
    echo         AKTION: Repository über GitHub Import importieren
)

echo.
echo ================================================================================
echo   NÄCHSTE SCHRITTE
echo ================================================================================
echo.

if !FIX_INSTALLED! equ 0 (
    echo 1. FIX INSTALLIEREN:
    echo    - Führe INSTALL_REPO_STRUCTURE_FIX.bat aus
    echo    - Oder kopiere Datei manuell und starte Backend neu
    echo.
)

if not defined FOUND_REPO (
    echo 2. REPOSITORY IMPORTIEREN:
    echo    - Öffne http://localhost:3000
    echo    - Klicke "GitHub Import"
    echo    - Gebe Repository URL ein
    echo    - Warte bis Import abgeschlossen
    echo.
)

echo 3. SESSION MIT PROJEKT VERKNÜPFEN:
echo    - Nach dem Import: Neue Chat-Session starten
echo    - Das importierte Projekt wird automatisch aktiviert
echo.

echo 4. BACKEND-LOGS PRÜFEN:
echo    - Schaue im Backend-Terminal nach den Scan-Logs
echo    - Wenn du "Scanning repository structure" siehst → ✅ ERFOLG!
echo.

echo 5. TESTEN:
echo    - Frage: "Welche Hauptverzeichnisse gibt es im Repository?"
echo    - Agent sollte die Struktur sehen können
echo.

echo ================================================================================
echo.

REM Öffne Anleitung im Browser falls verfügbar
if exist "INSTALLATION_ANLEITUNG.md" (
    echo Möchtest du die Installations-Anleitung öffnen? (J/N)
    set /p OPEN_GUIDE=
    if /i "!OPEN_GUIDE!"=="J" (
        start INSTALLATION_ANLEITUNG.md
    )
)

echo.
echo Drücke eine beliebige Taste um zu beenden...
pause >nul

endlocal
