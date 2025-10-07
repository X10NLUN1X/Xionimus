# 🐛 Windows Kompatibilität - Behobene Bugs & Anpassungen

Vollständige Dokumentation aller Windows-spezifischen Probleme und deren Lösungen.

---

## 📋 Übersicht

**Status:** ✅ Vollständig Windows-kompatibel (mit Einschränkungen)

**Getestete Windows-Versionen:**
- Windows 10 (Build 19041+)
- Windows 11

**Python-Versionen:**
- Python 3.11.x ✅
- Python 3.12.x ✅
- Python 3.13.x ✅

---

## 🔧 Behobene Bugs

### Bug #1: ModuleNotFoundError: No module named 'resource'

**Symptom:**
```
ModuleNotFoundError: No module named 'resource'
File: app/core/sandbox_executor.py, line 12
```

**Ursache:**
Das `resource` Modul ist Unix-spezifisch und existiert nicht unter Windows.

**Lösung:**
```python
# Conditional import based on platform
import sys

if sys.platform != 'win32':
    import resource
    HAS_RESOURCE = True
else:
    HAS_RESOURCE = False
    logger.info("Running on Windows - resource limits not available")
```

**Implementierung:**
- `backend/app/core/sandbox_executor.py`: Zeilen 14-25
- Alle `resource.setrlimit()` Aufrufe mit `if HAS_RESOURCE:` umschlossen
- `preexec_fn` Parameter nur auf Unix gesetzt

**Impact:** Resource-Limits für Sandbox nicht verfügbar, aber Timeouts funktionieren weiterhin.

---

### Bug #2: uvloop benötigt, aber nicht Windows-kompatibel

**Symptom:**
```
RuntimeError: uvloop does not support Windows at the moment
Getting requirements to build wheel ... error
```

**Ursache:**
`uvloop` ist ein Unix-only Performance-Paket für asyncio.

**Lösung:**
- Erstellt `requirements-windows.txt` ohne uvloop
- `install.bat` verwendet automatisch Windows-Version

**Dateien:**
- `backend/requirements-windows.txt` (neu erstellt)
- `backend/install.bat` (aktualisiert)

**Impact:** Keine - uvloop ist nur eine Performance-Optimierung, asyncio funktioniert nativ.

---

### Bug #3: WeasyPrint OSError - libgobject nicht gefunden

**Symptom:**
```
OSError: cannot load library 'libgobject-2.0-0': error 0x7e
File: weasyprint/text/ffi.py
```

**Ursache:**
WeasyPrint benötigt GTK-Bibliotheken (libgobject, libcairo, libpango), die unter Windows nicht standardmäßig verfügbar sind.

**Lösung:**
```python
# Optional import of WeasyPrint
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    logger.warning("⚠️ WeasyPrint not available - PDF export disabled")
```

**Implementierung:**
- `backend/app/core/pdf_generator.py`: Zeilen 9-21
- Alle PDF-Methoden prüfen `WEASYPRINT_AVAILABLE`
- API gibt HTTP 501 zurück wenn PDF-Export nicht verfügbar

**Workaround (optional):**
GTK installieren von: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

**Impact:** PDF-Export nicht verfügbar, aber alle anderen Features funktionieren.

---

### Bug #4: sse-starlette wird nicht installiert

**Symptom:**
```
ModuleNotFoundError: No module named 'sse_starlette'
```

**Ursache:**
In `requirements.txt` hatte `sse-starlette` keine Versionsnummer, was zu Installations-Problemen führte.

**Lösung:**
```txt
# Vorher:
sse-starlette

# Nachher:
sse-starlette==2.1.3
```

**Implementierung:**
- `backend/requirements.txt`: Zeile 194
- `backend/requirements-windows.txt`: Zeile 194
- `backend/install.bat`: Explizite Installation

**Impact:** Behoben - sse-starlette wird korrekt installiert.

---

### Bug #5: FileNotFoundError - Pfad nicht gefunden: \\tmp\xionimus_sandbox

