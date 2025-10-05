# 🤖 Xionimus AI - Agent, Modell & Funktions-Übersicht

**Datum:** 2. Oktober 2025  
**Status:** Claude Sonnet 4.5 (Coding) & Claude Opus 4.1 (Debugging) konfiguriert

---

## 🎯 Haupt-Konfiguration

### Standard-Modell für normale Nutzung:
- **Provider:** Anthropic
- **Modell:** `claude-sonnet-4-5-20250514` (Claude Sonnet 4.5)
- **Verwendung:** Coding, Code-Analyse, normale Konversation

---

## 🤖 Intelligente Agent-Zuweisung

Das System verwendet automatische Agent-Auswahl basierend auf dem Task-Typ:

### 1. **General Conversation Agent** (Allgemeine Unterhaltung)
- **Provider:** OpenAI
- **Modell:** `gpt-4o`
- **Temperature:** 0.8
- **Verwendung:** Normale Konversation, allgemeine Fragen

### 2. **Code Analysis Agent** (Code-Analyse)
- **Provider:** Anthropic
- **Modell:** `claude-sonnet-4-5-20250514` ✨ (Sonnet 4.5)
- **Temperature:** 0.3
- **Verwendung:** Code-Analyse, Code-Review, Programmierung
- **Keywords:** code, function, programming, script, api, class, method

### 3. **Debugging Agent** (Fehlerbehebung) 🔧
- **Provider:** Anthropic
- **Modell:** `claude-opus-4-1-20250805` ✨ (Opus 4.1)
- **Temperature:** 0.3
- **Verwendung:** Bug-Detection, Error-Analysis, Root Cause Analysis
- **Keywords:** bug, error, debug, fix, problem, issue
- **Besonderheit:** Verwendet das leistungsstärkere Opus 4.1 Modell für tiefgehende Fehleranalyse

### 4. **Complex Reasoning Agent** (Komplexes Denken)
- **Provider:** Anthropic
- **Modell:** `claude-sonnet-4-5-20250514` (Sonnet 4.5)
- **Temperature:** 0.5
- **Verwendung:** Komplexe Analysen, Schritt-für-Schritt-Denken
- **Keywords:** analyze, explain, why, how, compare, evaluate, assess

### 5. **Research Agent** (Web-Recherche)
- **Provider:** Perplexity
- **Modell:** `sonar-pro`
- **Temperature:** 0.6
- **Verwendung:** Web-Suche, aktuelle Informationen, Recherche
- **Keywords:** search, find, research, latest, current, news, internet

### 6. **Creative Writing Agent** (Kreatives Schreiben)
- **Provider:** OpenAI
- **Modell:** `gpt-4o`
- **Temperature:** 0.9
- **Verwendung:** Kreatives Schreiben, Storytelling

### 7. **Technical Documentation Agent** (Technische Dokumentation)
- **Provider:** Anthropic
- **Modell:** `claude-sonnet-4-5-20250514` (Sonnet 4.5)
- **Temperature:** 0.4
- **Verwendung:** Technische Dokumentation, API-Docs, READMEs
- **Keywords:** documentation, readme, api, guide, tutorial

### 8. **System Analysis Agent** (System-Analyse)
- **Provider:** Anthropic
- **Modell:** `claude-opus-4-1-20250805` (Opus 4.1)
- **Temperature:** 0.4
- **Verwendung:** System-Architektur-Analyse, Performance-Analyse
- **Keywords:** system, architecture, performance, infrastructure

---

## 🛠️ Spezialisierte Sub-Agents

### Testing Agent (Test-Automatisierung)
- **Modell:** `claude-sonnet-4-5-20250514`
- **Funktionen:**
  - Backend-Testing mit curl
  - Frontend-Testing mit Playwright
  - E2E-Testing
  - Automatische Test-Report-Generierung

### Code Review Agents

#### 1. Code Analysis Agent
- **Modell:** `claude-sonnet-4-5-20250514`
- **Prüft:** Code-Qualität, Best Practices, Performance

#### 2. Debug Agent (Bug Detection)
- **Modell:** `claude-opus-4-1-20250805` ✨ (Opus 4.1)
- **Prüft:** Runtime Errors, Logic Bugs, Edge Cases, Error Handling

