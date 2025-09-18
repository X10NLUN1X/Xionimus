# 🚀 XIONIMUS AI - INSTALLATION GUIDE

```
██╗  ██╗██╗ ██████╗ ███╗   ██╗██╗███╗   ███╗██╗   ██╗███████╗
╚██╗██╔╝██║██╔═══██╗████╗  ██║██║████╗ ████║██║   ██║██╔════╝
 ╚███╔╝ ██║██║   ██║██╔██╗ ██║██║██╔████╔██║██║   ██║███████╗
 ██╔██╗ ██║██║   ██║██║╚██╗██║██║██║╚██╔╝██║██║   ██║╚════██║
██╔╝ ██╗██║╚██████╔╝██║ ╚████║██║██║ ╚═╝ ██║╚██████╔╝███████║
╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝

> DYSTOPIAN_AI_SYSTEM_v2.0 - Installation Guide
```

---

## 🔧 **SYSTEMANFORDERUNGEN**

### **Minimum:**
- **OS**: Linux, macOS, Windows (mit WSL2)
- **RAM**: 4GB
- **Storage**: 10GB freier Speicherplatz
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### **Empfohlen:**
- **RAM**: 8GB oder mehr
- **Storage**: 50GB SSD
- **Internet**: Breitband für AI-APIs

---

## 🚀 **INSTALLATION METHODEN**

### **Methode 1: Automatische Installation (Empfohlen)**

```bash
# 1. Repository klonen
git clone <repository-url>
cd xionimus-ai

# 2. Automatisches Installationsskript ausführen
chmod +x install.sh
./install.sh

# 3. Warten bis Installation abgeschlossen ist
# System startet automatisch

# 4. Browser öffnen: http://localhost:3000
```

### **Methode 2: Docker Compose**

```bash
# 1. Repository klonen
git clone <repository-url>
cd xionimus-ai

# 2. Docker Services starten
docker-compose up -d

# 3. Warten (30-60 Sekunden)

# 4. Browser öffnen: http://localhost:3000
```

### **Methode 3: Manuelle Installation**

```bash
# 1. Abhängigkeiten prüfen
docker --version
docker-compose --version

# 2. Umgebungsvariablen konfigurieren
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Services starten
docker-compose build --no-cache
docker-compose up -d

# 4. Gesundheitscheck
curl http://localhost:8001/api/health
```

---

## ⚙️ **KONFIGURATION**

### **Backend (.env):**
```bash
# /app/backend/.env
MONGO_URL="mongodb://mongodb:27017"
DB_NAME="xionimus_ai"
CORS_ORIGINS="*"

# Optional: API-Schlüssel (können auch in UI hinzugefügt werden)
# PERPLEXITY_API_KEY=pplx-...
# ANTHROPIC_API_KEY=sk-ant-...
# GITHUB_TOKEN=ghp_...
```

### **Frontend (.env):**
```bash
# /app/frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_HOST=localhost
WDS_SOCKET_PORT=3000
GENERATE_SOURCEMAP=false
```

---

## 🔑 **API-SCHLÜSSEL SETUP**

### **1. In der UI konfigurieren (Empfohlen):**
1. Öffnen Sie http://localhost:3000
2. Klicken Sie auf das ⚙️ **Settings-Icon**
3. Fügen Sie Ihre API-Schlüssel hinzu

### **2. API-Schlüssel erhalten:**

#### **Perplexity API (Erforderlich):**
- **Website**: https://www.perplexity.ai/settings/api
- **Kosten**: ~$5-20/Monat je nach Nutzung
- **Format**: `pplx-...`
- **Verwendet für**: Recherche, QA, GitHub, normale Unterhaltung

#### **Anthropic Claude API (Erforderlich):**
- **Website**: https://console.anthropic.com/
- **Kosten**: ~$10-50/Monat je nach Nutzung
- **Format**: `sk-ant-...`
- **Verwendet für**: Code-Generierung, Writing, Data Analysis

#### **GitHub Token (Optional):**
- **Erstellung**: GitHub → Settings → Developer settings → Personal access tokens
- **Scopes**: `repo`, `user`, `gist`
- **Format**: `ghp_...`
- **Verwendet für**: Repository-Management, Code-Upload

---

## 🔧 **TROUBLESHOOTING**

### **Häufige Probleme:**

#### **Port bereits belegt:**
```bash
# Prüfen Sie welche Ports belegt sind
netstat -tulpn | grep :3000
netstat -tulpn | grep :8001

# Docker Services stoppen
docker-compose down

# Andere Services stoppen die Ports blockieren
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8001 | xargs kill -9
```

