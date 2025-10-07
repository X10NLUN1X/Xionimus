# 🔄 API Migration Guide - v1

## 📋 Übersicht

Xionimus AI hat API-Versionierung eingeführt. Alle Endpunkte sind jetzt unter `/api/v1/*` verfügbar. Die alten `/api/*` Endpunkte (ohne Version) funktionieren weiterhin, sind aber als **deprecated** markiert.

**Timeline**:
- **Ankündigung**: 6. Januar 2025
- **Sunset Date**: 31. Dezember 2025
- **Migration Window**: 12 Monate

---

## 🎯 Warum Versionierung?

✅ **Zukunftssicher**: Breaking Changes können sauber in v2, v3, etc. eingeführt werden  
✅ **Klarheit**: Explizite Version macht API-Kontrakt klar  
✅ **Graduelle Migration**: Beide Versionen laufen parallel  
✅ **Industriestandard**: Folgt Best Practices (Stripe, GitHub, Twitter APIs)

---

## 🔀 Was ändert sich?

### URL-Muster

| Alt (Deprecated) | Neu (Empfohlen) |
|------------------|------------------|
| `/api/auth/login` | `/api/v1/auth/login` |
| `/api/chat` | `/api/v1/chat` |
| `/api/sessions` | `/api/v1/sessions` |
| `/api/files/upload` | `/api/v1/files/upload` |
| `/api/github/connect` | `/api/v1/github/connect` |

**Regel**: Füge `/v1` nach `/api` ein

---

## 🚀 Migrations-Schritte

### Schritt 1: Audit

Finde alle API-Calls in deinem Code:

```bash
# Backend/Python
grep -r "http://.*:8001/api/" .
grep -r "localhost:8001/api/" .

# Frontend/JavaScript
grep -r "'/api/" src/
grep -r "\"/api/" src/
grep -r "REACT_APP_API_URL" .
```

### Schritt 2: Update Base URL

#### React / Frontend

**Datei**: `.env` oder `.env.production`

```diff
- REACT_APP_API_URL=http://localhost:8001/api
+ REACT_APP_API_URL=http://localhost:8001/api/v1

- VITE_API_URL=http://localhost:8001/api
+ VITE_API_URL=http://localhost:8001/api/v1
```

#### JavaScript/TypeScript Config

```javascript
// config.js / constants.js
const API_CONFIG = {
-  baseURL: '/api',
+  baseURL: '/api/v1',
  timeout: 30000,
};
```

#### Axios Instance

```javascript
// api.js
import axios from 'axios';

const api = axios.create({
-  baseURL: process.env.REACT_APP_API_URL || '/api',
+  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
});
```

#### Fetch Calls

```javascript
// Vorher
fetch('/api/auth/login', { ... })
fetch(`${API_BASE}/chat`, { ... })

// Nachher
fetch('/api/v1/auth/login', { ... })
fetch(`${API_BASE}/chat`, { ... })  // API_BASE ist jetzt /api/v1
```

### Schritt 3: Python Backend/Scripts

```python
# Vorher
BASE_URL = "http://localhost:8001/api"
response = requests.post(f"{BASE_URL}/auth/login", ...)

# Nachher
BASE_URL = "http://localhost:8001/api/v1"
response = requests.post(f"{BASE_URL}/auth/login", ...)
```

### Schritt 4: Testing

```bash
# Test v1 Endpoints
curl http://localhost:8001/api/v1/version

# Vergleiche Response Headers
curl -I http://localhost:8001/api/v1/auth/login
curl -I http://localhost:8001/api/auth/login  # Deprecated Headers
```

### Schritt 5: Deployment

1. **Development**: Update und teste lokal
2. **Staging**: Deploy zu Staging, E2E Tests
3. **Production**: Rolling Update
4. **Monitor**: Checke Logs für Legacy-Nutzung

---

## 🔍 Wie erkenne ich deprecated Endpoints?

### Response Headers (Legacy Endpoints)

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sun, 31 Dec 2025 00:00:00 GMT
Link: </api/v1/auth/login>; rel="successor-version"
Warning: 299 - "This API endpoint is deprecated. Please migrate to /api/v1/* before 2025-12-31. See documentation: /docs"
```

### Response Headers (V1 Endpoints)

```http
HTTP/1.1 200 OK
API-Version: v1
```

---

## 📊 Migration Tracking

### Check Version Info

```bash
# Get current version info
curl http://localhost:8001/api/v1/version

