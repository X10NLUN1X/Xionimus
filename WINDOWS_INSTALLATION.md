# 🪟 XIONIMUS AI - WINDOWS INSTALLATION

## ⚡ SCHNELL-INSTALLATION (1-KLICK)

**Laden Sie das Repository herunter und führen Sie aus:**

```batch
0_COMPLETE_SETUP.bat
```

**Das war's!** Dieses Skript installiert automatisch alles.

---

## 📋 MANUELLE INSTALLATION (SCHRITT-FÜR-SCHRITT)

### **Schritt 1: Repository herunterladen**
```batch
git clone https://github.com/X10NLUN1X/Xionimus.git
cd Xionimus
```

### **Schritt 2: MongoDB installieren**
```batch
1_INSTALL_MONGODB.bat
```

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

## 🚀 SYSTEM STARTEN (3 BAT-DATEIEN)

**Öffnen Sie 3 separate PowerShell/CMD-Fenster:**

### **Fenster 1: MongoDB starten**
```batch
3_START_MONGODB.bat
```

### **Fenster 2: Backend starten**
```batch
4_START_BACKEND.bat
```

### **Fenster 3: Frontend starten (öffnet automatisch Browser)**
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

3. **Backend neu starten** (Fenster 2: Ctrl+C, dann `4_START_BACKEND.bat`)

---

## ✅ NACH DEM START

**Testen Sie diese URLs:**
- **Frontend**: http://localhost:3000 (öffnet automatisch)
- **Backend API**: http://localhost:8001/api/health
- **API Dokumentation**: http://localhost:8001/docs

---

## 🔧 PROBLEMBEHANDLUNG

### **"Python nicht gefunden":**
- **Installieren Sie Python 3.9+**: https://python.org
- **Während Installation**: "Add Python to PATH" aktivieren

### **"Node.js nicht gefunden":**
- **Installieren Sie Node.js 18+**: https://nodejs.org
- **LTS Version wählen**

### **"MongoDB Fehler":**
- **Führen Sie als Administrator aus**: `1_INSTALL_MONGODB.bat`
- **Oder manuell installieren**: https://mongodb.com/try/download/community

### **"Port bereits belegt":**
```batch
# Port 3000 freigeben (Frontend)
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F

# Port 8001 freigeben (Backend)  
netstat -ano | findstr :8001
taskkill /PID [PID_NUMBER] /F
```

### **"Unicode Error" (wie Sie hatten):**
- **Gelöst!** Die BAT-Dateien erstellen .env Dateien mit korrekter UTF-8 Kodierung
- **Nicht mehr manuell .env Dateien erstellen**

### **"Fehler beim Laden der Projekte":**
- ✅ **Gelöst durch korrekte .env Dateien**
- ✅ **Frontend verbindet sich korrekt zu Backend**

---

## 🎯 VORTEILE DIESER INSTALLATION

✅ **1-Klick Installation** mit `0_COMPLETE_SETUP.bat`
✅ **Automatische .env Erstellung** (UTF-8 kompatibel)
✅ **Automatische Browser-Öffnung**
✅ **Automatische Dependency-Installation**
✅ **Kein Docker** - direkter PC-Zugriff
✅ **API Keys persistent gespeichert**
✅ **Alle Unicode-Probleme gelöst**

---

## 📝 DATEI-ÜBERSICHT

```
Xionimus/
├── 0_COMPLETE_SETUP.bat      # Komplette Installation
├── 1_INSTALL_MONGODB.bat     # MongoDB Installation  
├── 2_SETUP_ENV_FILES.bat     # .env Dateien erstellen
├── 3_START_MONGODB.bat       # MongoDB Server starten
├── 4_START_BACKEND.bat       # Backend API starten
├── 5_START_FRONTEND.bat      # Frontend + Browser starten
├── backend/
│   ├── .env                  # Backend Konfiguration (wird erstellt)
│   └── ...
└── frontend/
    ├── .env                  # Frontend Konfiguration (wird erstellt)
    └── ...
```

**Starten Sie mit `0_COMPLETE_SETUP.bat` und folgen Sie den Anweisungen!**