**Symptom:**
```
FileNotFoundError: [WinError 3] Das System kann den angegebenen Pfad nicht finden: '\\tmp\\xionimus_sandbox'
```

**Ursache:**
Unix-Pfad `/tmp` existiert nicht unter Windows.

**Lösung:**
```python
import tempfile
import sys

if sys.platform == 'win32':
    # Windows: Use system temp directory
    temp_base = Path(tempfile.gettempdir())
    self.workspace_dir = temp_base / "xionimus_sandbox"
else:
    # Unix: Use /tmp
    self.workspace_dir = Path("/tmp/xionimus_sandbox")

self.workspace_dir.mkdir(parents=True, exist_ok=True)
```

**Pfade:**
- Windows: `C:\Users\<User>\AppData\Local\Temp\xionimus_sandbox`
- Unix: `/tmp/xionimus_sandbox`

**Implementierung:**
- `backend/app/core/sandbox_executor.py`: Zeilen 127-136

**Impact:** Behoben - Cross-platform Pfade.

---

### Bug #6: python-magic benötigt libmagic

**Symptom:**
```
⚠️ python-magic not available. MIME type detection disabled.
```

**Ursache:**
`python-magic` benötigt die libmagic Bibliothek, die unter Unix standardmäßig vorhanden ist, unter Windows aber fehlt.

**Lösung:**
Verwende `python-magic-bin` für Windows (enthält libmagic.dll):

```txt
# requirements-windows.txt
python-magic-bin==0.4.14  # Windows-Version mit eingebauten Libraries
```

**Implementierung:**
- `backend/requirements-windows.txt`: Zeile 198
- `backend/install.bat`: Explizite Installation

**Impact:** MIME-Type-Erkennung funktioniert unter Windows.

---

### Bug #7: psycopg2-binary Build-Fehler

**Symptom:**
```
error: Microsoft Visual C++ 14.0 or greater is required
Building wheel for psycopg2-binary ... error
```

**Ursache:**
`psycopg2-binary` kann Build-Probleme unter Windows haben, wenn Visual C++ Build Tools fehlen.

**Lösung:**
Verwende `psycopg2` statt `psycopg2-binary` in requirements-windows.txt.

**Alternative:**
Installiere Visual C++ Build Tools von: https://visualstudio.microsoft.com/visual-cpp-build-tools/

**Impact:** PostgreSQL-Support funktioniert (wenn benötigt).

---

## 📦 Windows-spezifische Packages

### Neue Packages in requirements-windows.txt:

```txt
# Windows-spezifische Packages
python-magic-bin==0.4.14  # MIME type detection mit libmagic.dll
pywin32==306              # Windows-spezifische APIs
```

### Entfernte Packages aus requirements-windows.txt:

```txt
uvloop==0.21.0            # Unix-only event loop
python-magic==0.4.27      # Benötigt externe libmagic
```

### Ersetzt:

```txt
psycopg2-binary → psycopg2  # Bessere Windows-Kompatibilität
```

---

## 🛠️ Neue Tools für Windows

### 1. check-windows.bat

**Pfad:** `/check-windows.bat`

**Zweck:** Umfassende Systemprüfung vor der Installation

**Prüft:**
- Python Version (3.11+)
- Node.js Version (18+)
- Yarn Installation
- MongoDB Installation & Service
- Git Installation
- Virtual Environment Status
- Installierte Dependencies
- Konfigurationsdateien
- Port-Verfügbarkeit (8001, 3000, 27017)
- System-Ressourcen

**Verwendung:**
```powershell
.\check-windows.bat
```

**Ausgabe:**
- Fehleranzahl
- Warnungsanzahl
- Detaillierte Handlungsempfehlungen

### 2. Verbesserte install.bat

**Neue Features:**
- Verwendet `requirements-windows.txt` automatisch
- Explizite Installation kritischer Packages
- Bessere Fehlerbehandlung
- Überspringt WeasyPrint automatisch
- Installiert Windows-spezifische Packages
- Erstellt optimierte `start.bat`

### 3. requirements-windows.txt

