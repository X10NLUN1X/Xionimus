#!/bin/bash
# Verification Script for Autonomous Xionimus Agent System
# Run this to verify the installation is complete

echo "================================================"
echo "Xionimus Autonomous Agent - Verification"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
PASS=0
FAIL=0

# Function to check and report
check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAIL++))
    fi
}

echo "1. Checking Services..."
echo "------------------------"

# Check backend
sudo supervisorctl status backend | grep -q RUNNING
check $? "Backend service running"

# Check frontend
sudo supervisorctl status frontend | grep -q RUNNING
check $? "Frontend service running"

# Check backend health
curl -s http://localhost:8001/api/health > /dev/null 2>&1
check $? "Backend API responding"

echo ""
echo "2. Checking Agent Files..."
echo "------------------------"

# Check agent directory
[ -d "/app/agent" ]
check $? "Agent directory exists"

# Check agent files
[ -f "/app/agent/main.py" ]
check $? "main.py exists"

[ -f "/app/agent/file_watcher.py" ]
check $? "file_watcher.py exists"

[ -f "/app/agent/ws_client.py" ]
check $? "ws_client.py exists"

[ -f "/app/agent/requirements.txt" ]
check $? "requirements.txt exists"

[ -f "/app/agent/README.md" ]
check $? "README.md exists"

[ -f "/app/agent/config.example.json" ]
check $? "config.example.json exists"

echo ""
echo "3. Checking Backend Integration..."
echo "------------------------"

# Check backend files
[ -f "/app/backend/app/api/agent_ws.py" ]
check $? "agent_ws.py exists"

[ -f "/app/backend/app/api/agent_settings.py" ]
check $? "agent_settings.py exists"

[ -f "/app/backend/app/models/agent_models.py" ]
check $? "agent_models.py exists"

# Check if routes are registered
curl -s http://localhost:8001/docs | grep -q "agent" > /dev/null 2>&1
check $? "Agent routes registered in API"

echo ""
echo "4. Checking Frontend Integration..."
echo "------------------------"

[ -f "/app/frontend/src/pages/AgentSettingsPage.tsx" ]
check $? "AgentSettingsPage.tsx exists"

[ -f "/app/frontend/src/components/AgentStatusBadge.tsx" ]
check $? "AgentStatusBadge.tsx exists"

grep -q "AgentSettingsPage" /app/frontend/src/App.tsx > /dev/null 2>&1
check $? "Agent route registered in App.tsx"

echo ""
echo "5. Checking Documentation..."
echo "------------------------"

[ -f "/app/AUTONOMOUS_AGENT.md" ]
check $? "AUTONOMOUS_AGENT.md exists"

[ -f "/app/TESTING_GUIDE.md" ]
check $? "TESTING_GUIDE.md exists"

[ -f "/app/install_agent.bat" ]
check $? "install_agent.bat exists"

[ -f "/app/install_agent.ps1" ]
check $? "install_agent.ps1 exists"

echo ""
echo "6. Checking Configuration..."
echo "------------------------"

# Check if .env has placeholder for CLAUDE_API_KEY
grep -q "CLAUDE_API_KEY" /app/backend/.env > /dev/null 2>&1
check $? ".env has CLAUDE_API_KEY entry"

# Check if it's commented (placeholder)
grep -q "^#.*CLAUDE_API_KEY" /app/backend/.env > /dev/null 2>&1
check $? "CLAUDE_API_KEY is placeholder (not configured)"

# Check .env.example
grep -q "CLAUDE_API_KEY" /app/backend/.env.example > /dev/null 2>&1
check $? ".env.example has CLAUDE_API_KEY"

echo ""
echo "7. Testing Agent Dependencies..."
echo "------------------------"

# Check if watchdog is available
python3 -c "import watchdog" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    check 0 "watchdog library available"
else
    echo -e "${YELLOW}⚠${NC} watchdog not installed (run: pip install -r /app/agent/requirements.txt)"
    ((FAIL++))
fi

# Check if websockets is available
python3 -c "import websockets" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    check 0 "websockets library available"
else
    echo -e "${YELLOW}⚠${NC} websockets not installed (run: pip install -r /app/agent/requirements.txt)"
    ((FAIL++))
fi

echo ""
echo "8. Testing Backend APIs..."
echo "------------------------"

# Test status endpoint (should require auth)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/agent/status)
if [ "$HTTP_CODE" == "401" ]; then
    check 0 "Status API requires authentication"
else
    check 1 "Status API authentication issue (got $HTTP_CODE, expected 401)"
fi

echo ""
echo "================================================"
echo "Verification Summary"
echo "================================================"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next Steps:"
    echo "1. Add CLAUDE_API_KEY to /app/backend/.env"
    echo "2. Restart backend: sudo supervisorctl restart backend"
    echo "3. Follow TESTING_GUIDE.md for comprehensive testing"
    echo "4. Access agent settings: http://localhost:3000/agent"
else
    echo -e "${YELLOW}⚠ Some checks failed. Review the output above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Install agent dependencies: pip install -r /app/agent/requirements.txt"
    echo "- Restart services: sudo supervisorctl restart all"
    echo "- Check logs: tail -f /var/log/supervisor/backend.err.log"
fi

echo ""
