# 🚀 XIONIMUS AI - SCHNELLSTART

```
> DYSTOPIAN_AI_SYSTEM_v2.0 - QUICK DEPLOYMENT
> Neural Network Initialization in Progress...
```

## ⚡ **1-MINUTE SETUP**

### **Automatische Installation:**
```bash
# Repository klonen
git clone <your-repo-url>
cd xionimus-ai

# Automatische Installation
chmod +x install.sh
./install.sh

# Wählen Sie Option 1 (Docker - Empfohlen)
```

### **Oder Docker Compose direkt:**
```bash
# Sofort starten
docker-compose up -d

# Logs verfolgen
docker-compose logs -f
```

---

## 🌐 **ZUGRIFF**

Nach 30 Sekunden öffnen Sie:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Dokumentation**: http://localhost:8001/docs

---

## 🔑 **API-SCHLÜSSEL SETUP**

1. **Klicken Sie auf das ⚙️ Settings-Icon**
2. **Fügen Sie API-Schlüssel hinzu:**

### **Perplexity (Erforderlich):**
- Website: https://www.perplexity.ai/settings/api
- Kosten: ~$5-20/Monat
- Format: `pplx-...`

### **Anthropic Claude (Erforderlich):**
- Website: https://console.anthropic.com/
- Kosten: ~$10-50/Monat  
- Format: `sk-ant-...`

### **GitHub Token (Optional):**
- GitHub → Settings → Developer settings → Personal access tokens
- Scopes: `repo`, `user`, `gist`
- Format: `ghp_...`

---

## 🤖 **AGENTEN TESTEN**

### **Code Agent (Claude):**
```
"Erstelle eine Python Funktion für Fibonacci"
```

### **Research Agent (Perplexity):**
```
"Recherchiere die neuesten AI-Trends 2025"
```

### **GitHub Agent (Perplexity):**
```
"Liste meine GitHub Repositories auf"
```

### **File Agent (Claude):**
```
"Organisiere meine hochgeladenen Dateien"
```

### **Session Agent (Claude):**
```
"Erstelle einen Fork dieser Session"
```

---

## 🛠️ **TROUBLESHOOTING**

### **Services prüfen:**
```bash
docker-compose ps
docker-compose logs backend
docker-compose logs frontend
```

### **Neu starten:**
```bash
docker-compose restart
# oder
./stop.sh && ./start.sh
```

### **Komplett zurücksetzen:**
```bash
docker-compose down -v
docker-compose up -d --build
```

---

## 📱 **FEATURES TESTEN**

1. **Chat**: Stellen Sie Fragen an die AI-Agenten
2. **Code**: Lassen Sie Code generieren und analysieren
3. **Projekte**: Erstellen Sie ein neues Projekt
4. **GitHub**: Verbinden Sie Ihr GitHub-Konto
5. **Files**: Laden Sie Dateien hoch (Drag & Drop)
6. **Fork**: Erstellen Sie Session-Backups

---

## 🔄 **BEFEHLE**

```bash
# System starten
./start.sh

# System stoppen  
./stop.sh

# Status prüfen
docker-compose ps

# Logs anzeigen
docker-compose logs -f

# Update durchführen
git pull && docker-compose build --no-cache
```

---

## ⚠️ **WICHTIGE HINWEISE**

- **Erste Nutzung**: API-Schlüssel sind erforderlich für AI-Funktionen
- **Port 3000 & 8001**: Müssen frei sein
- **Internet**: Erforderlich für AI-APIs
- **Ressourcen**: 4GB RAM minimum, 8GB empfohlen

---

**> SYSTEM READY. NEURAL NETWORK ONLINE.**  
**> [WARNING] Autonomous AI active - proceed with caution.**

🎯 **Viel Erfolg mit XIONIMUS AI!**