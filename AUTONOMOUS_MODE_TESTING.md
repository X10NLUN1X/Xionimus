# 🧪 Autonomous Mode Testing Guide

## Pre-Test Checklist

### 1. Configure OpenAI API Key

```bash
# Option A: Add to .env file
nano /app/backend/.env
# Add line: OPENAI_API_KEY=sk-proj-your-key-here

# Option B: Use Settings UI
# Login → Settings → AI Provider API Keys → Add OpenAI key
```

### 2. Restart Services (if needed)

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

### 3. Verify Services Running

```bash
sudo supervisorctl status
# Both backend and frontend should show RUNNING
```

---

## Testing Scenarios

### Scenario 1: Basic File Operations ✅

**Objective:** Test autonomous file reading and writing

**Steps:**
1. Login to Xionimus AI (demo/demo123)
2. Enable "🤖 Autonomer Modus" toggle in header
3. Send message: "Read the file /app/AUTONOMOUS_MODE_SETUP.md"
4. **Expected:**
   - See `action_start` for `read_file`
   - See `action_complete` with file contents
   - File contents displayed in chat

**Success Criteria:**
- ✅ Action appears in Autonomous Activity Stream
- ✅ Status changes from "Ausführung..." to "Erfolgreich"
- ✅ File contents shown in AI response

---

### Scenario 2: Create New File 📝

**Objective:** Test file creation capability

**Steps:**
1. Enable autonomous mode
2. Send: "Create a file /app/test_autonomous.txt with content 'Hello from Autonomous AI!'"
3. Verify file created: `cat /app/test_autonomous.txt`

**Expected:**
- Action stream shows `create_file`
- File exists with correct content
- AI confirms creation

**Cleanup:**
```bash
rm /app/test_autonomous.txt
```

---

### Scenario 3: Execute Bash Command 🖥️

**Objective:** Test command execution

**Steps:**
1. Enable autonomous mode
2. Send: "List all Python files in /app/backend/app/core"
3. Watch autonomous action execute `execute_bash` with `ls` command

**Expected:**
- Command executes successfully
- Output shows Python files
- Action history logs the command

---

### Scenario 4: Install Package 📦

**Objective:** Test package installation

**Steps:**
1. Enable autonomous mode
2. Send: "Install the Python package 'colorama'"
3. Watch `install_pip_package` action
4. Verify: `pip list | grep colorama`

**Expected:**
- Package installs (may take 10-30s)
- Execution time shown in activity stream
- Success message from AI

---

### Scenario 5: Multi-Tool Workflow 🔄

**Objective:** Test complex multi-step tasks

**Steps:**
1. Enable autonomous mode
2. Send: "Create a simple Python hello world script at /app/test_hello.py and then run it"
3. Watch multiple actions:
   - `create_file` for test_hello.py
   - `execute_bash` to run python script

**Expected:**
- Both actions execute sequentially
- Script output shown in AI response
- Activity stream shows 2+ actions

**Cleanup:**
```bash
rm /app/test_hello.py
```

---

### Scenario 6: Error Handling ❌

**Objective:** Test error recovery and display

**Steps:**
1. Enable autonomous mode
2. Send: "Read the file /app/nonexistent_file_12345.txt"
3. Watch action fail gracefully

**Expected:**
- Action shows "Fehler" status
- Error message displayed: "File not found"
- AI acknowledges error and suggests alternatives

---

### Scenario 7: Rollback Last Action ↩️

**Objective:** Test per-action rollback

**Steps:**
1. Enable autonomous mode
2. Send: "Create a file /app/test_rollback.txt with content 'Test'"
3. Wait for file creation
4. Click "Aktionsverlauf" button
5. Click "Letzte Aktion rückgängig machen"
6. Verify file deleted: `ls /app/test_rollback.txt` (should not exist)

**Expected:**
- Rollback succeeds
- File removed
- Toast notification confirms rollback

---

### Scenario 8: Rollback Entire Session 🔄

**Objective:** Test session-wide rollback

**Steps:**
1. Enable autonomous mode
2. Create 3 files:
   - "Create /app/test1.txt with content 'A'"
   - "Create /app/test2.txt with content 'B'"
   - "Create /app/test3.txt with content 'C'"
3. Wait for all 3 files created
4. Open "Aktionsverlauf"
5. Click "Gesamte Session zurücksetzen"
6. Verify all 3 files deleted

**Expected:**
- All files removed
- Action history cleared
- Confirmation toast shown

---

### Scenario 9: Dangerous Command Blocking 🛡️

**Objective:** Test security constraints

**Steps:**
1. Enable autonomous mode
2. Send: "Execute the command 'rm -rf /tmp/test'"
3. Watch action get blocked

**Expected:**
- Action fails with security error
- Error message: "Dangerous command blocked"
- AI explains why command was blocked

**Test Other Dangerous Commands:**
- "Run shutdown command"
- "Execute dd if=/dev/zero"
- "chmod -R 777 /app"

All should be blocked.

---

### Scenario 10: Action History Export 💾

**Objective:** Test action history logging

**Steps:**
1. Perform 5-10 autonomous actions
2. Open "Aktionsverlauf"
3. Click export icon (download button)
4. Verify JSON file downloaded
5. Open JSON and verify structure

**Expected JSON Structure:**
```json
[
  {
    "id": "action_...",
    "tool_name": "create_file",
    "arguments": {...},
    "result": {...},
    "success": true,
    "execution_time": "0.34",
    "created_at": "2025-..."
  }
]
```

---

## Performance Testing

### Test 1: Execution Speed ⚡

