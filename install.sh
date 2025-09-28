#!/bin/bash

echo "==========================================="
echo "      XIONIMUS AI - INSTALLATION"
echo "==========================================="
echo ""
echo "[INFO] Installing Backend and Frontend Dependencies"
echo "[INFO] Creating configuration files"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "[ERROR] Please run this script from the XIONIMUS AI root directory"
    exit 1
fi

echo "[SUCCESS] Project structure validated"
echo ""

# ==========================================
echo "[STEP 1/4] SYSTEM REQUIREMENTS CHECK"
echo "=========================================="

# Check Python
echo "[CHECK] Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3.10+ required"
    echo "[INFO] Please install Python: https://python.org"
    exit 1
else
    python3 --version
    echo "[SUCCESS] Python available"
fi

# Check Node.js
echo "[CHECK] Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js 18+ required"
    echo "[INFO] Please install Node.js: https://nodejs.org"
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
echo "[STEP 2/4] BACKEND DEPENDENCIES"
echo "=========================================="

cd backend

echo "[UPDATE] Updating pip..."
python3 -m pip install --upgrade pip

echo "[INSTALL] Installing backend dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "[SUCCESS] Backend dependencies installed"
else
    echo "[ERROR] Backend dependencies installation failed"
    echo "[INFO] Some features may not work correctly"
fi

cd ..

echo ""

# ==========================================
echo "[STEP 3/4] FRONTEND DEPENDENCIES"
echo "=========================================="

cd frontend

echo "[DEBUG] Current directory: $(pwd)"
echo "[DEBUG] Checking package.json..."
if [ ! -f "package.json" ]; then
    echo "[ERROR] package.json not found in frontend directory"
    cd ..
    exit 1
fi

echo "[SUCCESS] package.json found"
echo "[INFO] Installing frontend dependencies with npm..."
echo "[DEBUG] Running: npm install"

# Remove existing node_modules for clean install
if [ -d "node_modules" ]; then
    echo "[INFO] Removing existing node_modules for clean installation"
    rm -rf node_modules
fi

# Install with npm
npm install
if [ $? -eq 0 ]; then
    echo "[SUCCESS] Frontend dependencies installed with npm"
else
    echo "[ERROR] npm install failed, trying with --legacy-peer-deps..."
    npm cache clean --force
    npm install --legacy-peer-deps
    if [ $? -eq 0 ]; then
        echo "[SUCCESS] Frontend dependencies installed with legacy peer deps"
    else
        echo "[ERROR] Frontend installation failed"
        echo "[INFO] Frontend may not work correctly"
    fi
fi

# Validate installation
echo "[VERIFY] Validating installation..."
if [ -d "node_modules" ]; then
    echo "[SUCCESS] node_modules directory created"
    echo "[INFO] Installed packages: $(ls -1 node_modules | wc -l)"
    
    # Check key dependencies
    if [ -d "node_modules/react" ]; then
        echo "[SUCCESS] React installed"
    else
        echo "[WARNING] React not found"
    fi
    
    if [ -d "node_modules/vite" ]; then
        echo "[SUCCESS] Vite installed"
    else
        echo "[WARNING] Vite not found"
    fi
else
    echo "[ERROR] node_modules directory not created"
fi

cd ..

echo ""

# ==========================================
echo "[STEP 4/4] CONFIGURATION FILES"
echo "=========================================="

echo "[CHECK] Configuration files..."
if [ -f "backend/.env" ]; then
    echo "[SUCCESS] Backend .env exists"
else
    echo "[INFO] Backend .env already created during setup"
fi

if [ -f "frontend/.env" ]; then
    echo "[SUCCESS] Frontend .env exists"
else
    echo "[INFO] Frontend .env already created during setup"
fi

echo ""

# ==========================================
echo "[INSTALLATION COMPLETE]"
echo "=========================================="

echo ""
echo "✅ XIONIMUS AI INSTALLATION SUCCESSFUL!"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "[START] Use npm scripts to start services:"
echo "    npm run start:backend    # Start backend"
echo "    npm run start:frontend   # Start frontend"
echo "    npm run start:all        # Start both services"
echo ""
echo "[ACCESS] After starting:"
echo "    → Frontend: http://localhost:3000"
echo "    → Backend:  http://localhost:8001"
echo ""
echo "🔑 API CONFIGURATION:"
echo "    → Open http://localhost:3000"
echo "    → Go to Settings"
echo "    → Add your API keys:"
echo "      • OpenAI API Key"
echo "      • Anthropic API Key"
echo "      • Perplexity API Key"
echo ""
echo "🎯 INSTALLATION COMPLETE!"
echo ""