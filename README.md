# 🚀 Xionimus AI

> **All-in-One AI Development Suite** - Your intelligent coding companion powered by multi-agent AI systems

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/yourusername/xionimus-ai)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18.x-blue.svg)](https://reactjs.org/)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Local Installation](#-local-installation)
- [Google Cloud Deployment](#-google-cloud-platform-deployment)
- [Configuration](#-configuration)
- [API Provider Setup](#-api-provider-setup)
- [Usage Guide](#-usage-guide)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Xionimus AI** is a cutting-edge, cloud-native AI development platform that combines multiple specialized AI agents, code execution capabilities, and advanced research tools into a single, elegant interface. Built with modern web technologies and powered by state-of-the-art language models (Claude, GPT, Perplexity), it transforms how developers interact with AI.

### What Makes Xionimus AI Special?

- 🤖 **8 Specialized AI Agents** - Each agent is an expert in its domain
- 🔬 **Deep Research Capabilities** - Powered by Perplexity Sonar with PDF export
- ⚡ **7-Language Code Execution** - Run Python, JavaScript, C++, C, C#, Perl, Bash
- 🎨 **Glossy Black-Gold UI** - Professional, responsive design with animations
- 🔐 **Enterprise Security** - JWT authentication, rate limiting, encrypted storage
- 📚 **Research History** - Auto-save with MongoDB cloud sync and PDF export
- 🔗 **GitHub Integration** - Full push/pull/import/export capabilities
- 🚦 **Developer Modes** - Junior (fast) and Senior (premium quality) modes

---

## ✨ Key Features

### 🤖 Multi-Agent System

**8 Specialized Agents:**
1. **Research Agent** 🔍 - Deep web research with Perplexity Sonar
2. **Code Review Agent** 👁️ - Expert code quality analysis
3. **Testing Agent** 🧪 - Automated test generation and validation
4. **Documentation Agent** 📝 - Comprehensive documentation generation
5. **Debugging Agent** 🐛 - Advanced error detection and fixes
6. **Security Agent** 🔒 - Security vulnerability scanning
7. **Performance Agent** ⚡ - Performance optimization recommendations
8. **Fork Agent** 🔀 - Project forking and branching assistance

**Autonomous Agent Routing** - Automatically selects the best agent based on your query

### 💻 Cloud Sandbox Execution

Execute code in **7 languages** with isolated, secure execution:
- Python 3.11+
- JavaScript (Node.js)
- Bash/Shell
- C++ (g++)
- C (gcc)
- C# (Mono)
- Perl

**Features:**
- Memory limits and timeouts
- Process isolation
- Error handling and compilation support
- Real-time output streaming

### 📚 Research & Export

- **Deep Research** - Leverages Perplexity Sonar Deep Research
- **PDF Export** - Individual and bulk export with rich formatting
- **MongoDB Storage** - Cloud sync with offline localStorage backup
- **Search & Filter** - Find past research instantly
- **Favorites** - Mark important research for quick access

### 🎨 User Interface

- **Glossy Black-Gold Theme** - Professional, modern design
- **Responsive** - Works on desktop, tablet, and mobile
- **German Localization** - Built-in i18n support
- **Smooth Animations** - Micro-interactions for better UX
- **Developer Modes** - 🌱 Junior (fast) | 🚀 Senior (quality)

### 🔐 Security & Authentication

- **JWT Authentication** - Secure token-based auth
- **Rate Limiting** - Endpoint-specific quotas
- **Encrypted API Keys** - Per-user secure storage
- **6 Security Headers** - CORS, CSP, HSTS, X-Frame-Options, etc.
- **Session Management** - SQLite with persistence

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- SQLite (User data & sessions)
- MongoDB (Research history)
- Redis (Caching - optional)
- PostgreSQL (Future pgvector support)

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Vite (Build tool)
- Chakra UI (Components)

**AI Providers:**
- Anthropic Claude (Sonnet 4.5, Opus 4.1, Haiku 3.5)
- OpenAI GPT (GPT-4, GPT-5)
- Perplexity (Sonar, Sonar Deep Research)

**Infrastructure:**
- Supervisor (Process management)
- MongoDB (NoSQL database)
- Nginx (Reverse proxy - optional)

### Project Structure

```
/app
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── core/           # Core services (auth, agents, etc.)
│   │   ├── models/         # Pydantic models
│   │   └── main.py         # Application entry point
│   ├── .env               # Backend configuration
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   ├── .env              # Frontend configuration
│   └── package.json       # Node dependencies
│
└── Documents/             # Documentation & test results
```

---

## 📋 Prerequisites

### Required Software

- **Python** 3.11 or higher ([Download](https://www.python.org/downloads/))
- **Node.js** 18.x or higher ([Download](https://nodejs.org/))
- **Yarn** package manager (`npm install -g yarn`)
- **MongoDB** 6.0+ ([Download](https://www.mongodb.com/try/download/community))
- **Git** ([Download](https://git-scm.com/downloads))

### Optional

- **Redis** 7.x (for caching)
- **PostgreSQL** 15+ (for future pgvector support)

### API Keys (Required for Full Functionality)

You'll need API keys from at least one of these providers:

1. **Anthropic** - [Get API Key](https://console.anthropic.com/)
2. **OpenAI** - [Get API Key](https://platform.openai.com/api-keys)
3. **Perplexity** - [Get API Key](https://www.perplexity.ai/settings/api)
4. **GitHub** (optional) - [Create Token](https://github.com/settings/tokens)

---

## 🚀 Local Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/xionimus-ai.git
cd xionimus-ai
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env file and add your API keys (see Configuration section)
nano .env
```

### Step 3: Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
yarn install

# Configure environment
# Copy .env.example to .env (already configured for local development)
# No changes needed for local setup
```

### Step 4: Database Setup

```bash
# Start MongoDB (in a new terminal)
# On macOS:
brew services start mongodb-community

# On Linux:
sudo systemctl start mongod

# On Windows:
# MongoDB runs as a service automatically after installation
```

### Step 5: Start the Application

**Option A: Using Supervisor (Recommended)**

```bash
# From project root
sudo supervisorctl start all

# Check status
sudo supervisorctl status

# Expected output:
# backend    RUNNING
# frontend   RUNNING
# mongodb    RUNNING
```

**Option B: Manual Start (Development)**

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 - Frontend
cd frontend
yarn dev

# Terminal 3 - MongoDB (if not running as service)
mongod --dbpath /path/to/data/directory
```

### Step 6: Access the Application

Open your browser and navigate to:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Documentation:** http://localhost:8001/docs

**Default Credentials:**
- Username: `demo`
- Password: `demo123`

---

## ☁️ Google Cloud Platform Deployment

### Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed ([Install](https://cloud.google.com/sdk/docs/install))
- Domain name (optional but recommended)

### Step 1: Set Up GCP Project

```bash
# Create new project
gcloud projects create xionimus-ai-prod --name="Xionimus AI"

# Set as active project
gcloud config set project xionimus-ai-prod

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable mongodb.googleapis.com
gcloud services enable dns.googleapis.com
```

### Step 2: Create Compute Engine Instance

```bash
# Create VM instance
gcloud compute instances create xionimus-ai-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-4 \
  --boot-disk-size=50GB \
  --boot-disk-type=pd-balanced \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --tags=http-server,https-server

# Create firewall rules
gcloud compute firewall-rules create allow-http \
  --allow tcp:80 \
  --target-tags http-server

gcloud compute firewall-rules create allow-https \
  --allow tcp:443 \
  --target-tags https-server

gcloud compute firewall-rules create allow-app \
  --allow tcp:8001,tcp:3000 \
  --target-tags http-server
```

### Step 3: Set Up MongoDB Atlas (Recommended)

Instead of self-hosting MongoDB, use MongoDB Atlas (free tier available):

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create database user
4. Whitelist GCP VM IP address
5. Get connection string
6. Update `MONGO_URL` in backend `.env`

### Step 4: Deploy Application to GCP

```bash
# SSH into VM
gcloud compute ssh xionimus-ai-vm --zone=us-central1-a

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Yarn
sudo npm install -g yarn

# Install MongoDB (if not using Atlas)
# Follow: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/

# Clone repository
git clone https://github.com/yourusername/xionimus-ai.git
cd xionimus-ai

# Backend setup
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
yarn install
yarn build

# Configure environment variables
cd ../backend
nano .env
# Add your API keys and MongoDB connection string
```

### Step 5: Set Up Nginx (Reverse Proxy)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/xionimus-ai
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Frontend
    location / {
        root /home/your-username/xionimus-ai/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/xionimus-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Set Up Supervisor

```bash
# Install Supervisor
sudo apt install supervisor -y

# Create Supervisor configuration
sudo nano /etc/supervisor/conf.d/xionimus-ai.conf
```

Add this configuration:

```ini
[program:xionimus-backend]
directory=/home/your-username/xionimus-ai/backend
command=/home/your-username/xionimus-ai/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
user=your-username
autostart=true
autorestart=true
stderr_logfile=/var/log/xionimus-backend.err.log
stdout_logfile=/var/log/xionimus-backend.out.log

[program:mongodb]
command=/usr/bin/mongod --config /etc/mongod.conf
user=mongodb
autostart=true
autorestart=true
stderr_logfile=/var/log/mongodb.err.log
stdout_logfile=/var/log/mongodb.out.log
```

Start services:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

### Step 7: Set Up SSL with Let's Encrypt (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### Step 8: Configure Domain (If Using Custom Domain)

1. Go to your domain registrar
2. Add an A record pointing to your GCP VM's external IP:
   ```
   Type: A
   Name: @
   Value: [YOUR_VM_EXTERNAL_IP]
   TTL: 300
   ```

3. Wait for DNS propagation (5-30 minutes)

### Step 9: Update Frontend Configuration

```bash
# On your local machine, update frontend/.env
VITE_API_URL=https://your-domain.com/api

# Rebuild frontend
cd frontend
yarn build

# Upload to GCP VM
scp -r dist/* your-username@your-vm-ip:/home/your-username/xionimus-ai/frontend/dist/
```

---

## ⚙️ Configuration

### Backend Configuration (`backend/.env`)

```bash
# Authentication
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Server
DEBUG=false  # Set to false in production
HOST=0.0.0.0
PORT=8001

# Databases
MONGO_URL=mongodb://localhost:27017/xionimus_ai  # Or MongoDB Atlas connection string
REDIS_URL=redis://localhost:6379/0

# AI Provider API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...  # Your Anthropic API key
OPENAI_API_KEY=sk-proj-...          # Your OpenAI API key
PERPLEXITY_API_KEY=pplx-...         # Your Perplexity API key
GITHUB_TOKEN=ghp_...                # Your GitHub Personal Access Token

# Encryption (for secure API key storage)
ENCRYPTION_KEY=your-encryption-key  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Frontend Configuration (`frontend/.env`)

```bash
# Backend API URL
VITE_API_URL=http://localhost:8001/api  # Local
# VITE_API_URL=https://api.yourdomain.com/api  # Production

# Application Info
VITE_APP_NAME=Xionimus AI
VITE_APP_VERSION=2.1.0

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_ANALYTICS=false

# GitHub OAuth (optional)
VITE_GITHUB_CLIENT_ID=your-github-oauth-client-id
```

---

## 🔑 API Provider Setup

### Anthropic Claude

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-api03-`)
6. Add to `backend/.env`: `ANTHROPIC_API_KEY=sk-ant-api03-...`

**Pricing (as of 2024):**
- Claude 3.5 Haiku: ~$0.80 per 1M tokens
- Claude 3.5 Sonnet: ~$3 per 1M tokens
- Claude 4 Opus: ~$15 per 1M tokens

### OpenAI GPT

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create new secret key**
5. Copy the key (starts with `sk-proj-`)
6. Add to `backend/.env`: `OPENAI_API_KEY=sk-proj-...`

**Pricing (as of 2024):**
- GPT-4: ~$30 per 1M input tokens, ~$60 per 1M output tokens
- GPT-3.5 Turbo: ~$0.50 per 1M input tokens, ~$1.50 per 1M output tokens

### Perplexity Sonar

1. Go to [Perplexity Settings](https://www.perplexity.ai/settings/api)
2. Sign up or log in
3. Click **Generate API Key**
4. Copy the key (starts with `pplx-`)
5. Add to `backend/.env`: `PERPLEXITY_API_KEY=pplx-...`

**Pricing (as of 2024):**
- Sonar: ~$1 per 1M tokens
- Sonar Deep Research: ~$5 per 1M tokens (includes web search)

### GitHub Token (Optional)

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:user` (Read user profile data)
4. Generate and copy token (starts with `ghp_`)
5. Add to `backend/.env`: `GITHUB_TOKEN=ghp_...`

---

## 📚 Usage Guide

### First Login

1. Navigate to http://localhost:3000
2. Login with default credentials:
   - **Username:** `demo`
   - **Password:** `demo123`
3. Go to **Settings** (⚙️ icon)
4. Add your API keys for each provider
5. Click **Save** for each provider

### Developer Modes

**🌱 Junior Developer Mode** (Fast & Budget-Friendly)
- Uses Claude 3.5 Haiku
- ~73% cheaper than Senior mode
- Best for: Learning, quick prototypes, simple tasks

**🚀 Senior Developer Mode** (Premium Quality)
- Uses Claude 4 Sonnet + Opus with smart routing
- Includes Ultra-Thinking for complex problems
- Best for: Production code, debugging, architecture

Toggle between modes using the buttons in the chat header.

### Using AI Agents

**Autonomous Mode** (Recommended)
- Simply type your request
- System automatically selects the best agent
- Example: "Review this code for security issues"

**Manual Agent Selection**
- Click the agent selector dropdown
- Choose specific agent (Research, Code Review, etc.)
- Agent remains selected until changed

### Code Execution

```python
# Type or paste code, select language, click "Execute"
# Example Python:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
```

Supported languages:
- Python, JavaScript, Bash, C++, C, C#, Perl

### Research with PDF Export

1. Type research query: "What are the latest trends in AI development?"
2. Wait for deep research to complete
3. Click **📜 Research History** button
4. Select research items (checkbox)
5. Click **Export Selected** or **Export PDF** for individual items
6. PDF downloads automatically with rich formatting

### GitHub Integration

**Export to GitHub:**
1. Click **GitHub** dropdown
2. Select **Export to GitHub**
3. Enter repository name
4. Choose branch (main/master)
5. Add commit message
6. Click **Push to GitHub**

**Import from GitHub:**
1. Click **GitHub** dropdown
2. Select **Import from GitHub**
3. Enter repository URL
4. Click **Import Repository**

---

## 🔧 Troubleshooting

### Backend Issues

**Issue: Backend won't start**
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Common fixes:
# 1. Check if port 8001 is in use
sudo lsof -i :8001
# 2. Activate virtual environment
source venv/bin/activate
# 3. Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue: MongoDB connection failed**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod

# Check connection string in .env
# Should be: MONGO_URL=mongodb://localhost:27017/xionimus_ai
```

**Issue: API keys not working**
```bash
# Verify API keys are set in .env
grep "API_KEY" backend/.env

# Test API key manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

### Frontend Issues

**Issue: Frontend shows "Cannot connect to backend"**
```bash
# 1. Check backend is running
curl http://localhost:8001/api/health

# 2. Check VITE_API_URL in frontend/.env
# Should be: VITE_API_URL=http://localhost:8001/api

# 3. Rebuild frontend
cd frontend
yarn build
sudo supervisorctl restart frontend
```

**Issue: Blank page after login**
```bash
# Check browser console for errors (F12)
# Common fix: Clear browser cache and localStorage
# In browser console:
localStorage.clear()
sessionStorage.clear()
# Then refresh page
```

**Issue: Send button not working**
```bash
# This is a known issue with CSS z-index
# Workaround: Use Enter key to send messages
# Or force-restart frontend:
cd frontend
rm -rf dist node_modules/.vite
yarn install
yarn build
sudo supervisorctl restart frontend
```

### Database Issues

**Issue: "Database is locked" error**
```bash
# SQLite database locked
# Stop all services
sudo supervisorctl stop all

# Remove lock file
rm /app/backend/xionimus_auth.db-journal

# Restart services
sudo supervisorctl start all
```

**Issue: MongoDB storage issues**
```bash
# Check disk space
df -h

# Check MongoDB logs
tail -f /var/log/mongodb/mongod.log

# Repair MongoDB
mongod --repair --dbpath /var/lib/mongodb
```

### Performance Issues

**Issue: Slow response times**
```bash
# 1. Check system resources
htop  # or top

# 2. Check MongoDB performance
# In mongo shell:
db.currentOp()

# 3. Enable Redis caching
# In backend/.env, verify:
REDIS_URL=redis://localhost:6379/0
# Then restart backend
```

**Issue: High memory usage**
```bash
# Check memory usage by service
sudo supervisorctl status

# Restart memory-heavy services
sudo supervisorctl restart backend frontend

# Increase swap if needed (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
cd backend
pip install -r requirements-dev.txt  # If exists

cd ../frontend
yarn add -D @types/node  # TypeScript types
```

### Code Style

- **Python:** Follow PEP 8, use Black formatter
- **TypeScript/React:** Use ESLint + Prettier
- **Commits:** Follow [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic** for Claude AI models
- **OpenAI** for GPT models
- **Perplexity** for Sonar research capabilities
- **FastAPI** for the excellent Python framework
- **React** & **Tailwind CSS** for frontend tools
- **MongoDB** for flexible data storage

---

## 📞 Support

For questions, issues, or feature requests:

- 📧 Email: support@xionimus.ai
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/xionimus-ai/issues)
- 💬 Discord: [Join our community](https://discord.gg/xionimus-ai)
- 📖 Documentation: [docs.xionimus.ai](https://docs.xionimus.ai)

---

## 🗺️ Roadmap

- [x] Phase 1-5: Core functionality (Complete)
- [ ] Phase 6: Plugin system & API marketplace
- [ ] Phase 7: Advanced deployment & scaling
- [ ] Phase 8: Team collaboration features
- [ ] Phase 9: Mobile apps (iOS & Android)
- [ ] Phase 10: Enterprise features

---

**Made with ❤️ by the Xionimus AI Team**

⭐ Star us on GitHub if you find this project useful!

