# 🚀 Windows Setup-Anleitung - Xionimus AI

**Letzte Aktualisierung:** 2. Oktober 2025

Diese Anleitung hilft Ihnen, das Projekt nach dem Klonen von GitHub auf Windows einzurichten.

---

## ⚠️ Wichtig: .env Dateien sind NICHT auf GitHub

Aus Sicherheitsgründen sind `.env` Dateien nicht im Repository enthalten. Sie müssen diese lokal erstellen.

---

## 📋 Schnell-Setup (3 Schritte)

### 1. Backend .env erstellen

```bash
cd backend
copy .env.example .env
```

Dann öffnen Sie `backend/.env` und setzen Sie SECRET_KEY:

```powershell
# Generieren Sie einen Key:
python -c "import secrets; print(secrets.token_hex(32))"

# Kopieren Sie den Output und fügen Sie ihn in .env ein:
# SECRET_KEY=<ihr_generierter_key>
```

### 2. Demo-User erstellen

```bash
python create_user.py
```

### 3. Starten

```bash
# Terminal 1
python main.py

# Terminal 2 (neues Terminal)
cd ..\frontend
yarn dev
```

**Login:** demo / demo123

---

## 📋 Detaillierte Anleitung

### Schritt 1: Backend .env Datei erstellen

#### PowerShell im backend-Verzeichnis:
```powershell
cd backend
Copy-Item .env.example .env
```

#### SECRET_KEY generieren:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### .env bearbeiten:
Öffnen Sie `backend/.env` mit Notepad++ oder VS Code:

```env
# Ersetzen Sie dies mit Ihrem generierten Key:
SECRET_KEY=a3f8d9c2e1b4567890abcdef1234567890abcdef1234567890abcdef12345678

JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
MONGO_URL=mongodb://localhost:27017/
LOG_LEVEL=INFO
```

---

### Schritt 2: Frontend .env erstellen (optional)

```powershell
cd ..\frontend
Copy-Item .env.example .env
```

Die Datei sollte enthalten:
```env
VITE_BACKEND_URL=http://localhost:8001
```

---

### Schritt 3: Demo-User erstellen

```bash
cd backend
python create_user.py
```

**Erwartete Ausgabe:**
```
✅ Demo user created!
   Username: demo
   Email: demo@xionimus.ai
```

---

### Schritt 4: Anwendung starten

#### Terminal 1 - Backend:
```bash
cd backend
python main.py
```

**Erfolg:** Sie sollten **NICHT** diese Warnung sehen:
```
🔴 SECRET_KEY not set!
```

#### Terminal 2 - Frontend:
```bash
cd frontend
yarn dev
```

---

## ✅ Checkliste

- [ ] `backend/.env` erstellt mit SECRET_KEY
- [ ] Demo-User erstellt
- [ ] Backend läuft ohne SECRET_KEY Warnung
- [ ] Frontend läuft auf Port 3000
- [ ] Login funktioniert (demo/demo123)

---

## 🔧 Häufige Probleme

### "SECRET_KEY not set" Warnung

**Lösung:**
1. Prüfen Sie ob `backend/.env` existiert
2. Öffnen Sie die Datei und prüfen Sie SECRET_KEY
3. Generieren Sie einen neuen Key: `python -c "import secrets; print(secrets.token_hex(32))"`
4. Backend neu starten

### "User not found" beim Login

**Lösung:**
```bash
cd backend
python create_user.py
```

### Frontend kann Backend nicht erreichen

**Lösung:**
1. Prüfen Sie `frontend/.env`: `VITE_BACKEND_URL=http://localhost:8001`
2. Frontend neu starten (Strg+C, dann `yarn dev`)

---

## 🔐 Sicherheitshinweise

1. **NIEMALS** `.env` Dateien auf GitHub pushen!
2. **NIEMALS** API Keys im Code hardcoden!
3. **IMMER** `.env.example` als Template verwenden
4. **IMMER** einen starken SECRET_KEY verwenden

---

## 🌐 API Keys hinzufügen (Optional)

Für volle AI-Funktionalität fügen Sie in `backend/.env` hinzu:

```env
# Anthropic (Empfohlen für Claude)
ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI (Optional)
OPENAI_API_KEY=sk-...

# Perplexity (Optional für Web-Recherche)
PERPLEXITY_API_KEY=pplx-...
```

**API Keys erhalten:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys
- Perplexity: https://www.perplexity.ai/settings/api

---

## 📁 Dateistruktur nach Setup

```
Xionimus-Genesis/
├── backend/
│   ├── .env                 ← ERSTELLEN (nicht auf GitHub)
│   ├── .env.example         ← Template (auf GitHub)
│   ├── create_user.py
│   └── main.py
├── frontend/
│   ├── .env                 ← ERSTELLEN (nicht auf GitHub)
│   └── .env.example         ← Template (auf GitHub)
└── WINDOWS_SETUP.md         ← Diese Anleitung
```

---

**Viel Erfolg! 🎉**
