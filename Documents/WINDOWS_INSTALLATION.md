# 🪟 Xionimus AI - Windows Installation Guide

Complete guide for installing and running Xionimus AI on Windows 10/11.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Steps](#installation-steps)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [Known Limitations](#known-limitations)

---

## Prerequisites

### Required Software

1. **Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ **IMPORTANT:** Check "Add Python to PATH" during installation
   - Verify: `python --version`

2. **Node.js 18.x+**
   - Download from [nodejs.org](https://nodejs.org/)
   - LTS version recommended
   - Verify: `node --version`

3. **Yarn Package Manager**
   ```powershell
   npm install -g yarn
   ```
   - Verify: `yarn --version`

4. **MongoDB Community Edition**
   - Download from [mongodb.com](https://www.mongodb.com/try/download/community)
   - Choose "Windows" platform
   - Install as a service (default option)
   - Verify: `mongosh --version`

5. **Git for Windows**
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use Git Bash terminal for Unix-like commands

### Optional Tools

- **Visual Studio Code** - [Download](https://code.visualstudio.com/)
- **Windows Terminal** - [Microsoft Store](https://aka.ms/terminal)
- **MongoDB Compass** (GUI) - [Download](https://www.mongodb.com/products/compass)

---

## Installation Steps

### Step 1: Clone the Repository

Open **PowerShell** or **Git Bash**:

```powershell
# Create project directory
mkdir C:\AI
cd C:\AI

# Clone repository
git clone https://github.com/yourusername/xionimus-ai.git
cd xionimus-ai
```

### Step 2: Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Windows-specific packages (optional)
pip install python-magic-bin  # For MIME type detection
```

### Step 3: Frontend Setup

Open a **new PowerShell window**:

```powershell
cd C:\AI\xionimus-ai\frontend

# Install dependencies
yarn install
```

### Step 4: MongoDB Setup

MongoDB should be running as a Windows service. To verify:

```powershell
# Check if MongoDB service is running
Get-Service MongoDB

# If not running, start it:
Start-Service MongoDB

# Connect to verify it works
mongosh

# In mongosh, type:
show dbs
exit
```

### Step 5: Configuration

#### Backend Configuration

Edit `C:\AI\xionimus-ai\backend\.env`:

```bash
# The file is auto-generated on first run, but you need to add API keys

# AI Provider API Keys (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here
GITHUB_TOKEN=ghp_your-token-here

# Database (default for Windows)
MONGO_URL=mongodb://localhost:27017/xionimus_ai

# Server settings (don't change for local development)
DEBUG=true
HOST=0.0.0.0
PORT=8001
```

**How to get API keys:** See [API Provider Setup](#api-provider-setup) section.

#### Frontend Configuration

The `frontend/.env` file is already configured for local development. No changes needed.

---

## Running the Application

### Method 1: Manual Start (Recommended for Windows)

**Terminal 1 - Backend:**
```powershell
cd C:\AI\xionimus-ai\backend
.\venv\Scripts\activate
python main.py
```

Expected output:
```
✅ Connected to MongoDB
✅ Backend started successfully
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Terminal 2 - Frontend:**
```powershell
cd C:\AI\xionimus-ai\frontend
yarn dev
```

Expected output:
```
  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Terminal 3 - MongoDB (if not running as service):**
```powershell
# Only needed if MongoDB service is not running
mongod --dbpath C:\data\db
```

### Method 2: Production Build

After development, you can build for production:

```powershell
# Build frontend
cd C:\AI\xionimus-ai\frontend
yarn build

# Serve with Python
cd ..\backend
.\venv\Scripts\activate
python main.py
```

The frontend build will be in `frontend/dist/` and served by the backend.

---

## API Provider Setup

### 1. Anthropic Claude

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-api03-`)
5. Add to `backend/.env`: 
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   ```

### 2. OpenAI GPT

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** → **Create new secret key**
4. Copy the key (starts with `sk-proj-`)
5. Add to `backend/.env`:
   ```
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

### 3. Perplexity Sonar

1. Go to [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Sign up or log in
3. Click **Generate API Key**
4. Copy the key (starts with `pplx-`)
5. Add to `backend/.env`:
   ```
   PERPLEXITY_API_KEY=pplx-your-key-here
   ```

### 4. GitHub Token (Optional)

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Select scopes: `repo`, `read:user`
4. Generate and copy token (starts with `ghp_`)
5. Add to `backend/.env`:
   ```
   GITHUB_TOKEN=ghp_your-token-here
   ```

---

## Using the Application

1. **Open browser:** http://localhost:3000

2. **Login with default credentials:**
   - Username: `demo`
   - Password: `demo123`

3. **Add your API keys:**
   - Click **Settings** (⚙️) in the top right
   - Enter API keys for each provider
   - Click **Save** for each provider

4. **Start using:**
   - Type your questions in the chat
   - Use **Developer Modes** (🌱 Junior / 🚀 Senior)
   - Try code execution, research, and more!

---

## Troubleshooting

### Issue 1: Python not found

```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Reinstall Python with "Add to PATH" checked
2. Or use `py` instead of `python`:
   ```powershell
   py -m venv venv
   py main.py
   ```

### Issue 2: Virtual environment won't activate

```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\activate
```

### Issue 3: MongoDB connection failed

```
MongoServerError: Authentication failed
```

**Solution:**
1. Check MongoDB service:
   ```powershell
   Get-Service MongoDB
   ```

2. Restart service if needed:
   ```powershell
   Restart-Service MongoDB
   ```

3. Verify connection string in `.env`:
   ```
   MONGO_URL=mongodb://localhost:27017/xionimus_ai
   ```

### Issue 4: Port already in use

```
ERROR: [Errno 10048] Only one usage of each socket address
```

**Solution:**
```powershell
# Find process using port 8001
netstat -ano | findstr :8001

# Kill the process (replace PID with actual number)
taskkill /PID 1234 /F
```

### Issue 5: Module not found errors

```
ModuleNotFoundError: No module named 'X'
```

**Solution:**
```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

### Issue 6: Frontend build fails

```
error An unexpected error occurred
```

**Solution:**
```powershell
cd frontend
# Clear cache
rd /s /q node_modules
rd /s /q .yarn

# Reinstall
yarn install
```

### Issue 7: Backend auto-generates minimal .env

```
🔧 AUTO-FIX: .env file not found - creating automatically...
```

**Solution:**
This is normal! The backend creates a basic `.env` file automatically. You just need to add your API keys to it.

```powershell
# Edit the file
notepad backend\.env

# Add your API keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
PERPLEXITY_API_KEY=pplx-...
```

### Issue 8: MIME type detection warning

```
⚠️ python-magic not available. MIME type detection disabled.
```

**Solution (Optional):**
```powershell
cd backend
.\venv\Scripts\activate
pip install python-magic-bin
```

---

## Known Limitations on Windows

### 1. Resource Limits Not Available

**Issue:** Windows doesn't support Unix `resource` module for memory/CPU limits.

**Impact:** Code execution sandbox has no hard memory limits (relies on timeout only).

**Mitigation:** 
- Timeouts still work (30 seconds default)
- Use trusted code only
- Monitor Task Manager during execution

### 2. Supervisor Not Available

**Issue:** Supervisor (process manager) is Unix-only.

**Impact:** Must start backend/frontend manually in separate terminals.

**Workaround:**
- Use **Task Scheduler** for auto-start
- Or create a batch script:

```batch
@echo off
start "MongoDB" mongod
start "Backend" cmd /k "cd C:\AI\xionimus-ai\backend && .\venv\Scripts\activate && python main.py"
start "Frontend" cmd /k "cd C:\AI\xionimus-ai\frontend && yarn dev"
```

### 3. No SIGTERM Support

**Issue:** Windows doesn't support Unix signals like SIGTERM.

**Impact:** Graceful shutdown may not work as expected.

**Workaround:** Use Ctrl+C to stop processes manually.

---

## Performance Tips

### 1. Use SSD for MongoDB Data

MongoDB performs better on SSDs:

```powershell
# Move MongoDB data directory to SSD
mongod --dbpath D:\MongoDB\data
```

### 2. Increase PowerShell Buffer

For better log viewing:

```powershell
# Set buffer size (in PowerShell profile)
$host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size(120, 3000)
```

### 3. Disable Windows Defender for Project Folder

(Optional, for faster development):

1. Open **Windows Security**
2. Go to **Virus & threat protection**
3. **Manage settings** → **Exclusions**
4. Add `C:\AI\xionimus-ai`

---

## VS Code Integration

### Recommended Extensions

- **Python** (Microsoft)
- **ESLint** (Microsoft)
- **Prettier** (Prettier)
- **MongoDB for VS Code** (MongoDB)
- **GitLens** (GitKraken)

### Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Backend",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

---

## Uninstallation

To remove Xionimus AI:

```powershell
# Stop all processes (Ctrl+C in each terminal)

# Remove project directory
cd C:\AI
rd /s /q xionimus-ai

# Stop and remove MongoDB service (if you want to remove MongoDB completely)
Stop-Service MongoDB
sc delete MongoDB

# Uninstall MongoDB via "Add or Remove Programs"
```

---

## Getting Help

If you encounter issues not covered here:

1. Check **Documents/test_result.md** for detailed test results
2. Look for similar issues in **Documents/** folder
3. Open an issue on GitHub with:
   - Your Windows version (`winver`)
   - Python version (`python --version`)
   - Node version (`node --version`)
   - Full error message
   - Steps to reproduce

---

## Next Steps

Once installed and running:

1. ✅ Complete the [Usage Guide](../README.md#usage-guide)
2. ✅ Learn about [Developer Modes](../README.md#developer-modes)
3. ✅ Try the [Code Execution Sandbox](../README.md#code-execution)
4. ✅ Explore [Research & PDF Export](../README.md#research--export)

---

**Happy Coding with Xionimus AI on Windows! 🚀**

