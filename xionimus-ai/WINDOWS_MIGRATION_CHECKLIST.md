# 🪟 Windows-Migration Checklist - emergent-next → Xionimus AI

**Datum:** 30. September 2025

---

## ❌ Zu entfernende/ändernde Referenzen

### 1. Projekt-Namen
**Alt:** `emergent-next`  
**Neu:** `xionimus-ai`

**Vorkommen prüfen in:**
- [ ] install-windows.bat
- [ ] START_BACKEND.bat
- [ ] START_FRONTEND.bat
- [ ] package.json (Frontend)
- [ ] pyproject.toml / setup.py (Backend)
- [ ] README.md
- [ ] Dokumentations-Dateien

### 2. Verzeichnis-Pfade

#### Alt (zu ersetzen):
```batch
C:\emergent-next\
%APPDATA%\emergent-next\
.\emergent-next\backend
.\emergent-next\frontend
```

#### Neu:
```batch
C:\AI\Xionimus-Genesis\xionimus-ai\
%USERPROFILE%\.xionimus_ai\
.\xionimus-ai\backend
.\xionimus-ai\frontend
```

### 3. Fehlerhafte Checks in install-windows.bat

#### Alt:
```batch
if not exist "emergent-next\" (
    echo [ERROR] emergent-next directory not found
)
```

#### Neu:
```batch
if not exist "%PROJECT_ROOT%\backend\" (
    echo [FEHLER] Backend-Verzeichnis nicht gefunden!
)
```

### 4. Ausgabe-Texte

#### Alt:
```batch
echo Installing Emergent Next...
echo Starting Emergent platform...
```

#### Neu:
```batch
echo Installiere Xionimus AI...
echo Starte Xionimus AI...
```

---

## 🐍 Python/Backend spezifisch

### 1. requirements.txt - Linux-only Pakete

**Zu entfernen für Windows:**
```
uvloop==0.19.0  # ❌ Linux/macOS only
```

**Zu behalten:**
```
fastapi
uvicorn[standard]  # ✅ Ohne uvloop
pypdf  # ✅ Muss hinzugefügt werden
pillow
chromadb
sentence-transformers
```

### 2. Import-Statements

**Datei:** `backend/main.py` oder `backend/server.py`

**Zu entfernen/anpassen:**
```python
# ❌ Alt - conditional uvloop import
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # Windows - uvloop not available
```

**Besser:**
```python
# ✅ Neu - nur auf Linux/macOS
import sys
if sys.platform != 'win32':
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass
```

### 3. Pfad-Trennzeichen

**Alt (Linux):**
```python
path = "emergent-next/data/uploads"
```

**Neu (plattformunabhängig):**
```python
from pathlib import Path
path = Path("xionimus-ai") / "data" / "uploads"
```

---

## 📦 package.json (Frontend)

### Zu ändern:

```json
{
  "name": "emergent-next",  // ❌ Alt
  "name": "xionimus-ai",     // ✅ Neu
  
  "description": "Emergent Next Frontend",  // ❌
  "description": "Xionimus AI Frontend",    // ✅
  
  "homepage": "https://emergent-next.app",  // ❌
  "homepage": "https://xionimus-ai.app"     // ✅
}
```

---

## 🔧 START_BACKEND.bat - Häufige Fehler

### Problem 1: Falscher Pfad
```batch
REM ❌ Alt
cd emergent-next\backend

REM ✅ Neu
cd /d "%~dp0backend"
```

### Problem 2: Fehlende Dependency-Checks
```batch
REM ❌ Alt - keine Validierung
python main.py

REM ✅ Neu - mit Check
call venv\Scripts\activate.bat
python check_dependencies.py
if %errorLevel% neq 0 (
    echo [FEHLER] Fehlende Abhängigkeiten!
    pip install -r requirements.txt
)
python main.py
```

### Problem 3: Keine Error-Handling
```batch
REM ❌ Alt
python main.py

REM ✅ Neu
python main.py
if %errorLevel% neq 0 (
    echo [FEHLER] Backend-Start fehlgeschlagen!
    echo Pruefen Sie die Logs oben.
    pause
    exit /b 1
)
```

---

## 🌐 Environment Variables

### Alt (zu ändern):
```bash
EMERGENT_DATA_DIR=C:\emergent-next\data
EMERGENT_CONFIG=C:\emergent-next\config.json
```

### Neu:
```bash
XIONIMUS_DATA_DIR=%USERPROFILE%\.xionimus_ai\data
XIONIMUS_CONFIG=%USERPROFILE%\.xionimus_ai\config.json
```

---

## 📝 Dokumentations-Dateien

### Zu aktualisieren:

1. **README.md**
   - Projekt-Name
   - Repository-URLs
   - Installations-Anweisungen

2. **CONTRIBUTING.md**
   - Projekt-Referenzen
   - Setup-Befehle

3. **docs/** Verzeichnis
   - Alle Markdown-Dateien
   - Code-Beispiele
   - Screenshots (falls vorhanden)

---

## 🔍 Automatische Suche-Befehle

### Windows PowerShell:
```powershell
# Suche nach "emergent-next" in allen Dateien
Get-ChildItem -Recurse -File | Select-String "emergent-next" | Select-Object Path, LineNumber

# Suche nach "emergent" (case-insensitive)
Get-ChildItem -Recurse -File | Select-String -Pattern "emergent" -CaseSensitive:$false
```

### Git Bash / WSL:
```bash
# Suche rekursiv
grep -r "emergent-next" .

# Suche mit Ausschluss von node_modules
grep -r "emergent-next" . --exclude-dir=node_modules --exclude-dir=venv
```

---

## ✅ Checklist für Migration

- [ ] install-windows.bat ersetzt
- [ ] START_BACKEND.bat aktualisiert
- [ ] START_FRONTEND.bat aktualisiert
- [ ] requirements.txt Windows-kompatibel
- [ ] package.json aktualisiert
- [ ] README.md aktualisiert
- [ ] Alle Skripte getestet
- [ ] Dokumentation aktualisiert
- [ ] Environment Variables angepasst
- [ ] Git Repository umbenannt (falls nötig)

---

## 🎯 Kritische Änderungen (Priorität 1)

1. ✅ `install-windows.bat` - komplett neu geschrieben
2. ✅ `requirements.txt` - uvloop entfernt
3. ⚠️ `START_BACKEND.bat` - Dependency-Checks hinzufügen
4. ⚠️ Alle "emergent-next" Referenzen suchen & ersetzen

---

**Status:** In Arbeit  
**Nächster Schritt:** START_BACKEND.bat mit Dependency-Checks erstellen
