# Testing Guide for Xionimus Autonomous Agent

This guide will help you test the autonomous agent system once API keys are configured.

---

## Prerequisites

Before testing, you need to add API keys to the backend `.env` file:

### Required API Keys

1. **Claude API Key** (for code analysis)
   - Get from: https://console.anthropic.com/settings/keys
   - Add to `/app/backend/.env`:
   ```env
   CLAUDE_API_KEY=sk-ant-api03-your-key-here
   ```

2. **Restart Backend** after adding keys:
   ```bash
   sudo supervisorctl restart backend
   ```

---

## Phase 1: Backend API Testing

### 1. Test Agent Settings API

**Get Settings:**
```bash
# Login first to get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo","password":"demo123"}' | jq -r '.access_token')

# Get agent settings
curl -s -X GET http://localhost:8001/api/agent/settings \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": "demo",
  "watch_directories": [],
  "sonnet_enabled": true,
  "opus_enabled": true,
  "auto_analysis_enabled": true,
  "suggestions_enabled": true,
  "notification_level": "all"
}
```

### 2. Test Agent Status API

```bash
curl -s -X GET http://localhost:8001/api/agent/status \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Expected Response:**
```json
{
  "connected": false,
  "agent_count": 0,
  "last_activity": null,
  "last_connection": null
}
```

### 3. Update Agent Settings

```bash
curl -s -X PUT http://localhost:8001/api/agent/settings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "watch_directories": ["C:\\Users\\Test\\Projects"],
    "auto_analysis_enabled": true,
    "notification_level": "all"
  }' | jq
```

---

## Phase 2: Local Agent Testing

### 1. Install Agent Dependencies

```bash
cd /app/agent
pip install -r requirements.txt
```

### 2. Create Test Configuration

Create `/app/agent/config.json`:
```json
{
  "backend_url": "http://localhost:8001",
  "watch_directories": [
    "/app/test_projects"
  ]
}
```

### 3. Create Test Project Directory

```bash
mkdir -p /app/test_projects
cd /app/test_projects

# Create a test Python file
cat > test_script.py << 'EOF'
def calculate_sum(a, b):
    # Bug: no type checking
    result = a + b
    return result

# Security issue: eval is dangerous
user_input = input("Enter expression: ")
eval(user_input)
EOF
```

### 4. Start the Agent

```bash
cd /app/agent
python main.py --config config.json
```

**Expected Output:**
```
================================================
🚀 Xionimus Autonomous Agent
================================================
Agent ID: [uuid]
Backend: http://localhost:8001
Watching 1 directories:
  📁 /app/test_projects
================================================
✅ Agent is running. Press Ctrl+C to stop.
🟢 Xionimus Agent: CONNECTED
```

### 5. Test File Change Detection

In another terminal:
```bash
# Modify the test file
echo "print('Hello, World!')" >> /app/test_projects/test_script.py
```

**Expected Agent Output:**
```
File modified: /app/test_projects/test_script.py
Sent file event: modified - /app/test_projects/test_script.py
```

**Expected Analysis (if Claude API configured):**
```
📊 Analysis for /app/test_projects/test_script.py:
  WARNING: eval() usage is a security risk (line 9)
  INFO: Consider adding type hints to function parameters
  INFO: Input validation recommended before eval
