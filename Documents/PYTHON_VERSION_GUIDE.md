# 🐍 Python Version Guide für Xionimus AI

## Problem: Python 3.13 Kompatibilität

### ⚠️ Aktuelles Problem

Sie haben Python 3.13 installiert. Viele Python-Packages unterstützen Python 3.13 noch nicht:

```
ERROR: Could not find a version that satisfies the requirement pywin32==306
ERROR: Ignored versions that require a different python version: <3.13
```

---

## ✅ Empfohlene Lösung

### Option 1: Python 3.12 installieren (EMPFOHLEN)

**Beste Kompatibilität mit allen Packages**

1. **Python 3.12 herunterladen:**
   - Gehe zu: https://www.python.org/downloads/
   - Wähle **Python 3.12.x** (neueste 3.12 Version)
   - Download "Windows installer (64-bit)"

2. **Installation:**
   ```
   ✅ Add Python 3.12 to PATH
   ✅ Install for all users (optional)
   ```

3. **Mehrere Python-Versionen verwalten:**
   
   **Mit py Launcher (empfohlen):**
   ```powershell
   # Python 3.13 verwenden
   py -3.13 --version
   
   # Python 3.12 verwenden
   py -3.12 --version
   
   # Standard Python setzen
   py -3.12 -m venv venv
   ```

4. **Xionimus AI mit Python 3.12 installieren:**
   ```powershell
   cd C:\AI\Xionimus-Autonom
   
   # Altes venv löschen (wenn vorhanden)
   rd /s /q backend\venv
   
   # Neues venv mit Python 3.12 erstellen
   py -3.12 -m venv backend\venv
   
   # Installation durchführen
   .\install.bat
   ```

---

### Option 2: Python 3.13 mit Anpassungen verwenden

**Wenn Sie Python 3.13 behalten möchten:**

1. **requirements-windows.txt anpassen:**

   Öffne `backend\requirements-windows.txt` und ersetze:
   
   ```diff
   - pywin32==306
   + pywin32>=307
   ```

2. **Packages einzeln installieren:**
   ```powershell
   cd backend
   .\venv\Scripts\activate
   
   # Basis-Packages
   pip install fastapi uvicorn pydantic
   pip install anthropic openai
   pip install motor pymongo
   pip install sse-starlette==2.1.3
   pip install python-magic-bin
   pip install pywin32  # Neueste Version
   
   # Rest der Requirements
   pip install -r requirements-windows.txt --no-deps
   pip install -r requirements-windows.txt  # Versuche Dependencies
   ```

3. **Bekannte Probleme mit Python 3.13:**
   - Einige C-Extensions müssen neu kompiliert werden
   - Nicht alle Packages haben Wheels für 3.13
   - Längere Installationszeiten durch Kompilierung

---

### Option 3: Beide Versionen parallel (Fortgeschritten)

**Python 3.12 für Xionimus, 3.13 für andere Projekte:**

1. **Python 3.12 zusätzlich installieren**
   - Verwende "py launcher" (oben beschrieben)

2. **Projekt-spezifische Python-Version:**
   ```powershell
   # In Xionimus-Autonom Verzeichnis
   echo 3.12 > .python-version
   ```

3. **PowerShell Alias erstellen:**
   ```powershell
   # In PowerShell Profile ($PROFILE)
   function python312 { py -3.12 $args }
   function python313 { py -3.13 $args }
   ```

---

## 📊 Kompatibilitäts-Übersicht

| Python Version | Xionimus AI | Alle Packages | Empfehlung |
|----------------|-------------|---------------|------------|
| **3.11.x** | ✅ Perfekt | ✅ Vollständig | ⭐ Empfohlen |
| **3.12.x** | ✅ Perfekt | ✅ Vollständig | ⭐ Empfohlen |
| **3.13.x** | ⚠️ Teilweise | ❌ Eingeschränkt | ⚠️ Mit Anpassungen |
| 3.10.x | ⚠️ Funktioniert | ✅ Ja | ℹ️ Veraltet |
| 3.9.x und älter | ❌ Nein | ⚠️ Teilweise | ❌ Zu alt |

