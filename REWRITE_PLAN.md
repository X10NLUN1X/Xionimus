# XIONIMUS AI - Komplett-Neuschreibung Plan

## 🎯 **ZIEL**
Komplette Neuschreibung des XIONIMUS AI Systems mit moderner Architektur, NPM-Kompatibilität und allen bestehenden Features.

## 📋 **BEIBEHALTENE FEATURES**
- ✅ 9 AI-Agenten (Code, Research, Writing, Data, QA, GitHub, File, Session, Experimental)
- ✅ Multi-Agent Chat System mit intelligenter Weiterleitung
- ✅ GitHub Repository Integration
- ✅ File Upload und Management
- ✅ Session Management (Gespräche speichern)
- ✅ Monaco Code Editor Integration
- ✅ Gold/Schwarz Theme

## 🛠️ **MODERNE TECH-STACK**
- **Frontend:** React 18 + TypeScript + shadcn/ui + Tailwind CSS
- **Backend:** FastAPI + Python 3.11+ + MongoDB
- **AI-Provider:** OpenAI, Anthropic, Perplexity (direkte APIs)
- **Package Manager:** NPM-only (keine yarn Abhängigkeit)
- **Build Tools:** Vite (statt Create React App/Craco)

## 🗂️ **NEUE ARCHITEKTUR**

### Backend (/backend):
```
/backend
├── main.py              # FastAPI App
├── requirements.txt     # Python Dependencies
├── api/                 # API Routes
│   ├── agents.py        # Agent Management
│   ├── chat.py          # Chat Endpoints
│   ├── files.py         # File Upload/Management
│   └── sessions.py      # Session Management
├── core/                # Core Logic
│   ├── config.py        # Configuration
│   ├── database.py      # MongoDB Connection
│   └── ai_orchestrator.py # AI Orchestration
├── agents/              # AI Agent System
│   ├── base.py          # Base Agent Class
│   ├── code.py          # Code Agent
│   ├── research.py      # Research Agent
│   └── ...              # Other Agents
└── utils/               # Utilities
```

### Frontend (/frontend):
```
/frontend
├── package.json         # NPM Dependencies (React 18)
├── vite.config.js       # Vite Configuration
├── src/
│   ├── main.tsx         # App Entry Point
│   ├── App.tsx          # Main App Component
│   ├── components/      # UI Components
│   │   ├── ui/          # shadcn/ui Components
│   │   ├── Chat/        # Chat Components
│   │   ├── Agents/      # Agent Components
│   │   └── Editor/      # Monaco Editor
│   ├── lib/             # Utilities
│   ├── hooks/           # Custom Hooks
│   ├── context/         # React Context
│   └── styles/          # CSS/Tailwind
```

## 🚀 **PHASEN-PLAN**

### Phase 1: Clean Setup
- Backup bestehender Code
- Neue Projektstruktur erstellen
- Moderne Dependencies definieren

### Phase 2: Backend (FastAPI)
- MongoDB Connection + Models
- AI Orchestrator (OpenAI, Anthropic, Perplexity)
- API Endpoints für alle Features
- Agent System implementieren

### Phase 3: Frontend (React + TypeScript)
- Vite + React 18 Setup
- shadcn/ui + Tailwind CSS
- Chat Interface
- Agent Management UI
- Monaco Editor Integration

### Phase 4: AI Integration
- OpenAI API Integration
- Anthropic API Integration  
- Perplexity API Integration
- Multi-Agent Orchestration

### Phase 5: Features
- File Upload/Management
- Session Management
- GitHub Integration
- Code Editor Features

### Phase 6: Testing & Polish
- Backend Testing
- Frontend Testing
- Cross-browser Testing
- Performance Optimierung

## ⚡ **MODERNE VERBESSERUNGEN**
- **TypeScript** für bessere Typsicherheit
- **Vite** für schnelleres Development
- **shadcn/ui** für moderne, konsistente UI
- **NPM scripts** statt .bat Dateien
- **Docker support** (optional)
- **Environment-based Configuration**
- **Proper Error Handling**
- **Loading States & UX**