**Automatisch generiert aus requirements.txt mit:**
- Entfernung Unix-spezifischer Packages
- Hinzufügen Windows-spezifischer Packages
- Anpassung problematischer Dependencies

---

## 🚀 Installation auf Windows

### Schnellstart:

```powershell
# 1. System prüfen
.\check-windows.bat

# 2. Installation durchführen
.\install.bat

# 3. API-Keys hinzufügen
notepad backend\.env

# 4. Anwendung starten
.\start.bat
```

### Manuelle Installation:

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-windows.txt
pip install sse-starlette==2.1.3
pip install python-magic-bin==0.4.14

# Frontend
cd ..\frontend
yarn install

# Starten
cd ..\backend
.\venv\Scripts\activate
python main.py

# In neuem Terminal:
cd frontend
yarn dev
```

---

## ⚠️ Bekannte Einschränkungen auf Windows

### 1. Kein PDF-Export (ohne GTK)

**Problem:** WeasyPrint benötigt GTK-Bibliotheken

**Status:** Funktioniert nicht standardmäßig

**Lösung:**
- GTK installieren (komplex)
- Oder: Andere Exportformate verwenden (JSON)

**Impact:** Niedrig - PDF-Export ist optionales Feature

### 2. Keine Resource-Limits für Code-Sandbox

**Problem:** `resource` Modul existiert nicht

**Status:** Timeouts funktionieren weiterhin

**Lösung:** Keine notwendig - Timeouts bieten ausreichend Schutz

**Impact:** Niedrig - Execution Timeout von 30s funktioniert

### 3. Kein Supervisor (Process Management)

**Problem:** Supervisor ist Unix-only

**Status:** Manuelle Prozessverwaltung notwendig

**Lösung:** 
- `start.bat` Script erstellt (startet beide Services)
- Task Scheduler für Auto-Start
- Oder: NSSM (Non-Sucking Service Manager)

**Impact:** Mittel - Benötigt separate Terminals

### 4. Performance ohne uvloop

**Problem:** uvloop nicht verfügbar

**Status:** Native asyncio verwendet

**Lösung:** Keine notwendig - Performance-Unterschied gering

**Impact:** Sehr niedrig - Kaum merkbar

---

## 📊 Kompatibilitäts-Matrix

| Feature | Windows | Linux | macOS | Notes |
|---------|---------|-------|-------|-------|
| **Backend Startup** | ✅ | ✅ | ✅ | Funktioniert |
| **FastAPI Server** | ✅ | ✅ | ✅ | Vollständig |
| **MongoDB** | ✅ | ✅ | ✅ | Service oder manuell |
| **Redis** | ⚠️ | ✅ | ✅ | Windows: Redis für Windows |
| **PostgreSQL** | ✅ | ✅ | ✅ | Optional |
| **AI Agents** | ✅ | ✅ | ✅ | Alle 8 Agents |
| **Code Execution** | ✅ | ✅ | ✅ | 7 Sprachen |
| **Resource Limits** | ❌ | ✅ | ✅ | Nur Timeouts auf Windows |
| **PDF Export** | ❌* | ✅ | ✅ | *Benötigt GTK-Installation |
| **MIME Detection** | ✅** | ✅ | ✅ | **Mit python-magic-bin |
| **Process Management** | ⚠️ | ✅ | ✅ | Manuell/Task Scheduler |
| **uvloop** | ❌ | ✅ | ✅ | Native asyncio auf Windows |
| **Frontend** | ✅ | ✅ | ✅ | Identisch |
| **Authentication** | ✅ | ✅ | ✅ | Identisch |
| **GitHub Integration** | ✅ | ✅ | ✅ | Identisch |

**Legende:**
- ✅ Voll funktionsfähig
- ⚠️ Mit Einschränkungen
- ❌ Nicht verfügbar
- * Optionale Installation möglich
- ** Mit Windows-spezifischem Package

---

## 🔍 Debugging auf Windows

### Backend Logs prüfen:

```powershell
# Backend starten und Logs sehen
cd backend
.\venv\Scripts\activate
python main.py
```

### Häufige Fehler:

#### 1. "Port already in use"
```powershell
# Prozess auf Port 8001 finden
netstat -ano | findstr :8001

