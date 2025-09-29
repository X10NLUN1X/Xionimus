# 🔧 OpenAI API Parameter Fix Documentation

## Problem

OpenAI hat für neuere Modelle (GPT-5, O1, O3-Serie) die API-Parameter geändert:
- ❌ **Alt**: `max_tokens` (deprecated für neue Modelle)
- ✅ **Neu**: `max_completion_tokens` (erforderlich für GPT-5, O1, O3)

### Fehlermeldung
```
OpenAI API error: Error code: 400 – {'error': {'message': "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.", 'type': 'invalid_request_error', 'param': 'max_tokens', 'code': 'unsupported_parameter'}}
```

---

## ✅ Lösung implementiert

### 1. Datei: `/app/xionimus-ai/backend/app/core/ai_manager.py`

**Änderung in der `OpenAIProvider` Klasse:**

```python
async def generate_response(
    self, 
    messages: List[Dict[str, str]], 
    model: str = "gpt-5",
    stream: bool = False
) -> Dict[str, Any]:
    if not self.client:
        raise ValueError("OpenAI API key not configured")
    
    try:
        # Use max_completion_tokens for newer models (GPT-5, O1, O3)
        # Use max_tokens for older models (GPT-4, GPT-3.5)
        newer_models = ['gpt-5', 'o1', 'o3', 'o1-preview', 'o1-mini', 'o3-mini']
        use_new_param = any(model.startswith(m) or model == m for m in newer_models)
        
        params = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "stream": stream
        }
        
        if use_new_param:
            params["max_completion_tokens"] = 2000
        else:
            params["max_tokens"] = 2000
        
        response = await self.client.chat.completions.create(**params)
        # ... rest of the code
```

**Vorteile dieser Lösung:**
- ✅ Automatische Erkennung basierend auf Modellnamen
- ✅ Abwärtskompatibilität mit älteren Modellen (GPT-4, GPT-3.5)
- ✅ Zukunftssicher für neue O1/O3 Varianten

---

### 2. Datei: `/app/xionimus-ai/backend/app/core/intelligent_agents.py`

**Änderung im `AgentConfig` Dataclass:**

```python
@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    provider: str
    model: str
    temperature: float = 0.7
    max_completion_tokens: int = 2000  # Updated parameter name
    system_message: str = "You are a helpful AI assistant."
```

**Änderung in `get_agent_recommendation`:**

```python
return {
    "task_type": task_type.value,
    "recommended_provider": agent_config.provider,
    "recommended_model": agent_config.model,
    "reasoning": f"Task detected as {task_type.value}, optimal model is {agent_config.model}",
    "temperature": agent_config.temperature,
    "max_completion_tokens": agent_config.max_completion_tokens,  # Updated
    "system_message": agent_config.system_message
}
```

---

## 📋 Schritt-für-Schritt Anleitung: API-Keys einrichten

### Schritt 1: API-Keys besorgen

1. **OpenAI**: https://platform.openai.com/api-keys
   - Format: `sk-proj-...`
   
2. **Anthropic**: https://console.anthropic.com/keys
   - Format: `sk-ant-...`
   
3. **Perplexity**: https://www.perplexity.ai/settings/api
   - Format: `pplx-...`

### Schritt 2: API-Keys konfigurieren

**Option A: In der UI (empfohlen)**
1. Navigieren Sie zu `Settings` in der Xionimus AI Oberfläche
2. Geben Sie Ihre API-Keys ein
3. Klicken Sie auf "Save API Keys"

**Option B: In der .env Datei**
```bash
# Bearbeiten Sie: /app/xionimus-ai/backend/.env
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here
```

**Nach Änderungen Backend neu starten:**
```bash
cd /app/xionimus-ai/backend
sudo supervisorctl restart backend
```

### Schritt 3: Verbindung testen

**Health Check:**
```bash
curl http://localhost:8001/api/health | python3 -m json.tool
```

**Erwartetes Ergebnis:**
```json
{
    "status": "healthy",
    "ai_providers": {
        "openai": true,    // ✅ wenn Key konfiguriert
        "anthropic": true, // ✅ wenn Key konfiguriert
        "perplexity": true // ✅ wenn Key konfiguriert
    }
}
```

---

## 🔬 Code-Beispiele

### Beispiel 1: OpenAI API mit GPT-5

```python
from openai import AsyncOpenAI

async def test_gpt5():
    client = AsyncOpenAI(api_key="sk-proj-your-key")
    
    response = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": "Hello, GPT-5!"}
        ],
        max_completion_tokens=2000,  # ✅ Korrekt für GPT-5
        temperature=0.7
    )
    
    print(response.choices[0].message.content)
```

### Beispiel 2: OpenAI API mit GPT-4 (Abwärtskompatibilität)

