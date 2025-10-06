# Xionimus Autonomous Agent System

**Transform Xionimus into a GitHub Copilot-style autonomous coding assistant for Windows**

---

## Overview

The Xionimus Autonomous Agent is a local Windows application that monitors your code directories in real-time and provides AI-powered analysis and suggestions as you code. Similar to GitHub Copilot or Emergent.sh, it runs continuously in the background and seamlessly integrates with your development workflow.

### Key Features

✅ **Real-time File Monitoring** - Automatically detects file changes in your projects
✅ **AI-Powered Analysis** - Uses Claude Sonnet 4.5 and Opus 4.1 for code analysis
✅ **Autonomous Suggestions** - Proactive bug detection and improvement recommendations
✅ **Windows Native** - Built specifically for Windows paths and workflows
✅ **Web Dashboard** - Full control and monitoring via browser
✅ **Privacy-Focused** - Runs locally, sends data only to your Xionimus backend

---

## Architecture

```
┌─────────────────────┐
│   Windows PC        │
│  ┌───────────────┐  │
│  │  Local Agent  │  │◄─── Monitors C:\Users\...\Projects
│  │  (Python)     │  │
│  └───────┬───────┘  │
│          │ WebSocket│
└──────────┼──────────┘
           │
           ▼
┌──────────────────────┐
│ Xionimus Backend     │
│ ┌──────────────────┐ │
│ │ WebSocket Server │ │
│ │ Claude AI        │ │
│ │ SQLite Database  │ │
│ └──────────────────┘ │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Web Dashboard        │
│ • Status Monitor     │
│ • Settings           │
│ • Suggestions Feed   │
│ • Activity Log       │
└──────────────────────┘
```

---

## Installation

### Prerequisites

- **Windows 10/11**
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Xionimus Backend** (running and accessible)

### Method 1: Automated Installation (Recommended)

**Option A: Batch File**
```batch
install_agent.bat
```

**Option B: PowerShell**
```powershell
.\install_agent.ps1
```

### Method 2: Manual Installation

1. **Install Dependencies**
   ```bash
   cd agent
   pip install -r requirements.txt
   ```

2. **Create Configuration**
   ```bash
   copy config.example.json config.json
   ```

3. **Edit Configuration**
   Open `config.json` and update:
   ```json
   {
     "backend_url": "http://your-backend-url:8001",
     "watch_directories": [
       "C:\\Users\\YourName\\Documents\\Projects",
       "C:\\Users\\YourName\\Code"
     ]
   }
   ```

---

## Configuration

### Backend Configuration

The backend automatically includes the autonomous agent system with the following features:

1. **WebSocket Endpoint**: `/api/ws/agent/{agent_id}`
2. **Settings API**: `/api/agent/settings`
3. **Status API**: `/api/agent/status`
4. **Activity API**: `/api/agent/activity`

### Claude API Keys

**Option 1: Use Server API Key (Default)**
- Configure in backend `.env`:
  ```env
  CLAUDE_API_KEY=sk-ant-api03-...
  ```

**Option 2: User-Specific API Key**
- Configure via Web UI: http://your-backend/agent
- Stored encrypted in database
- Overrides server key if provided

### Watch Directories

Configure directories in two ways:

**Method 1: Config File**
```json
{
  "watch_directories": [
    "C:\\Users\\YourName\\Projects",
    "C:\\Users\\YourName\\WebDev"
  ]
}
```

**Method 2: Web UI**
- Navigate to http://your-backend/agent
- Add/remove directories dynamically
- Changes sync automatically

---

## Usage

### Starting the Agent

**Command Line**
```bash
python agent/main.py --config agent/config.json
```

**With Custom Backend**
```bash
python agent/main.py --backend http://custom-url:8001 --directories "C:\Projects"
```

### Running on Startup

**Option 1: Task Scheduler**

1. Open Task Scheduler
2. Create Basic Task
   - Name: "Xionimus Agent"
   - Trigger: At log on
   - Action: Start a program
     - Program: `C:\Python311\python.exe`
     - Arguments: `C:\path\to\agent\main.py --config C:\path\to\agent\config.json`
     - Start in: `C:\path\to\agent`

**Option 2: Startup Folder**

1. Create `start_xionimus.bat`:
   ```batch
   @echo off
   cd C:\path\to\xionimus\agent
   python main.py --config config.json
   ```

2. Place in:
   ```
   C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
   ```

### Web Dashboard

Access the agent dashboard at: `http://your-backend/agent`

**Features:**
- 🟢 **Connection Status** - Real-time agent connectivity
- 📁 **Directory Management** - Add/remove watch directories
- ⚙️ **Settings** - Configure analysis preferences
- 📊 **Activity Log** - View file changes and analysis results
- 🔑 **API Key Management** - Store Claude keys securely

---

## How It Works

### 1. File Monitoring

The agent watches configured directories for:
- ✅ File creation
- ✅ File modification
- ✅ File deletion

**Monitored File Types:**
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`
- Web: `.html`, `.css`
- Data: `.json`
- Docs: `.md`

**Auto-Ignored:**
- `node_modules/`
- `.git/`
- `__pycache__/`
- `venv/`
- `dist/`, `build/`

### 2. AI Analysis

When you save a file:

1. **Event Detection** - Agent detects the file change
2. **Content Extraction** - Reads file content
3. **WebSocket Transmission** - Sends to backend
4. **AI Processing** - Claude analyzes the code
5. **Results Delivery** - Suggestions appear in dashboard

**Analysis Types:**
- 🐛 Bug detection
- 💡 Code quality improvements
- ⚡ Performance optimizations
- 🔒 Security vulnerabilities

### 3. Proactive Suggestions

The system provides real-time suggestions:

```
📊 Analysis for src/utils/helpers.ts:
  WARNING: Potential null reference on line 42
  INFO: Consider using optional chaining
  