**Measure:**
- File read: < 0.5s
- File write: < 1.0s
- Bash command: < 2.0s
- Package install: 10-60s (varies)

**How to Check:**
- Execution time shown in action details
- Expand action in activity stream to see timing

---

### Test 2: Concurrent Actions 🔄

**Test:**
1. Send complex request requiring 5+ tool calls
2. Watch actions execute sequentially
3. Verify no race conditions

**Example:**
"Create 5 files: test1.txt through test5.txt, each with unique content"

**Expected:**
- All 5 files created
- No conflicts
- Actions in order

---

### Test 3: Execution Limit Safety 🚨

**Test:**
1. Try to trigger > 100 actions in one session
2. System should stop at 100

**How:**
"Create 150 files named file001.txt through file150.txt"

**Expected:**
- Stops at 100 actions
- Warning message shown
- Session reset required

---

## Integration Testing

### Test 1: WebSocket Reliability 📡

**Test:**
1. Enable autonomous mode
2. Send message
3. Close browser tab mid-execution
4. Reopen and check action history

**Expected:**
- Actions that completed are saved
- Incomplete actions marked as failed
- No data loss

---

### Test 2: Authentication & Authorization 🔐

**Test:**
1. Logout
2. Try to access `/api/autonomous/history/session_123`
3. Should get 401 Unauthorized

**Command:**
```bash
curl -X GET "http://localhost:3000/api/autonomous/history/session_123"
# Expected: 401 or redirect to login
```

---

### Test 3: Cross-Session Isolation 🔒

**Test:**
1. Create Session A with autonomous actions
2. Create Session B with different actions
3. Verify rollback in A doesn't affect B

**Expected:**
- Each session has independent checkpoint system
- Action histories are separate
- No cross-contamination

---

## UI/UX Testing

### Test 1: Toggle Behavior 🎚️

**Test:**
1. Toggle autonomous mode ON
2. Send message
3. Toggle OFF mid-execution

**Expected:**
- Message completes (can't interrupt mid-stream)
- Future messages use conversational mode
- Action history persists

---

### Test 2: Activity Stream Updates 📊

**Test:**
1. Enable autonomous mode
2. Send complex task
3. Watch activity stream update in real-time

**Expected:**
- Actions appear immediately when started
- Status updates smoothly (pending → executing → complete)
- No flickering or jumping

---

### Test 3: Responsive Design 📱

**Test:**
1. Enable autonomous mode
2. Resize browser window to mobile size
3. Verify activity stream still visible and usable

**Expected:**
- Activity stream adapts to screen size
- Buttons remain accessible
- Text wraps properly

---

## Edge Cases

### Edge Case 1: Empty File Write

**Test:** "Create an empty file /app/test_empty.txt"

**Expected:** File created with 0 bytes

---

### Edge Case 2: Very Long File Path

**Test:** "Create file /app/very/long/nested/path/that/does/not/exist/test.txt"

**Expected:** 
- Parent directories created automatically
- File created successfully

---

### Edge Case 3: Special Characters in Filename

**Test:** "Create file '/app/test file with spaces & special$chars.txt'"

**Expected:** 
- File created with exact name
- No escaping issues

---

### Edge Case 4: Concurrent User Sessions

**Test:**
1. Open 2 browser tabs
2. Enable autonomous mode in both
3. Send different requests

**Expected:**
- Each session independent
- No conflicts
- Action histories separate

---

## Troubleshooting

### Issue: "OpenAI API key not configured"

**Solution:**
1. Check `/app/backend/.env` has `OPENAI_API_KEY=...`
2. Restart backend: `sudo supervisorctl restart backend`
3. Verify in logs: `tail -f /var/log/supervisor/backend.*.log`

---

### Issue: Actions not appearing in stream

**Solution:**
1. Check browser console for errors
2. Verify WebSocket connection: Look for "WebSocket connected" in console
3. Check autonomous mode toggle is ON

---

### Issue: Rollback not working

**Solution:**
1. Check database exists: `ls ~/.xionimus_ai/autonomous_state.db`
2. Verify checkpoints: Look in action history for checkpoint count
3. Check browser console for API errors

---

### Issue: "Execution limit reached"

**Solution:**
1. This is a safety feature
2. Start a new session
3. Or increase limit in `/app/backend/app/core/autonomous_engine.py` (line ~14)

---

## Test Results Log

Copy this table to track your testing:

| Scenario | Status | Notes | Timestamp |
|----------|--------|-------|-----------|
| 1. Basic File Ops | ⬜ | | |
| 2. Create File | ⬜ | | |
| 3. Bash Command | ⬜ | | |
| 4. Install Package | ⬜ | | |
| 5. Multi-Tool | ⬜ | | |
| 6. Error Handling | ⬜ | | |
| 7. Rollback Action | ⬜ | | |
| 8. Rollback Session | ⬜ | | |
| 9. Dangerous Block | ⬜ | | |
| 10. Export History | ⬜ | | |

**Legend:**
- ⬜ Not tested
- ✅ Passed
- ❌ Failed
- ⚠️ Partial success

---

## Success Criteria

**Minimum for Production:**
- ✅ All 10 core scenarios pass
- ✅ No security vulnerabilities (dangerous commands blocked)
- ✅ Rollback works reliably
- ✅ Action history persists
- ✅ UI responsive and intuitive

**Optional Enhancements:**
- [ ] Add keyboard shortcut to toggle autonomous mode (Ctrl+Shift+A)
- [ ] Add confirmation dialog for dangerous-looking actions
- [ ] Add action preview before execution
- [ ] Add batch action planning
- [ ] Add cost estimation before execution

---

🎉 **Happy Testing!**

Report any issues or improvements to the development team.
