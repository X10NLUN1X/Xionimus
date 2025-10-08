# 📊 Generated Code Project

Ein Python-basiertes Projekt zur automatischen Code-Generierung und -Verarbeitung. Dieses Projekt bietet eine flexible Infrastruktur für die Erstellung, Verwaltung und Ausführung von generiertem Code.

## ✨ Hauptfeatures

- 🔄 Automatische Code-Generierung und -Verwaltung
- 📂 Strukturierte Organisation generierter Dateien
- 🐍 Python-basierte Implementierung für maximale Flexibilität
- 🛠️ Einfache Integration in bestehende Workflows
- 📝 Saubere Projektverwaltung und Dokumentation

## 🚀 Quick Start

```bash
# Repository klonen
git clone <repository-url>
cd generated-code-project

# Virtuelle Umgebung erstellen
python -m venv venv
source venv/bin/activate  # Auf Windows: venv\Scripts\activate

# Generierte Dateien ausführen
python generated/code_block_1.py
```

## 📦 Installation

### Prerequisites

- Python 3.8 oder höher
- pip (Python Package Manager)
- Git

### Schritt-für-Schritt Anleitung

1. **Repository klonen:**
   ```bash
   git clone <repository-url>
   cd generated-code-project
   ```

2. **Virtuelle Umgebung einrichten:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oder
   venv\Scripts\activate  # Windows
   ```

3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

### Environment Setup

Erstellen Sie eine `.env` Datei im Projekt-Root (optional):

```env
# Projekt-Konfiguration
PROJECT_NAME=generated-code-project
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 🔧 Konfiguration

### Environment Variables

| Variable | Beschreibung | Standard | Erforderlich |
|----------|--------------|----------|--------------|
| `PROJECT_NAME` | Name des Projekts | generated-code-project | Nein |
| `ENVIRONMENT` | Ausführungsumgebung | development | Nein |
| `LOG_LEVEL` | Logging-Level | INFO | Nein |
| `OUTPUT_DIR` | Ausgabeverzeichnis | ./generated | Nein |

### Config-Dateien

Erstellen Sie eine `config.json` für erweiterte Konfiguration:

```json
{
  "generator": {
    "output_directory": "generated",
    "file_prefix": "code_block_",
    "default_extension": ".py"
  },
  "execution": {
    "auto_run": false,
    "timeout": 30
  }
}
```

## 💻 Verwendung

### Grundlegende Verwendung

```python
# Generierte Code-Datei ausführen
python generated/code_block_1.py
```

### Programmatische Verwendung

```python
# Beispiel: Code-Generator verwenden
from generator import CodeGenerator

# Generator initialisieren
generator = CodeGenerator(output_dir="generated")

# Code generieren
code = """
def hello_world():
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
"""

# Code-Block speichern
generator.save_code_block(code, block_id=1)

# Code ausführen
generator.execute_code_block(block_id=1)
```

### Typische Use-Cases

**1. Batch-Verarbeitung mehrerer Code-Blöcke:**

```python
from pathlib import Path

generated_dir = Path("generated")
for code_file in generated_dir.glob("*.py"):
    print(f"Executing {code_file.name}...")
    exec(open(code_file).read())
```

**2. Code-Validierung vor Ausführung:**

```python
import ast

def validate_code(filepath):
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True
    except SyntaxError:
        return False

if validate_code("generated/code_block_1.py"):
    exec(open("generated/code_block_1.py").read())
```

## 📁 Projekt-Struktur

```
generated-code-project/
│
├── generated/              # Generierte Code-Dateien
│   └── code_block_1.py    # Beispiel-Code-Block
│
├── src/                    # Quellcode (optional)
│   ├── __init__.py
│   ├── generator.py       # Code-Generator-Logik
│   └── executor.py        # Code-Ausführungs-Logik
│
├── tests/                  # Test-Dateien
│   ├── __init__.py
│   └── test_generator.py
│
├── .env                    # Environment Variables (nicht versioniert)
├── .gitignore             # Git-Ignore-Regeln
├── config.json            # Projekt-Konfiguration
├── requirements.txt       # Python-Abhängigkeiten
└── README.md              # Projekt-Dokumentation
```

### Wichtige Dateien erklärt

- **`generated/`**: Verzeichnis für alle automatisch generierten Code-Dateien
- **`code_block_1.py`**: Erste generierte Code-Datei, enthält ausführbaren Python-Code
- **`requirements.txt`**: Liste aller Python-Pakete und deren Versionen
- **`config.json`**: Zentrale Konfigurationsdatei für Generator-Einstellungen

## 🧪 Testing

### Tests ausführen

```bash
# Alle Tests ausführen
python -m pytest

# Tests mit Coverage-Report
python -m pytest --cov=src --cov-report=html

# Spezifische Test-Datei ausführen
python -m pytest tests/test_generator.py -v
```

### Test-Coverage

```bash
# Coverage-Report generieren
coverage run -m pytest
coverage report
coverage html  # Erstellt HTML-Report in htmlcov/
```

### Beispiel-Test

```python
# tests/test_generator.py
import pytest
from src.generator import CodeGenerator

def test_code_generation():
    generator = CodeGenerator()
    code = "print('test')"
    result = generator.save_code_block(code, block_id=999)
    assert result is True
    
def test_code_execution():
    generator = CodeGenerator()
    output = generator.execute_code_block(block_id=1)
    assert output is not None
```

## 🚀 Deployment

### Lokale Entwicklung

```bash
# Entwicklungsserver starten
python -m src.main

# Mit Hot-Reload (falls unterstützt)
python -m src.main --reload
```

### Produktions-Build

```bash
# Abhängigkeiten einfrieren
pip freeze > requirements.txt

# Projekt paketieren
python setup.py sdist bdist_wheel

# Mit Docker deployen
docker build -t generated-code-project .
docker run -p 8000:8000 generated-code-project
```

### Docker-Setup (optional)

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "src.main"]
```

## 📝 API-Dokumentation

### Code-Generator API

#### Generate Code Block

```python
generator.save_code_block(code: str, block_id: int) -> bool
```

**Parameter:**
- `code` (str): Python