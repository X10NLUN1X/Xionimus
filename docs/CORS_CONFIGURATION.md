# 🌐 CORS Configuration Guide

## Overview

Xionimus AI verwendet environment-aware CORS-Konfiguration für sichere Cross-Origin Requests.

## 🔧 Konfiguration

### Development Mode (DEBUG=true)

**Automatisch erlaubt**:
- Alle localhost-Varianten (Port 3000, 3001, 3002, 5173)
- http://localhost, http://127.0.0.1
- WebSocket-kompatibel

**Zusätzliche Origins**:
```bash
# .env
DEBUG=true
CORS_ORIGINS=https://staging.example.com
```

**Verhalten**:
- ✅ Alle localhost + custom origins
- ✅ Wildcard Methods (`*`)
- ✅ Wildcard Headers (`*`)
- ✅ Alle Expose Headers

### Production Mode (DEBUG=false)

**Nur explizite Origins**:
```bash
# .env
DEBUG=false
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Verhalten**:
- ✅ NUR spezifizierte Domains
- ✅ Eingeschränkte Methods (GET, POST, PUT, DELETE, PATCH, OPTIONS)
- ✅ Eingeschränkte Headers (Content-Type, Authorization, etc.)
- ⚠️  Validierung gegen unsichere Patterns

## 🔒 Sicherheits-Features

### Automatische Validierung

**Warnt vor**:
- ❌ Wildcard (`*`) in Production
- ⚠️  localhost/127.0.0.1 in Production
- ⚠️  HTTP (nicht HTTPS) in Production

**Logs**:
```
❌ INSECURE: Wildcard in production CORS origin: *
⚠️  WARNING: Localhost in production CORS: http://localhost:3000
⚠️  WARNING: Non-HTTPS origin in production: http://example.com
```

### Best Practices

#### ✅ DO

```bash
# Production
DEBUG=false
CORS_ORIGINS=https://app.example.com,https://www.example.com

# Staging
DEBUG=false  
CORS_ORIGINS=https://staging.example.com

# Development
DEBUG=true
CORS_ORIGINS=  # localhost auto-enabled
```

#### ❌ DON'T

```bash
# NIEMALS in Production!
CORS_ORIGINS=*

# Vermeiden in Production
CORS_ORIGINS=http://example.com  # Use HTTPS!
CORS_ORIGINS=http://localhost:3000  # Only for dev!
```

## 📊 Environment Matrix

| Environment | DEBUG | CORS_ORIGINS | Erlaubte Origins |
|-------------|-------|--------------|------------------|
| **Local Dev** | true | _(empty)_ | Alle localhost-Varianten |
| **Dev + Custom** | true | `https://dev.com` | localhost + dev.com |
| **Staging** | false | `https://staging.com` | Nur staging.com |
| **Production** | false | `https://app.com,https://www.app.com` | Nur app.com, www.app.com |

## 🧪 Testing

### Manual Testing

```bash
# Development
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     http://localhost:8001/api/v1/health

# Should return:
# Access-Control-Allow-Origin: http://localhost:3000
# Access-Control-Allow-Credentials: true
```

### Automated Tests

```bash
cd /app/backend
pytest tests/test_cors_config.py -v
```

**Coverage**: 15 tests
- Development mode
- Production mode
- Security validation
- Environment switching

## 🔄 Migration from Old Config

### Before (Hardcoded)

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # ... many more
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### After (Environment-aware)

```python
# main.py
from app.core.cors_config import get_cors_middleware_config

cors_config = get_cors_middleware_config()
app.add_middleware(CORSMiddleware, **cors_config)
```

**Benefits**:
- ✅ Environment-aware
- ✅ Security validation
- ✅ Centralized configuration
- ✅ Easy to maintain

## 🐛 Troubleshooting

### CORS Error in Browser

**Symptom**:
```
Access to fetch at 'http://localhost:8001/api/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solutions**:

1. **Check DEBUG mode**:
   ```bash
   # .env
   DEBUG=true  # Should allow localhost
   ```

2. **Add origin explicitly**:
   ```bash
   CORS_ORIGINS=http://localhost:3000
   ```

3. **Check logs**:
   ```bash
   tail -f /var/log/supervisor/backend.out.log | grep CORS
   ```

4. **Restart backend**:
   ```bash
   sudo supervisorctl restart backend
   ```

### Production CORS Issues

1. **Verify configuration**:
   ```bash
   # Check .env
   cat /var/www/xionimus-ai/backend/.env | grep CORS
   
   # Should show:
   DEBUG=false
   CORS_ORIGINS=https://yourdomain.com
   ```

2. **Check startup logs**:
   ```bash
   sudo supervisorctl restart backend
   tail -f /var/log/supervisor/backend.out.log
   
   # Should show:
   # 🔒 CORS: Production mode - 1 origins allowed
   # Allowed origins: https://yourdomain.com
   ```

3. **Test with curl**:
   ```bash
   curl -H "Origin: https://yourdomain.com" \
        -I https://yourdomain.com/api/v1/health
   ```

## 📚 Code Reference

- **Configuration**: `backend/app/core/cors_config.py`
- **Integration**: `backend/main.py`
- **Tests**: `backend/tests/test_cors_config.py`
- **Environment**: `backend/.env.example`

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Production-Ready