```

---

## Phase 3: Frontend Testing

### 1. Access Agent Settings Page

1. Login to Xionimus: http://localhost:3000
2. Navigate to: http://localhost:3000/agent
3. Or click the "AGENT" badge in the header

### 2. Test Agent Status Badge

**Before starting agent:**
- Badge should show: ⚫ AGENT (gray)
- Status: "Nicht verbunden"

**After starting agent:**
- Badge should show: 🟢 AGENT (green)
- Status: "Verbunden"
- Agent count: 1

### 3. Test Directory Management

1. In Agent Settings page, add a directory:
   - Click "Hinzufügen"
   - Enter: `/app/test_projects`
   - Should appear in list with green checkmark

2. Save settings:
   - Click "Einstellungen speichern"
   - Should see success toast

3. Verify in agent:
   - Agent should receive updated configuration
   - Check agent logs for "Settings updated" message

### 4. Test Activity Log

1. Make several file changes in watched directory
2. Refresh Agent Settings page
3. Check "Activity" section (if implemented)
4. Should see list of file events with timestamps

---

## Phase 4: End-to-End Testing

### Full Workflow Test

1. **Start Fresh:**
   ```bash
   # Stop agent if running
   pkill -f "python.*main.py"
   
   # Clear test directory
   rm -rf /app/test_projects/*
   ```

2. **Configure via Web UI:**
   - Go to http://localhost:3000/agent
   - Add directory: `/app/test_projects`
   - Enable all features
   - Save settings

3. **Start Agent:**
   ```bash
   cd /app/agent
   python main.py --config config.json
   ```

4. **Create New File:**
   ```bash
   cat > /app/test_projects/hello.js << 'EOF'
   function greet(name) {
       console.log("Hello " + name)
   }
   
   greet()  // Bug: missing argument
   EOF
   ```

5. **Verify:**
   - Agent detects file creation
   - Backend receives file content
   - Claude analyzes the code
   - Issues identified:
     * Missing argument in function call
     * Consider using template literals
     * Add parameter validation

6. **Modify File:**
   ```bash
   echo "// Fixed version" >> /app/test_projects/hello.js
   echo "greet('World')" >> /app/test_projects/hello.js
   ```

7. **Check Status:**
   - Web UI shows agent connected
   - Activity log shows 2 events (create + modify)
   - Analysis results available

---

## Troubleshooting Tests

### Agent Won't Connect

**Check 1: Backend Running**
```bash
sudo supervisorctl status backend
# Should show: backend RUNNING
```

**Check 2: WebSocket Endpoint**
```bash
curl -s http://localhost:8001/api/agent/status
# Should return 401 (needs auth) not 404
```

**Check 3: Agent Logs**
```bash
tail -f /app/agent/xionimus_agent.log
```

### No Analysis Results

**Check 1: Claude API Key**
```bash
grep CLAUDE_API_KEY /app/backend/.env
# Should show: CLAUDE_API_KEY=sk-ant-api03-...
```

**Check 2: Backend Logs**
```bash
tail -f /var/log/supervisor/backend.err.log | grep -i claude
```

**Check 3: Test Claude API Directly**
```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $CLAUDE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4.5-20250514",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }' | jq
```

### File Changes Not Detected

**Check 1: Directory Exists**
```bash
ls -la /app/test_projects
```

**Check 2: File Watcher Running**
```bash
ps aux | grep "python.*main.py"
```

**Check 3: Supported File Type**
Supported: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.html`, `.css`, `.json`, `.md`

### Frontend Badge Not Updating

**Check 1: Login Status**
```bash
# Check if token exists
# In browser console:
localStorage.getItem('token')
```

**Check 2: API Call**
```bash
# Should work with valid token
curl -s -X GET http://localhost:8001/api/agent/status \
  -H "Authorization: Bearer $TOKEN"
```

**Check 3: React State**
- Open browser DevTools
- Check Network tab for `/api/agent/status` calls
- Should poll every 10 seconds

---

## Performance Testing

### Load Test: Multiple Files

```bash
# Create 10 test files rapidly
for i in {1..10}; do
  echo "console.log('Test $i')" > /app/test_projects/test_$i.js
  sleep 0.5
done
```

**Expected:**
- Agent processes all 10 files
- No crashes or memory leaks
- Backend handles WebSocket messages
- Analysis completes for each file

### Stress Test: Large File

```bash
# Create 100KB file
python3 << 'EOF'
with open('/app/test_projects/large.py', 'w') as f:
    for i in range(3000):
        f.write(f"def function_{i}():\n    pass\n\n")
EOF
```

**Expected:**
- Agent sends file content
- Backend processes without timeout
- Claude API call succeeds (if under 1MB limit)

### Endurance Test: Long Running

```bash
# Run agent for 1 hour with periodic changes
for i in {1..60}; do
  echo "# Update $i" >> /app/test_projects/test.py
  sleep 60
done
```

**Check:**
- Agent stays connected
- No memory leaks
- WebSocket heartbeat active
- All events processed

---

## Success Criteria

### ✅ Backend Tests Pass
- [ ] Agent settings API responds correctly
- [ ] Status API shows connection state
- [ ] Activity logging works
- [ ] Authentication required for all endpoints

### ✅ Agent Tests Pass
- [ ] Agent connects to backend
- [ ] File changes detected
- [ ] WebSocket messages sent
- [ ] Reconnection works after disconnect

### ✅ Analysis Tests Pass
- [ ] Claude API key configured
- [ ] Code analysis returns results
- [ ] Issues identified correctly
- [ ] Suggestions make sense

### ✅ Frontend Tests Pass
- [ ] Agent badge shows correct status
- [ ] Settings page accessible
- [ ] Directory management works
- [ ] Real-time updates function

### ✅ Integration Tests Pass
- [ ] End-to-end workflow completes
- [ ] Multiple file types supported
- [ ] Performance acceptable
- [ ] No crashes or errors

---

## Next Steps After Testing

Once all tests pass:

1. **Production Deployment:**
   - Use HTTPS for backend
   - Configure CORS properly
   - Set up monitoring
   - Enable backups

2. **Windows Agent Distribution:**
   - Package as .exe (PyInstaller)
   - Create installer
   - Add to startup
   - User documentation

3. **Feature Enhancements:**
   - IDE extensions
   - Real-time notifications
   - Team collaboration
   - Custom analysis rules

---

## Test Data Cleanup

```bash
# Clean up test files
rm -rf /app/test_projects
rm -f /app/agent/xionimus_agent.log
rm -f /app/agent/config.json

# Reset database (optional)
# Backup first!
# sqlite3 ~/.xionimus_ai/xionimus.db "DELETE FROM agent_connections;"
# sqlite3 ~/.xionimus_ai/xionimus.db "DELETE FROM agent_activities;"
```

---

**Ready to test! 🚀**

Add API keys → Run tests → Report results
