# 🪟 Windows-Fehler Analyse & Lösungen - Xionimus AI

**Version:** 2.0.0  
**Datum:** 30. September 2025

---

## ❌ Fehler 1: uvloop does not support Windows

### Symptome:
```
RuntimeError: uvloop does not support Windows at the moment
    or
ERROR: Failed building wheel for uvloop
```

### Root Cause:
`uvloop` ist eine **Linux/macOS-only** Bibliothek, die eine schnellere Event Loop für asyncio bereitstellt. Sie nutzt `libuv` (aus Node.js), das auf Unix-Systemen optimiert ist.

**Technischer Hintergrund:**
```python
# uvloop implementiert asyncio.AbstractEventLoop für Unix
# Windows verwendet ProactorEventLoop (IOCP-basiert)
# uvloop kann NICHT auf Windows kompiliert werden
```

### Warum ist es im Projekt?

`uvloop` wird oft in FastAPI/Uvicorn-Projekten verwendet für bessere Performance:

```python
# Typischer Production-Code (Linux):
import uvloop
uvloop.install()  # 30-40% schnellere asyncio Performance

uvicorn.run(app, host="0.0.0.0", port=8001, loop="uvloop")
```

### ✅ Lösung 1: Aus requirements.txt entfernen

**Für Windows:**
```bash
# requirements-windows.txt erstellen
findstr /v /i "uvloop" requirements.txt > requirements-windows.txt
pip install -r requirements-windows.txt
```

**Oder manuell:**
```txt
# requirements.txt
fastapi==0.115.5
uvicorn[standard]==0.32.1  # ✅ Ohne uvloop
# uvloop==0.21.0  # ❌ AUSKOMMENTIERT für Windows
```

### ✅ Lösung 2: Bedingter Import im Code

**Datei:** `backend/main.py` oder `backend/server.py`

```python
import sys

# Nur auf Linux/macOS installieren
if sys.platform != 'win32':
    try:
        import uvloop
        uvloop.install()
        print("✅ uvloop aktiviert (Linux/macOS)")
    except ImportError:
        print("⚠️ uvloop nicht verfügbar, verwende Standard Event Loop")
else:
    print("ℹ️ Windows erkannt - verwende ProactorEventLoop")
```

### ✅ Lösung 3: Plattform-spezifische requirements

**Projekt-Struktur:**
```
backend/
├── requirements.txt          # Linux/macOS (mit uvloop)
├── requirements-windows.txt  # Windows (ohne uvloop)
└── requirements-base.txt     # Gemeinsame Pakete
```

**Installation:**
```bash
# Windows
pip install -r requirements-windows.txt

# Linux/macOS
pip install -r requirements.txt
```

### Performance-Vergleich:

| Event Loop | Windows | Linux | macOS |
|------------|---------|-------|-------|
| asyncio (Standard) | ✅ 100% | ✅ 100% | ✅ 100% |
| uvloop | ❌ Nicht verfügbar | ✅ 130-140% | ✅ 130-140% |
| ProactorEventLoop | ✅ Standard auf Windows | - | - |

**Fazit:** Auf Windows ist die Standard-Event-Loop die einzige Option, aber ausreichend performant.

---

## ❌ Fehler 2: ModuleNotFoundError: No module named 'pypdf'

### Symptome:
```python
Traceback (most recent call last):
  File "main.py", line 5, in <module>
    from app.core.multimodal import MultiModalProcessor
  File "app/core/multimodal.py", line 8, in <module>
    from pypdf import PdfReader
ModuleNotFoundError: No module named 'pypdf'
```

### Root Cause:

Das `pypdf` Paket wurde in **Sprint 3** (Multi-Modal Support) hinzugefügt, ist aber nicht in der `requirements.txt` enthalten.

**Chronologie:**
1. Sprint 1 & 2: PDF-Support nicht vorhanden
2. Sprint 3: Multi-Modal Feature implementiert
3. ❌ `requirements.txt` wurde nicht aktualisiert
4. ✅ `pip freeze > requirements.txt` nötig

