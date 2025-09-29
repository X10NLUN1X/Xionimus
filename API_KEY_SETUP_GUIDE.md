# API-Keys Setup Guide - Behebung des Chat-Problems

## 🔍 Problem-Diagnose

**Situation:** API-Keys wurden korrekt eingegeben, aber der Chat bleibt gesperrt.

**Ursache:** Architektur-Problem in der API-Key-Übertragung:
- Frontend speichert Keys nur in localStorage
- Backend liest Keys nur aus .env-Datei  
- Keine Kommunikation zwischen Frontend und Backend

## ✅ Lösung: Verbesserte API-Key Integration

### Schritt 1: Backend-Verbesserungen (BEREITS IMPLEMENTIERT)

Das Backend wurde erweitert um:
- Dynamische API-Keys über Request-Body
- Fallback auf .env-Konfiguration
- Erweiterte Provider-Status-Logik

### Schritt 2: Frontend-Integration (BEREITS IMPLEMENTIERT)

Das Frontend sendet jetzt:
- API-Keys mit jeder Chat-Anfrage
- Aktualisierte Provider-Status-Logik
- Verbesserte Fehlerbehandlung

### Schritt 3: API-Keys konfigurieren

#### Option A: Über Settings-UI (EMPFOHLEN)
1. Starte die Anwendung: `cd /app/emergent-next && ./start-dev.sh`
2. Öffne http://localhost:3000  
3. Klicke auf "Settings" in der Sidebar
4. Gib deine API-Keys ein:
   - **OpenAI**: sk-proj-... (von https://platform.openai.com/api-keys)
   - **Anthropic**: sk-ant-... (von https://console.anthropic.com/keys)  
   - **Perplexity**: pplx-... (von https://www.perplexity.ai/settings/api)
5. Klicke "Save API Keys"
6. Gehe zu "AI Chat" - sollte jetzt funktionieren!

#### Option B: Über Backend .env-Datei
```bash
# Bearbeite die Backend-Konfiguration
nano /app/emergent-next/backend/.env

# Füge deine Keys hinzu:
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here  
PERPLEXITY_API_KEY=pplx-your-key-here

# Backend neu starten
cd /app/emergent-next/backend
source venv/bin/activate
python main.py
```

### Schritt 4: CORS-Problem beheben

Wenn CORS-Fehler auftreten:

```bash
# Backend neu starten um CORS-Konfiguration zu laden
cd /app/emergent-next
pkill -f "python.*main.py"
./start-dev.sh
```

### Schritt 5: Testen

1. Öffne http://localhost:3000
2. Gehe zu "Settings" 
3. Überprüfe Status: "X/3 AI Providers Configured"
4. Gehe zu "AI Chat"
5. Wähle Provider (OpenAI/Anthropic/Perplexity)
6. Sende eine Test-Nachricht

## 🎨 Black & Gold Design - Implementierungsschritte

### Schritt 1: Theme-Konfiguration (BEREITS IMPLEMENTIERT)

Das Chakra UI Theme wurde komplett aktualisiert:

**Farbschema:**
- **Primärfarbe**: Gold (#FFB300)
- **Hintergrund**: Schwarz (#0A0A0A)
- **Karten**: Dunkelgrau (#111111)
- **Text**: Weiß (#FFFFFF)
- **Akzente**: Verschiedene Gold-Abstufungen

### Schritt 2: Komponenten-Styling (BEREITS IMPLEMENTIERT)

**Aktualisierte Komponenten:**
- Buttons: Gold mit schwarzem Text
- Cards: Dunkler Hintergrund mit Gold-Hover
- Inputs: Dunkle Hintergründe mit Gold-Focus
- Layout: Schwarze Sidebar mit goldenen Akzenten

### Schritt 3: Weitere Anpassungen (OPTIONAL)

Für weitere Design-Anpassungen:

```typescript
// In /app/emergent-next/frontend/src/theme/index.ts

// Neue Farben hinzufügen:
const colors = {
  primary: {
    // Bestehende Gold-Palette
    500: '#FFB300', // Hauptfarbe ändern
  },
  custom: {
    darkGold: '#B8860B',    // Für spezielle Elemente
    lightGold: '#FFD700',   // Für Highlights
    deepBlack: '#000000',   // Für maximalen Kontrast
  }
}

// Komponenten anpassen:
const components = {
  // Neue Komponente stylen
  NewComponent: {
    baseStyle: {
      bg: 'custom.deepBlack',
      color: 'primary.500',
      border: '1px solid',
      borderColor: 'primary.500',
    }
  }
}
```

## 🔧 Fehlerbehebung

### Problem: Chat zeigt "0/3 AI PROVIDERS"
**Lösung:**
1. Überprüfe Settings-Seite  
2. Stelle sicher, dass API-Keys gespeichert sind
3. Backend neu starten
4. Browser-Cache leeren

### Problem: CORS-Fehler in Konsole
**Lösung:**
```bash
# Backend mit korrekter CORS-Konfiguration neu starten
cd /app/emergent-next
pkill -f "python.*main.py"
python backend/main.py
```

### Problem: Design nicht aktualisiert
**Lösung:**
```bash
# Frontend neu starten für Theme-Update
cd /app/emergent-next/frontend
yarn dev
```

### Problem: API-Keys nicht gespeichert
**Lösung:**
1. Browser Developer Tools öffnen (F12)
2. Application → Local Storage → http://localhost:3000
3. Prüfe `emergent_api_keys` Eintrag
4. Falls leer: Keys erneut in Settings eingeben

## 📊 Erfolgskontrolle

**Chat funktioniert, wenn:**
- ✅ Settings zeigt "X/3 AI Providers Configured" (X > 0)
- ✅ AI Chat zeigt keine rote Warnung
- ✅ Provider-Dropdown zeigt verfügbare Modelle
- ✅ Test-Nachricht erhält AI-Antwort

**Design korrekt, wenn:**
- ✅ Hintergrund ist schwarz
- ✅ Sidebar ist dunkel mit goldenen Akzenten  
- ✅ Buttons sind gold mit schwarzem Text
- ✅ Logo "EN" ist gold
- ✅ Überschriften sind gold

## 🚀 Schnell-Test

```bash
# Alles neu starten
cd /app/emergent-next
pkill -f "python.*main.py" && pkill -f "yarn.*dev"
./start-dev.sh

# Browser öffnen
echo "Öffne: http://localhost:3000"
echo "1. Settings → API-Keys eingeben → Save"  
echo "2. AI Chat → Provider wählen → Test-Nachricht"
```