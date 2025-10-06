# Xionimus Autonomous Agent

Windows-based local agent that monitors your code directories and provides real-time AI-powered analysis and suggestions.

## Features

- 🔍 **Real-time File Monitoring**: Watches your code directories for changes
- 🤖 **AI-Powered Analysis**: Automatic code analysis using Claude Sonnet 4.5 & Opus 4.1
- 💡 **Smart Suggestions**: Proactive suggestions for improvements
- 🔒 **Windows Native**: Built specifically for Windows paths (C:\...)
- 🌐 **Web Dashboard**: Control and monitor via web interface

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows OS

### Setup

1. **Install Dependencies**:
```bash
cd agent
pip install -r requirements.txt
```

2. **Configure Directories**:
   - Copy `config.example.json` to `config.json`
   - Edit `config.json` and add your Windows project directories:
```json
{
  "backend_url": "http://localhost:8001",
  "watch_directories": [
    "C:\\Users\\YourUsername\\Documents\\Projects",
    "C:\\Users\\YourUsername\\Code"
  ]
}
```

## Usage

### Method 1: Using Config File (Recommended)

```bash
python main.py --config config.json
```

### Method 2: Command Line Arguments

```bash
python main.py --directories "C:\\Users\\YourName\\Projects" "C:\\Users\\YourName\\Code"
```

### Custom Backend URL

```bash
python main.py --backend http://your-backend-url:8001 --config config.json
```

## Running on Startup (Windows)

### Option 1: Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At log on
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `C:\\path\\to\\main.py --config C:\\path\\to\\config.json`

### Option 2: Startup Folder

Create a batch file `start_xionimus_agent.bat`:
```batch
@echo off
cd C:\\path\\to\\agent
python main.py --config config.json
```

Place this in:
```
C:\\Users\\YourUsername\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup
```

## Supported File Types

The agent monitors the following file types:
- Python: `.py`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`
- Web: `.html`, `.css`
- Data: `.json`
- Documentation: `.md`

## How It Works

1. **File Monitoring**: The agent watches your configured directories for file changes
2. **Event Detection**: When you save a file, the agent detects the change
3. **Analysis**: File content is sent to the backend for AI analysis
4. **Results**: Analysis results and suggestions appear in the web dashboard

## Configuration Options

### config.json

```json
{
  "backend_url": "http://localhost:8001",
  "watch_directories": [
    "C:\\path\\to\\project1",
    "C:\\path\\to\\project2"
  ],
  "agent_settings": {
    "auto_analysis": true,
    "suggestions_enabled": true,
    "notification_level": "all"
  }
}
```

## Troubleshooting

### Agent Not Connecting

- Ensure backend is running (`sudo supervisorctl status backend`)
- Check backend URL in config
- Verify firewall settings

### Files Not Being Detected

- Check directory paths use Windows format: `C:\\Users\\...`
- Ensure directories exist and are readable
- Check agent logs: `xionimus_agent.log`

### High CPU Usage

- Reduce number of watched directories
- Exclude large directories (node_modules, etc.) - these are automatically ignored

## Logs

Agent logs are saved to `xionimus_agent.log` in the agent directory.

View logs in real-time:
```bash
tail -f xionimus_agent.log
```

## Security

- Agent runs locally on your machine
- Only sends file content to your Xionimus backend
- API keys stored securely in backend
- No external connections except to configured backend

## Support

For issues or questions, check the web dashboard or backend logs:
```bash
tail -f /var/log/supervisor/backend.*.log
```