### Warum passiert das?

**Entwicklungs-Workflow:**
```bash
# Developer installiert neue Pakete
pip install pypdf pillow

# ❌ Vergisst requirements.txt zu aktualisieren
# Code funktioniert lokal, aber nicht auf anderen Systemen
```

### ✅ Lösung 1: Pakete nachinstallieren

```bash
# Aktiviere venv
cd backend
call venv\Scripts\activate.bat

# Installiere fehlende Pakete
pip install pypdf pillow
```

### ✅ Lösung 2: requirements.txt aktualisieren

```bash
# Alle installierten Pakete exportieren
pip freeze > requirements.txt

# Oder nur Sprint 3 Pakete hinzufügen
echo pypdf==6.1.1 >> requirements.txt
echo pillow==11.3.0 >> requirements.txt
echo chromadb==0.5.23 >> requirements.txt
echo sentence-transformers==3.3.1 >> requirements.txt
```

### ✅ Lösung 3: Automatischer Dependency-Check

**Datei:** `backend/check_dependencies.py`

```python
import sys
import importlib.util

REQUIRED_MODULES = {
    'pypdf': 'Sprint 3 - PDF Processing',
    'PIL': 'Sprint 3 - Image Processing (pillow)',
    'chromadb': 'Sprint 3 - RAG System',
    'sentence_transformers': 'Sprint 3 - Embeddings',
    'fastapi': 'Core - Web Framework',
    'uvicorn': 'Core - ASGI Server',
}

missing = []
for module, description in REQUIRED_MODULES.items():
    if importlib.util.find_spec(module) is None:
        missing.append(f"{module} ({description})")

if missing:
    print("❌ Fehlende Module:")
    for mod in missing:
        print(f"   - {mod}")
    print("\n📦 Installiere mit: pip install pypdf pillow chromadb sentence-transformers")
    sys.exit(1)

print("✅ Alle Module vorhanden")
```

**In START_BACKEND.bat integrieren:**
```batch
python check_dependencies.py
if %errorLevel% neq 0 (
    echo Installiere fehlende Pakete...
    pip install pypdf pillow chromadb sentence-transformers
)
```

### Sprint 3 Abhängigkeiten (komplett):

```txt
# Multi-Modal Support
pypdf==6.1.1              # PDF text extraction
pillow==11.3.0            # Image processing
python-magic-bin==0.4.14  # File type detection (Windows binary)

# RAG System
chromadb==0.5.23          # Vector database
sentence-transformers==3.3.1  # Embeddings
onnxruntime==1.20.1       # ML runtime
torch==2.8.0              # Deep learning (ChromaDB dependency)
transformers==4.56.2      # Hugging Face models
```

---

## ❌ Fehler 3: "Das System kann den angegebenen Pfad nicht finden"

### Symptome:
```
Das System kann den angegebenen Pfad nicht finden.
[ERROR] emergent-next directory not found
```

### Root Cause:

**Alte install-windows.bat:**
```batch
cd emergent-next\backend  # ❌ Falsches Verzeichnis!
```

**Problem:**
- Projekt wurde von `emergent-next` zu `xionimus-ai` umbenannt
- Batch-Skripte verwenden noch alten Namen
- Verzeichnis existiert nicht

### ✅ Lösung: Dynamische Pfad-Erkennung

**Richtig:**
```batch
REM Hole aktuelles Verzeichnis des Skripts
cd /d "%~dp0"

REM Navigiere relativ
cd backend
```

**Erklärung:**
- `%~dp0` = Verzeichnis des Batch-Skripts
- `/d` = Wechsle auch Laufwerk (z.B. C: → D:)

### Robuste Pfad-Validierung:

```batch
REM Projekt-Root ermitteln
set "PROJECT_ROOT=%~dp0"

REM Prüfe Backend-Verzeichnis
if not exist "%PROJECT_ROOT%backend\" (
    echo [FEHLER] Backend nicht gefunden!
    echo Erwartet: %PROJECT_ROOT%backend\
    echo Aktuell: %CD%
    pause
    exit /b 1
)

REM Wechsle zu Backend
cd /d "%PROJECT_ROOT%backend"
```

