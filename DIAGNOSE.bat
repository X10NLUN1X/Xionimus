@echo off
echo.
echo XIONIMUS DIAGNOSE
echo ================
echo.
echo [1] Pruefe Workspace-Struktur...
dir /b backend\workspace\github_imports 2>nul
echo.
echo [2] Pruefe API Keys in DB...
python CHECK_API_KEYS.py
echo.
echo [3] Pruefe Backend-Status...
curl http://localhost:8000/health 2>nul
echo.
pause
