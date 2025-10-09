# 🔑 How to Add API Keys - Xionimus AI

## Important: Use the UI, Not .env File!

**✅ CORRECT WAY:** Add API keys through the web interface  
**❌ WRONG WAY:** Manually editing `backend/.env` file

---

## Why Use the UI?

1. **Secure Encryption**: Keys are encrypted with Fernet (AES-128) before storage
2. **Per-User Keys**: Each user can have their own API keys
3. **Easy Management**: Add, update, or delete keys with one click
4. **No Restart Required**: Changes take effect immediately
5. **Safe Storage**: Keys stored in encrypted database, never in plain text

---

## Step-by-Step Guide

### 1. Start the Application

```cmd
# Double-click or run in CMD
START.bat
```

Wait for browser to open automatically at `http://localhost:3000`

### 2. Login

First-time users:
- Clear browser cache: Press `F12` → `Application` → `Clear storage`
- Username: `admin`
- Password: `admin123`

### 3. Navigate to Settings

**Option A:** Click on the **Settings** link in the navigation menu

**Option B:** Go directly to: `http://localhost:3000/settings`

### 4. Add Your API Keys

You'll see cards for each provider:

#### OpenAI
1. Click **"API Key erhalten →"** or visit: https://platform.openai.com/api-keys
2. Generate a new API key in OpenAI dashboard
3. Copy the key (starts with `sk-proj-...`)
4. Paste into **OpenAI API Key** field in Xionimus
5. Click **"Speichern"** (Save)

#### Anthropic
1. Click **"API Key erhalten →"** or visit: https://console.anthropic.com/settings/keys
2. Create a new API key in Anthropic console
3. Copy the key (starts with `sk-ant-...`)
4. Paste into **Anthropic API Key** field in Xionimus
5. Click **"Speichern"** (Save)

#### Perplexity (Optional)
1. Visit: https://www.perplexity.ai/settings/api
2. Generate API key
3. Copy and paste into **Perplexity API Key** field
4. Click **"Speichern"** (Save)

### 5. Verify

- Green checkmark (✓) appears when key is saved
- "Aktiv" (Active) status shown
- You can now use AI features immediately!

---

## Key Status Indicators

| Status | Meaning |
|--------|---------|
| ✓ Aktiv (Active) | Key saved and working |
| ⚠️ Nicht gesetzt | No key configured |
| ❌ Fehler | Invalid key or error |

---

## Managing Your Keys

### Update a Key
1. Click **"Bearbeiten"** (Edit) on the key card
2. Enter new key
3. Click **"Speichern"** (Save)

### Delete a Key
1. Click **"Löschen"** (Delete) on the key card
2. Confirm deletion
3. Key is permanently removed

### View Current Key
- Keys are masked for security (shown as `sk-***...***`)
- You can see if a key is active without viewing the full key

---

## Security Features

### Encryption
- All API keys encrypted with **Fernet (AES-128)**
- Encryption key stored securely in `backend/.env`:
  ```
  ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=
  ```
- This key is permanent and should never be changed

### Per-User Storage
- Each user has their own encrypted API keys
- Keys are not shared between users
- Stored in MongoDB with user association

### Database Security
- Keys stored in encrypted form in MongoDB
- Never transmitted in plain text
- Decrypted only when needed for API calls

---

## Troubleshooting

### "Chat antwortet nicht" (Chat not responding)
**Problem:** No API keys configured  
**Solution:** Add keys in Settings page (see steps above)

### "Ungültiger API Key" (Invalid API key)
**Problem:** Key format is incorrect or expired  
**Solution:** 
1. Verify key from provider dashboard
2. Regenerate key if needed
3. Ensure no extra spaces or characters

### "API Key konnte nicht gespeichert werden" (Could not save key)
**Problem:** Backend or database issue  
**Solution:**
1. Check backend is running (`http://localhost:8001/api/health`)
2. Verify MongoDB is accessible
3. Check backend logs for errors

### Can't Access Settings Page
**Problem:** Not logged in or session expired  
**Solution:**
1. Login again with `admin` / `admin123`
2. Clear browser cache if needed
3. Check browser console for errors (F12)

---

## Backend .env File (System Configuration Only)

The `backend/.env` file should contain:

### System Keys (DO NOT CHANGE)
```env
SECRET_KEY=4cb353004a7ae0e073c297622427791121baba5c7194529927db4ea6781dd307
ENCRYPTION_KEY=89LbBC5YLnyYyicldiTigqG0TneY7XeiAAstkqb30-Q=
```

### Provider Keys (Optional Defaults)
```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PERPLEXITY_API_KEY=
```

**Note:** These are system-wide defaults. User-specific keys from the UI take precedence.

---

## API Key Usage Flow

```
User enters key in UI
    ↓
Key encrypted with Fernet
    ↓
Stored in MongoDB with user_id
    ↓
User makes chat request
    ↓
Key retrieved and decrypted
    ↓
Used for API call to provider
    ↓
Response returned to user
```

---

## FAQ

### Q: Do I need to restart after adding keys?
**A:** No! Keys take effect immediately.

### Q: Can multiple users have different keys?
**A:** Yes! Each user can configure their own API keys.

### Q: What happens if I change ENCRYPTION_KEY?
**A:** ⚠️ **DON'T!** All stored keys will become unreadable.

### Q: Are my keys shared with other users?
**A:** No, keys are user-specific and encrypted.

### Q: Can I use the same key for all providers?
**A:** No, each provider requires their own unique API key.

### Q: What if I don't add any keys?
**A:** The app works, but AI chat features won't function.

---

## Best Practices

1. ✅ **Generate separate keys** for development and production
2. ✅ **Rotate keys regularly** for security
3. ✅ **Use minimal permissions** when generating keys
4. ✅ **Delete old keys** from provider dashboards
5. ✅ **Monitor usage** in provider dashboards
6. ❌ **Never share keys** via email or chat
7. ❌ **Never commit keys** to git repositories
8. ❌ **Never hardcode keys** in code

---

## Getting API Keys

### OpenAI
1. Visit: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Name it (e.g., "Xionimus AI")
5. Copy and save immediately (won't be shown again)

### Anthropic
1. Visit: https://console.anthropic.com/settings/keys
2. Sign in or create account
3. Click "Create Key"
4. Name it (e.g., "Xionimus AI")
5. Copy the key

### Perplexity
1. Visit: https://www.perplexity.ai/settings/api
2. Sign in or create account
3. Generate API key
4. Copy the key

---

## Support

For issues:
1. Check backend logs: `backend/logs/` or supervisor logs
2. Verify MongoDB is running
3. Check browser console (F12) for errors
4. Review this guide

---

**Remember:** Always use the Settings page UI to manage API keys. Never manually edit the .env file for user keys!

---

**Last Updated:** 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
