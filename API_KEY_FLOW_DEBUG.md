# API Key Flow - Debugging Guide

## Problem Fixed
**Issue:** Anthropic provider showing "not configured" even with correct API key  
**Root Cause:** WebSocket handler was not passing `api_keys` parameter to `stream_response()` method

## Solution Applied
✅ Fixed `/app/backend/app/api/chat_stream.py`:
- Removed incorrect `setattr()` approach (lines 147-150)
- Added `api_keys` parameter to `stream_response()` call (line 154)
- Added debug logging to trace API key flow

## API Key Flow (Correct Path)

### 1. Frontend (AppContext.tsx)
```typescript
const [apiKeys, setApiKeys] = useState({
  openai: '',
  anthropic: '',
  perplexity: ''
})

// Sent via WebSocket
ws.send(JSON.stringify({
  type: 'chat',
  provider: 'anthropic',
  model: 'claude-sonnet-4-5-20250929',
  api_keys: apiKeys  // ← Sent here
}))
```

### 2. Backend WebSocket (chat_stream.py)
```python
# Received from frontend
api_keys = message_data.get("api_keys", {})
# Example: {"openai": "", "anthropic": "sk-ant-xxx", "perplexity": ""}

# Passed to AI Manager
async for chunk in ai_manager.stream_response(
    provider=provider,
    model=model,
    messages=conversation_history,
    ultra_thinking=ultra_thinking,
    api_keys=api_keys  # ← FIXED: Now passes api_keys
):
```

### 3. AI Manager (ai_manager.py)
```python
async def stream_response(
    self,
    provider: str,
    model: str,
    messages: List[Dict[str, str]],
    ultra_thinking: bool = False,
    api_keys: Optional[Dict[str, str]] = None  # ← Receives api_keys
):
    # Use dynamic API keys if provided
    if api_keys and api_keys.get(provider):  # ← Checks for provider-specific key
        provider_instance = self._create_dynamic_provider(provider, api_keys[provider])
    elif provider not in self.providers or self.providers[provider] is None:
        raise ValueError(f"Provider {provider} not configured")
    else:
        provider_instance = self.providers[provider]
```

## Testing Steps

### 1. Check Frontend API Keys
1. Open browser DevTools (F12)
2. Go to Application → Local Storage
3. Look for `xionimus_api_keys`
4. Verify your Anthropic key is stored

### 2. Test WebSocket Connection
1. Open browser DevTools → Network → WS (WebSocket)
2. Send a message
3. Click on the WebSocket connection
4. Check the "Messages" tab
5. Verify the sent message includes `api_keys`

Example WebSocket message:
```json
{
  "type": "chat",
  "content": "Hello",
  "provider": "anthropic",
  "model": "claude-sonnet-4-5-20250929",
  "ultra_thinking": false,
  "api_keys": {
    "openai": "",
    "anthropic": "sk-ant-xxxxx",
    "perplexity": ""
  },
  "messages": [...]
}
```

### 3. Check Backend Logs
```bash
tail -f /var/log/supervisor/backend.*.log | grep -E "(WebSocket|anthropic|api_keys)"
```

Look for these debug messages:
```
INFO: 🔍 WebSocket received - Provider: anthropic, Model: claude-sonnet-4-5-20250929
INFO: 🔍 API keys received: ['openai', 'anthropic', 'perplexity']
INFO: 🔍 API key for anthropic: ✅ Present
```

### 4. Verify API Key Format
Your Anthropic API key should:
- Start with `sk-ant-`
- Be approximately 100+ characters long
- Not contain spaces or newlines
- Be active (not revoked)

## Common Issues & Solutions

### Issue 1: "Provider anthropic not configured"
**Cause:** API key not reaching the stream_response method  
**Solution:** ✅ Fixed by passing api_keys parameter

### Issue 2: API Key Empty in WebSocket
**Cause:** Frontend not storing API key  
**Solution:**
1. Go to Settings page
2. Enter API key in "Anthropic API Key" field
3. Click "Save API Keys"
4. Verify in localStorage

### Issue 3: API Key Present But Still Not Working
**Causes:**
1. Invalid API key format
2. Revoked API key
3. Billing issue on Anthropic account
4. API key has trailing/leading whitespace

**Solution:**
1. Verify key at https://console.anthropic.com/
2. Generate new key if needed
3. Make sure to copy without spaces
4. Check Anthropic account billing

## Debug Commands

### Check if API key is in environment
```bash
cd /app/backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -c "from app.core.config import settings; print(f'Anthropic: {bool(settings.ANTHROPIC_API_KEY)}')"
```

### Test Anthropic client directly
```bash
python -c "
import anthropic
client = anthropic.Anthropic(api_key='sk-ant-YOUR_KEY_HERE')
message = client.messages.create(
    model='claude-sonnet-4-5-20250929',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print(message.content)
"
```

### Monitor WebSocket connections
```bash
# Check active WebSocket connections
curl http://localhost:8001/api/stream/status
```

## Files Modified
- ✅ `/app/backend/app/api/chat_stream.py` - Fixed API key passing
- ✅ Added debug logging for API key flow

## Expected Behavior After Fix
1. User enters API key in Settings
2. Frontend stores in localStorage
3. Frontend sends via WebSocket in every message
4. Backend receives and passes to AI Manager
5. AI Manager creates dynamic provider with key
6. Anthropic streaming works correctly

## Verify Fix is Working
After applying the fix, you should see in backend logs:
```
INFO: 🔍 WebSocket received - Provider: anthropic, Model: claude-sonnet-4-5-20250929
INFO: 🔍 API keys received: ['openai', 'anthropic', 'perplexity']
INFO: 🔍 API key for anthropic: ✅ Present
```

And NO MORE:
```
WARNING: ⚠️ Configuration error: Provider anthropic not configured
```