---

## ❌ Fehler 4: Port bereits belegt (Address already in use)

### Symptome:
```
ERROR: [Errno 98] error while attempting to bind on address ('0.0.0.0', 8001):
address already in use
```

### Root Cause:

Port 8001 wird bereits von einem anderen Prozess verwendet.

**Häufige Ursachen:**
1. Backend läuft bereits
2. Anderer Server auf Port 8001
3. Prozess wurde nicht sauber beendet

### ✅ Lösung 1: Port-Check vor Start

```batch
REM Prüfe ob Port 8001 frei ist
netstat -ano | findstr ":8001"
if %errorLevel% equ 0 (
    echo [WARNUNG] Port 8001 ist bereits belegt!
    echo Soll der alte Prozess beendet werden? (j/n)
    set /p KILL_PROC="> "
    
    if /i "!KILL_PROC!"=="j" (
        REM Finde PID und beende Prozess
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8001"') do (
            taskkill /PID %%a /F
        )
    )
)
```

### ✅ Lösung 2: Alternativen Port verwenden

```python
# main.py
import uvicorn

# Port aus Environment Variable oder Fallback
import os
PORT = int(os.getenv("PORT", 8001))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
```

---

## ❌ Fehler 5: ModuleNotFoundError: No module named 'magic'

### Symptome:
```python
from magic import Magic
ModuleNotFoundError: No module named 'magic'
```

### Root Cause:

`python-magic` benötigt die `libmagic` C-Bibliothek.

**Auf Linux/macOS:**
```bash
# Wird vom System bereitgestellt
/usr/lib/libmagic.so
```

**Auf Windows:**
```
❌ libmagic.dll nicht vorhanden!
```

### ✅ Lösung: python-magic-bin (Windows binary included)

```bash
# Statt python-magic
pip install python-magic-bin
```

**Unterschied:**
```python
# python-magic (benötigt libmagic separat)
import magic
m = magic.Magic()

# python-magic-bin (bundled binary)
import magic
m = magic.Magic()  # Gleicher Code, aber mit integrierter DLL
```

**In requirements-windows.txt:**
```txt
python-magic-bin==0.4.14  # Windows-Binaries included
```

---

## 📋 Zusammenfassung: Windows-Anpassungen

### Benötigte Änderungen:

| Problem | Lösung | Priorität |
|---------|--------|-----------|
| uvloop nicht verfügbar | Aus requirements entfernen | 🔴 Kritisch |
| pypdf fehlt | Zu requirements hinzufügen | 🔴 Kritisch |
| Falsche Pfade | %~dp0 verwenden | 🔴 Kritisch |
| python-magic | python-magic-bin verwenden | 🟡 Mittel |
| Port belegt | Port-Check einbauen | 🟢 Nice-to-have |

### Dateien zum Erstellen/Ändern:

1. ✅ `install-windows.bat` - Neu geschrieben
2. ✅ `requirements-windows.txt` - Erstellt
3. ✅ `START_BACKEND.bat` - Mit Dependency-Check
4. ⚠️ `backend/main.py` - uvloop conditional import
5. ⚠️ `backend/check_dependencies.py` - Erstellen

### Testing-Checklist:

- [ ] `install-windows.bat` ausführen
- [ ] Alle Pakete installieren sich ohne Fehler
- [ ] `START_BACKEND.bat` startet ohne Fehler
- [ ] Backend läuft auf http://localhost:8001
- [ ] `/api/health` antwortet
- [ ] PDF-Upload funktioniert (pypdf)
- [ ] Image-Upload funktioniert (pillow)
- [ ] RAG System funktioniert (chromadb)

---

**Status:** ✅ Lösungen implementiert  
**Nächster Schritt:** Testen auf Windows 10/11
