# Security Utils Usage Guide

## API Key Masking

Die `security_utils.py` bietet Funktionen zum sicheren Loggen von API Keys:

### Usage Examples

```python
from app.core.security_utils import mask_api_key, mask_sensitive_data, sanitize_log_message

# 1. Einzelnen API Key maskieren
api_key = "sk-proj-abc123def456xyz789"
logger.info(f"Using API key: {mask_api_key(api_key)}")
# Output: Using API key: ********...z789

# 2. Dictionary mit sensiblen Daten maskieren
config = {
    "api_key": "sk-proj-secret123",
    "username": "john",
    "password": "mypassword"
}
logger.info(f"Config: {mask_sensitive_data(config)}")
# Output: {'api_key': '********...t123', 'username': 'john', 'password': '****'}

# 3. Log Message automatisch sanitizen
message = "Error with key sk-proj-abc123: Connection failed"
logger.error(sanitize_log_message(message))
# Output: Error with key ********[REDACTED]: Connection failed
```

### Automatische Integration

Um alle Logs automatisch zu schützen, kann ein Custom LogHandler erstellt werden:

```python
import logging
from app.core.security_utils import sanitize_log_message

class SecureLogHandler(logging.StreamHandler):
    def emit(self, record):
        record.msg = sanitize_log_message(str(record.msg))
        super().emit(record)

# Setup
handler = SecureLogHandler()
logging.root.addHandler(handler)
```

### Best Practices

1. ✅ **Immer maskieren** wenn API Keys geloggt werden
2. ✅ **Regex-Sanitization** für freien Text verwenden
3. ✅ **Dict-Maskierung** für strukturierte Daten verwenden
4. ❌ **Nie** rohe API Keys loggen, auch nicht in Debug-Mode

### Wo zu verwenden

- API Key Validierung
- Request/Response Logging
- Error Messages mit Keys
- Configuration Dumps
- Webhook Payloads
