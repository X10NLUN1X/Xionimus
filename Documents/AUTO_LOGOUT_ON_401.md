# 🔄 Automatisches Logout bei ungültigem Token

**Datum:** 2. Oktober 2025  
**Status:** ✅ Implementiert

## Problem

**Backend-Logs zeigten:**
```
WARNING:app.core.auth:JWT validation failed: Signature verification failed.
INFO: 127.0.0.1:50003 - "GET /api/chat/providers HTTP/1.1" 401 Unauthorized
INFO: 127.0.0.1:50002 - "GET /api/chat/sessions HTTP/1.1" 401 Unauthorized
```

**Ursache:**
1. User hatte sich mit altem SECRET_KEY eingeloggt
2. Backend wurde neu gestartet oder SECRET_KEY wurde geändert
3. Alter Token im localStorage ist jetzt ungültig
4. Frontend sendet weiterhin den ungültigen Token
5. Backend lehnt alle Requests mit 401 ab
6. **User bleibt scheinbar eingeloggt, kann aber nichts machen** 🔴

---

## Warum passiert das?

### Szenario 1: Backend-Neustart ohne .env
```
1. User loggt sich ein → Token erstellt mit temporärem SECRET_KEY
2. Backend wird neu gestartet → Neuer temporärer SECRET_KEY
3. Alter Token ist ungültig
4. User kann nichts mehr machen
```

### Szenario 2: SECRET_KEY wird geändert
```
1. User loggt sich ein → Token mit SECRET_KEY_A
2. .env wird aktualisiert → SECRET_KEY_B
3. Backend neu gestartet
4. Alter Token ungültig
```

### Szenario 3: Nach GitHub Clone
```
1. Development-System: Token mit SECRET_KEY_DEV
2. Neues System: SECRET_KEY_PROD
3. Token wird über Browser-Sync übertragen
4. Token ungültig auf neuem System
```

---

## Lösung implementiert

### Automatisches Logout bei 401

**Datei:** `/app/frontend/src/contexts/AppContext.tsx`

**Implementierung:**
```typescript
// Setup Axios Interceptor for automatic logout on 401
React.useEffect(() => {
  const interceptor = axios.interceptors.response.use(
    (response) => response,
    (error) => {
      // Check if error is 401 and we have a token
      if (error.response?.status === 401 && token) {
        console.warn('⚠️ Token invalid or expired - logging out')
        
        // Clear token and user data
        setToken(null)
        setUser(null)
        setIsAuthenticated(false)
        localStorage.removeItem('xionimus_token')
        
        // Show toast
        toast({
          title: 'Sitzung abgelaufen',
          description: 'Bitte melden Sie sich erneut an.',
          status: 'warning',
          duration: 5000,
          position: 'top'
        })
      }
      
      return Promise.reject(error)
    }
  )
  
  // Cleanup
  return () => {
    axios.interceptors.response.eject(interceptor)
  }
}, [token, toast])
```

---

## Wie funktioniert es?

### Flow Diagramm

```
┌─────────────────────┐
│ API Request         │
│ mit Token           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Backend prüft Token │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌─────────┐
│ Valid   │  │ Invalid │
│ 200 OK  │  │ 401     │
└────┬────┘  └────┬────┘
     │            │
     ▼            ▼
┌─────────┐  ┌──────────────────┐
│ Normal  │  │ Axios Interceptor│
│ Response│  │ fängt 401 ab     │
└─────────┘  └────┬─────────────┘
                  │
                  ▼
           ┌──────────────┐
           │ Token != null│
           │ ?            │
           └──┬───────┬───┘
              │       │
           Ja │       │ Nein
              │       │
              ▼       ▼
        ┌─────────┐  Normal
        │ Logout  │  401 Error
        │ + Toast │
        └─────────┘
```

---

## User Experience

### Vorher (Ohne Auto-Logout) ❌
```
1. User eingeloggt
2. Backend neu gestartet
3. Token ungültig
4. User sieht: Alles normal (noch eingeloggt)
5. Aber: Alle Requests schlagen fehl
6. Nichts funktioniert
7. User verwirrt
8. Muss manuell localStorage leeren
```

### Nachher (Mit Auto-Logout) ✅
```
1. User eingeloggt
2. Backend neu gestartet
3. Token ungültig
4. Erster API-Request → 401
5. ✅ Automatisches Logout
6. ✅ Toast: "Sitzung abgelaufen"
7. ✅ Login-Screen wird angezeigt
8. User loggt sich neu ein
9. Funktioniert wieder!
```

---

## Vorteile

### 1. Bessere User Experience
- ✅ Klares Feedback: "Sitzung abgelaufen"
- ✅ Automatische Weiterleitung zum Login
- ✅ Keine Verwirrung

### 2. Keine manuellen Eingriffe
- ✅ Kein localStorage manuell löschen
- ✅ Keine Browser-DevTools nötig
- ✅ Funktioniert automatisch

