# GitHub OAuth Integration Guide

## Overview

Xionimus AI now supports GitHub OAuth 2.0 authentication, allowing users to connect their GitHub accounts without manually managing Personal Access Tokens (PATs). This integration enables seamless repository import/export functionality.

---

## Features

### ✅ What You Can Do

- **Import Repositories**: Browse and import your GitHub repositories directly
- **Export Code**: Push session code to new or existing repositories
- **Secure Authentication**: OAuth 2.0 with encrypted token storage
- **No Token Management**: No need to create or manage Personal Access Tokens
- **Branch Selection**: Choose specific branches when importing
- **Real-time Progress**: See import progress with file counts

---

## How It Works

### OAuth Flow Diagram

```
User → Xionimus → GitHub Authorization → Callback → Token Storage → Ready!
```

### Detailed Steps

1. **User Initiates OAuth**
   - User clicks "Connect with GitHub" in Settings or Import/Export dialogs
   - Frontend calls `/api/github/oauth/authorize-url`
   - Backend generates authorization URL with CSRF state token

2. **GitHub Authorization**
   - User redirected to GitHub authorization page
   - Scopes requested: `repo` (repository access) and `user` (profile info)
   - User approves access

3. **Callback & Token Exchange**
   - GitHub redirects to `http://localhost:3000/github/callback?code=xxx`
   - Frontend extracts authorization code
   - Frontend sends code to `/api/github/oauth/callback`
   - Backend exchanges code for access token
   - Token encrypted and stored in database

4. **Ready to Use**
   - User redirected back to main application
   - GitHub functionality now available
   - Token automatically used for all GitHub operations

---

## Backend Implementation

### OAuth Endpoints

#### 1. GET `/api/github/oauth/authorize-url`

Generates GitHub OAuth authorization URL.

**Request:**
```bash
curl -X GET "http://localhost:8001/api/github/oauth/authorize-url" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response:**
```json
{
  "authorization_url": "https://github.com/login/oauth/authorize?client_id=...&redirect_uri=...&scope=repo+user&state=...",
  "state": "CSRF_TOKEN"
}
```

#### 2. POST `/api/github/oauth/callback`

Exchanges authorization code for access token.

**Request:**
```bash
curl -X POST "http://localhost:8001/api/github/oauth/callback" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"code":"AUTHORIZATION_CODE"}'
```

**Response:**
```json
{
  "connected": true,
  "github_username": "johndoe",
  "message": "Successfully connected to GitHub as johndoe via OAuth"
}
```

#### 3. GET `/api/github/oauth/status`

Check GitHub OAuth connection status.

**Request:**
```bash
curl -X GET "http://localhost:8001/api/github/oauth/status" \
  -H "Authorization: Bearer {JWT_TOKEN}"
