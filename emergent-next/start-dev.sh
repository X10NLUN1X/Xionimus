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
