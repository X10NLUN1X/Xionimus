# Emergent-Next - Modern Development Platform

## 🚀 Schnellstart

### Installation
```bash
# Automatische Installation
./install.sh

# Oder manuell
npm run install:all
```

### Services starten
```bash
# Beide Services
npm run dev

# Oder einzeln
npm run start:backend
npm run start:frontend
```

### Zugriff
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

## 🏗️ Architektur

- **Frontend:** React 18 + Chakra UI + Vite + TypeScript
- **Backend:** FastAPI + Python 3.10+ + MongoDB
- **AI-Integration:** OpenAI, Anthropic, Perplexity (direkte APIs)
- **Realtime:** WebSockets für Chat
- **Deployment:** Lokale Installation (Docker optional)

## 🎯 Features

### MVP (Phase 1):
- ✅ AI-Chat Engine mit Multi-Provider Support
- ✅ Markdown-Rendering
- ✅ Chat History & Sessions
- ✅ Modern UI mit Chakra UI

### Geplant (Phase 2):
- 🔄 Monaco Code-Editor
- 🔄 File-Manager mit Tree-View
- 🔄 Upload/Download System
- 🔄 Git Integration

### Zukunft (Phase 3):
- 🔄 JWT/OAuth2 Authentication
- 🔄 User Management
- 🔄 Role-based Access
- 🔄 Team Collaboration

## 🛠️ Development

```bash
# Development-Modus
npm run dev

# Backend-Tests
npm run test:backend

# Frontend-Tests  
npm run test:frontend

# Production Build
npm run build
```