# Response:
{
  "current_version": "v1",
  "deprecated_versions": ["unversioned"],
  "sunset_date": "2025-12-31",
  "migration_guide_url": "/docs#/v1"
}
```

### Get Migration Guide

```bash
curl http://localhost:8001/api/v1/migration-guide
```

Vollständiger Guide mit:
- Timeline
- Code-Beispiele (JS, Python, React)
- FAQ
- Migration Steps

---

## 💡 Best Practices

### 1. Environment Variables

**✅ DO**:
```javascript
const API_BASE = process.env.REACT_APP_API_URL || '/api/v1';
```

**❌ DON'T**:
```javascript
const API_BASE = '/api';  // Hardcoded, schwer zu ändern
```

### 2. Centralized API Config

**✅ DO**:
```javascript
// api/config.js
export const API_CONFIG = {
  baseURL: '/api/v1',
  endpoints: {
    auth: '/auth',
    chat: '/chat',
    // ...
  }
};

// In components:
fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.auth}/login`)
```

### 3. API Client Library

**✅ DO**:
```javascript
// api/client.js
class APIClient {
  constructor() {
    this.baseURL = '/api/v1';
  }
  
  async login(credentials) {
    return fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }
}

export default new APIClient();
```

### 4. Versioning in Client

```javascript
// Support multiple versions during transition
const API_VERSION = process.env.API_VERSION || 'v1';
const API_BASE = `/api/${API_VERSION}`;
```

---

## ❓ FAQ

### Muss ich sofort migrieren?

**Nein**. Legacy Endpoints funktionieren bis **31. Dezember 2025**. Du hast 12 Monate Zeit für die Migration.

### Gibt es Breaking Changes in v1?

**Nein**. v1 ist funktional identisch zu den Legacy-Endpoints. Nur das URL-Muster hat sich geändert.

### Kann ich beide Versionen parallel nutzen?

**Ja**! Während der Migration kannst du beide Versionen nutzen. Ideal für schrittweise Migration.

### Was passiert nach dem Sunset Date?

Legacy `/api/*` Endpoints werden entfernt und geben `410 Gone` zurück. Migriere vorher!

### Wie teste ich ob meine App v1 nutzt?

```bash
# Checke Browser Network Tab
# Oder Backend Logs nach "unversioned API usage"

# Oder curl mit Header-Check
curl -I https://your-app.com/api/auth/login
# Wenn "Deprecation: true" → noch legacy
# Wenn "API-Version: v1" → bereits migriert ✅
```

### Wie migriere ich WebSockets?

```javascript
// Vorher
const ws = new WebSocket('ws://localhost:8001/api/chat/stream');

// Nachher
const ws = new WebSocket('ws://localhost:8001/api/v1/chat/stream');
```

### Werden Query Parameters beeinflusst?

**Nein**. Query Parameters bleiben identisch:

```
/api/sessions?limit=10 → /api/v1/sessions?limit=10
```

### Was ist mit Request/Response Bodies?

**Keine Änderung**. Alle Request/Response Schemas bleiben identisch.

---

## 🔧 Troubleshooting

### Problem: 404 Not Found nach Migration

**Lösung**: 
- Prüfe URL genau: `/api/v1/` (mit trailing slash falls nötig)
- Checke Typos: `v1` nicht `V1`
- Prüfe ob Endpoint tatsächlich existiert: `/api/v1/version`

### Problem: CORS Errors

**Lösung**:
- Backend CORS Settings unterstützen beide Versionen
- Falls eigenes Proxy: Update Proxy-Config für `/api/v1/*`

### Problem: Tests schlagen fehl

**Lösung**:
```javascript
// Test Config aktualisieren
beforeEach(() => {
  mock.onAny(/api\/v1/).reply(200, { ... });
});
```

---

## 📚 Weitere Ressourcen

- **OpenAPI Docs**: http://localhost:8001/docs
- **Version Info Endpoint**: `/api/v1/version`
- **Migration Guide API**: `/api/v1/migration-guide`
- **Source Code**: `backend/app/core/versioning.py`

---

## ✅ Migration Checklist

- [ ] Audit: Alle `/api/*` Calls identifiziert
- [ ] Environment Variables aktualisiert
- [ ] API Config/Constants aktualisiert
- [ ] Code-Änderungen committed
- [ ] Lokal getestet (alle Features funktionieren)
- [ ] Staging deployed und getestet
- [ ] Production deployed
- [ ] Monitoring: Keine Legacy-Warnings in Logs
- [ ] Dokumentation aktualisiert
- [ ] Team informiert

---

**Version**: 1.0  
**Datum**: 6. Januar 2025  
**Status**: Active Migration Period  
**Support**: Siehe README.md
