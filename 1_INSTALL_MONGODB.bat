@echo off
echo =====================================
echo   XIONIMUS AI - MONGODB INSTALLATION
echo =====================================
echo.

REM Prüfen ob MongoDB bereits installiert ist
where mongod >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] MongoDB ist bereits installiert!
    echo [INFO] Version:
    mongod --version | findstr "db version"
    echo.
    goto :setup_data_dir
)

echo [INFO] MongoDB ist nicht installiert. Installiere MongoDB...
echo.

REM MongoDB Download URL (Community Edition 7.0)
set MONGODB_URL=https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.4-signed.msi

echo [INFO] Downloade MongoDB Community Edition...
echo [URL] %MONGODB_URL%
echo.

REM Temporärer Download-Pfad
set TEMP_INSTALLER=%TEMP%\mongodb-installer.msi

REM Download mit PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%MONGODB_URL%' -OutFile '%TEMP_INSTALLER%'}"

if not exist "%TEMP_INSTALLER%" (
    echo [ERROR] Download fehlgeschlagen!
    echo [INFO] Bitte MongoDB manuell installieren von: https://mongodb.com/try/download/community
    pause
    exit /b 1
)

echo [INFO] Starte MongoDB Installation...
echo [INFO] Folgen Sie dem Installationsassistenten
echo [INFO] Wichtig: Wahlen Sie "Complete Installation"
echo.
pause

REM Silent Installation (falls gewünscht, auskommentieren für GUI)
REM msiexec /i "%TEMP_INSTALLER%" /quiet /norestart INSTALLLOCATION="C:\Program Files\MongoDB\Server\7.0\" ADDLOCAL="ServerService,Client,MonitoringTools"

REM GUI Installation
msiexec /i "%TEMP_INSTALLER%"

REM Cleanup
del "%TEMP_INSTALLER%" >nul 2>nul

:setup_data_dir
echo.
echo [INFO] Erstelle MongoDB Datenverzeichnis...

REM Erstelle MongoDB Datenverzeichnis
if not exist "C:\data\db" (
    mkdir "C:\data\db"
    echo [SUCCESS] Verzeichnis C:\data\db erstellt
) else (
    echo [INFO] Verzeichnis C:\data\db existiert bereits
)

REM MongoDB zu PATH hinzufügen (falls nicht bereits vorhanden)
set MONGODB_PATH=C:\Program Files\MongoDB\Server\7.0\bin
echo %PATH% | find /i "%MONGODB_PATH%" >nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Füge MongoDB zu PATH hinzu...
    setx PATH "%PATH%;%MONGODB_PATH%" /M >nul 2>nul
    set PATH=%PATH%;%MONGODB_PATH%
)

echo.
echo [SUCCESS] MongoDB Installation abgeschlossen!
echo.
echo [TEST] Teste MongoDB Installation...
where mongod >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] MongoDB ist korrekt installiert und im PATH
    mongod --version | findstr "db version"
) else (
    echo [WARNING] MongoDB nicht im PATH gefunden
    echo [INFO] Möglicherweise ist ein Neustart erforderlich
)

echo.
echo [INFO] Um MongoDB zu starten, verwenden Sie: 3_START_MONGODB.bat
echo [INFO] Oder manuell: mongod --dbpath C:\data\db
echo.
pause