#### **Docker-Berechtigungen:**
```bash
# Docker ohne sudo verwenden (Linux)
sudo usermod -aG docker $USER
newgrp docker

# Docker-Berechtigung testen
docker ps
```

#### **Services starten nicht:**
```bash
# Logs überprüfen
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Services neu starten
docker-compose restart

# Komplette Neuinstallation
docker-compose down -v
docker-compose up -d --build
```

#### **Frontend lädt nicht:**
```bash
# Überprüfen Sie Netzwerk-Einstellungen
docker-compose ps
docker network ls

# Cache leeren
docker-compose down
docker system prune -a
docker-compose up -d --build
```

#### **Backend API nicht erreichbar:**
```bash
# Gesundheitscheck
curl http://localhost:8001/api/health

# Backend-Logs prüfen
docker-compose logs backend

# MongoDB-Verbindung prüfen
docker-compose logs mongodb
```

---

## 🛠️ **ERWEITERTE KONFIGURATION**

### **Produktionsumgebung:**

#### **Nginx Reverse Proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### **SSL mit Let's Encrypt:**
```bash
# Certbot installieren
sudo apt install certbot

# SSL-Zertifikat erstellen  
sudo certbot --nginx -d your-domain.com

# Automatische Erneuerung
sudo crontab -e
# Hinzufügen: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Backup-Konfiguration:**

#### **MongoDB Backup:**
```bash
# Automatisches Backup-Skript erstellen
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec xionimus_mongodb mongodump --out /backup/mongodb_$DATE
EOF

chmod +x backup.sh

# Cron-Job für tägliches Backup
crontab -e
# Hinzufügen: 0 2 * * * /path/to/backup.sh
```

#### **Session/Files Backup:**
```bash
# Sessions und Uploads sichern
tar -czf backup_$(date +%Y%m%d).tar.gz uploads/ sessions/
```

---

## 📊 **MONITORING & LOGGING**

### **Logs verfolgen:**
```bash
# Alle Services
docker-compose logs -f

# Einzelne Services
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### **System-Monitoring:**
```bash
# Ressourcenverbrauch prüfen
docker stats

# Speicherplatz prüfen
docker system df

# Cleanup
docker system prune -a
```

---

## 🔄 **UPDATE PROZESS**

### **System aktualisieren:**
```bash
# 1. Code aktualisieren
git pull origin main

# 2. Services stoppen
./stop.sh

# 3. Images neu erstellen
docker-compose build --no-cache

# 4. Services starten
./start.sh

# 5. Gesundheitscheck
curl http://localhost:8001/api/health
```

### **Rollback bei Problemen:**
```bash
# Zu vorheriger Version zurück
git checkout HEAD~1

# Services neu starten
docker-compose down -v
docker-compose up -d --build
```

---

## 🔒 **SICHERHEIT**

### **Produktions-Sicherheit:**
```bash
# 1. Firewall konfigurieren
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 3000
sudo ufw deny 8001
sudo ufw enable

# 2. Docker-Sicherheit
# Keine privilegierten Container verwenden
# Regelmäßige Updates durchführen

# 3. API-Schlüssel schützen
# Niemals in Git committen
# Umgebungsvariablen verwenden
# Regelmäßig rotieren
```

---

## 🎯 **ERSTE SCHRITTE NACH INSTALLATION**

1. **✅ Installation verifizieren**: http://localhost:3000
2. **🔑 API-Schlüssel konfigurieren**: Settings → API Keys
3. **🤖 Ersten Agent testen**: "Hallo, wie geht es dir?"
4. **📁 Erstes Projekt erstellen**: PROJ Tab → Neues Projekt
5. **💻 Code generieren**: CODE Tab → Code-Generierung
6. **🔗 GitHub verbinden**: GIT Tab → Repository verknüpfen
7. **📂 Dateien hochladen**: FILES Tab → Drag & Drop
8. **🍴 Session forken**: FORK Tab → Session Backup

---

## 📞 **SUPPORT**

### **Hilfe erhalten:**
- **GitHub Issues**: Bug-Reports und Feature-Requests
- **Logs sammeln**: `docker-compose logs > debug.log`
- **System-Info**: `docker version && docker-compose version`

### **Debug-Informationen sammeln:**
```bash
# System-Status
docker-compose ps > system_status.txt
docker-compose logs > all_logs.txt
docker system df > disk_usage.txt
```

---

**> INSTALLATION COMPLETE. NEURAL NETWORK READY.**  
**> [STATUS] All agents operational - system monitoring active**

🎉 **Viel Erfolg mit XIONIMUS AI!**