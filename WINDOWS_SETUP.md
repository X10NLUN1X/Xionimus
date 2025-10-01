# Xionimus AI - Windows Setup Guide

Complete setup guide for running Xionimus AI on Windows.

---

## 📋 Prerequisites

### Required Software
1. **Python 3.10 or higher**
   - Download: https://www.python.org/downloads/
   - ⚠️ **Important:** Check "Add Python to PATH" during installation

2. **Node.js 18 or higher**
   - Download: https://nodejs.org/
   - Includes npm/yarn package managers

3. **MongoDB Community Edition**
   - Download: https://www.mongodb.com/try/download/community
   - Or use MongoDB Atlas (cloud): https://www.mongodb.com/cloud/atlas

4. **Git** (optional, for version control)
   - Download: https://git-scm.com/download/win

---

## 🚀 Installation Steps

### Step 1: Extract/Clone Project

```powershell
# If you have Git
git clone <your-repository-url>
cd Xionimus-Genesis

# Or extract the ZIP file to a directory like:
# C:\AI\Xionimus-Genesis
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment
```powershell
cd backend
python -m venv venv
```

#### 2.2 Activate Virtual Environment
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# CMD
.\venv\Scripts\activate.bat
```

#### 2.3 Install Dependencies

**🔥 IMPORTANT for Windows:** Use the Windows-specific requirements file:

```powershell
pip install --upgrade pip
pip install -r requirements-windows.txt
```

**Why Windows-specific?**
- Uses `python-magic-bin` (includes Windows binaries for libmagic)
- Excludes Linux-only packages like `uvloop`
- Optimized for Windows compatibility

**Alternative (if error persists):**
```powershell
# Install minimal dependencies first
pip install fastapi uvicorn pydantic anthropic openai httpx tenacity python-magic-bin aiofiles python-dotenv

# Then install rest
pip install -r requirements.txt
```

#### 2.4 Configure Environment Variables
```powershell
# Copy example file
copy .env.example .env

# Edit .env file with your API keys
notepad .env
```

**Minimum configuration for .env:**
```env
# Database (local MongoDB)
MONGO_URL=mongodb://localhost:27017/xionimus_ai

# At least one AI provider API key
OPENAI_API_KEY=sk-proj-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
PERPLEXITY_API_KEY=pplx-your-key-here

# Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-generated-secret-key-here

# Application
DEBUG=true
HOST=0.0.0.0
PORT=8001
```

#### 2.5 Generate Secret Key (optional but recommended)
```powershell
# PowerShell
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the output and paste into .env as SECRET_KEY
```

### Step 3: Frontend Setup

#### 3.1 Install Dependencies
```powershell
cd ..\frontend
npm install
# OR
yarn install
```

#### 3.2 Configure Environment Variables
```powershell
# Copy example file
copy .env.example .env

# Edit if needed (default should work)
notepad .env
```

**Default .env for frontend:**
```env
VITE_BACKEND_URL=http://localhost:8001
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Step 4: MongoDB Setup (Local)

#### Option A: Local MongoDB Installation
1. Install MongoDB Community Edition
2. Start MongoDB service:
   ```powershell
   # Using Windows Services
   net start MongoDB
   
   # Or using MongoDB Compass
   # Open MongoDB Compass and connect to: mongodb://localhost:27017
   ```

#### Option B: MongoDB Atlas (Cloud)
1. Create free account: https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string
4. Update `MONGO_URL` in backend `.env`:
   ```env
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/xionimus_ai
   ```

---

## 🎯 Running the Application

### Method 1: Two Separate Terminals (Recommended for Development)

#### Terminal 1 - Backend
```powershell
cd C:\AI\Xionimus-Genesis\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
🚀 Xionimus AI Backend starting...
✅ OpenAI provider available
✅ Rate limiting enabled
```

#### Terminal 2 - Frontend
```powershell
cd C:\AI\Xionimus-Genesis\frontend
npm run dev
# OR
yarn dev
```

**Expected output:**
```
  VITE v5.x.x  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://192.168.x.x:3000/
```

### Method 2: Using Start Scripts

Create `start-backend.bat`:
```batch
@echo off
cd /d C:\AI\Xionimus-Genesis\backend
call venv\Scripts\activate.bat
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
pause
```

Create `start-frontend.bat`:
```batch
@echo off
cd /d C:\AI\Xionimus-Genesis\frontend
call npm run dev
pause
```

---

## ✅ Verify Installation

### 1. Check Backend Health
Open browser or use curl:
```powershell
# PowerShell
Invoke-WebRequest -Uri http://localhost:8001/api/health | Select-Object -Expand Content

