# GitHub Integration Setup Guide

## Overview
GitHub integration uses Personal Access Token (PAT) stored encrypted in database.

## Quick Setup

### 1. Generate GitHub PAT
- Visit: https://github.com/settings/tokens
- Create token with `repo` and `user` scopes
- Copy token (starts with `ghp_`)

### 2. Store Securely
```bash
cd /app/scripts
./setup_github_pat.sh YOUR_GITHUB_PAT
```

### 3. Verify
```bash
curl http://localhost:8001/api/v1/github/admin/github-pat/status
```

## Security
- PAT encrypted with AES-128
- Stored in database only
- Never in .env or code files
- Safe to commit configuration

## Configuration
Backend .env contains only:
```env
GITHUB_USE_PAT=true
```
No secrets in this file - safe to commit.

## Token Rotation
```bash
./setup_github_pat.sh NEW_TOKEN
```

## Troubleshooting
- Check status: `curl http://localhost:8001/api/v1/github/admin/github-pat/status`
- View logs: `tail -f /var/log/supervisor/backend.err.log`
- Restart: `supervisorctl restart backend`

## Documentation
- Setup script: `/app/scripts/setup_github_pat.sh`
- Storage module: `/app/backend/app/core/github_pat_storage.py`
- API endpoints: `/app/backend/app/api/github_admin.py`

---
**Note**: All examples use placeholders. Never commit real tokens.
