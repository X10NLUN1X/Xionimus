# GitHub Integration - Status & Setup

## ✅ Was ist implementiert?

### Backend API Endpoints (vollständig implementiert):

1. **OAuth Flow**
   - ✅ `GET /api/github/oauth/url` - OAuth URL generieren
   - ✅ `POST /api/github/oauth/token` - Code gegen Token tauschen
   - ✅ `GET /api/github/user` - User Info abrufen

2. **Repository Management**
   - ✅ `GET /api/github/repositories` - Repos auflisten
   - ✅ `POST /api/github/repositories` - Neues Repo erstellen
   - ✅ `GET /api/github/repositories/{owner}/{repo}/branches` - Branches auflisten
   - ✅ `POST /api/github/repositories/{owner}/{repo}/branches` - Branch erstellen

3. **Code Pushing**
   - ✅ `POST /api/github/push` - Dateien zu GitHub pushen

4. **Health Check**
   - ✅ `GET /api/github/health` - GitHub-Konfiguration prüfen

### Core Integration (vollständig implementiert):

- ✅ `GitHubIntegration` Klasse mit allen Funktionen
- ✅ OAuth Helper-Funktionen
- ✅ Async/Await Pattern
- ✅ Error Handling & Logging

---

## ⚠️ Was fehlt noch?

### 1. Environment-Variablen (.env Datei)

**Aktuell:** Keine .env Datei vorhanden  
**Benötigt:**

```env
# GitHub OAuth Credentials (Optional - für OAuth)
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_REDIRECT_URI=http://localhost:3000/github/callback
```

**Ohne diese Credentials:**
- ❌ OAuth-Login funktioniert NICHT
- ✅ Direktes Pushen mit Personal Access Token funktioniert

---

### 2. Frontend-Integration

**Aktuell implementiert:**
- ✅ UI-Buttons in SettingsPage
- ✅ `handleGithubConnect()` Funktion (Platzhalter)
- ✅ `handlePushToGithub()` Funktion (Platzhalter)

**Fehlt noch:**
- ❌ API-Aufrufe zum Backend
- ❌ Token-Speicherung (localStorage)
- ❌ OAuth-Callback-Seite
- ❌ File-Selection für Push

---

## 🚀 Wie bekomme ich GitHub OAuth zum Laufen?

### Option 1: Mit OAuth (empfohlen für Produktiv)

**Schritt 1: GitHub OAuth App erstellen**

1. Gehe zu https://github.com/settings/developers
2. Klicke "New OAuth App"
3. Fülle aus:
   - **Application name:** Xionimus AI
   - **Homepage URL:** http://localhost:3000
   - **Authorization callback URL:** http://localhost:3000/github/callback
4. Notiere `Client ID` und `Client Secret`

**Schritt 2: .env Datei erstellen**

```batch
cd backend
echo GITHUB_CLIENT_ID=dein_client_id > .env
echo GITHUB_CLIENT_SECRET=dein_client_secret >> .env
echo GITHUB_REDIRECT_URI=http://localhost:3000/github/callback >> .env
```

**Schritt 3: Backend neu starten**

```batch
cd backend
python main.py
```

**Schritt 4: Testen**

```
GET http://localhost:8001/api/github/health
```

Sollte zurückgeben:
```json
{
  "status": "configured",
  "oauth_enabled": true,
  "redirect_uri": "http://localhost:3000/github/callback"
}
```

---

### Option 2: Mit Personal Access Token (schneller Test)

**Ohne OAuth, direkt mit Token:**

**Schritt 1: Personal Access Token erstellen**

1. Gehe zu https://github.com/settings/tokens
2. Klicke "Generate new token (classic)"
3. Wähle Scopes:
   - ✅ `repo` (full control)
   - ✅ `user` (read user info)
4. Generiere und kopiere den Token

**Schritt 2: Direkt pushen (ohne OAuth)**

```javascript
// Im Frontend:
const response = await fetch('http://localhost:8001/api/github/push', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    owner: 'dein-github-username',
    repo: 'dein-repo-name',
    files: [
      { path: 'test.txt', content: 'Hello from Xionimus AI!' }
    ],
    commit_message: 'Test commit from Xionimus AI',
    branch: 'main',
    access_token: 'ghp_deinPersonalAccessToken'
  })
});
```