# Or open in browser
start http://localhost:8001/api/health
```

**Expected response:**
```json
{
  "status": "limited",
  "version": "2.0.0",
  "platform": "Xionimus AI",
  "services": {
    "database": {
      "status": "connected"
    },
    "ai_providers": {
      "configured": 1
    }
  }
}
```

### 2. Check Frontend
Open in browser:
```powershell
start http://localhost:3000
```

You should see the Xionimus AI chat interface.

### 3. Test API Keys
1. Go to Settings page
2. Check "System Status" card
3. Should show "1/3 AI Providers Configured" (or more)

---

## 🔧 Troubleshooting

### Error: "FileNotFoundError: [WinError 3]"
**Cause:** Windows path compatibility issue  
**Solution:** Already fixed in latest code (uses `tempfile.gettempdir()`)

### Error: "python is not recognized"
**Cause:** Python not in PATH  
**Solution:** 
1. Reinstall Python with "Add to PATH" checked
2. Or manually add Python to PATH:
   - Search "Environment Variables" in Windows
   - Edit PATH
   - Add: `C:\Users\YourUser\AppData\Local\Programs\Python\Python3XX`

### Error: "ModuleNotFoundError: No module named 'fastapi'"
**Cause:** Dependencies not installed  
**Solution:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements-windows.txt  # Use Windows-specific file
```

### Error: "ImportError: failed to find libmagic"
**Cause:** `python-magic` needs libmagic.dll on Windows  
**Solution:**
```powershell
# Uninstall python-magic and install python-magic-bin
pip uninstall python-magic -y
pip install python-magic-bin

# Or use Windows requirements file
pip install -r requirements-windows.txt
```

**What's the difference?**
- `python-magic` - Requires system libmagic library (Linux/Mac)
- `python-magic-bin` - Includes libmagic.dll for Windows ✅

### Error: "MongoDB connection failed"
**Cause:** MongoDB not running  
**Solution:**
```powershell
# Start MongoDB service
net start MongoDB

# Or check MongoDB Compass connection
```

### Error: "Port 8001 already in use"
**Cause:** Another process using port  
**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8001

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in backend/.env
PORT=8002
```

### Error: "VITE build failed"
**Cause:** Node modules not installed  
**Solution:**
```powershell
cd frontend
rm -r node_modules
rm package-lock.json
npm install
```

### Warning: "SECRET_KEY not set"
**Not critical for development**  
**Solution for production:**
```powershell
# Generate key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to backend/.env
SECRET_KEY=<generated-key>
```

---

## 🔐 API Keys Setup

### Required: At least ONE AI provider

#### OpenAI (Recommended for beginners)
1. Visit: https://platform.openai.com/api-keys
2. Create account / Sign in
3. Click "Create new secret key"
4. Copy key (starts with `sk-proj-...`)
5. Add to backend `.env`:
   ```env
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

#### Anthropic (Best for reasoning)
1. Visit: https://console.anthropic.com/keys
2. Create account / Sign in
3. Click "Create Key"
4. Copy key (starts with `sk-ant-...`)
5. Add to backend `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

#### Perplexity (Best for research)
1. Visit: https://www.perplexity.ai/settings/api
2. Create account / Sign in
3. Generate API key
4. Copy key (starts with `pplx-...`)
5. Add to backend `.env`:
   ```env
   PERPLEXITY_API_KEY=pplx-your-key-here
   ```

**See `API_KEYS_SETUP.md` for detailed instructions.**

---

## 📁 Windows Directory Structure

```
C:\AI\Xionimus-Genesis\
├── backend\
│   ├── venv\                 # Python virtual environment
│   ├── app\                  # Application code
│   ├── main.py               # Backend entry point
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Configuration (create from .env.example)
│
├── frontend\
│   ├── node_modules\         # Node dependencies
│   ├── src\                  # React source code
│   ├── package.json          # Node dependencies list
│   └── .env                  # Configuration (create from .env.example)
│
└── Data directories (auto-created):
    └── %USERPROFILE%\.xionimus_ai\
        ├── xionimus.db       # SQLite database
        ├── chroma_db\        # Vector database
        ├── workspaces\       # User workspaces
        └── temp_uploads\     # Temporary files
```

---

## 🚀 Production Deployment (Windows Server)

### Using IIS + Windows Service

1. **Install IIS with FastCGI**
2. **Install wfastcgi**
   ```powershell
   pip install wfastcgi
   wfastcgi-enable
   ```

3. **Configure IIS site for Python backend**
4. **Build frontend for production**
   ```powershell
   cd frontend
   npm run build
   ```

5. **Configure IIS site for frontend** (serve `dist/` folder)

**Or use PM2 for Node.js process management:**
```powershell
npm install -g pm2-windows-startup
pm2 start backend\start.py --name xionimus-backend
pm2 start frontend\server.js --name xionimus-frontend
pm2 save
pm2-startup install
```

---

## 🆘 Additional Support

### Check Logs

**Backend logs:**
```powershell
# View in console (if running in terminal)
# Or check Python error output

# Enable detailed logging in .env
LOG_LEVEL=DEBUG
```

**Frontend logs:**
- Open browser DevTools (F12)
- Go to Console tab

### Get Help

1. Check documentation:
   - `README.md` - Overview
   - `API_KEYS_SETUP.md` - API key setup
   - `PROJECT_STATUS.md` - Project details

2. Common issues:
   - Path issues → Use absolute paths
   - Permission issues → Run as Administrator
   - Port conflicts → Change ports in `.env`

---

## ✨ Next Steps

1. ✅ Backend running on http://localhost:8001
2. ✅ Frontend running on http://localhost:3000
3. ✅ MongoDB connected
4. ✅ At least one AI provider configured

**You're ready to use Xionimus AI! Open http://localhost:3000 and start chatting!** 🎉

---

**For Linux/Mac setup, see `README.md`**
