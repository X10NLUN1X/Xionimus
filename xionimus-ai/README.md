# 🤖 Xionimus AI
> **Advanced AI Development Platform with Multi-Agent Intelligence**

Xionimus AI is a cutting-edge development platform that combines the power of multiple AI models with intelligent agent selection, professional code editing, and seamless file management. Built for developers, researchers, and AI enthusiasts who demand the best tools for their work.

![Xionimus AI Platform](https://img.shields.io/badge/Platform-Xionimus%20AI-gold?style=for-the-badge&logo=ai)
![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=for-the-badge)

---

## 🌟 **What is Xionimus AI?**

Xionimus AI is more than just another AI chat interface. It's a **complete development ecosystem** that:

🧠 **Intelligently routes your requests** to the optimal AI model  
💻 **Provides a VS Code-like editor** with full syntax highlighting  
📁 **Manages your files** with drag & drop uploads up to 250MB  
🎨 **Delivers a beautiful, responsive interface** that adapts to any device  
⚡ **Connects to the latest AI models** including GPT-5, Claude Opus 4.1, and Perplexity  

### 🤖 **Intelligent Agent System**

What makes Xionimus AI unique is its **intelligent agent selection**:

| Task Type | Optimal AI Model | Use Case |
|-----------|------------------|----------|
| 💬 **General Conversation** | GPT-5 (OpenAI) | Everyday chat, questions, brainstorming |
| 🔍 **Code Analysis** | Claude Opus 4.1 (Anthropic) | Code review, debugging, optimization |
| 🧮 **Complex Reasoning** | Claude Opus 4.1 (Anthropic) | Logic puzzles, analysis, research |
| 🌐 **Web Research** | Perplexity Sonar | Real-time information, current events |
| ✍️ **Creative Writing** | GPT-5 (OpenAI) | Stories, content creation, brainstorming |
| 📚 **Documentation** | Claude Sonnet 4 (Anthropic) | Technical docs, guides, explanations |
| 🐛 **Debugging** | GPT-4.1 (OpenAI) | Error fixing, troubleshooting |
| 🏗️ **System Analysis** | Claude Opus 4.1 (Anthropic) | Architecture review, system design |

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.10+ 
- Node.js 18+
- MongoDB (local or cloud)

### **1. Clone & Setup**
```bash
# Navigate to the platform
cd /app/xionimus-ai

# Start both backend and frontend
./start-dev.sh

# Or start individually
cd backend && python main.py    # Backend on :8001
cd frontend && npm run dev       # Frontend on :3000
```

### **2. Configure AI Providers**
1. Open **Settings** in the web interface
2. Add your API keys:
   - **OpenAI API Key** → Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Anthropic API Key** → Get from [Anthropic Console](https://console.anthropic.com/keys)  
   - **Perplexity API Key** → Get from [Perplexity Settings](https://www.perplexity.ai/settings/api)

### **3. Start Using Xionimus AI**
- 💬 **Chat**: Start conversations with the latest AI models
- 💻 **Workspace**: Code with Monaco Editor and file management
- 📁 **Files**: Upload and organize your documents
- ⚙️ **Settings**: Configure providers and enable intelligent agents

---

## 🏗️ **Architecture**

```mermaid
graph TB
    A[Frontend - React + TypeScript] --> B[Backend - FastAPI + Python]
    B --> C[MongoDB Database]
    B --> D[AI Providers]
    D --> E[OpenAI GPT-5]
    D --> F[Anthropic Claude Opus 4.1]  
    D --> G[Perplexity Sonar]
    
    H[Intelligent Agent Manager] --> D
    I[Monaco Editor] --> A
    J[File Management] --> B
    K[WebSocket Real-time] --> B
```

### **Technology Stack**
- **Frontend**: React 18, TypeScript, Chakra UI, Monaco Editor, Vite
- **Backend**: FastAPI, Python 3.10+, MongoDB, WebSockets
- **AI Integration**: OpenAI, Anthropic, Perplexity APIs
- **Development**: Hot reload, ESLint, TypeScript strict mode

---

## 🎯 **Key Features**

### **🤖 Intelligent AI Agent Selection**
- Automatically selects the best AI model based on your message content
- 8 different task types with optimized model assignments
- Seamless switching between providers for optimal results
- Configurable auto-selection (can be disabled)

### **💻 Professional Code Editor**
- VS Code-like Monaco Editor with full syntax highlighting
- Support for 20+ programming languages
- Auto-save functionality with Ctrl+S shortcuts
- File tree navigation with create/delete operations
- Welcome file auto-loads for immediate productivity

### **📁 Advanced File Management**
- Drag & drop file uploads up to 250MB
- File preview for images and text files
- Download and delete operations
- Upload progress indicators
- File type recognition with icons

### **🎨 Beautiful, Responsive Design**
- Luxury black & gold theme inspired by premium platforms
- Fully responsive (mobile, tablet, desktop)
- Dark/Light mode toggle
- Collapsible sidebar navigation
- Professional typography and spacing

### **⚡ Real-time Communication**
- WebSocket support for instant AI responses
- Session management and chat history
- Message persistence across browser sessions
- Copy message functionality

---

## 🛠️ **Installation & Setup**

### **Environment Configuration**
Create `/app/xionimus-ai/backend/.env`:
```env
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017/xionimus_ai

# AI API Keys (add your own)
OPENAI_API_KEY=sk-proj-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO

# Security (change in production)
SECRET_KEY=xionimus-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### **Backend Setup**
```bash
cd /app/xionimus-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python main.py
```

### **Frontend Setup**
```bash
cd /app/xionimus-ai/frontend

# Install dependencies
yarn install

# Start development server
yarn dev
```

---

## 🔧 **Configuration**

### **AI Provider Setup**

#### **OpenAI (GPT-5, GPT-4o, O1 Series)**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to Settings: `OPENAI_API_KEY=sk-proj-...`
4. **Models Available**: GPT-5, GPT-4o, GPT-4.1, O1, O3

#### **Anthropic (Claude Opus 4.1)**
1. Visit [Anthropic Console](https://console.anthropic.com/keys)
2. Generate an API key
3. Add to Settings: `ANTHROPIC_API_KEY=sk-ant-...`
4. **Models Available**: claude-opus-4-1-20250805, claude-4-sonnet-20250514

#### **Perplexity (Real-time Research)**
1. Visit [Perplexity API](https://www.perplexity.ai/settings/api)
2. Get your API key
3. Add to Settings: `PERPLEXITY_API_KEY=pplx-...`
4. **Models Available**: llama-3.1-sonar-large-128k-online

---

## 📖 **Usage Examples**

### **Smart AI Selection**
```typescript
// Enable intelligent agent selection (default: enabled)
const chatRequest = {
  message: "Help me debug this Python function",
  auto_agent_selection: true  // Will auto-select Claude Opus 4.1
}
```

### **Manual Provider Selection**
```typescript
// Manually choose provider/model
const chatRequest = {
  message: "Write a creative story",
  provider: "openai",
  model: "gpt-5",
  auto_agent_selection: false
}
```

### **File Upload & Processing**
```typescript
// Upload files for AI analysis
const fileUpload = new FormData()
fileUpload.append('file', selectedFile)
fileUpload.append('description', 'Code for review')

await axios.post('/api/files/upload', fileUpload)
```

---

## 🌐 **API Documentation**

### **Core Endpoints**

#### **Health Check**
```http
GET /api/health
```
```json
{
  "status": "healthy",
  "platform": "Xionimus AI",
  "ai_models": "Latest models with classic API keys",
  "services": {
    "database": "connected",
    "ai_providers": {...},
    "available_models": {...}
  }
}
```

#### **AI Chat Completion**
```http
POST /api/chat
```
```json
{
  "messages": [{"role": "user", "content": "Hello"}],
  "provider": "openai",
  "model": "gpt-5",
  "auto_agent_selection": true,
  "api_keys": {
    "openai": "sk-proj-...",
    "anthropic": "sk-ant-...",
    "perplexity": "pplx-..."
  }
}
```

#### **Agent Recommendations**
```http
POST /api/chat/agent-recommendation
```
```json
{
  "message": "Help me debug this code",
  "available_providers": {"openai": true, "anthropic": true}
}
```

**Response:**
```json
{
  "task_type": "code_analysis",
  "recommended_provider": "anthropic", 
  "recommended_model": "claude-opus-4-1-20250805",
  "reasoning": "Task detected as code_analysis, optimal model is claude-opus-4-1-20250805"
}
```

---

## 🎨 **Screenshots**

### **Main Chat Interface**
- Golden "X" logo with "Xionimus AI PLATFORM" branding
- Provider/model selection with GPT-5, Claude Opus 4.1, Perplexity
- Real-time chat with syntax highlighting and markdown support
- Session management and chat history

### **Monaco Editor Workspace**
- VS Code-like editing experience
- File tree navigation with create/delete operations
- Auto-save functionality and unsaved changes indicators
- Multi-language syntax highlighting (20+ languages)

### **File Management System**
- Drag & drop upload zone with progress indicators
- File table with type recognition and action buttons
- Preview modals for images and text files
- 250MB file size limit with chunked uploads

### **Settings & Configuration**
- **Intelligent Agent Selection** toggle
- AI provider configuration with API key management
- Model recommendations and use case descriptions
- System status and version information

---

## 🔧 **Development**

### **Project Structure**
```
xionimus-ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   │   ├── chat.py     # AI chat completion + agent selection
│   │   │   ├── files.py    # File upload/management
│   │   │   ├── workspace.py # Monaco Editor file operations
│   │   │   └── auth.py     # Authentication (MVP)
│   │   └── core/           # Core modules
│   │       ├── ai_manager.py          # AI provider management
│   │       ├── intelligent_agents.py  # Smart agent selection
│   │       ├── config.py              # Configuration
│   │       └── database.py            # MongoDB connection
│   ├── main.py             # FastAPI app entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment configuration
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── Layout/     # XionimusLayout + responsive design
│   │   │   ├── Chat/       # XionimusChatInterface
│   │   │   ├── Editor/     # Monaco Editor integration
│   │   │   ├── FileTree/   # File navigation
│   │   │   └── FileUpload/ # Drag & drop file uploads
│   │   ├── pages/          # Main application pages
│   │   │   ├── ChatPage.tsx    # AI chat interface
│   │   │   ├── WorkspacePage.tsx # Monaco Editor + file tree
│   │   │   ├── FilesPage.tsx   # File management
│   │   │   └── SettingsPage.tsx # Configuration
│   │   ├── contexts/       # React Context (global state)
│   │   └── theme/          # Chakra UI theme (black & gold)
│   ├── package.json        # Node.js dependencies
│   └── index.html         # Main HTML file
└── README.md              # This file
```

### **Available Scripts**

#### **Development**
```bash
# Start both services
./start-dev.sh

# Individual services
cd backend && python main.py     # Backend on :8001
cd frontend && npm run dev       # Frontend on :3000
```

#### **Production**
```bash
# Build frontend
cd frontend && yarn build

# Start production backend
cd backend && uvicorn main:app --host 0.0.0.0 --port 8001
```

#### **Testing**
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd frontend && yarn test

# Linting
cd frontend && yarn lint
cd backend && ruff check .
```

---

## 💡 **Usage Examples**

### **🤖 Intelligent Conversations**
Ask Xionimus AI anything, and it will automatically route your request to the best AI model:

**"Help me debug this Python function"** → Routes to Claude Opus 4.1 (best for code analysis)  
**"Write a creative story about space"** → Routes to GPT-5 (best for creative tasks)  
**"What are the latest AI research developments?"** → Routes to Perplexity (real-time research)

### **💻 Code Development**
1. Open **Workspace** 
2. Files auto-load with "Welcome to Xionimus AI Workspace"
3. Create new files or select from file tree
4. Edit with full Monaco Editor features:
   - IntelliSense and autocomplete
   - Syntax highlighting for 20+ languages
   - Auto-save with Ctrl+S
   - Error detection and hints

### **📁 File Management**
1. Navigate to **Files**
2. Drag & drop files up to 250MB
3. View upload progress in real-time
4. Manage files with view/download/delete actions
5. Preview images and text files instantly

---

## 🔑 **API Keys Guide**

### **Getting Your API Keys**

#### **OpenAI (Required for GPT-5)**
1. Visit [platform.openai.com](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key (starts with `sk-proj-`)
4. Add to Xionimus AI Settings

#### **Anthropic (Required for Claude Opus 4.1)**
1. Visit [console.anthropic.com](https://console.anthropic.com/keys)
2. Create a new API key
3. Copy the key (starts with `sk-ant-`)
4. Add to Xionimus AI Settings

#### **Perplexity (Optional, for research)**
1. Visit [perplexity.ai/settings/api](https://www.perplexity.ai/settings/api)
2. Generate an API key
3. Copy the key (starts with `pplx-`)
4. Add to Xionimus AI Settings

### **💰 Pricing**
- **OpenAI**: Pay-per-use (typically $0.01-0.06 per 1K tokens)
- **Anthropic**: Pay-per-use (typically $0.015-0.075 per 1K tokens)
- **Perplexity**: Various plans available

---

## 🛡️ **Security & Privacy**

- **API Keys**: Stored locally in your browser (localStorage)
- **Data**: Your conversations and files stay on your system
- **Encryption**: HTTPS for all API communications
- **No Tracking**: We don't collect or store your personal data
- **Open Source**: Full transparency in how your data is handled

---

## 📋 **Requirements**

### **System Requirements**
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for AI API calls

### **Development Requirements**
- **Python**: 3.10+ with pip
- **Node.js**: 18+ with npm/yarn
- **MongoDB**: Local instance or cloud connection
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+

---

## 🔧 **Configuration Options**

### **Environment Variables**
```env
# Database
MONGO_URL=mongodb://localhost:27017/xionimus_ai

# Server Settings
DEBUG=true
HOST=0.0.0.0
PORT=8001
LOG_LEVEL=INFO

# File Upload
MAX_FILE_SIZE=262144000  # 250MB
UPLOAD_DIR=uploads
WORKSPACE_DIR=workspace

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### **Frontend Environment**
```env
VITE_BACKEND_URL=http://localhost:8001
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Backend not starting**
```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
cd backend && pip install -r requirements.txt

# Check MongoDB connection
mongosh --eval "db.adminCommand('ping')"
```

#### **Frontend not loading**
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear cache and reinstall
cd frontend && rm -rf node_modules yarn.lock
yarn install
```

#### **AI Chat not working**
1. Check API keys are configured in Settings
2. Verify internet connection for AI API calls
3. Check browser console for error messages
4. Ensure sufficient API credits/quota

#### **File uploads failing**
1. Check file size (max 250MB)
2. Verify backend storage permissions
3. Check available disk space
4. Try smaller files first

---

## 📚 **Advanced Usage**

### **Custom System Messages**
Configure custom system messages for different AI models in the intelligent agent manager.

### **WebSocket Integration**
Connect to real-time chat via WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/chat/session-id')
ws.onmessage = (event) => {
  const response = JSON.parse(event.data)
  console.log('AI Response:', response.content)
}
```

### **Batch File Processing**
Upload multiple files and process them with AI:
```python
# Backend API example
files = request.files.getlist("files")
for file in files:
    result = await ai_manager.analyze_file(file, provider="anthropic")
```

---

## 🤝 **Contributing**

We welcome contributions to Xionimus AI! Here's how you can help:

### **Development Setup**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly: `yarn test && python -m pytest`
5. Submit a pull request

### **Areas for Contribution**
- 🤖 **AI Integrations**: Add support for new AI providers
- 🎨 **UI/UX**: Improve design and user experience  
- 📱 **Mobile**: Enhance mobile responsiveness
- 🔧 **Performance**: Optimize loading times and memory usage
- 📚 **Documentation**: Improve guides and examples
- 🧪 **Testing**: Add more comprehensive tests

---

## 📄 **License**

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🆘 **Support**

### **Getting Help**
- 📖 **Documentation**: Read this README thoroughly
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💬 **Discussions**: Ask questions in GitHub Discussions
- 📧 **Contact**: support@xionimus-ai.com

### **Community**
- 🌟 **Star this repo** if you find it useful
- 🔄 **Share** with fellow developers
- 🤝 **Contribute** to make it even better

---

## 🎯 **Roadmap**

### **✅ Completed (v1.0.0)**
- Multi-provider AI chat (GPT-5, Claude Opus 4.1, Perplexity)
- Intelligent agent selection system
- Monaco Editor with file management
- File upload with 250MB limit
- Responsive web interface
- Theme toggle (dark/light)

### **🔄 In Progress (v1.1.0)**
- Advanced file versioning with Git integration
- User authentication and profiles
- Team collaboration features
- Enhanced error boundaries

### **📋 Planned (v1.2.0)**
- Plugin system for custom AI agents
- Advanced code analysis tools
- Integration with external IDEs
- Mobile native applications

---

<div align="center">

**🤖 Built with ❤️ by the Xionimus AI Team**

[![Platform](https://img.shields.io/badge/Platform-Xionimus%20AI-gold?style=for-the-badge)](https://xionimus-ai.com)
[![AI Models](https://img.shields.io/badge/AI-GPT5%20%7C%20Claude%20Opus%204.1%20%7C%20Perplexity-blue?style=for-the-badge)](https://github.com/xionimus-ai)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=for-the-badge)](https://github.com/xionimus-ai)

*Empowering developers with intelligent AI agents since 2025*

</div>
