@echo off
title XIONIMUS AI - Python 3.13 Quick Fix
color 0A
echo.
echo ==========================================
echo    XIONIMUS AI - PYTHON 3.13 QUICK FIX
echo ==========================================
echo.
echo [INFO] Behebt fehlende aiohttp und andere Dependencies für Python 3.13
echo [INFO] Ihr System: Python 3.13.2032.0
echo.

echo [STEP 1/3] FEHLENDE DEPENDENCIES INSTALLIEREN
echo [INSTALL] Installiere aiohttp (fehlt gerade)...
pip install aiohttp

echo [INSTALL] Installiere andere kritische Dependencies...
pip install fastapi uvicorn motor pymongo anthropic openai python-dotenv

echo [INSTALL] Installiere async und network Libraries...
pip install aiosignal anyio multidict frozenlist yarl propcache

echo [INSTALL] Installiere data processing...
pip install "numpy>=1.24.0" "pandas>=2.0.0" pydantic typing_extensions

echo [INSTALL] Installiere HTTP clients...
pip install httpx httpcore requests urllib3 certifi

echo [INSTALL] Installiere utilities...
pip install click tqdm python-multipart PyYAML

echo.
echo [STEP 2/3] VERZEICHNISSE UND .ENV PRÜFEN
if not exist ".env" (
    echo [CREATE] Erstelle backend\.env...
    (
    echo MONGO_URL=mongodb://localhost:27017/xionimus_ai
    echo ANTHROPIC_API_KEY=
    echo OPENAI_API_KEY=
    echo PERPLEXITY_API_KEY=
    ) > .env
) else (
    echo [INFO] .env bereits vorhanden
)

echo.
echo [STEP 3/3] BACKEND TEST STARTEN
echo [TEST] Teste Backend Import...
python -c "import aiohttp; print('✅ aiohttp verfügbar')"
python -c "import fastapi; print('✅ FastAPI verfügbar')"
python -c "import motor; print('✅ MongoDB verfügbar')"

echo.
echo [SUCCESS] Quick Fix abgeschlossen!
echo.
echo [INFO] Jetzt Backend starten:
echo   python server.py
echo.
pause