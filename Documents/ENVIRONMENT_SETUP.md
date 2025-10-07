# 🔐 Environment Setup Guide

Diese Anleitung beschreibt die Konfiguration der Environment-Variablen für Xionimus AI.

## 📋 Schnellstart

### Backend Setup

```bash
# 1. Kopiere Template
cd backend
cp .env.example .env

# 2. Generiere sicheren SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# 3. Füge generierten Key in .env ein
# SECRET_KEY=<dein-generierter-key>

# 4. Konfiguriere Database
# MONGO_URL=mongodb://localhost:27017/xionimus_ai

# 5. Optional: AI Provider API Keys hinzufügen
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# PERPLEXITY_API_KEY=pplx-...
```

### Frontend Setup

```bash
# 1. Kopiere Template
cd frontend
cp .env.example .env

# 2. Konfiguriere Backend-URL
# VITE_API_URL=http://localhost:8001/api
```

## 🔍 Environment Validation

Das Backend validiert automatisch beim Start alle kritischen Environment-Variablen.

### Validierungs-Levels

#### ❌ **CRITICAL** (Server startet NICHT)
- `SECRET_KEY` - Muss sicher sein (min. 32 Zeichen)
- `MONGO_URL` - Gültige MongoDB Connection String

#### ⚠️ **WARNING** (Server startet mit Einschränkungen)
- AI Provider API Keys - Mindestens einer empfohlen
- CORS Settings - In Produktion nicht zu permissiv
- Log Level - In Produktion nicht DEBUG

### Validierung überspringen (nur für Tests!)

```bash
export SKIP_ENV_VALIDATION=true
python main.py
```

## 🔐 Kritische Variablen

### SECRET_KEY

**Verwendung**: JWT Token Signierung, Session Encryption

**Anforderungen**:
- Mindestens 32 Zeichen (256-bit Security)
- Kryptographisch sicher generiert
- NIEMALS mit anderen teilen oder committen

**Generierung**:
```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32

# Online (NUR für Development!)
# https://generate-secret.vercel.app/32
```

**Unsichere Defaults (werden abgelehnt)**:
- `your-secret-key-here`
- `changeme`
- `secret`
- `test`
- Jede Zeichenkette < 32 Zeichen

### MONGO_URL

**Format**:
```bash
# Lokal
MONGO_URL=mongodb://localhost:27017/xionimus_ai

# Cloud (MongoDB Atlas)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/xionimus_ai

# Mit Authentication
MONGO_URL=mongodb://user:pass@localhost:27017/xionimus_ai?authSource=admin
```

## 🤖 AI Provider Keys

### OpenAI

**Erstellen**: https://platform.openai.com/api-keys

```bash
OPENAI_API_KEY=sk-proj-...
```

**Features**:
- GPT-4, GPT-3.5 Text Generation
- Code Generation & Review
- DALL-E Image Generation

### Anthropic Claude

**Erstellen**: https://console.anthropic.com/settings/keys

```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**Features**:
- Claude 3 Opus/Sonnet/Haiku
- Lange Kontexte (200k tokens)
- Code Analysis

### Perplexity

**Erstellen**: https://www.perplexity.ai/settings/api

```bash
PERPLEXITY_API_KEY=pplx-...
```

**Features**:
- Web-basierte AI Suche
- Aktuelle Informationen
- Quellenangaben

### Google Gemini

**Erstellen**: https://makersuite.google.com/app/apikey

```bash
GOOGLE_API_KEY=AIza...
```

## 🌐 CORS Configuration

### Development

```bash
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Production

```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

⚠️ **NIEMALS** in Produktion: `CORS_ORIGINS=*`

## 📊 Optional Settings

### Rate Limiting

```bash
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### File Upload

```bash
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_EXTENSIONS=.txt,.pdf,.docx,.md,.py,.js,.json,.csv
```

### Session & Cache

```bash
SESSION_TIMEOUT_MINUTES=60
CACHE_TTL_SECONDS=3600
```

## 🚨 Sicherheits-Checkliste

- [ ] `.env` ist in `.gitignore` eingetragen ✅ (bereits konfiguriert)
- [ ] `SECRET_KEY` ist kryptographisch sicher generiert
- [ ] `SECRET_KEY` ist mindestens 32 Zeichen lang
- [ ] Keine API Keys im Code hardcoded
- [ ] CORS nur für benötigte Domains aktiviert (Produktion)
- [ ] `DEBUG=false` in Produktion
- [ ] `LOG_LEVEL=INFO` oder `WARNING` in Produktion
- [ ] Alle kritischen Variablen in Vault/Secret Manager (Cloud Deployment)

## 🔄 Environment per Stage

### Development

```bash
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Staging

```bash
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://staging.yourdomain.com
```

### Production

```bash
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
ENABLE_METRICS=true
SENTRY_DSN=https://...
```

## 🆘 Troubleshooting

### Server startet nicht - "Environment validation failed"

**Ursache**: Kritische Environment-Variablen fehlen oder sind ungültig

**Lösung**:
1. Prüfe Fehlermeldung genau
2. Vergleiche deine `.env` mit `.env.example`
3. Stelle sicher, dass alle kritischen Variablen gesetzt sind
4. Prüfe `SECRET_KEY` auf Länge und Sicherheit

### "No AI Provider API Keys configured"

**Info**: Dies ist nur eine Warnung, Server startet trotzdem

**Optional**: 
- Konfiguriere mindestens einen AI Provider für volle Funktionalität
- Oder nutze eingeschränkten Mode ohne AI-Features

### "CORS origin not allowed"

**Ursache**: Frontend-URL nicht in `CORS_ORIGINS` aufgelistet

**Lösung**:
```bash
# Backend .env
CORS_ORIGINS=http://localhost:3000,<deine-frontend-url>
```

## 📚 Weitere Ressourcen

- [.env.example](backend/.env.example) - Vollständige Template-Datei
- [config.py](backend/app/core/config.py) - Settings-Klasse
- [env_validator.py](backend/app/core/env_validator.py) - Validierungs-Logik

---

**Letzte Aktualisierung**: Januar 2025  
**Version**: 2.1.0
