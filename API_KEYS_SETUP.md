# API Keys Setup Guide

Complete guide for obtaining and configuring AI provider API keys for Xionimus AI.

---

## 🔑 Required API Keys

Xionimus AI supports three AI providers. You need **at least one** to use the chat functionality.

### Supported Providers
1. **OpenAI** - GPT-4.1 for general conversation and coding
2. **Anthropic** - Claude Opus 4.1 for reasoning and analysis
3. **Perplexity** - Sonar Pro for real-time research and web search

---

## 📋 API Key Setup Instructions

### 1. OpenAI API Key

**Best for:** General conversations, coding assistance, complex problem-solving

#### Steps:
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-proj-...`)

#### Configuration:
```env
# In /app/backend/.env
OPENAI_API_KEY=sk-proj-your-key-here
```

#### Available Models:
- `gpt-4.1` - Latest GPT-4 model (recommended)
- `gpt-4o` - Optimized GPT-4
- `o1` - Reasoning model (experimental)
- `o3` - Advanced reasoning model (experimental)

#### Pricing:
- Check [OpenAI Pricing](https://openai.com/pricing)
- Pay-as-you-go model
- Typical cost: $0.01-0.03 per request

---

### 2. Anthropic API Key

**Best for:** Complex reasoning, detailed analysis, research workflows

#### Steps:
1. Visit [Anthropic Console](https://console.anthropic.com/keys)
2. Sign in or create an account
3. Navigate to **API Keys** section
4. Click **"Create Key"**
5. Copy the key (starts with `sk-ant-...`)

#### Configuration:
```env
# In /app/backend/.env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

#### Available Models:
- `claude-opus-4-1-20250805` - Latest Claude Opus 4.1 (recommended)
- `claude-sonnet-4-5-20250929` - Claude Sonnet 4.5 (faster)
- `claude-4-sonnet-20250514` - Claude 4 Sonnet

#### Pricing:
- Check [Anthropic Pricing](https://www.anthropic.com/pricing)
- Pay-as-you-go model
- Typical cost: $0.015-0.075 per request

---

### 3. Perplexity API Key

**Best for:** Real-time web research, current information, fact-checking

#### Steps:
1. Visit [Perplexity API Settings](https://www.perplexity.ai/settings/api)
2. Sign in or create an account
3. Navigate to **API** section
4. Click **"Generate API Key"**
5. Copy the key (starts with `pplx-...`)

#### Configuration:
```env
# In /app/backend/.env
PERPLEXITY_API_KEY=pplx-your-key-here
```

#### Available Models:
- `sonar-pro` - Best for research and synthesis (recommended)
- `sonar` - Default free model
- `sonar-deep-research` - Deep research with reasoning

#### Pricing:
- Check [Perplexity Pricing](https://www.perplexity.ai/hub/pricing)
- Free tier available
- Pro tier: $20/month

---

## 🛠️ Backend Configuration

### Step 1: Create .env File
```bash
cd /app/backend
cp .env.example .env
```

### Step 2: Edit .env File
```env
# Add your API keys
OPENAI_API_KEY=sk-proj-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here

# Database (default is fine for local development)
MONGO_URL=mongodb://localhost:27017/xionimus_ai

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
```

### Step 3: Restart Backend
```bash
sudo supervisorctl restart backend
```

---

## 🎨 Frontend Configuration

### Option 1: Settings Page (Recommended)
1. Open Xionimus AI in browser
2. Navigate to **Settings** page
3. Enter your API keys in the **AI Provider API Keys** section
4. Click **Save API Keys**

**Note:** Keys are stored securely in browser localStorage

### Option 2: Manual Configuration
1. Open browser DevTools (F12)
2. Go to **Application** → **Local Storage**
3. Add key `xionimus_ai_api_keys` with value:
```json
{
  "openai": "sk-proj-your-key",
  "anthropic": "sk-ant-your-key",
  "perplexity": "pplx-your-key"
}
```

---

## ✅ Verify Configuration

### Backend Verification
1. Check backend logs:
```bash
tail -f /var/log/supervisor/backend.*.log
```

2. Look for messages like:
```
✅ OpenAI provider available
✅ Anthropic provider available
✅ Perplexity provider available
```

### Frontend Verification
1. Open **Settings** page
2. Check **System Status** card
3. Look for "X/3 AI Providers Configured"
4. Each provider should show **"Configured"** badge

### Health Check
```bash
curl http://localhost:8001/api/health
```

Look for:
```json
{
  "status": "healthy",
  "services": {
    "ai_providers": {
      "configured": 3,
      "total": 3,
      "status": {
        "openai": true,
        "anthropic": true,
        "perplexity": true
      }
    }
  }
}
```

---

## 🔐 Security Best Practices

### ✅ DO:
- Store API keys in `.env` file (never commit to git)
- Use environment variables for production
- Rotate keys regularly
- Monitor usage and costs
- Set rate limits on provider dashboards

### ❌ DON'T:
- Commit `.env` file to version control
- Share API keys publicly
- Hardcode keys in source code
- Use personal keys in production
- Store keys in frontend code (use backend proxy)

---

## 💰 Cost Management

### Recommended Settings
```env
# Rate Limiting (prevents cost explosions)
CHAT_RATE_LIMIT=30/minute
CODE_REVIEW_RATE_LIMIT=10/minute
```

### Monitor Usage
- **OpenAI:** [Usage Dashboard](https://platform.openai.com/usage)
- **Anthropic:** [Console Usage](https://console.anthropic.com/usage)
- **Perplexity:** [API Settings](https://www.perplexity.ai/settings/api)

### Set Spending Limits
Configure monthly spending limits on each provider's dashboard to prevent unexpected charges.

---

## 🆘 Troubleshooting

### "No API keys configured"
- Check `.env` file exists in `/app/backend/`
- Verify keys are not empty
- Restart backend service

### "Invalid API key provided"
- Check key format (OpenAI: `sk-proj-...`, Anthropic: `sk-ant-...`, Perplexity: `pplx-...`)
- Verify key is active on provider dashboard
- Check for whitespace or special characters

### "Rate limit exceeded"
- Wait for rate limit window to reset
- Adjust `CHAT_RATE_LIMIT` in `.env`
- Upgrade provider plan if needed

### "Provider not configured"
- Check backend logs for errors
- Verify `.env` file is loaded
- Restart backend service

---

## 📞 Support

### Provider Support
- **OpenAI:** [Help Center](https://help.openai.com/)
- **Anthropic:** [Support](https://support.anthropic.com/)
- **Perplexity:** [Discord](https://discord.gg/perplexity-ai)

### Application Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs
# Open browser DevTools (F12) → Console
```

---

**Ready to start? Configure your API keys and enjoy the power of multi-provider AI!** 🚀
