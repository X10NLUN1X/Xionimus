# 🔧 API-Schlüssel Fehlerbehebung Guide

## Problem: "Entschuldigung, ich konnte Ihre Anfrage nicht verarbeiten. Bitte stellen Sie sicher, dass die API-Schlüssel konfiguriert sind."

### ✅ LÖSUNG - Schritt für Schritt:

## 1. Backend Server starten und testen

### Backend starten:
```bash
# Terminal 1: Backend starten
cd backend
python server.py
```

**Erwartete Ausgabe:**
```
INFO: Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### Backend testen:
```bash
# Terminal 2: Verbindung testen
curl http://localhost:8001/api/health
```

**Erwartete Antwort:** JSON mit `"status":"healthy"`

## 2. Frontend starten

```bash
# Terminal 3: Frontend starten  
cd frontend
npm start
```

**Erwartete Ausgabe:** Browser öffnet http://localhost:3000

## 3. Backend-Verbindung in der UI testen

1. **Einstellungen öffnen** → ⚙️ Klicken
2. **"🔧 Backend testen"** Button klicken
3. **Erfolg:** Grüne Meldung "✅ Backend-Verbindung erfolgreich!"
4. **Fehler:** Rote Fehlermeldung mit spezifischen Anweisungen

## 4. API-Schlüssel korrekt konfigurieren

### Format-Anforderungen:
- **Anthropic**: `sk-ant-api03-...` (mindestens 15 Zeichen)
- **Perplexity**: `pplx-...` (mindestens 10 Zeichen)  
- **OpenAI**: `sk-...` (mindestens 10 Zeichen)

### Schlüssel hinzufügen:
1. **Einstellungen** → **API-Schlüssel konfigurieren**
2. **Schlüssel eingeben** (Format prüfen!)
3. **"💾 Alle Speichern"** klicken
4. **Erfolg warten:** "✅ [Service] API-Schlüssel erfolgreich gespeichert"

## 5. Chat testen

1. **Nachricht eingeben**: "Hello, test message"
2. **Senden** klicken
3. **Mögliche Antworten:**

### ✅ Erfolg:
Normale AI-Antwort von Claude/Perplexity/OpenAI

### ⚠️ Ungültige Schlüssel:
```
🔧 DEBUG: AI-Services sind konfiguriert, aber die API-Schlüssel sind ungültig oder es besteht ein Verbindungsproblem. Bitte überprüfen Sie Ihre API-Schlüssel oder Internetverbindung.
```
**→ Lösung:** API-Schlüssel bei den Anbietern überprüfen

### ❌ Backend-Verbindungsfehler:
```
🔌 Verbindung zum Backend fehlgeschlagen. Bitte stellen Sie sicher, dass der Backend-Server läuft (http://localhost:8001). Verwenden Sie die Einstellungen → "Backend testen" um die Verbindung zu prüfen.
```
**→ Lösung:** Backend neu starten, Port 8001 prüfen

## 6. Häufige Probleme und Lösungen

### Problem: Generic Error "Entschuldigung, ich konnte Ihre Anfrage nicht verarbeiten..."
**Ursache:** Frontend kann Backend nicht erreichen
**Lösung:** 
1. Backend Server Status prüfen
2. "Backend testen" Button verwenden
3. Beide Server neu starten

### Problem: "🔧 DEBUG: AI-Services sind konfiguriert, aber..."
**Ursache:** API-Schlüssel ungültig oder abgelaufen
**Lösung:**
1. Neue Schlüssel bei Anbietern generieren
2. Guthaben/Billing bei Anbietern prüfen
3. Schlüssel-Format nochmal prüfen

### Problem: CORS Fehler
**Ursache:** Frontend läuft auf anderem Port
**Lösung:**
```bash
# .env Dateien prüfen:
# backend/.env sollte enthalten: CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
# frontend/.env sollte enthalten: REACT_APP_BACKEND_URL=http://localhost:8001
```

## 7. Debug-Kommandos

### API-Schlüssel Status prüfen:
```bash
curl http://localhost:8001/api/api-keys/status
```

### Test-Chat ohne Frontend:
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "conversation_history": [], "use_agent": true}'
```

### API-Schlüssel manuell hinzufügen:
```bash
curl -X POST http://localhost:8001/api/api-keys \
  -H "Content-Type: application/json" \
  -d '{"service": "anthropic", "key": "sk-ant-YOUR_KEY_HERE", "is_active": true}'
```

## ✅ System ist korrekt konfiguriert wenn:

1. ✅ Backend läuft auf http://localhost:8001
2. ✅ Frontend läuft auf http://localhost:3000  
3. ✅ "Backend testen" zeigt Erfolg
4. ✅ API-Schlüssel sind gespeichert (grüne Bestätigung)
5. ✅ Chat zeigt AI-Antworten oder spezifische Debug-Nachrichten (nicht generic error)

**Bei weiteren Problemen:** Konsole im Browser (F12) prüfen für detaillierte Fehlermeldungen.