---

## 🔧 Frontend vervollständigen

### Fehlende Implementierung in SettingsPage.tsx:

```typescript
// Aktuell (Platzhalter):
const handleGithubConnect = () => {
  toast({
    title: 'GitHub Integration',
    description: 'Opening GitHub OAuth connection...',
    status: 'info',
    duration: 3000,
  })
  // TODO: Implement GitHub OAuth
}

// Soll sein (vollständig):
const handleGithubConnect = async () => {
  try {
    // 1. OAuth URL vom Backend holen
    const response = await fetch('http://localhost:8001/api/github/oauth/url')
    const data = await response.json()
    
    // 2. Zu GitHub OAuth umleiten
    window.location.href = data.oauth_url
  } catch (error) {
    toast({
      title: 'Fehler',
      description: 'GitHub OAuth konnte nicht gestartet werden',
      status: 'error',
    })
  }
}

// Push Funktion:
const handlePushToGithub = async () => {
  const token = localStorage.getItem('github_token')
  if (!token) {
    toast({
      title: 'Nicht verbunden',
      description: 'Bitte erst mit GitHub verbinden',
      status: 'warning',
    })
    return
  }
  
  try {
    const response = await fetch('http://localhost:8001/api/github/push', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        owner: 'username',  // TODO: aus localStorage
        repo: 'repo-name',  // TODO: UI für Auswahl
        files: [/* TODO: aktuelle Workspace-Files */],
        commit_message: 'Update from Xionimus AI',
        branch: 'main',
        access_token: token
      })
    })
    
    const result = await response.json()
    toast({
      title: 'Erfolgreich!',
      description: `${result.files_pushed} Dateien gepusht`,
      status: 'success',
    })
  } catch (error) {
    toast({
      title: 'Push fehlgeschlagen',
      description: error.message,
      status: 'error',
    })
  }
}
```

### Fehlende OAuth Callback Seite:

Erstellen: `frontend/src/pages/GitHubCallback.tsx`

```typescript
// Diese Seite verarbeitet den OAuth-Redirect von GitHub
import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

export const GitHubCallback = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  
  useEffect(() => {
    const code = searchParams.get('code')
    if (code) {
      // Token austauschen
      fetch('http://localhost:8001/api/github/oauth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      })
      .then(res => res.json())
      .then(data => {
        // Token speichern
        localStorage.setItem('github_token', data.access_token)
        localStorage.setItem('github_user', JSON.stringify(data.user))
        // Zurück zu Settings
        navigate('/settings')
      })
    }
  }, [searchParams, navigate])
  
  return <div>Verbinde mit GitHub...</div>
}
```

---

## 📊 Zusammenfassung

### ✅ Funktioniert bereits:

- **Backend API** - Alle Endpoints implementiert
- **Core Logic** - GitHub Integration Klasse fertig
- **UI Buttons** - Vorhanden in Settings

### ⚠️ Benötigt Konfiguration:

- **OAuth Credentials** - GitHub App erstellen
- **.env Datei** - CLIENT_ID & SECRET eintragen

### ❌ Muss noch implementiert werden:

- **Frontend API Calls** - Verbindung Backend ↔ Frontend
- **Token Management** - localStorage Handling
- **OAuth Callback** - Callback-Seite erstellen
- **File Selection** - UI für Dateiauswahl beim Push

---

## 🎯 Schnelltest (ohne OAuth)

**Mit Personal Access Token direkt testen:**

```bash
# Backend testen
curl -X POST http://localhost:8001/api/github/push \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "dein-username",
    "repo": "test-repo",
    "files": [{"path": "test.txt", "content": "Hello World"}],
    "commit_message": "Test",
    "branch": "main",
    "access_token": "ghp_deinToken"
  }'
```

**Wenn das funktioniert:** Backend ist fertig ✅  
**Dann fehlt nur:** Frontend-Integration

---

**Status:** Backend ✅ fertig | Frontend ⚠️ UI da, API-Calls fehlen | OAuth ❌ nicht konfiguriert
