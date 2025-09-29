#!/bin/bash

echo "🚨 Applying Emergency Bug Fixes..."

# Kill existing processes
echo "⏹️ Stopping existing services..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "yarn.*dev" 2>/dev/null || true

# Give processes time to stop
sleep 2

echo "🔄 Starting fixed backend..."
cd /app/emergent-next/backend
python main.py > backend_fixed.log 2>&1 &
BACKEND_PID=$!

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🔄 Starting frontend..."
cd /app/emergent-next/frontend
yarn dev > frontend_fixed.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "✅ Emergency fixes applied!"
echo ""
echo "🔧 Fixed Issues:"
echo "  - Database boolean check error (critical)"
echo "  - Automatic model selection for each provider"
echo "  - API key whitespace trimming" 
echo "  - Provider-specific default models"
echo ""
echo "📊 Services:"
echo "  - Backend: http://localhost:8002 (PID: $BACKEND_PID)"
echo "  - Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "🧪 Test Steps:"
echo "  1. Open http://localhost:3000"
echo "  2. Go to Settings → Add your API keys → Save"
echo "  3. Go to AI Chat → Select different providers" 
echo "  4. Notice models auto-change per provider"
echo "  5. Send test messages"
echo ""
echo "📋 To stop: pkill -f 'python.*main.py' && pkill -f 'yarn.*dev'"