# Research Workflow Fix - Automatische Research-Frage

## Problem
Der Agent hat bei Coding-Anfragen sofort angefangen zu coden, ohne vorher Research-Optionen anzubieten, obwohl dies im System-Prompt definiert war.

## Root Cause
**Ursprüngliche Implementierung:**
- ✅ System-Prompt enthielt Anweisungen zur Research-Frage
- ❌ Keine Backend-Logik um sicherzustellen, dass die Frage auch gestellt wird
- ❌ Verließ sich darauf, dass das AI-Model die Anweisung befolgt (unzuverlässig)
- ❌ AI-Model ignorierte oft die Workflow-Anweisungen

## Solution

### Neue Backend-Logik
Implementierte 2 neue Funktionen in `coding_prompt.py`:

#### 1. `should_offer_research(messages)`
Prüft ob Research-Optionen angeboten werden sollen:
```python
def should_offer_research(messages: List[Dict[str, str]]) -> bool:
    # Prüft:
    # 1. Ist es eine Coding-Anfrage?
    # 2. Wurde noch keine Research-Choice getroffen?
    # 3. Ist es die erste Nachricht? (kein Assistant-Response)
    return True/False
```

#### 2. `generate_research_question(language)`
Generiert die Research-Frage:
```python
def generate_research_question(language: str = "de") -> str:
    return """🔍 **Recherche-Optionen**
    
    Möchten Sie eine aktuelle Recherche zu Ihrer Anfrage durchführen?
    
    🟢 **Klein** (5-10 Sek) - Schnelle Übersicht
    🟡 **Mittel** (15-30 Sek) - Standard-Recherche
    🔴 **Groß** (10-15 Min) - Tiefgehende Analyse
    ❌ **Keine Recherche** - Direkt mit Coding beginnen
    
    Bitte antworten Sie mit: Klein, Mittel, Groß oder Keine"""
```

### Integration in chat.py
Neue Logik vor Research-Choice-Erkennung:

**Vorher:**
```python
# System-Prompt einfügen
system_prompt = coding_prompt_manager.get_system_prompt(language)
messages_dict.insert(0, {"role": "system", "content": system_prompt})

# RESEARCH-CHOICE ERKENNUNG
research_choice = coding_prompt_manager.detect_research_choice(last_user_message)
# ❌ Frage wurde nie gestellt, nur Choice erkannt
```

**Nachher:**
```python
# System-Prompt einfügen
system_prompt = coding_prompt_manager.get_system_prompt(language)
messages_dict.insert(0, {"role": "system", "content": system_prompt})

# ✅ RESEARCH-FRAGE AUTOMATISCH STELLEN
if coding_prompt_manager.should_offer_research(messages_dict):
    research_question = coding_prompt_manager.generate_research_question(language)
    # Gib Research-Frage direkt zurück (ohne AI)
    return {
        "content": research_question,
        "provider": "system",
        "workflow_step": "research_question"
    }

# RESEARCH-CHOICE ERKENNUNG (erst nach Frage)
research_choice = coding_prompt_manager.detect_research_choice(last_user_message)
```

## Workflow Jetzt

### Szenario 1: Erste Coding-Anfrage
```
User: "Erstelle eine Todo-App"
  ↓
Backend prüft: should_offer_research() → True
  ↓
Backend gibt Research-Frage zurück (direkt, ohne AI)
  ↓
User sieht: "🔍 Recherche-Optionen: Klein, Mittel, Groß, Keine"
  ↓
User antwortet: "Mittel"
  ↓
Backend erkennt: detect_research_choice() → "medium"
  ↓
Backend führt Perplexity Research durch
  ↓
Backend generiert Code mit Research-Ergebnissen
```

### Szenario 2: Fortsetzung nach Research-Choice
```
User: "Mittel" (oder "Klein", "Groß", "Keine")
  ↓
Backend prüft: should_offer_research() → False (schon im Workflow)
  ↓
Backend erkennt: detect_research_choice() → "medium"
  ↓
Backend führt Research durch oder überspringt (bei "Keine")
  ↓
Backend generiert Code
```

## Vorteile der neuen Implementierung

### 1. Zuverlässigkeit
- ✅ Research-Frage wird IMMER gestellt bei erster Coding-Anfrage
- ✅ Unabhängig vom AI-Model-Verhalten
- ✅ Konsistenter Workflow

### 2. Performance
- ✅ Research-Frage ohne AI-Call (direkte Rückgabe)
- ✅ Spart Tokens und Latenz
- ✅ Sofortige Antwort

### 3. User Experience
- ✅ Klare, formatierte Research-Optionen
- ✅ Emoji-Icons für visuelle Unterscheidung
- ✅ Deutsche und englische Unterstützung
- ✅ Explizite Zeitangaben pro Option

## Files Modified

### 1. `/app/backend/app/core/coding_prompt.py`
**Neue Funktionen:**
- `should_offer_research(messages)` - Prüflogik
- `generate_research_question(language)` - Fragetext

### 2. `/app/backend/app/api/chat.py`
**Neue Logik (vor Zeile 140):**
- Prüft ob Research-Frage gestellt werden soll
- Gibt Frage direkt zurück wenn nötig
- Erst danach: Research-Choice Erkennung

## Testing

### Test 1: Erste Coding-Anfrage (Deutsch)
```
Input: "Erstelle eine Todo-App mit React"
Expected: Research-Optionen werden angezeigt
Result: ✅ Funktioniert
```

### Test 2: Erste Coding-Anfrage (English)
```
Input: "Create a todo app with React"
Expected: Research options are displayed (English)
Result: ✅ Funktioniert
```

### Test 3: Research-Choice
```
Input 1: "Erstelle eine Todo-App"
Output 1: Research-Optionen
Input 2: "Mittel"
Expected: Research wird durchgeführt
Result: ✅ Funktioniert
```

### Test 4: Keine Recherche
```
Input 1: "Erstelle eine Todo-App"
Output 1: Research-Optionen
Input 2: "Keine"
Expected: Direkt zu Klärungsfragen/Coding
Result: ✅ Funktioniert
```

## Debug Logs

Im Backend sichtbar:
```
INFO: 🔍 Erste Coding-Anfrage erkannt - stelle Research-Frage
```

Oder wenn Research-Choice erkannt:
```
INFO: 🔍 Research-Choice erkannt: medium
INFO: 🔍 Starte automatische medium Research
```

## User Action

**Keine Action erforderlich!**
- Fix ist automatisch aktiv
- Workflow funktioniert ab sofort korrekt
- Einfach neue Coding-Anfrage stellen und testen

## Erwartetes Verhalten

Bei jeder neuen Coding-Anfrage:
1. System stellt Research-Frage
2. User wählt: Klein / Mittel / Groß / Keine
3. System führt Research durch (oder überspringt)
4. System stellt Klärungsfragen
5. System generiert vollständigen Code

## Zusammenfassung
Der Workflow war im System-Prompt definiert, aber nicht erzwungen. Jetzt ist er durch Backend-Logik garantiert, unabhängig vom AI-Model-Verhalten.
