@echo off
title Xionimus AI Backend
echo Starting Xionimus AI Backend Server...

cd /d "%~dp0\backend"

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Starting FastAPI server...
python main.py

pause
