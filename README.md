# Xionimus AI - Multi-Provider AI Chat Platform

Eine leistungsstarke AI-Chat-Plattform mit Unterstützung für OpenAI, Anthropic und Perplexity.

## Funktionen

- 🤖 **Multi-Provider Support**: OpenAI (GPT-4o, GPT-4.1), Anthropic (Claude Sonnet 4.5), Perplexity (Sonar Pro)
- 🧠 **Intelligent Agent Selection**: Automatische Modell-Auswahl basierend auf der Aufgabe
- 🌐 **Web-Recherche**: Integriert Perplexity für Echtzeit-Web-Informationen
- 💬 **Session Management**: Speichert Chat-Verläufe in MongoDB
- 🎨 **Modernes UI**: React-basiertes Frontend mit Tailwind CSS
- ⚡ **FastAPI Backend**: Schnell und skalierbar

## Verfügbare Modelle

### OpenAI
- **gpt-4o** ⭐ (Empfohlen für General Chat)
- **gpt-4.1** (Alternative zu GPT-4o)
- **o1**, **o3** (Reasoning-Modelle - experimentell)

### Anthropic
- **claude-sonnet-4-5-20250929** ⭐ (Beste Balance aus Leistung und Geschwindigkeit)

### Perplexity
- **sonar-pro** ⭐ (Empfohlen für Web-Recherchen)
- **sonar** (Schneller, kostenlos)
- **sonar-deep-research** (Tiefe Analysen)

## Installation

### Windows

```cmd
# 1. Repository klonen
git clone <repository-url>
cd xionimus-ai

# 2. Backend-Abhängigkeiten installieren
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend-Abhängigkeiten installieren
cd ..\frontend
yarn install

# 4. Umgebungsvariablen konfigurieren
# Kopiere .env.example zu .env und füge API-Keys hinzu

# 5. Services starten
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2 - Frontend
cd frontend
yarn start
```

### Linux/Docker (Emergent Platform)

Die App läuft automatisch mit Supervisor:
- Backend: http://localhost:8001
- Frontend: http://localhost:3000
- MongoDB: localhost:27017

## API-Keys

Fügen Sie Ihre API-Keys in der Settings-Seite hinzu oder in den `.env` Dateien:

```env
# Backend .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
MONGO_URL=mongodb://localhost:27017/xionimus
```

```env
# Frontend .env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## Verwendung

### Automatische Modell-Auswahl

Die App wählt automatisch das beste Modell für Ihre Aufgabe:

- **General Chat** → GPT-4o
- **Code-Analyse** → Claude Sonnet 4.5
- **Web-Recherche** → Perplexity Sonar Pro
- **Komplexes Reasoning** → Claude Sonnet 4.5
- **Debugging** → GPT-4.1

### Manuelle Modell-Auswahl

1. Öffnen Sie die Settings
2. Wählen Sie Provider und Modell
3. Die Auswahl wird für zukünftige Chats gespeichert

### Web-Recherchen

Verwenden Sie Keywords wie:
- "Suche nach..."
- "Finde aktuelle Informationen über..."
- "Was sind die neuesten..."
- "Search for..."
- "Find current data on..."

Das System leitet die Anfrage automatisch an Perplexity weiter.

## Projektstruktur

```
xionimus-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # API Endpoints
│   │   ├── core/         # AI Manager, Providers
│   │   └── models/       # Datenmodelle
│   ├── main.py           # Backend Entry Point
│   └── requirements.txt  # Python Dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React Components
│   │   ├── contexts/     # State Management
│   │   └── pages/        # Seiten
│   └── package.json      # Node Dependencies
└── README.md
```

## Bekannte Einschränkungen

### GPT-5, O1, O3 Reasoning-Modelle

Diese Modelle haben derzeit ein Problem mit der Content-Ausgabe über die Standard Chat Completions API:
- Sie generieren `reasoning_tokens` statt normalem `content`
- Die Reasoning-Inhalte sind nicht über die Standard-API zugänglich
- **Empfehlung**: Verwenden Sie GPT-4o oder GPT-4.1 für normale Chats

## Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
tail -f /var/log/supervisor/backend.err.log

# Service neu starten
sudo supervisorctl restart backend
```

### Frontend zeigt keine Daten

1. Prüfen Sie, ob Backend läuft: http://localhost:8001/api/health
2. Prüfen Sie Browser Console (F12) auf Fehler
3. Verifizieren Sie REACT_APP_BACKEND_URL in frontend/.env

### API-Fehler

- **400 Bad Request**: Ungültiges Modell oder Parameter
- **401 Unauthorized**: API-Key ungültig oder fehlt
- **429 Too Many Requests**: Rate Limit erreicht
- **500 Internal Server Error**: Prüfen Sie Backend-Logs

## Support

Bei Problemen:
1. Prüfen Sie die Logs: `/var/log/supervisor/*.log`
2. Überprüfen Sie API-Keys in Settings
3. Stellen Sie sicher, dass alle Services laufen: `sudo supervisorctl status`

## Lizenz

[Ihre Lizenz hier einfügen]

---

**Version**: 1.0.0  
**Letztes Update**: September 2025
