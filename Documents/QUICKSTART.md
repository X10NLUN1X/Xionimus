# Quick Start Guide - Autonomous Xionimus Agent

Get the autonomous agent running in **5 minutes**.

---

## Prerequisites Check

```bash
# Run verification script
bash /app/verify_agent_setup.sh
```

✅ Should show **26+ passed checks**

---

## Option 1: Quick Demo (Local Testing)

### Step 1: Add API Key

```bash
# Edit backend .env file
nano /app/backend/.env

# Uncomment and add your Claude API key:
CLAUDE_API_KEY=sk-ant-api03-your-key-here

# Save: Ctrl+X, Y, Enter
```

### Step 2: Restart Backend

```bash
sudo supervisorctl restart backend

# Wait 3 seconds for restart
sleep 3

# Verify backend is healthy
curl -s http://localhost:8001/api/health | jq -r '.status'
# Should output: limited or healthy
```

### Step 3: Setup Test Environment

```bash
# Create test directory
mkdir -p /tmp/test_projects

# Install agent dependencies
cd /app/agent
pip install -r requirements.txt

# Create config
cat > config.json << 'EOF'
{
  "backend_url": "http://localhost:8001",
  "watch_directories": [
    "/tmp/test_projects"
  ]
}
EOF
```

### Step 4: Start the Agent

```bash
# Start agent (in background)
cd /app/agent
nohup python main.py --config config.json > agent.log 2>&1 &

# Check if running
ps aux | grep "python.*main.py"

# View logs
tail -f agent.log
```

**Expected output:**
```
================================================
🚀 Xionimus Autonomous Agent
================================================
Agent ID: [uuid]
Backend: http://localhost:8001
Watching 1 directories:
  📁 /tmp/test_projects
================================================
✅ Agent is running. Press Ctrl+C to stop.
🟢 Xionimus Agent: CONNECTED
```

### Step 5: Test File Detection

```bash
# In another terminal, create a test file
cat > /tmp/test_projects/test.py << 'EOF'
def divide(a, b):
    # Bug: no zero check
    return a / b

result = divide(10, 0)  # This will crash!
EOF
```

**Check agent log:**
```bash
tail -f /app/agent/agent.log
```

**Expected:**
```
File created: /tmp/test_projects/test.py
Sent file event: created
Received message: analysis_result
📊 Analysis for /tmp/test_projects/test.py:
  ERROR: ZeroDivisionError risk on line 3
  WARNING: Missing input validation
```

### Step 6: Access Web Dashboard

1. Open browser: http://localhost:3000
2. Login: **demo** / **demo123**
3. Look for **AGENT** badge in header
   - Should show: 🟢 AGENT (green)
4. Click badge or navigate to: http://localhost:3000/agent
5. You should see:
   - ✅ Agent status: Connected
   - ✅ Agent count: 1
   - ✅ Watch directories configured

---

## Option 2: Windows User Setup

### For End Users (Windows PC)

**1. Download Agent Files**
- Copy `/app/agent/` folder to Windows PC
- Location: `C:\Users\YourName\XionimusAgent\`

**2. Install Python**
- Download: https://www.python.org/downloads/
- ✅ Check "Add Python to PATH"
- Install

**3. Run Installer**
```cmd
cd C:\Users\YourName\XionimusAgent
install_agent.bat
```

**4. Configure**
- Edit `agent\config.json`:
  ```json
  {
    "backend_url": "http://your-server:8001",
    "watch_directories": [
      "C:\\Users\\YourName\\Documents\\Projects",
      "C:\\Users\\YourName\\Code"
    ]
  }
  ```

**5. Start Agent**
```cmd
python agent\main.py --config agent\config.json
```

**6. Configure via Web UI**
- Navigate to: http://your-server:3000/agent
- Add/remove directories
- Configure AI models
- Set notification preferences

---

## Verification Checklist

After starting the agent:

- [ ] **Backend running**: `sudo supervisorctl status backend`
- [ ] **Agent connected**: Check `agent.log` for "CONNECTED"
- [ ] **Web badge green**: http://localhost:3000 shows 🟢 AGENT
- [ ] **File detection works**: Save a file in watched directory
- [ ] **Analysis running**: Check logs for analysis results
- [ ] **Web UI accessible**: http://localhost:3000/agent works

---

## Troubleshooting

### Agent Won't Start

**Error: "Module not found"**
```bash
cd /app/agent
pip install -r requirements.txt
```

**Error: "Connection refused"**
```bash
# Check backend is running
sudo supervisorctl status backend

# Check backend URL in config.json
cat /app/agent/config.json | grep backend_url
```

### Agent Connects But No Analysis

**Check Claude API Key:**
```bash
grep CLAUDE_API_KEY /app/backend/.env
# Should NOT be commented with #
```

**Test Claude API:**
```bash
CLAUDE_KEY=$(grep CLAUDE_API_KEY /app/backend/.env | cut -d '=' -f2)
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4.5-20250514","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}' | jq
```

### Web UI Shows Gray Badge

**Status: ⚫ AGENT (disconnected)**

1. Check agent is running:
   ```bash
   ps aux | grep "python.*main.py"
   ```

2. Check agent logs:
   ```bash
   tail -f /app/agent/agent.log
   ```

3. Check WebSocket connection:
   ```bash
   # Look for WebSocket errors
   grep -i websocket /app/agent/agent.log
   ```

---

## Next Steps

Once basic setup works:

1. **Production Deployment**
   - Use HTTPS for backend
   - Configure proper CORS
   - Set up monitoring

2. **Advanced Configuration**
   - Custom analysis rules
   - Team settings
   - Notification webhooks

3. **IDE Integration**
   - VS Code extension (future)
   - JetBrains plugin (future)

---

## Support

**Documentation:**
- Complete Guide: `/app/AUTONOMOUS_AGENT.md`
- Testing Guide: `/app/TESTING_GUIDE.md`
- Agent README: `/app/agent/README.md`

**Logs:**
- Agent: `/app/agent/agent.log` or `nohup.out`
- Backend: `/var/log/supervisor/backend.err.log`
- Frontend: `/var/log/supervisor/frontend.err.log`

**Health Checks:**
```bash
# Backend health
curl http://localhost:8001/api/health

# Agent status (requires login token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8001/api/agent/status
```

---

**🎉 You're all set! Start coding and let the agent analyze in real-time!**
