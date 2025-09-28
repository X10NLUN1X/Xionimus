@echo off
title XIONIMUS AI - Quick Fix für aiohttp Fehler
color 0C
echo.
echo ==========================================
echo    QUICK FIX - AIOHTTP FEHLER BEHEBEN
echo ==========================================
echo.
echo [INFO] Behebt: ModuleNotFoundError: No module named 'aiohttp'
echo [INFO] Für Python 3.13 optimiert
echo.

echo [STEP 1/3] AIOHTTP UND DEPENDENCIES INSTALLIEREN
cd backend
echo [INSTALL] Installiere aiohttp...
pip install aiohttp

echo [INSTALL] Installiere aiohttp dependencies...
pip install aiohappyeyeballs aiosignal anyio multidict frozenlist yarl propcache

echo [INSTALL] Installiere FastAPI basics...
pip install fastapi uvicorn motor pymongo

echo.
echo [STEP 2/3] TEST IMPORTS
python -c "import aiohttp; print('[✅] aiohttp - OK')" || echo [❌] aiohttp - IMMER NOCH FEHLER
python -c "import fastapi; print('[✅] fastapi - OK')" || echo [❌] fastapi - FEHLT

echo.
echo [STEP 3/3] BACKEND STARTEN
echo [INFO] Versuche Backend zu starten...
echo [INFO] Wenn kein Fehler erscheint, ist der Fix erfolgreich!
echo.
python server.py

pause