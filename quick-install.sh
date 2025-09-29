#!/bin/bash

# =============================================================================
# Emergent-Next Quick Installation Script
# =============================================================================
# Fast installation script for development environments
# =============================================================================

set -e

echo "🚀 Emergent-Next Quick Install Starting..."

# Navigate to project directory
cd /app/emergent-next

echo "📦 Installing Backend Dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "📦 Installing Frontend Dependencies..."
cd ../frontend
rm -f package-lock.json
rm -rf node_modules 2>/dev/null || true
yarn install

echo "🔧 Creating startup script..."
cd ..
cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Emergent-Next Development Environment..."

# Kill existing processes
pkill -f "python.*main.py" || true
pkill -f "yarn.*dev" || true

# Start MongoDB if not running
sudo systemctl start mongod 2>/dev/null || true

# Start backend
cd /app/emergent-next/backend
source venv/bin/activate
python main.py > backend.log 2>&1 &
echo "✅ Backend started on http://localhost:8002"

# Start frontend
cd /app/emergent-next/frontend
yarn dev > frontend.log 2>&1 &
echo "✅ Frontend starting on http://localhost:3000"

echo ""
echo "🎉 Emergent-Next is starting up!"
echo "📖 Backend API: http://localhost:8002/docs"
echo "🖥️  Frontend App: http://localhost:3000"
echo ""
echo "📋 To stop: pkill -f 'python.*main.py' && pkill -f 'yarn.*dev'"
EOF

chmod +x start-dev.sh

echo ""
echo "✅ Quick installation completed!"
echo ""
echo "🎯 Next steps:"
echo "   1. cd /app/emergent-next"
echo "   2. ./start-dev.sh"
echo "   3. Open http://localhost:3000"
echo ""