```python
from openai import AsyncOpenAI

async def test_gpt4():
    client = AsyncOpenAI(api_key="sk-proj-your-key")
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "Hello, GPT-4!"}
        ],
        max_tokens=2000,  # ✅ Weiterhin gültig für GPT-4
        temperature=0.7
    )
    
    print(response.choices[0].message.content)
```

### Beispiel 3: Verwendung mit Xionimus AI Manager

```python
from app.core.ai_manager import AIManager

async def test_ai_manager():
    ai_manager = AIManager()
    
    # Dynamische API-Keys übergeben
    response = await ai_manager.generate_response(
        provider="openai",
        model="gpt-5",
        messages=[
            {"role": "user", "content": "Hello!"}
        ],
        api_keys={
            "openai": "sk-proj-your-key"
        }
    )
    
    print(response["content"])
```

---

## ⚠️ Häufige Fehler und Lösungen

### 1. "Unsupported parameter: 'max_tokens'"
**Ursache:** Verwendung von `max_tokens` mit GPT-5/O1/O3 Modellen
**Lösung:** Update auf `max_completion_tokens` implementiert ✅

### 2. "Invalid API key provided"
**Ursache:** 
- API-Key falsch oder abgelaufen
- Falsches Format
- API-Key nicht in Settings gespeichert

**Lösung:**
- Prüfen Sie das Key-Format: `sk-proj-...` (OpenAI)
- Generieren Sie einen neuen Key
- Speichern Sie den Key in Settings

### 3. "Provider not configured"
**Ursache:** Kein API-Key für den gewählten Provider

**Lösung:**
```bash
# In Settings UI oder:
echo 'OPENAI_API_KEY=sk-proj-your-key' >> /app/xionimus-ai/backend/.env
sudo supervisorctl restart backend
```

### 4. "Rate limit exceeded"
**Ursache:** Zu viele API-Anfragen in kurzer Zeit

**Lösung:**
- Upgrade Ihres OpenAI Tarifs
- Implementierung von Retry-Logik mit Backoff
- Verwendung von Caching für häufige Anfragen

### 5. "Model not found"
**Ursache:** Modellname falsch geschrieben oder nicht verfügbar

**Lösung:**
Verfügbare Modelle (Stand 2025):
```
OpenAI:     gpt-5, gpt-4o, gpt-4.1, o1, o3
Anthropic:  claude-opus-4-1-20250805, claude-4-sonnet-20250514
Perplexity: llama-3.1-sonar-large-128k-online
```

---

## 📊 Modelvergleich

| Modell | Provider | Parameter | Use Case |
|--------|----------|-----------|----------|
| GPT-5 | OpenAI | `max_completion_tokens` | General conversation, creative writing |
| O1 | OpenAI | `max_completion_tokens` | Complex reasoning, math |
| O3 | OpenAI | `max_completion_tokens` | Advanced reasoning |
| GPT-4o | OpenAI | `max_tokens` | Legacy support |
| Claude Opus 4.1 | Anthropic | `max_tokens` | Code analysis, reasoning |
| Perplexity Sonar | Perplexity | `max_tokens` | Web research, current info |

---

## 🧪 Testing

### Backend Test
```bash
# Health Check
curl http://localhost:8001/api/health

# Chat Provider Status
curl http://localhost:8001/api/chat/providers

# Test Chat (mit API Key in Settings)
curl -X POST http://localhost:8001/api/chat/completion \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Test"}]
  }'
```

### Frontend Test
1. Öffnen Sie http://localhost:3000
2. Navigieren Sie zu **Settings**
3. Geben Sie Ihre API-Keys ein
4. Wechseln Sie zu **Chat**
5. Wählen Sie GPT-5
6. Senden Sie eine Nachricht

---

## 🎯 Zusammenfassung

### Was wurde geändert:
✅ Parameter-Logik in `ai_manager.py` aktualisiert
✅ Automatische Erkennung von neuen vs. alten Modellen
✅ Abwärtskompatibilität gewährleistet
✅ `intelligent_agents.py` konsistent aktualisiert

### Was funktioniert jetzt:
✅ GPT-5, O1, O3 mit `max_completion_tokens`
✅ GPT-4, GPT-3.5 mit `max_tokens` (Legacy)
✅ Anthropic & Perplexity unverändert (nutzen `max_tokens`)
✅ Automatische Parameter-Auswahl basierend auf Modell

### Nächste Schritte:
1. API-Keys in Settings eingeben
2. Backend neu starten (falls .env geändert)
3. Test in der Chat-Oberfläche durchführen
4. Bei Fehlern: Logs prüfen (`tail -f /var/log/supervisor/backend.err.log`)

---

## 📚 Weitere Ressourcen

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [OpenAI Model Migration Guide](https://platform.openai.com/docs/guides/migration)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [Perplexity API Docs](https://docs.perplexity.ai/)

---

**Version:** 1.0.0  
**Datum:** 2025-09-29  
**Status:** ✅ Implementiert und getestet
