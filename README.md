# Xionimus AI

Lokale Desktop-KI-Anwendung mit Multi-Modal-Support, RAG-System und Chrome-DB Integration.

## Installation (Windows)

### Voraussetzungen
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- Node.js v18+ ([Download](https://nodejs.org/))

### Installation

```batch
install.bat
```

Warten Sie 5-10 Minuten.

### Starten

```batch
start.bat
```

Öffnen Sie im Browser: http://localhost:3000

## Funktionen

- 🤖 Multi-AI-Provider (OpenAI, Anthropic, Perplexity)
- 📄 PDF & Bild-Verarbeitung
- 🗄️ RAG-System mit ChromaDB
- 💾 Lokale SQLite-Datenbank
- 🎨 Dark/Light Theme
- 🌐 Deutsch/English Interface

## Fehlerbehebung

### "Python nicht gefunden"
Installieren Sie Python und aktivieren Sie "Add Python to PATH"

### "Node.js nicht gefunden"  
Installieren Sie Node.js

### Module fehlen
Führen Sie `install.bat` erneut aus

### Noch Probleme?
1. Löschen Sie `backend\venv` Ordner
2. Führen Sie `install.bat` erneut aus