#### 3. Enhancement Agent
- **Modell:** `claude-sonnet-4-5-20250514`
- **Prüft:** Code-Verbesserungen, Optimierungen, Refactoring

#### 4. Test Agent
- **Modell:** `claude-sonnet-4-5-20250514`
- **Prüft:** Test Coverage, Missing Tests, Test Quality

### Documentation Agent
- **Modell:** `claude-sonnet-4-5-20250514`
- **Funktionen:**
  - Automatische Dokumentation
  - README-Generierung
  - API-Dokumentation

### Auto-Routing Manager
- **Funktion:** Erkennt automatisch unklare Anfragen und routet zu passenden Agents
- **Modell:** `claude-sonnet-4-5-20250514`
- **Routing zu:**
  - Testing Agent
  - Code Review Agent
  - Documentation Agent
  - Research Agent

---

## 📊 Modell-Übersicht

### Anthropic Claude Modelle

#### Claude Sonnet 4.5 (`claude-sonnet-4-5-20250514`)
**Hauptmodell für Coding**
- ✅ Code-Analyse
- ✅ Programmierung
- ✅ Code-Review
- ✅ Technische Dokumentation
- ✅ Testing
- ✅ Complex Reasoning
- **Stärken:** Schnell, effizient, exzellent für Code

#### Claude Opus 4.1 (`claude-opus-4-1-20250805`)
**Spezialisiert für Debugging & Deep Analysis**
- ✅ Debugging
- ✅ Root Cause Analysis
- ✅ System-Analyse
- ✅ Tiefgehende Fehleranalyse
- **Stärken:** Höchste Reasoning-Fähigkeiten, beste Fehleranalyse

### OpenAI Modelle

#### GPT-4o (`gpt-4o`)
- ✅ Allgemeine Konversation
- ✅ Kreatives Schreiben
- **Stärken:** Vielseitig, gut für Konversation

#### GPT-4.1 (`gpt-4.1`)
- Fallback-Option
- **Verwendung:** Wenn Anthropic nicht verfügbar

### Perplexity Modelle

#### Sonar Pro (`sonar-pro`)
- ✅ Web-Recherche
- ✅ Aktuelle Informationen
- ✅ Real-time Daten
- **Stärken:** Zugriff auf Web, aktuelle Informationen

---

## 🔧 Funktions-Übersicht

### 1. Chat & Messaging
- **Streaming-Antworten:** Real-time AI-Antworten via WebSocket
- **Multi-Turn-Conversations:** Session-basierte Konversationen
- **File Attachments:** Dateien hochladen und im Chat verwenden
- **Ultra Thinking:** Erweitertes Denken für komplexe Aufgaben (Claude)

### 2. Intelligent Agent Selection (Auto-Agent-Auswahl)
- **Status:** Standardmäßig aktiviert
- **Funktion:** Automatische Auswahl des besten Modells basierend auf Task
- **Trigger:** Analysiert User-Message und wählt passenden Agent
- **Fallback:** Falls bevorzugter Provider nicht verfügbar

### 3. Code-Features
- **Code Analysis:** Automatische Code-Analyse mit Sonnet 4.5
- **Debugging:** Tiefgehende Fehleranalyse mit Opus 4.1
- **Code Review:** Multi-Agent Code-Review System
- **Testing:** Automatisierte Backend & Frontend Tests
- **Documentation:** Auto-Generierung von Dokumentation

### 4. Auto-Routing System
- **Unklarheiten-Erkennung:** Erkennt wenn User unklar ist
- **Automatisches Routing:** Leitet zu passenden Agents weiter
- **Loop Prevention:** Verhindert Endlosschleifen
- **Agents:** Testing, Review, Documentation, Research

### 5. Session Management
- **Session-Speicherung:** SQLite-basierte Sessions
- **Session-Liste:** Alle Konversationen abrufbar
- **Session-Wiederaufnahme:** Sessions können fortgesetzt werden

### 6. Authentication & Security
- **JWT-basierte Auth:** Sichere Token-basierte Authentifizierung
- **Rate Limiting:** User-basierte Rate Limits
  - General: 100 requests/Minute
  - AI Calls: 20 calls/Minute
- **Security Headers:** X-Content-Type-Options, X-Frame-Options, etc.