---

## 🔧 Schnell-Fix für Python 3.13

**Wenn Sie sofort starten möchten:**

```powershell
cd C:\AI\Xionimus-Autonom\backend

# Virtual Environment erstellen
python -m venv venv
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Kritische Packages zuerst
pip install fastapi==0.115.6 uvicorn==0.34.0
pip install anthropic==0.43.1 openai==1.59.5
pip install motor==3.7.1 pymongo==4.15.1
pip install sse-starlette==2.1.3
pip install python-magic-bin==0.4.14

# pywin32 neueste Version (für Python 3.13)
pip install pywin32

# Rest ohne strikte Versionen
pip install aiofiles aiohttp
pip install redis cryptography
pip install reportlab

# Optional: WeasyPrint überspringen (GTK Problem)
echo [INFO] WeasyPrint übersprungen - PDF Export nicht verfügbar
```

**Dann Frontend:**
```powershell
cd ..\frontend
yarn install
```

**Starten:**
```powershell
# Terminal 1
cd backend
.\venv\Scripts\activate
python main.py

# Terminal 2
cd frontend
yarn dev
```

---

## 🎯 Welche Version wählen?

### Für Xionimus AI: Python 3.12

**Vorteile:**
- ✅ 100% Package-Kompatibilität
- ✅ Keine Installationsprobleme
- ✅ Bewährte Stabilität
- ✅ Alle Features funktionieren

**Installation:**
```powershell
# 1. Python 3.12 herunterladen und installieren
# 2. Altes venv löschen
rd /s /q backend\venv

# 3. Mit Python 3.12 neu erstellen
py -3.12 -m venv backend\venv

# 4. Installation durchführen
.\install.bat
```

---

## 🔍 Python-Version prüfen

```powershell
# Welche Python-Version ist Standard?
python --version

# Alle installierten Python-Versionen
py --list

# Wo ist Python installiert?
where python

# Welches Python verwendet das venv?
.\backend\venv\Scripts\python.exe --version
```

---

## 📝 FAQs

### F: Muss ich Python 3.13 deinstallieren?

**A:** Nein! Sie können mehrere Versionen parallel installieren. Verwenden Sie den `py` Launcher um zu wählen.

### F: Was passiert mit meinen anderen Python-Projekten?

**A:** Die bleiben unberührt. Jedes Projekt kann sein eigenes Virtual Environment mit seiner eigenen Python-Version haben.

### F: Kann ich Python 3.13 später verwenden?

**A:** Ja! In 3-6 Monaten werden die meisten Packages Python 3.13 unterstützen. Dann können Sie problemlos upgraden.

### F: Warum unterstützt Python 3.13 nicht alle Packages?

**A:** Python 3.13 wurde im Oktober 2024 veröffentlicht. Viele Packages brauchen Zeit, um ihre C-Extensions anzupassen und zu testen.

---

## ⚡ Schnellstart-Zusammenfassung

**Wenn Sie Python 3.13 haben:**

```powershell
# Option 1: Python 3.12 installieren (5 Minuten)
# Download: https://www.python.org/downloads/release/python-3120/
# Dann: .\install.bat

# Option 2: Mit Python 3.13 fortfahren (10 Minuten)
# Siehe "Schnell-Fix für Python 3.13" oben
```

**Empfehlung:** Python 3.12 installieren = problemlose Installation

---

## 🆘 Hilfe bei Problemen

**Problem bleibt bestehen?**

1. Führe aus: `.\check-windows.bat`
2. Prüfe Python-Version: `python --version`
3. Siehe Logs im Terminal
4. Konsultiere: `Documents\WINDOWS_INSTALLATION.md`

**Noch Fragen?**

Siehe auch:
- `Documents\WINDOWS_BUGS_FIXED.md` - Bekannte Probleme
- `Documents\WINDOWS_INSTALLATION.md` - Vollständige Installation
- `README.md` - Hauptdokumentation

---

**Stand:** Januar 2025  
**Python 3.13 Support:** In Entwicklung  
**Empfohlene Version:** Python 3.12.x
