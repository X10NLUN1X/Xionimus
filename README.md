# XIONIMUS AI - Clean Installation

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (tested with 3.13)
- Node.js 18+
- MongoDB (optional)

### Installation

1. **Backend Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Frontend Dependencies:**
   ```bash
   cd frontend
   yarn install
   ```

3. **Start System:**
   ```bash
   # Backend (Terminal 1):
   cd backend && python server.py
   
   # Frontend (Terminal 2): 
   cd frontend && yarn start
   ```

4. **Open:** http://localhost:3000

### Configuration

- Configure API keys in the web interface
- MongoDB runs locally on default port
- Backend: http://localhost:8001
- Frontend: http://localhost:3000

### Features

- 9 AI Agents (Code, Research, Writing, Data, QA, GitHub, File, Session, Experimental)
- Multi-Agent Chat System
- GitHub Integration
- Project Management
- Modern Gold/Black UI