💡 Suggestion: Refactor Authentication
   The authentication logic could be simplified
   using a middleware pattern.
```

---

## API Reference

### WebSocket Messages

**Client → Server:**
```json
{
  "type": "file_event",
  "agent_id": "uuid",
  "timestamp": "2025-10-06T10:00:00",
  "data": {
    "event_type": "modified",
    "file_path": "C:\\Users\\..\\file.py",
    "content": "..."
  }
}
```

**Server → Client:**
```json
{
  "type": "analysis_result",
  "data": {
    "file_path": "...",
    "issues": [
      {
        "severity": "warning",
        "line": 42,
        "message": "..."
      }
    ],
    "suggestions": [...]
  }
}
```

### HTTP Endpoints

**Get Settings**
```http
GET /api/agent/settings
Authorization: Bearer <token>
```

**Update Settings**
```http
PUT /api/agent/settings
Content-Type: application/json
Authorization: Bearer <token>

{
  "watch_directories": ["C:\\..."],
  "auto_analysis_enabled": true,
  "suggestions_enabled": true
}
```

**Get Status**
```http
GET /api/agent/status
Authorization: Bearer <token>
```

**Get Activity**
```http
GET /api/agent/activity?limit=50
Authorization: Bearer <token>
```

---

## Troubleshooting

### Agent Not Connecting

**Symptoms:** Badge shows "⚫ AGENT" (gray)

**Solutions:**
1. Check backend is running: `sudo supervisorctl status backend`
2. Verify backend URL in `config.json`
3. Check firewall settings
4. Review agent logs: `agent/xionimus_agent.log`

### Files Not Being Detected

**Symptoms:** No activity when saving files

**Solutions:**
1. Verify directory paths use Windows format: `C:\\Users\\...`
2. Ensure directories exist and are readable
3. Check file extensions are supported
4. Review agent logs for errors

### High CPU Usage

**Symptoms:** Agent consuming excessive resources

**Solutions:**
1. Reduce number of watched directories
2. Exclude large projects temporarily
3. Check for recursive directory structures
4. Adjust debounce settings in `file_watcher.py`

### Connection Drops

**Symptoms:** Agent disconnects frequently

**Solutions:**
1. Check network stability
2. Increase heartbeat interval
3. Review backend logs for WebSocket errors
4. Ensure backend is not overloaded

---

## Advanced Configuration

### Custom Debounce Timing

Edit `agent/file_watcher.py`:
```python
DEBOUNCE_SECONDS = 2  # Increase to reduce duplicate events
```

### Heartbeat Interval

Edit `agent/ws_client.py`:
```python
ping_interval=30,  # Increase if connection unstable
ping_timeout=10
```

### Analysis Threshold

Configure minimum file size for analysis:
```python
MIN_FILE_SIZE = 100  # bytes
MAX_FILE_SIZE = 1000000  # 1MB
```

---

## Security

### Data Privacy

- ✅ Agent runs entirely on your local machine
- ✅ File content sent only to **your** Xionimus backend
- ✅ No external connections except configured backend
- ✅ API keys encrypted in database

### Authentication

- All API endpoints require JWT authentication
- Agent inherits user permissions from web login
- WebSocket connections validated on connect

### Best Practices

1. **Use HTTPS** in production environments
2. **Rotate API keys** regularly
3. **Monitor activity** via dashboard
4. **Restrict watch directories** to necessary paths only

---

## Performance

### Resource Usage

**Typical:**
- CPU: <1% (idle), 2-5% (analyzing)
- RAM: ~50MB
- Network: <1KB/s (idle), <100KB/s (analyzing)

**Tips:**
- Limit watch directories to active projects
- Exclude `node_modules/` and build directories (auto-excluded)
- Use SSD for better file monitoring performance

---

## Roadmap

### Planned Features

- [ ] IDE Extension (VS Code, JetBrains)
- [ ] Real-time code completion
- [ ] Project-wide refactoring suggestions
- [ ] Integration with GitHub Issues
- [ ] Team collaboration features
- [ ] Custom analysis rules
- [ ] Multi-language support for UI

---

## Support

### Resources

- **Documentation**: `/app/docs/`
- **Agent README**: `/app/agent/README.md`
- **Backend Logs**: `/var/log/supervisor/backend.*.log`
- **Agent Logs**: `agent/xionimus_agent.log`

### Common Questions

**Q: Can I run multiple agents?**
A: Yes, each agent gets a unique ID. All appear in the dashboard.

**Q: Does it work with WSL?**
A: No, designed specifically for native Windows. Use Linux paths in WSL.

**Q: Can I use without Claude API key?**
A: No, Claude API key required for AI analysis features.

**Q: Is it free?**
A: Agent code is included. Claude API usage incurs costs.

---

## Contributing

The autonomous agent system is part of Xionimus. Improvements welcome!

**Key Files:**
- Agent: `/app/agent/`
- Backend: `/app/backend/app/api/agent_*.py`
- Frontend: `/app/frontend/src/pages/AgentSettingsPage.tsx`
- Models: `/app/backend/app/models/agent_models.py`

---

## License

Part of Xionimus AI platform. See main LICENSE file.

---

**Made with ❤️ for autonomous coding**