```

**Response (Connected):**
```json
{
  "connected": true,
  "github_username": "johndoe",
  "message": "Connected to GitHub as johndoe"
}
```

**Response (Not Connected):**
```json
{
  "connected": false,
  "github_username": null,
  "message": "Not connected to GitHub. Please authorize the application."
}
```

---

## Frontend Implementation

### OAuth Service

Located at: `/app/frontend/src/services/githubOAuthService.ts`

**Functions:**
- `getGitHubOAuthUrl(token)` - Get authorization URL
- `getGitHubOAuthStatus(token)` - Check connection status
- `initiateGitHubOAuth(token)` - Start OAuth flow (redirects to GitHub)
- `exchangeOAuthCode(code, token)` - Exchange code for token

### UI Components

#### 1. Settings Page
**Location:** `/app/frontend/src/pages/SettingsPage.tsx`

**Features:**
- Dedicated GitHub OAuth section
- Connection status badge (Not Connected/Connected)
- Benefits list explaining OAuth advantages
- "Connect with GitHub" button
- Refresh connection status button
- Shows GitHub username when connected

#### 2. GitHub Import Dialog
**Location:** `/app/frontend/src/components/GitHubImportDialog.tsx`

**Features:**
- OAuth status check on dialog open
- Warning card when not connected
- "Mit GitHub verbinden" button
- Auto mode (browse repositories) disabled until connected
- Manual mode (URL import) disabled until connected

#### 3. GitHub Export Dialog
**Location:** `/app/frontend/src/components/GitHubPushDialog.tsx`

**Features:**
- OAuth status check on dialog open
- Warning card when not connected
- "Mit GitHub verbinden" button
- Export functionality disabled until connected

#### 4. Callback Page
**Location:** `/app/frontend/src/pages/GitHubCallbackPage.tsx`

**Features:**
- Extracts authorization code from URL
- Exchanges code for token via backend
- Shows loading/success/error states
- Auto-redirects back to chat after success

---

## Configuration

### Environment Variables

**Backend:** `/app/backend/.env`

```env
GITHUB_OAUTH_CLIENT_ID=Ov23liCIa2aVTC3ttGFf
GITHUB_OAUTH_CLIENT_SECRET=2f7c3c314053aa3be665742ad0ac06d732a2d5d5
GITHUB_OAUTH_CALLBACK_URL=http://localhost:3000/github/callback
```

### OAuth App Settings

**GitHub OAuth App Configuration:**
- **Application Name:** Xionimus AI
- **Homepage URL:** http://localhost:3000
- **Authorization Callback URL:** http://localhost:3000/github/callback
- **Scopes:** repo, user

---

## Security

### Token Storage

- **Encryption:** All tokens encrypted using Fernet (symmetric encryption)
- **Storage:** Stored in MongoDB `user_api_keys` collection
- **Access:** Only accessible by token owner (user_id verified)
- **Metadata:** Stores GitHub username and OAuth flag

### CSRF Protection

- **State Parameter:** Generated on authorization URL request
- **Validation:** State parameter included in callback (currently simplified)
- **Future Enhancement:** Store state in Redis/DB for strict validation

---

## Usage Examples

### For Users

**Connecting GitHub:**

1. Go to **Settings** page
2. Scroll to **GitHub** section
3. Click **"Connect with GitHub"** button
4. Authorize Xionimus AI on GitHub
5. Automatically redirected back
6. Status shows: **"Connected as {username}"**

**Importing a Repository:**

1. Click **GitHub** dropdown in chat
2. Select **"Importieren"**
3. If not connected: Click **"Mit GitHub verbinden"**
4. After connection: Choose **Auto** or **Manual** mode
5. Select repository and branch
6. Click **"Importieren"**
7. Watch real-time import progress

**Exporting Code:**

1. Click **GitHub** dropdown in chat
2. Select **"Exportieren"**
3. If not connected: Click **"Mit GitHub verbinden"**
4. After connection: Enter repository details
5. Select files to export
6. Click **"Zu GitHub pushen"**

---

## Troubleshooting

### Common Issues

**1. OAuth Not Working**
- Check if `GITHUB_OAUTH_CLIENT_ID` and `GITHUB_OAUTH_CLIENT_SECRET` are set
- Verify callback URL matches GitHub OAuth App settings
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

**2. Token Invalid/Expired**
- Click "Refresh Connection Status" in Settings
- If still invalid, reconnect via "Connect with GitHub" button
- GitHub tokens expire after inactivity or revocation

**3. Callback Redirect Issues**
- Ensure callback URL is exactly: `http://localhost:3000/github/callback`
- Check browser console for errors
- Verify route is registered in `App.tsx`

**4. Import/Export Not Working**
- Verify connection status in Settings
- Check if token has correct scopes (repo, user)
- Check backend logs for API errors

---

## API Testing

### Test OAuth Endpoints (cURL)

```bash
# 1. Login and get JWT token
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}' | jq -r '.access_token')

# 2. Get OAuth authorization URL
curl -X GET "http://localhost:8001/api/github/oauth/authorize-url" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 3. Check OAuth status
curl -X GET "http://localhost:8001/api/github/oauth/status" \
  -H "Authorization: Bearer $TOKEN" | jq .

# 4. Test callback (with code from GitHub)
curl -X POST "http://localhost:8001/api/github/oauth/callback" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"AUTHORIZATION_CODE_FROM_GITHUB"}' | jq .
```

---

## Future Enhancements

### Potential Improvements

1. **State Validation:** Store state tokens in Redis for strict CSRF protection
2. **Token Refresh:** Implement OAuth token refresh flow (GitHub tokens don't expire but can be revoked)
3. **Scope Management:** Allow users to select specific scopes
4. **Organization Access:** Support GitHub organization repositories
5. **Multiple Accounts:** Allow users to connect multiple GitHub accounts
6. **Webhook Integration:** Real-time notifications for repository changes
7. **Deploy Keys:** Generate and manage deploy keys for repositories

---

## Related Documentation

- [GitHub OAuth Apps Documentation](https://docs.github.com/en/apps/oauth-apps)
- [GitHub REST API](https://docs.github.com/en/rest)
- [Xionimus AI Architecture](./code_architecture.md)
- [Testing Guide](./test_result.md)

---

## Support

For issues or questions:
1. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
2. Check frontend logs: Browser DevTools Console
3. Review this documentation
4. Check GitHub OAuth App settings

---

**Last Updated:** October 8, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