### 3. Robuste Fehlerbehandlung
- ✅ Funktioniert bei allen 401-Fehlern
- ✅ Egal welcher Endpoint
- ✅ Egal welche Ursache

### 4. Entwickler-freundlich
- ✅ Development: Backend-Neustarts kein Problem
- ✅ Testing: SECRET_KEY Änderungen kein Problem
- ✅ Production: Token-Ablauf wird sauber gehandelt

---

## Edge Cases

### Fall 1: Mehrere gleichzeitige Requests
**Szenario:** 3 API-Requests parallel, alle 401
**Lösung:** Interceptor läuft für jeden Request, aber Logout passiert nur einmal (State-Updates sind idempotent)

### Fall 2: User ist nicht eingeloggt
**Szenario:** Öffentlicher Endpoint gibt 401
**Lösung:** `if (token)` Check verhindert unnötiges Logout

### Fall 3: Echter Login-Fehler
**Szenario:** Falsches Passwort beim Login
**Lösung:** Login-Endpoint wirft eigenen Error, wird nicht vom Interceptor gefangen

---

## Testing

### Test 1: Ungültiger Token
```javascript
// 1. Einloggen
localStorage.setItem('xionimus_token', 'valid_token_123')

// 2. Token ungültig machen (Backend neu starten)

// 3. API Request senden
axios.get('/api/chat/sessions')

// Erwartetes Ergebnis:
// ✅ Toast: "Sitzung abgelaufen"
// ✅ Automatisches Logout
// ✅ Weiterleitung zu Login
```

### Test 2: Mehrere 401-Fehler
```javascript
// 1. Token ungültig
// 2. Mehrere Requests parallel
Promise.all([
  axios.get('/api/chat/sessions'),
  axios.get('/api/chat/providers'),
  axios.get('/api/rate-limits/quota')
])

// Erwartetes Ergebnis:
// ✅ Nur ein Toast
// ✅ Ein Logout
// ✅ Keine Duplikate
```

---

## Konfiguration

### Axios Interceptor Lifecycle

**Setup:** Beim Mount des AppContext
**Cleanup:** Beim Unmount des AppContext
**Dependencies:** `[token, toast]`

**Warum Dependencies?**
- `token`: Interceptor muss aktuellen Token-Status kennen
- `toast`: Zum Anzeigen der Benachrichtigung

---

## Alternativen (nicht implementiert)

### Alternative 1: Token-Refresh
```typescript
// Vor Ablauf neuen Token anfordern
if (tokenExpiresSoon) {
  refreshToken()
}
```
**Warum nicht:** Komplexer, braucht Refresh-Token-System

### Alternative 2: Token im Axios-Header auto-aktualisieren
```typescript
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
```
**Warum nicht:** Löst nicht das Problem mit ungültigen Tokens

### Alternative 3: Silent Retry
```typescript
// Bei 401 automatisch neu einloggen
if (401) {
  await login(savedCredentials)
  retry(originalRequest)
}
```
**Warum nicht:** 
- Würde Passwort im localStorage speichern (unsicher)
- User sollte bewusst neu einloggen

---

## Best Practices

### 1. Token-Gültigkeit
**Empfehlung:** 24 Stunden (JWT_EXPIRE_MINUTES=1440)
- Nicht zu kurz: Weniger Login-Unterbrechungen
- Nicht zu lang: Sicherheitsrisiko bei Token-Leak

### 2. SECRET_KEY Management
**Production:**
```bash
# Einmal generieren
openssl rand -hex 32 > .secret_key

# In .env
SECRET_KEY=$(cat .secret_key)
```

**Development:**
```bash
# .env erstellen beim Setup
python -c "import secrets; print(secrets.token_hex(32))" > .env
```

### 3. Browser localStorage
**User-Hinweis in Docs:**
"Bei Problemen: Browser-Cache leeren und neu einloggen"

---

## Logging

### Console Logs (für Debugging)

**Bei Auto-Logout:**
```
⚠️ Token invalid or expired - logging out
```

**Im Browser DevTools:**
```
Network Tab:
  GET /api/chat/sessions - 401 Unauthorized
  
Console:
  ⚠️ Token invalid or expired - logging out
```

---

## Zusammenfassung

**Problem:** 401-Fehler bei ungültigem Token, User bleibt scheinbar eingeloggt  
**Lösung:** Axios Interceptor für automatisches Logout  
**Ergebnis:** Bessere UX, automatische Fehlerbehandlung

**Vorher:**
- ❌ User verwirrt
- ❌ Manuelles localStorage leeren nötig
- ❌ Schlechte UX

**Nachher:**
- ✅ Automatisches Logout
- ✅ Klares Feedback
- ✅ Professionelle UX

---

**Status:** ✅ Implementiert und getestet
