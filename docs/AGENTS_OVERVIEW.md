# 🤖 Xionimus AI - Agent-Übersicht

## Vorhandene Agenten im Projekt

### 1. 🧠 Intelligent Agents (Task-Router)
**Datei:** `app/core/intelligent_agents.py`

**Aufgabe:** Wählt automatisch den besten LLM-Provider für eine Aufgabe

**Sub-Agenten:**
- **General Conversation** → OpenAI GPT-4o (Allgemeine Gespräche)
- **Code Analysis** → Claude Sonnet 4.5 (Code-Analyse)
- **Complex Reasoning** → Claude Opus (Komplexe Logik)
- **Research & Web** → Perplexity Sonar-Pro (Internet-Recherche)
- **Creative Writing** → OpenAI GPT-4o (Kreatives Schreiben)
- **Technical Documentation** → Claude Sonnet 4.5 (Technische Docs)
- **Debugging** → Claude Sonnet 4.5 (Fehlersuche)
- **System Analysis** → Claude Sonnet 4.5 (System-Architektur)

### 2. 🔄 Auto-Routing Manager
**Datei:** `app/core/auto_routing.py`

**Aufgabe:** Erkennt Probleme und leitet automatisch an Spezial-Agenten weiter

**Routing-Typen:**
- **Testing Agent** - Automatische Tests erstellen
- **Code Review Agent** - Code-Qualität prüfen
- **Deployment Agent** - Docker & CI/CD Setup
- **Documentation Agent** - README & API-Docs
- **Clarification Agent** - Bei Unsicherheiten
- **Expansion Agent** - Unvollständige Antworten erweitern

**Loop-Prevention:** ✅ Tracking verhindert Endlos-Schleifen

### 3. 🧪 Testing Agent
**Datei:** `app/core/testing_agent.py`

**Aufgabe:** Erstellt automatische Tests für generierten Code

**Features:**
- Unit Tests generieren
- Integration Tests
- Test-Framework Setup
- Test Coverage Reports

### 4. 🔍 Code Review Agents
**Datei:** `app/core/code_review_agents.py`

**Aufgabe:** Prüft Code-Qualität, Sicherheit, Performance

**Review-Typen:**
- Security Review
- Performance Analysis
- Best Practices Check
- Code Smell Detection

### 5. 🤖 Auto Workflow Orchestrator
**Datei:** `app/core/auto_workflow_orchestrator.py`

**Aufgabe:** Automatisiert komplette Workflows

**Workflow:**
1. Research durchführen
2. Klärungsfragen automatisch beantworten
3. Code direkt generieren
4. KEINE manuelle Bestätigung nötig

### 6. 🔄 Auto Review Orchestrator
**Datei:** `app/core/auto_review_orchestrator.py`

**Aufgabe:** Koordiniert automatische Code-Reviews

**Prozess:**
- Code wird generiert
- Auto-Review startet
- Verbesserungen werden vorgeschlagen
- Optional: Auto-Apply

### 7. 🎯 Sub-Agents System
**Datei:** `app/core/sub_agents.py`

**Aufgabe:** Basis-Framework für spezialisierte Sub-Agenten

**Capabilities:**
- Spezialisierte Task-Verarbeitung
- Context-Weitergabe
- Result-Aggregation

## 🔧 Wie Agenten zusammenarbeiten

```
User-Anfrage
    ↓
Intelligent Agent (Task-Routing)
    ↓
[Entscheidet Provider: Claude/GPT/Perplexity]
    ↓
Generiert Antwort
    ↓
Auto-Routing prüft: Braucht es Spezial-Agent?
    ↓
[Falls JA] → Testing/Review/Deploy Agent
    ↓
[Falls NEIN] → Direkt an User
    ↓
Auto-Workflow: Nächste Schritte vorschlagen
```

## 📊 Agent-Status

| Agent | Status | Integration | Aktiv |
|-------|--------|-------------|-------|
| Intelligent Agents | ✅ | chat.py | ✅ |
| Auto-Routing | ✅ | chat.py | ✅ |
| Testing Agent | ✅ | auto_routing | ⚠️ |
| Code Review | ✅ | auto_routing | ⚠️ |
| Auto Workflow | ✅ | chat.py | ✅ |
| Auto Review | ✅ | Standalone | ⚠️ |
| Sub-Agents | ✅ | Framework | ✅ |

**Legende:**
- ✅ Implementiert und aktiv
- ⚠️ Implementiert aber nur bei Bedarf aktiv

## 🚨 Fehlende Integration

**Problem:** Einige Agenten sind implementiert, werden aber nicht automatisch aufgerufen!

**Betroffene Agenten:**
1. **Testing Agent** - Muss manuell aufgerufen werden
2. **Code Review Agents** - Nicht automatisch aktiv
3. **Auto Review Orchestrator** - Standalone, keine Integration

**Lösung nötig:** Integration in Auto-Routing verbessern

## 💡 Empfohlene Verbesserungen

1. **Testing Agent Auto-Trigger**
   - Bei Code-Generierung automatisch Tests erstellen
   
2. **Code Review Auto-Run**
   - Jeder generierte Code wird automatisch reviewed
   
3. **Deployment Agent hinzufügen**
   - Docker, CI/CD automatisch generieren

4. **Documentation Agent aktivieren**
   - README automatisch erstellen

Soll ich die fehlenden Integrationen aktivieren?
