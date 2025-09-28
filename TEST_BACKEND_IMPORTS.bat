@echo off
title XIONIMUS AI - Backend Import Test
color 0E
echo.
echo ==========================================
echo    XIONIMUS AI - BACKEND IMPORT TEST
echo ==========================================
echo.

cd /d "%~dp0"

REM Prüfe ob Backend-Verzeichnis existiert
if not exist "backend\server.py" (
    echo [ERROR] Backend nicht gefunden!
    echo [INFO] Aktuelles Verzeichnis: %CD%
    pause
    exit /b 1
)

echo [TEST] Teste Backend Imports schrittweise...
cd backend

echo.
echo [STEP 1] Teste server.py Import...
python -c "
try:
    import server
    print('[✅] server.py - Import erfolgreich')
except ImportError as e:
    print(f'[❌] server.py - Import-Fehler: {e}')
except Exception as e:
    print(f'[⚠️] server.py - Anderer Fehler: {e}')
"

echo.
echo [STEP 2] Teste ai_orchestrator.py Import...
python -c "
try:
    import ai_orchestrator
    print('[✅] ai_orchestrator.py - Import erfolgreich')
except ImportError as e:
    print(f'[❌] ai_orchestrator.py - Import-Fehler: {e}')
except Exception as e:
    print(f'[⚠️] ai_orchestrator.py - Anderer Fehler: {e}')
"

echo.
echo [STEP 3] Teste research_agent.py Import...
python -c "
try:
    from agents.research_agent import ResearchAgent
    print('[✅] research_agent.py - Import erfolgreich')
except ImportError as e:
    print(f'[❌] research_agent.py - Import-Fehler: {e}')
except Exception as e:
    print(f'[⚠️] research_agent.py - Anderer Fehler: {e}')
"

echo.
echo [STEP 4] Teste AgentManager Import...
python -c "
try:
    from agents.agent_manager import AgentManager
    print('[✅] AgentManager - Import erfolgreich')
except ImportError as e:
    print(f'[❌] AgentManager - Import-Fehler: {e}')
except Exception as e:
    print(f'[⚠️] AgentManager - Anderer Fehler: {e}')
"

echo.
echo [INFO] Import-Tests abgeschlossen
echo [INFO] Falls alle grün (✅) sind, sollte das Backend starten
echo.
echo [NEXT] Backend starten mit: python server.py
echo.
cd ..
pause