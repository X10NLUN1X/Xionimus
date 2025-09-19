# 🪟 XIONIMUS AI - WINDOWS INSTALLATION

## ⚡ 1-KLICK INSTALLATION

**Für komplette automatische Installation:**

1. **Repository herunterladen/klonen**
2. **Als Administrator ausführen:**
   ```batch
   WINDOWS_INSTALL.bat
   ```
3. **System starten (2 Dateien doppelklicken):**
   - `START_BACKEND.bat`
   - `START_FRONTEND.bat`

**Das war's!** 🎉

---

## 📋 WAS DIE INSTALLATION MACHT

### **WINDOWS_INSTALL.bat:**
✅ **Python 3.11** - Automatischer Download & Installation  
✅ **Node.js 20 LTS** - Automatischer Download & Installation  
✅ **MongoDB Datenverzeichnis** - `C:\data\db` erstellen  
✅ **Yarn** - Global installieren  
✅ **Projektverzeichnisse** - `uploads`, `sessions`, `logs`  
✅ **`.env` Dateien** - Korrekte Windows-Konfiguration  
✅ **Python Dependencies** - `pip install -r requirements.txt`  
✅ **Node Dependencies** - `yarn install`  

### **START_BACKEND.bat:**
✅ **Backend Server** - Startet auf `localhost:8001`  
✅ **MongoDB Check** - Verbindung prüfen  
✅ **Dependencies Check** - Automatische Reparatur  
✅ **API Dokumentation** - `http://localhost:8001/docs`  

### **START_FRONTEND.bat:**
✅ **Frontend Server** - Startet auf `localhost:3000`  
✅ **Backend Check** - Verbindung prüfen  
✅ **Auto-Browser** - Öffnet automatisch nach 15 Sekunden  
✅ **Dependencies Check** - Automatische Reparatur  

---

## 🗃️ MONGODB COMPASS INTEGRATION

### **Verbindung einrichten:**
1. **Öffnen Sie MongoDB Compass**
2. **Connection String:** `mongodb://localhost:27017`
3. **Klicken Sie "Connect"**
4. **Database:** `xionimus_ai` (wird automatisch erstellt)

### **Collections die Sie sehen werden:**
- **`projects`** - Ihre AI-Projekte
- **`chat_sessions`** - Chat-Verläufe  
- **`uploaded_files`** - Hochgeladene Dateien
- **`api_keys`** - Verschlüsselt gespeicherte Keys

---

## 🔑 API KEYS KONFIGURIEREN

### **Nach der Installation:**

1. **API Keys holen:**
   - **Perplexity:** https://www.perplexity.ai/settings/api
   - **Anthropic:** https://console.anthropic.com/

2. **`backend\.env` bearbeiten:**
   ```env
   # Uncomment diese Zeilen:
   PERPLEXITY_API_KEY=pplx-your_actual_key_here
   ANTHROPIC_API_KEY=sk-ant-your_actual_key_here
   ```

3. **Backend neu starten** (`START_BACKEND.bat`)

---

## ✅ SYSTEM TESTEN

### **URLs nach dem Start:**
- **Frontend:** http://localhost:3000 (öffnet automatisch)
- **Backend API:** http://localhost:8001/api/health
- **API Dokumentation:** http://localhost:8001/docs
- **MongoDB:** `mongodb://localhost:27017` (für Compass)

### **Funktionstest:**
1. **Frontend öffnet sich automatisch**
2. **Klicken Sie auf verschiedene Tabs** (CHAT, CODE, PROJ)
3. **Testen Sie API Key Eingabe** (⚙️ Settings)
4. **Schauen Sie in MongoDB Compass** - neue Collections erscheinen

---

## 🔧 PROBLEMBEHANDLUNG

### **Installation Probleme:**

**"Python nicht gefunden":**
- Installation war nicht erfolgreich
- Manuell installieren: https://python.org
- "Add to PATH" aktivieren

**"Node.js nicht gefunden":**
- Installation war nicht erfolgreich  
- Manuell installieren: https://nodejs.org
- LTS Version wählen

**"Administrator-Rechte erforderlich":**
- Rechtsklick auf `WINDOWS_INSTALL.bat`
- "Als Administrator ausführen"

### **Laufzeit Probleme:**

**Backend startet nicht:**
```batch
# Port freigeben
netstat -ano | findstr :8001
taskkill /PID [PID_NUMBER] /F

# Dependencies neu installieren
cd backend
pip install -r requirements.txt
```

**Frontend startet nicht:**
```batch
# Port freigeben
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F

# Dependencies neu installieren
cd frontend
yarn install
```

**MongoDB Verbindung fehlt:**
- MongoDB Compass starten
- Verbindung zu `mongodb://localhost:27017` herstellen
- Oder MongoDB als Windows Service installieren

**"Fehler beim Laden der Projekte":**
- ✅ **Gelöst!** Windows-Installation verwendet korrekte lokale Pfade
- Backend verwendet jetzt `uploads/` und `sessions/` Verzeichnisse
- Keine Docker-Pfade mehr

---

## 🎯 VORTEILE WINDOWS-INSTALLATION

✅ **Vollautomatisch** - Eine BAT-Datei installiert alles  
✅ **Lokale Pfade** - Keine Docker-Container Probleme  
✅ **MongoDB Compass** - Visuelle Datenverwaltung  
✅ **Auto-Browser** - Frontend öffnet automatisch  
✅ **Error-Recovery** - Automatische Problem-Erkennung  
✅ **Persistent Storage** - Alle Daten bleiben erhalten  
✅ **Windows-Optimiert** - Native Windows-Pfade und -Konfiguration  

---

## 📁 DATEI-STRUKTUR NACH INSTALLATION

```
Xionimus/
├── WINDOWS_INSTALL.bat      # 1-Klick Installation
├── START_BACKEND.bat        # Backend starten
├── START_FRONTEND.bat       # Frontend starten  
├── uploads/                 # Hochgeladene Dateien (lokaler Pfad)
├── sessions/                # Session-Backups (lokaler Pfad)
├── logs/                    # Log-Dateien (lokaler Pfad)
├── backend/
│   ├── .env                 # Backend Konfiguration
│   └── ...
└── frontend/
    ├── .env                 # Frontend Konfiguration  
    └── ...
```

---

## 🚀 QUICK START

1. **Download/Clone Repository**
2. **Rechtsklick `WINDOWS_INSTALL.bat` → "Als Administrator ausführen"**
3. **Doppelklick `START_BACKEND.bat`**  
4. **Doppelklick `START_FRONTEND.bat`**
5. **Browser öffnet automatisch → http://localhost:3000**
6. **Fertig!** 🎉

**Xionimus AI läuft jetzt nativ auf Windows ohne Docker!**