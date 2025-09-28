#!/bin/bash

echo "==========================================="
echo "   EMERGENT-NEXT - INSTALLATION"
echo "==========================================="
echo ""
echo "[INFO] Modern Development Platform Installation"
echo ""

# Wechsle ins Skript-Verzeichnis
cd "$(dirname "$0")"

# Prüfe Projektstruktur
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "[ERROR] Please run this script from the emergent-next root directory"
    exit 1
fi

echo "[SUCCESS] Project structure validated"
echo ""

# ==========================================
echo "[STEP 1/4] SYSTEM REQUIREMENTS CHECK"
echo "=========================================="

# Check Python
echo "[CHECK] Python 3.10+ installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3.10+ required"
    echo "[INFO] Install from: https://python.org"
    exit 1
else
    python3 --version
    echo "[SUCCESS] Python available"
fi

# Check Node.js
echo "[CHECK] Node.js 18+ installation..."
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js 18+ required"
    echo "[INFO] Install from: https://nodejs.org"
    exit 1
else
    node --version
    echo "[SUCCESS] Node.js available"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "[ERROR] npm required"
    exit 1
else
    npm --version
    echo "[SUCCESS] npm available"
fi

echo ""

# ==========================================
echo "[STEP 2/4] BACKEND SETUP"
echo "=========================================="

cd backend

echo "[CREATE] Backend environment files..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017/emergent_next

# AI API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PERPLEXITY_API_KEY=

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO

# Security
SECRET_KEY=emergent-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
EOF
    echo "[SUCCESS] Backend .env created"
else
    echo "[INFO] Backend .env already exists"
fi

echo "[INSTALL] Backend dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Backend dependencies installed"
else
    echo "[ERROR] Backend installation failed"
    echo "[INFO] Some features may not work"
fi

cd ..

echo ""

# ==========================================
echo "[STEP 3/4] FRONTEND SETUP"
echo "=========================================="

cd frontend

echo "[CREATE] Frontend environment files..."
if [ ! -f ".env" ]; then
    echo "VITE_BACKEND_URL=http://localhost:8001" > .env
    echo "[SUCCESS] Frontend .env created"
else
    echo "[INFO] Frontend .env already exists"
fi

echo "[INSTALL] Frontend dependencies with npm..."
# Clean installation
if [ -d "node_modules" ]; then
    echo "[INFO] Removing existing node_modules for clean install"
    rm -rf node_modules package-lock.json
fi

npm install
if [ $? -eq 0 ]; then
    echo "[SUCCESS] Frontend dependencies installed"
    echo "[INFO] Packages installed: $(ls -1 node_modules 2>/dev/null | wc -l)"
    
    # Validate key dependencies
    if [ -d "node_modules/react" ]; then
        echo "[SUCCESS] React installed"
    fi
    
    if [ -d "node_modules/vite" ]; then
        echo "[SUCCESS] Vite installed"
    fi
    
    if [ -d "node_modules/@chakra-ui" ]; then
        echo "[SUCCESS] Chakra UI installed"
    fi
else
    echo "[ERROR] Frontend installation failed"
    echo "[INFO] Try manual installation: cd frontend && npm install"
fi

cd ..

echo ""

# ==========================================
echo "[STEP 4/4] SYSTEM VALIDATION"
echo "=========================================="

echo "[TEST] Configuration files..."
if [ -f "backend/.env" ]; then
    echo "✅ Backend .env"
else
    echo "❌ Backend .env missing"
fi

if [ -f "frontend/.env" ]; then
    echo "✅ Frontend .env"
else
    echo "❌ Frontend .env missing"
fi

echo ""
echo "[TEST] Dependencies..."
if [ -f "backend/requirements.txt" ] && [ -f "frontend/package.json" ]; then
    echo "✅ Dependency files present"
else
    echo "❌ Missing dependency files"
fi

echo ""

# ==========================================
echo "[INSTALLATION COMPLETE]"
echo "=========================================="

echo ""
echo "✅ EMERGENT-NEXT INSTALLATION SUCCESSFUL!"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "[START] Launch the platform:"
echo "    npm run dev              # Both services"
echo "    npm run start:backend   # Backend only"
echo "    npm run start:frontend  # Frontend only"
echo ""
echo "[ACCESS] After starting:"
echo "    → Platform: http://localhost:3000"
echo "    → API:      http://localhost:8001"
echo "    → API Docs: http://localhost:8001/docs"
echo ""
echo "🔑 CONFIGURATION:"
echo "    → Open http://localhost:3000"
echo "    → Go to Settings"
echo "    → Add your AI API keys:"
echo "      • OpenAI API Key (for GPT models)"
echo "      • Anthropic API Key (for Claude)"
echo "      • Perplexity API Key (for research)"
echo ""
echo "🎯 READY TO BUILD!"
echo ""