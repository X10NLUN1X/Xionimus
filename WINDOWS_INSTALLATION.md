# 🪟 XIONIMUS AI - WINDOWS INSTALLATION (MongoDB Compass)

## ⚡ SCHNELL-INSTALLATION (1-KLICK)

**Sie haben MongoDB Compass bereits ✓**

**Laden Sie das Repository herunter und führen Sie aus:**

```batch
0_COMPLETE_SETUP.bat
```

**Das war's!** Dieses Skript richtet alles für MongoDB Compass ein.

---

## 📋 MANUELLE INSTALLATION (SCHRITT-FÜR-SCHRITT)

### **Schritt 1: Repository herunterladen**
```batch
git clone https://github.com/X10NLUN1X/Xionimus.git
cd Xionimus
```

### **Schritt 2: MongoDB Compass Setup**
```batch
1_INSTALL_MONGODB.bat
```
*Dieses Skript konfiguriert die Verbindung zu Ihrem vorhandenen MongoDB Compass*

### **Schritt 3: .env Dateien erstellen**
```batch
2_SETUP_ENV_FILES.bat
```

### **Schritt 4: Dependencies installieren**
```batch
cd backend
pip install -r requirements.txt
cd ..\frontend  
yarn install
cd ..
```

---

## 🗃️ MONGODB COMPASS KONFIGURATION

### **Verbindung in Compass einrichten:**

1. **Öffnen Sie MongoDB Compass**
2. **Verbindungsstring eingeben:**
   ```
   mongodb://localhost:27017
   ```
3. **Klicken Sie "Connect"**
4. **Database wird automatisch erstellt:** `xionimus_ai`

### **Nach dem ersten Start sehen Sie:**
- **Database:** `xionimus_ai`
- **Collections:** `projects`, `chat_sessions`, `uploaded_files`, etc.

---

## 🚀 SYSTEM STARTEN (3 BAT-DATEIEN + COMPASS)

### **Schritt 1: MongoDB Compass öffnen**
- Starten Sie MongoDB Compass
- Verbinden Sie sich mit: `mongodb://localhost:27017`

### **Schritt 2: MongoDB Server starten**
```batch
3_START_MONGODB.bat
```
*Falls der Server nicht automatisch läuft*

### **Schritt 3: Backend starten**
```batch
4_START_BACKEND.bat
```

### **Schritt 4: Frontend starten (öffnet automatisch Browser)**
```batch
5_START_FRONTEND.bat
```

---

## 🔑 API KEYS KONFIGURIEREN

**Nach der Installation:**

1. **Holen Sie sich API Keys:**
   - **Perplexity**: https://www.perplexity.ai/settings/api (Format: `pplx-...`)
   - **Anthropic**: https://console.anthropic.com/ (Format: `sk-ant-...`)

2. **Bearbeiten Sie `backend\.env`:**
```env
# Uncomment diese Zeilen und fügen Sie Ihre Keys ein:
PERPLEXITY_API_KEY=pplx-your_actual_key_here
ANTHROPIC_API_KEY=sk-ant-your_actual_key_here
```

3. **Backend neu starten** (4_START_BACKEND.bat)

---

## ✅ NACH DEM START

**Testen Sie diese URLs:**
- **Frontend**: http://localhost:3000 (öffnet automatisch)
- **Backend API**: http://localhost:8001/api/health
- **API Dokumentation**: http://localhost:8001/docs
- **MongoDB**: `mongodb://localhost:27017` (in Compass)

---

## 🗃️ MONGODB COMPASS VORTEILE

### **Warum Compass perfekt für Xionimus AI ist:**

✅ **Visuelle Datenverwaltung** - Sehen Sie Ihre Projekte, Chat-Sessions, Dateien
✅ **Echtzeit-Updates** - Änderungen sofort sichtbar
✅ **Query-Builder** - Einfache Datenabfragen ohne Code
✅ **Performance-Monitoring** - Überwachen Sie Datenbankleistung
✅ **Backup & Export** - Ihre Daten sichern und exportieren

### **Was Sie in Compass sehen werden:**

**Database: `xionimus_ai`**
- **Collection: `projects`** - Ihre AI-Projekte
- **Collection: `chat_sessions`** - Chat-Verlauf mit AI Agents
- **Collection: `uploaded_files`** - Hochgeladene Dateien
- **Collection: `api_keys`** - Verschlüsselt gespeicherte API Keys

---

## 🔧 PROBLEMBEHANDLUNG

### **Compass kann sich nicht verbinden:**
```batch
# MongoDB Server starten
3_START_MONGODB.bat

# Oder Windows Service prüfen:
# Win+R → services.msc → "MongoDB" Service starten
```

### **"Python nicht gefunden":**
- **Installieren Sie Python 3.9+**: https://python.org
- **Während Installation**: "Add Python to PATH" aktivieren

### **"Node.js nicht gefunden":**
- **Installieren Sie Node.js 18+**: https://nodejs.org
- **LTS Version wählen**

### **"Port bereits belegt":**
```batch
# Port 3000 freigeben (Frontend)
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F

# Port 8001 freigeben (Backend)
netstat -ano | findstr :8001
taskkill /PID [PID_NUMBER] /F

# Port 27017 freigeben (MongoDB)
netstat -ano | findstr :27017
taskkill /PID [PID_NUMBER] /F
```

### **"Unicode Error" (gelöst):**
- ✅ **Gelöst!** Die BAT-Dateien erstellen .env Dateien mit korrekter UTF-8 Kodierung

### **"Fehler beim Laden der Projekte" (gelöst):**
- ✅ **Gelöst durch korrekte .env Dateien**
- ✅ **Frontend verbindet sich korrekt zu Backend**
- ✅ **Backend verbindet sich zu MongoDB via Compass**

---

## 🎯 VORTEILE DIESER LÖSUNG

✅ **MongoDB Compass Integration** - Nutzt Ihre vorhandene Installation
✅ **Visuelle Datenverwaltung** - Sehen Sie alle Daten in Echtzeit
✅ **1-Klick Installation** mit `0_COMPLETE_SETUP.bat`
✅ **Automatische .env Erstellung** (UTF-8 kompatibel)
✅ **Automatische Browser-Öffnung**
✅ **Kein Docker** - direkter PC-Zugriff
✅ **API Keys persistent in MongoDB gespeichert**
✅ **Alle Unicode-Probleme gelöst**

---

## 📝 DATEI-ÜBERSICHT

```
Xionimus/
├── 0_COMPLETE_SETUP.bat         # Komplette Installation (für Compass)
├── 1_INSTALL_MONGODB.bat        # MongoDB Compass Setup
├── 2_SETUP_ENV_FILES.bat        # .env Dateien erstellen
├── 3_START_MONGODB.bat          # MongoDB Server starten
├── 4_START_BACKEND.bat          # Backend API starten  
├── 5_START_FRONTEND.bat         # Frontend + Browser starten
├── backend/
│   ├── .env                     # Backend Konfiguration (wird erstellt)
│   └── ...
└── frontend/
    ├── .env                     # Frontend Konfiguration (wird erstellt)
    └── ...
```

## 🎉 MONGODB COMPASS WORKFLOW

1. **Starten Sie `0_COMPLETE_SETUP.bat`**
2. **Öffnen Sie MongoDB Compass**
3. **Verbinden Sie sich mit `mongodb://localhost:27017`**
4. **Starten Sie die 3 Services**
5. **Schauen Sie in Compass zu, wie sich die Database füllt!**

**Perfect für visuelle Datenverwaltung und Entwicklung!**