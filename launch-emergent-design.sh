#!/bin/bash

echo "🎨 Launching Emergent.sh Clone Design..."

# Kill existing processes
echo "⏹️ Stopping existing services..."
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "yarn.*dev" 2>/dev/null || true

# Give processes time to stop
sleep 2

echo "🚀 Starting backend with luxury theme..."
cd /app/emergent-next/backend
python main.py > backend_luxury.log 2>&1 &
BACKEND_PID=$!

echo "⏳ Waiting for backend to initialize..."
sleep 5

echo "🎯 Starting frontend with Emergent.sh design..."
cd /app/emergent-next/frontend
yarn dev > frontend_luxury.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "✨ EMERGENT.SH CLONE LAUNCHED ✨"
echo ""
echo "🎨 Design Features:"
echo "  ✅ Luxury Black & Gold color scheme"
echo "  ✅ Left sidebar navigation (collapsible)"
echo "  ✅ Clean, minimal Emergent.sh layout"
echo "  ✅ Dark/light theme toggle"
echo "  ✅ Responsive design (desktop + mobile)"
echo "  ✅ Gradient effects and blur backgrounds"
echo "  ✅ Smooth animations and transitions"
echo ""
echo "🖥️  Services:"
echo "  - Backend: http://localhost:8002 (PID: $BACKEND_PID)"
echo "  - Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "🎯 Features to Test:"
echo "  1. Collapsible sidebar (hamburger icon)"
echo "  2. Theme toggle (light/dark switch)"
echo "  3. Provider selection with color coding"
echo "  4. Luxury message bubbles with gradients"
echo "  5. Mobile responsive layout"
echo "  6. Smooth hover animations"
echo ""
echo "📱 Mobile Test:"
echo "  - Resize browser to mobile size"
echo "  - Sidebar becomes drawer"
echo "  - All functionality preserved"
echo ""
echo "🔧 New Components:"
echo "  - EmergentLayout.tsx (main layout clone)"
echo "  - EmergentChatInterface.tsx (chat UI clone)"
echo "  - Luxury theme with Emergent.sh colors"
echo ""
echo "📋 To stop: pkill -f 'python.*main.py' && pkill -f 'yarn.*dev'"