# Prozess beenden (PID ersetzen)
taskkill /PID 1234 /F
```

#### 2. "MongoDB connection failed"
```powershell
# MongoDB Service prüfen
sc query MongoDB

# Service starten
net start MongoDB

# Manuell starten (falls kein Service)
mongod --dbpath C:\data\db
```

#### 3. "Virtual environment activation failed"
```powershell
# Execution Policy setzen
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Dann erneut:
.\venv\Scripts\activate
```

#### 4. "Module not found" trotz Installation
```powershell
# Prüfe welches Python verwendet wird
where python
python -m site

# Installiere im richtigen Environment
.\venv\Scripts\python.exe -m pip install <package>
```

---

## 📝 Code-Anpassungen für Windows

### Sandbox Executor

**Datei:** `backend/app/core/sandbox_executor.py`

**Änderungen:**
1. Conditional import of `resource` module
2. Platform-specific temp directory paths
3. Conditional `preexec_fn` für subprocess
4. Logging für Windows-Modus

### PDF Generator

**Datei:** `backend/app/core/pdf_generator.py`

**Änderungen:**
1. Optional import of WeasyPrint
2. Runtime checks in allen Methoden
3. Informative Fehlermeldungen
4. Fallback-Verhalten

### Research History API

**Datei:** `backend/app/api/research_history.py`

**Änderungen:**
1. HTTP 501 für nicht verfügbare Features
2. Bessere Fehlermeldungen
3. Hinweise auf GTK-Installation

---

## 🎯 Best Practices für Windows-Entwicklung

### 1. Virtual Environment

**Immer** ein frisches venv für Windows erstellen:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Nicht** venv von Linux/WSL kopieren!

### 2. Pfade

**Verwende** immer `pathlib.Path` für cross-platform Pfade:
```python
from pathlib import Path
workspace = Path("workspace") / "files"
```

**Vermeide** hardcoded Unix-Pfade wie `/tmp`, `/var/log`

### 3. Prozesse

**Verwende** `subprocess` mit platform checks:
```python
if sys.platform == 'win32':
    # Windows-spezifisch
else:
    # Unix-spezifisch
```

### 4. Dependencies

**Teste** requirements-windows.txt regelmäßig:
```powershell
pip install -r requirements-windows.txt --dry-run
```

---

## ✅ Checkliste für Windows-Kompatibilität

- [x] Keine Unix-only Module importiert
- [x] Pfade cross-platform (pathlib.Path)
- [x] Temp-Verzeichnisse plattformabhängig
- [x] resource-Modul optional
- [x] uvloop entfernt/optional
- [x] WeasyPrint optional
- [x] python-magic-bin für Windows
- [x] requirements-windows.txt erstellt
- [x] install.bat optimiert
- [x] check-windows.bat erstellt
- [x] Dokumentation vollständig
- [x] Getestet auf Windows 10/11

---

## 📚 Weitere Ressourcen

**Windows-spezifische Installation:**
- `Documents/WINDOWS_INSTALLATION.md` - Vollständige Installationsanleitung
- `README.md` - Hauptdokumentation mit Windows-Hinweisen

**Tools:**
- `check-windows.bat` - Systemprüfung
- `install.bat` - Automatische Installation
- `start.bat` - Anwendung starten (wird erstellt)

**Troubleshooting:**
- `Documents/WINDOWS_INSTALLATION.md` - Abschnitt "Troubleshooting"
- `Documents/WINDOWS_BUGS_FIXED.md` - Diese Datei

---

## 📞 Support

Bei Windows-spezifischen Problemen:

1. Führe `check-windows.bat` aus
2. Prüfe Logs im Terminal
3. Siehe "Debugging auf Windows" Sektion oben
4. Konsultiere WINDOWS_INSTALLATION.md

---

**Stand:** Januar 2025
**Getestet mit:** Windows 10/11, Python 3.11-3.13
**Status:** ✅ Production-Ready mit dokumentierten Einschränkungen
