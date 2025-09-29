# GitHub OAuth Setup für Xionimus AI

## Schritt 1: GitHub OAuth App erstellen

1. Gehen Sie zu https://github.com/settings/developers
2. Klicken Sie auf "New OAuth App"
3. Füllen Sie die Felder aus:
   - **Application name**: Xionimus AI
   - **Homepage URL**: http://localhost:3000
   - **Authorization callback URL**: http://localhost:3000/github/callback
4. Klicken Sie auf "Register application"
5. Notieren Sie sich:
   - **Client ID**
   - **Client Secret** (generieren Sie einen neuen)

## Schritt 2: Environment Variables setzen

### Backend (.env)

Erstellen/Bearbeiten Sie `/app/xionimus-ai/backend/.env`:

```env
# Bestehende Variablen...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
MONGO_URL=mongodb://localhost:27017/xionimus

# GitHub OAuth (NEU)
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here
GITHUB_REDIRECT_URI=http://localhost:3000/github/callback
```

### Frontend (.env)

Die Frontend-Variablen sind bereits korrekt gesetzt.

## Schritt 3: Backend neu starten

```bash
sudo supervisorctl restart backend
```

## Schritt 4: Testen

1. Öffnen Sie http://localhost:3000
2. Klicken Sie auf "📤 GitHub Push"
3. Sie werden zu GitHub weitergeleitet
4. Autorisieren Sie die App
5. Sie werden zurück zur App geleitet mit Access Token

## OAuth Flow Diagramm

```
User                Frontend              Backend              GitHub
 |                     |                     |                    |
 |--Click "GitHub"--->|                     |                    |
 |                     |--GET /oauth/url--->|                    |
 |                     |<--oauth_url--------|                    |
 |                     |                     |                    |
 |<--Redirect to GitHub OAuth-------------->|                    |
 |                                           |                    |
 |--Authorize App--------------------------------->|              |
 |                                                 |--Grant------>|
 |<--Redirect with code----------------------------|<------------|
 |                     |                     |                    |
 |                     |--POST /oauth/token--|                    |
 |                     |   {code}            |--Exchange code--->|
 |                     |                     |<--access_token-----|
 |                     |<--{access_token,    |                    |
 |                     |     user_info}------|                    |
 |                     |                     |                    |
 |<--Store token-------|                     |                    |
```

## API Endpoints

### GET /api/github/oauth/url
Gibt GitHub OAuth URL zurück

**Response:**
```json
{
  "oauth_url": "https://github.com/login/oauth/authorize?client_id=...",
  "redirect_uri": "http://localhost:3000/github/callback"
}
```

### POST /api/github/oauth/token
Tauscht OAuth Code gegen Access Token

**Request:**
```json
{
  "code": "oauth_code_from_github"
}
```

**Response:**
```json
{
  "access_token": "gho_...",
  "user": {
    "login": "username",
    "name": "User Name",
    "avatar_url": "https://..."
  }
}
```

### GET /api/github/repositories?access_token=...
Listet Repositories des Users

### POST /api/github/repositories?access_token=...
Erstellt neues Repository

**Request:**
```json
{
  "name": "my-project",
  "description": "Created with Xionimus AI",
  "private": false
}
```

### GET /api/github/repositories/{owner}/{repo}/branches?access_token=...
Listet Branches

### POST /api/github/push
Pusht Code zu GitHub

**Request:**
```json
{
  "owner": "username",
  "repo": "my-project",
  "files": [
    {
      "path": "src/App.tsx",
      "content": "import React from 'react'..."
    },
    {
      "path": "README.md",
      "content": "# My Project"
    }
  ],
  "commit_message": "Initial commit from Xionimus AI",
  "branch": "main",
  "access_token": "gho_..."
}
```

**Response:**
```json
{
  "success": true,
  "commit_sha": "abc123...",
  "files_pushed": 2,
  "repository": "username/my-project",
  "branch": "main",
  "message": "Successfully pushed 2 files"
}
```

## Scopes

Die App benötigt folgende GitHub Scopes:
- **repo**: Voller Zugriff auf Repositories (lesen, schreiben, erstellen)
- **user**: Lesen von User-Profildaten

## Sicherheit

- Access Token wird nur im Frontend (localStorage) gespeichert
- Token wird bei jedem API-Call mitgesendet
- Token läuft nicht ab (Personal Access Token Behavior)
- User kann Token jederzeit in GitHub Settings widerrufen

## Troubleshooting

### "GitHub OAuth not configured"
- Prüfen Sie ob GITHUB_CLIENT_ID und GITHUB_CLIENT_SECRET gesetzt sind
- Backend neu starten

### "Invalid redirect_uri"
- Prüfen Sie ob die URL in GitHub OAuth App Settings exakt übereinstimmt
- Format: http://localhost:3000/github/callback (kein trailing slash!)

### "Bad credentials"
- Access Token ist ungültig oder abgelaufen
- User muss sich neu authentifizieren

### "Not Found" beim Push
- Repository existiert nicht
- Branch existiert nicht
- User hat keine Schreibrechte

## Production Setup

Für Production (deployed app):

1. Erstellen Sie neue OAuth App mit Production URLs:
   - Homepage URL: https://yourdomain.com
   - Callback URL: https://yourdomain.com/github/callback

2. Setzen Sie Environment Variables:
```env
GITHUB_CLIENT_ID=prod_client_id
GITHUB_CLIENT_SECRET=prod_client_secret
GITHUB_REDIRECT_URI=https://yourdomain.com/github/callback
```

3. Verwenden Sie HTTPS für alle URLs
