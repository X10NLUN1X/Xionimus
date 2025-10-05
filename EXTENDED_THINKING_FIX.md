# Extended Thinking (Ultra Thinking) Fix

## Problem
Erweitertes Denken (Ultra Thinking) zeigte folgenden Fehler:
```
ERROR: `max_tokens` must be greater than `thinking.budget_tokens`
```

## Root Cause
Im Streaming-Code wurde `max_tokens` fest auf 4096 gesetzt, aber `thinking.budget_tokens` war 10000:
```python
stream_params = {
    "max_tokens": 4096,  # ❌ Zu klein!
    "messages": messages
}

if ultra_thinking:
    stream_params["thinking"] = {
        "budget_tokens": 10000  # ❌ Größer als max_tokens!
    }
```

**Anthropic Anforderung:** `max_tokens > thinking.budget_tokens`

## Solution

**Vorher (Falsch):**
```python
stream_params = {
    "max_tokens": 4096,  # Immer gleich
    "messages": messages
}
if ultra_thinking:
    stream_params["thinking"] = {"budget_tokens": 10000}  # 10000 > 4096 → ERROR
```

**Nachher (Korrekt):**
```python
if ultra_thinking:
    thinking_budget = 5000
    stream_params["thinking"] = {
        "type": "enabled",
        "budget_tokens": thinking_budget  # 5000
    }
    stream_params["max_tokens"] = thinking_budget + 3000  # 8000 > 5000 ✅
    stream_params["temperature"] = 1.0  # Pflicht für Extended Thinking
else:
    stream_params["max_tokens"] = 4096
    stream_params["temperature"] = 0.7
```

## Anthropic Extended Thinking Anforderungen

1. **max_tokens > budget_tokens**
   - Beispiel: budget_tokens=5000 → max_tokens=8000 ✅
   
2. **temperature = 1.0 (Pflicht)**
   - Bei Extended Thinking muss temperature genau 1.0 sein
   - Andere Werte werden von der API abgelehnt

3. **Token-Verteilung**
   - `budget_tokens`: Reserviert für den Denkprozess (z.B. 5000)
   - `max_tokens`: Gesamt-Tokens für Denken + Antwort (z.B. 8000)
   - Effektive Ausgabe: max_tokens - budget_tokens = 3000 Tokens

## Vergleich: Standard vs. Extended Thinking

### Standard Mode (ultra_thinking = False)
```python
max_tokens: 4096
temperature: 0.7
thinking: nicht vorhanden
```

### Extended Thinking Mode (ultra_thinking = True)
```python
thinking.budget_tokens: 5000  # Für Denkprozess
max_tokens: 8000              # Gesamt (5000 + 3000)
temperature: 1.0              # Pflicht bei Extended Thinking
```

## Implementierung

### Streaming (Jetzt behoben)
`/app/backend/app/core/ai_manager.py` Zeilen 552-583

### Non-Streaming (War bereits korrekt)
`/app/backend/app/core/ai_manager.py` Zeilen 206-227

Beide verwenden jetzt die gleiche Logik:
- thinking_budget = 5000
- max_tokens = thinking_budget + 3000 = 8000
- temperature = 1.0

## Testing

### Standard Streaming (ultra_thinking = False)
```
✅ max_tokens: 4096
✅ temperature: 0.7
✅ Kein thinking parameter
```

### Extended Thinking Streaming (ultra_thinking = True)
```
✅ thinking.budget_tokens: 5000
✅ max_tokens: 8000 (> 5000)
✅ temperature: 1.0
```

## Debug Logs

Wenn Extended Thinking aktiviert:
```
INFO: 🧠 Extended Thinking streaming: budget=5000, max_tokens=8000, temperature=1.0
```

Wenn Standard Mode:
```
INFO: 💬 Standard streaming: max_tokens=4096, temperature=0.7
```

## Dokumentation

Anthropic Docs:
https://docs.claude.com/en/docs/build-with-claude/extended-thinking#max-tokens-and-context-window-size

## User Action
1. **Browser aktualisieren** (Ctrl+Shift+R)
2. **Erweitertes Denken testen**
3. Sollte jetzt perfekt funktionieren!

## Zusammenfassung
Das Problem war eine falsche Token-Konfiguration beim Streaming mit Extended Thinking. Jetzt synchron mit Non-Streaming Implementierung, die bereits korrekt war.