### 7. Multimodal Support
- **Bilder:** Upload und Analyse von Bildern
- **Dokumente:** PDF, DOCX, TXT Verarbeitung
- **Claude Vision:** Bildanalyse mit Claude

### 8. Research & Web
- **Web-Recherche:** Via Perplexity Sonar Pro
- **Real-time Daten:** Aktuelle Informationen aus dem Web

---

## 🎨 UI-Anpassungen

### Entfernte Elemente:
- ❌ Provider/Model Anzeige im Chat (z.B. "openai / gpt-4.1")
- ❌ Provider Icon (🟢🟣🔵) im Input-Bereich
- ❌ Model Selector Dropdown (ausgeblendet, nicht entfernt)

### Verbleibende UI-Elemente:
- ✅ Chat Input & Messages
- ✅ Ultra Thinking Toggle (für Claude)
- ✅ File Attachments
- ✅ Session Management
- ✅ User Profile & Logout

---

## 📋 Konfigurations-Dateien

### Frontend:
- **`/app/frontend/src/contexts/AppContext.tsx`**
  - Standard-Provider: `anthropic`
  - Standard-Modell: `claude-sonnet-4-5-20250514`

### Backend:
- **`/app/backend/app/core/intelligent_agents.py`**
  - Agent-Assignments konfiguriert
  - Debugging → Opus 4.1
  - Coding → Sonnet 4.5

- **`/app/backend/app/core/code_review_agents.py`**
  - Debug Agent → Opus 4.1

- **`/app/backend/app/api/chat.py`**
  - Auto-Agent-Selection Logic
  - Sonnet 4.5 für Sub-Agents

---

## 🚀 Verwendungs-Beispiele

### Coding-Aufgabe:
```
User: "Erstelle eine Python-Funktion für API-Authentifizierung"
→ Agent: Code Analysis Agent (Sonnet 4.5)
→ Temperature: 0.3
→ Output: Präziser, gut strukturierter Code
```

### Debugging-Aufgabe:
```
User: "Warum funktioniert mein Login nicht? Ich bekomme 401 Errors"
→ Agent: Debugging Agent (Opus 4.1)
→ Temperature: 0.3
→ Output: Tiefgehende Analyse, Root Cause, Lösungsvorschläge
```

### System-Analyse:
```
User: "Analysiere die Sicherheit meiner Anwendung"
→ Agent: System Analysis Agent (Opus 4.1)
→ Temperature: 0.4
→ Output: Umfassende Security-Analyse
```

### Web-Recherche:
```
User: "Was sind die neuesten React 19 Features?"
→ Agent: Research Agent (Perplexity Sonar Pro)
→ Temperature: 0.6
→ Output: Aktuelle Informationen aus dem Web
```

---

## 🔑 API-Schlüssel Anforderungen

Für volle Funktionalität benötigt:
- **Anthropic API Key:** Für Sonnet 4.5 (Coding) & Opus 4.1 (Debugging)
- **OpenAI API Key:** (Optional) Für GPT-4o Fallback
- **Perplexity API Key:** (Optional) Für Web-Recherche

**Aktuell konfiguriert:** Anthropic als Haupt-Provider

---

## 📈 Performance & Token-Limits

### Claude Sonnet 4.5
- **Context Window:** 200,000 tokens
- **Output:** Bis zu 8,192 tokens
- **Geschwindigkeit:** Sehr schnell

### Claude Opus 4.1
- **Context Window:** 200,000 tokens
- **Output:** Bis zu 4,096 tokens
- **Geschwindigkeit:** Langsamer, aber höchste Qualität

---

## ✅ Zusammenfassung

**Hauptkonfiguration:**
- 🎯 **Standard:** Claude Sonnet 4.5 (für alles Coding-bezogene)
- 🔧 **Debugging:** Claude Opus 4.1 (automatisch bei Debug-Tasks)
- 🤖 **8 Intelligente Agents** mit automatischer Task-Erkennung
- 🚫 **UI:** Alle Modellbezeichnungen entfernt
- ✨ **Auto-Selection:** System wählt automatisch bestes Modell

**Vorteile:**
- Optimal für Entwickler (Sonnet 4.5 für Code)
- Beste Debugging-Erfahrung (Opus 4.1)
- Nahtlose Nutzung ohne Modell-Auswahl
- Automatische Optimierung basierend auf Task
