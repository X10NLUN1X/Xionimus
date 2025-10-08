#!/bin/bash
# Setup GitHub Personal Access Token
# This script stores the PAT securely in the encrypted database

echo "=================================="
echo "GitHub PAT Setup Script"
echo "=================================="
echo ""

# Check if PAT is provided as argument
if [ -z "$1" ]; then
    echo "Usage: ./setup_github_pat.sh <your_github_pat>"
    echo ""
    echo "Example:"
    echo "  ./setup_github_pat.sh ghp_xxxxxxxxxxxx"
    echo ""
    echo "Get your PAT from: https://github.com/settings/tokens"
    echo "Required scopes: repo, user"
    exit 1
fi

PAT_TOKEN="$1"

# Validate PAT format
if [[ ! "$PAT_TOKEN" =~ ^ghp_ ]]; then
    echo "❌ Error: Invalid PAT format"
    echo "GitHub Personal Access Tokens must start with 'ghp_'"
    exit 1
fi

echo "📡 Connecting to backend..."

# Store the PAT
RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/github/admin/github-pat/store \
  -H "Content-Type: application/json" \
  -d "{\"pat_token\":\"$PAT_TOKEN\"}")

# Check if successful
if echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✅ GitHub PAT stored successfully!"
    echo ""
    echo "🔒 Your PAT is encrypted and stored securely in the database"
    echo "📁 Database location: /root/.xionimus_ai/xionimus.db"
    echo ""
    echo "Next steps:"
    echo "  1. Your .env file is now safe to commit (no secrets)"
    echo "  2. All GitHub features are ready to use"
    echo "  3. Restart services if needed: supervisorctl restart backend"
    echo ""
else
    echo "❌ Failed to store GitHub PAT"
    echo "Response: $RESPONSE"
    exit 1
fi

# Verify storage
echo "🔍 Verifying configuration..."
STATUS=$(curl -s http://localhost:8001/api/v1/github/admin/github-pat/status)

if echo "$STATUS" | grep -q '"configured":true'; then
    echo "✅ Verification successful - GitHub PAT is active"
else
    echo "⚠️  Warning: PAT stored but verification failed"
fi

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
