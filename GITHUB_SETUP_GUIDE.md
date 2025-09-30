# GitHub Integration Setup Guide

Es gibt **zwei Methoden** um GitHub mit Xionimus AI zu verbinden:

---

## 🎯 Methode 1: Personal Access Token (EMPFOHLEN - Einfach)

### Vorteile:
- ✅ Keine OAuth-Konfiguration nötig
- ✅ Funktioniert sofort
- ✅ Keine Backend-Konfiguration erforderlich

### Schritte:

1. **Gehe zu GitHub Token Settings:**
   ```
   https://github.com/settings/tokens
   ```

2. **Klicke auf "Generate new token (classic)"**

3. **Konfiguriere den Token:**
   - **Note:** `Xionimus AI Access`
   - **Expiration:** 90 days (oder No expiration)
   - **Select scopes:**
     - ✅ `repo` (Full control of private repositories)
     - ✅ `user` (Read user profile data)

4. **Generiere und kopiere den Token**
   - ⚠️ **WICHTIG:** Speichere den Token sicher!
   - Der Token wird nur EINMAL angezeigt

5. **Verwende den Token in Xionimus AI:**
   ```javascript
   // Im Frontend (oder direkt API-Call):
   localStorage.setItem('github_token', 'ghp_your_token_here');
   ```

### Direkter Push (ohne UI):

```bash
# Backend API aufrufen
curl -X POST http://localhost:8001/api/github/push \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "your-username",
    "repo": "your-repo",
    "files": [
      {"path": "README.md", "content": "# Test from Xionimus AI"}
    ],
    "commit_message": "Update from Xionimus AI",
    "branch": "main",
    "access_token": "ghp_your_token_here"
  }'
```

---

## 🔐 Methode 2: OAuth (Erweitert - Für Multi-User-Setups)

### Vorteile:
- ✅ Kein Token manuell verwalten
- ✅ Automatische Token-Erneuerung
- ✅ Sicherer für Multi-User-Anwendungen

### Nachteile:
- ⚠️ Komplexere Einrichtung
- ⚠️ Benötigt GitHub OAuth App

### Schritte:

#### 1. GitHub OAuth App erstellen

Gehe zu:
```
https://github.com/settings/developers
```

Klicke: **"New OAuth App"**

Fülle aus:
```
Application name: Xionimus AI
Homepage URL: http://localhost:3000
Authorization callback URL: http://localhost:3000/github/callback
```

Nach dem Erstellen erhältst du:
- **Client ID:** (z.B., `Iv1.1234567890abcdef`)
- **Client Secret:** (klicke "Generate a new client secret")

#### 2. Backend konfigurieren

Erstelle/editiere `backend/.env`:

```env
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=Iv1.1234567890abcdef
GITHUB_CLIENT_SECRET=your_secret_here
GITHUB_REDIRECT_URI=http://localhost:3000/github/callback
```

#### 3. Backend neu starten

```bash
cd backend
python main.py
```

Du solltest sehen:
```
✅ GitHub Integration enabled
```

#### 4. Im Frontend testen

1. Öffne Settings → GitHub Integration
2. Klicke "Connect GitHub"
3. Du wirst zu GitHub weitergeleitet
4. Autorisiere die App
5. Du wirst zurück zu Xionimus AI geleitet
6. ✅ Verbunden!

---

## 🧪 Testen der Integration

### Test 1: Check Configuration

```bash
# Backend muss laufen
curl http://localhost:8001/api/github/oauth/url
```

**Erwartete Antwort (OAuth konfiguriert):**
```json
{
  "configured": true,
  "oauth_url": "https://github.com/login/oauth/authorize?...",
  "redirect_uri": "http://localhost:3000/github/callback"
}
```

**Erwartete Antwort (OAuth NICHT konfiguriert):**
```json
{
  "configured": false,
  "message": "GitHub OAuth is optional...",
  "setup_guide": { ... },
  "alternative": { ... }
}
```

### Test 2: Push mit Personal Access Token

```bash
curl -X POST http://localhost:8001/api/github/push \
  -H "Content-Type: application/json" \
  -d '{
    "owner": "YOUR_GITHUB_USERNAME",
    "repo": "test-repo",
    "files": [
      {
        "path": "test.txt",
        "content": "Hello from Xionimus AI!"
      }
    ],
    "commit_message": "Test commit from Xionimus AI",
    "branch": "main",
    "access_token": "ghp_YOUR_TOKEN_HERE"
  }'
```

**Erwartete Antwort:**
```json
{
  "success": true,
  "commit_sha": "abc123...",
  "files_pushed": 1,
  "repository": "your-username/test-repo",
  "branch": "main",
  "message": "Successfully pushed 1 file(s)"
}
```

---

## 🔍 Troubleshooting

### Problem: "GitHub OAuth not configured"

**Lösung:**
- Verwende Personal Access Token (Methode 1) ODER
- Konfiguriere OAuth (Methode 2)

### Problem: "Failed to push to GitHub"

**Mögliche Ursachen:**
1. **Token ungültig:** Generiere neuen Token
2. **Keine Berechtigung:** Token braucht `repo` scope
3. **Repository existiert nicht:** Erstelle es auf GitHub
4. **Branch existiert nicht:** Verwende existierenden Branch

### Problem: OAuth-Redirect funktioniert nicht

**Lösung:**
- Stelle sicher, dass `GITHUB_REDIRECT_URI` mit der Callback-URL der OAuth App übereinstimmt
- Frontend muss auf `http://localhost:3000` laufen
- Backend muss auf Port 8001 laufen

---

## 📊 Vergleich der Methoden

| Feature | Personal Token | OAuth |
|---------|---------------|-------|
| Setup-Zeit | 2 Minuten | 10 Minuten |
| Sicherheit | Gut | Ausgezeichnet |
| Multi-User | Nein | Ja |
| Token-Verwaltung | Manuell | Automatisch |
| Backend-Config | Nicht nötig | Erforderlich |
| Empfohlen für | Single User | Production/Teams |

---

## ✅ Zusammenfassung

**Für schnellen Test:**
→ Verwende **Personal Access Token** (Methode 1)

**Für Production:**
→ Verwende **OAuth** (Methode 2)

**Beide Methoden funktionieren parallel!**
Du kannst OAuth für normale Benutzer anbieten und gleichzeitig Personal Tokens für Power-User erlauben.

---

## 🔗 Nützliche Links

- GitHub OAuth Apps: https://github.com/settings/developers
- Personal Access Tokens: https://github.com/settings/tokens
- GitHub API Docs: https://docs.github.com/en/rest
- Xionimus AI Docs: README.md

---

**Status:** ✅ GitHub Integration vollständig dokumentiert  
**Beide Methoden:** Funktionsfähig  
**Empfehlung:** Start mit Personal Token, upgrade zu OAuth bei Bedarf
