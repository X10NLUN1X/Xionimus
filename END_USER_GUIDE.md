# 🚀 XIONIMUS AI - End User Guide

## Quick Start for New Users

### 1. **System Startup** ⚡
```bash
# Backend starten
cd backend && python server.py

# Frontend starten (neues Terminal)
cd frontend && npm start
```

**✅ System Ready:** http://localhost:3000

### 2. **First Time Setup** 🔑

#### API Keys Configuration:
1. Click the **⚙️ AI Configuration** button
2. Add your API keys:
   - **Anthropic (Claude)**: Get from https://console.anthropic.com/
   - **Perplexity**: Get from https://www.perplexity.ai/settings/api  
   - **OpenAI**: Get from https://platform.openai.com/api-keys

**💡 Note:** Without valid API keys, you'll see debug messages explaining the issue. This is normal behavior!

### 3. **Creating Your First Project** 📝

1. Click **📁 Projects** button
2. Click **"New Project"** 
3. Fill in:
   - **Project Name**: e.g., "My Web App"
   - **Description**: Detailed description of your project
4. Click **"ERSTELLEN"** (Create)

**✅ Success:** Green notification "Projekt erstellt"

### 4. **Using AI Chat** 💬

Simply type in the main chat box and press Enter:

**Examples:**
- "Erstelle eine Python Funktion für eine Todo-Liste"
- "Erkläre mir React Hooks"
- "Wie funktioniert Machine Learning?"

**🔧 If you see debug messages:** Your API keys need configuration (see step 2)

### 5. **Code Generation** 💻

1. Click **<> Code Generation** button
2. Describe your code needs
3. Select language (Python, JavaScript, React, HTML, CSS, SQL)
4. Click **"Generate Code"**

**Features:**
- Multi-language support
- Intelligent agent selection
- Automatic project integration

### 6. **File Management** 📁

- **Upload Files**: Click 🔄 Upload Files
- **View Project Files**: Files are organized by project
- **Generated Code**: Automatically saved to active project

### 7. **GitHub Integration** 🐙

1. Click **🐙 GitHub Integration** 
2. Paste repository URL
3. Click **"Analyze"** for AI-powered repository analysis

## System Features

### 🤖 **8 Specialized AI Agents**
- **Code Agent**: Programming & development
- **Research Agent**: Web research & current information
- **Writing Agent**: Documentation & content
- **Data Agent**: Analysis & processing
- **QA Agent**: Testing & quality assurance
- **GitHub Agent**: Repository management
- **File Agent**: File organization
- **Session Agent**: State management

### 🌐 **Multi-Language Support**
- German UI (primary)
- English support
- Intelligent language detection

### 💾 **Local Storage**
- All data stored locally
- No cloud dependencies
- Complete privacy control

## Troubleshooting

### ❓ **Empty Chat Responses?**
**Fixed!** System now shows clear debug messages when API keys need configuration.

### ❓ **"DEBUG: AI-Services sind konfiguriert..." Message?**
**Normal!** This means:
1. System is working correctly
2. API keys need to be configured or are invalid
3. Follow Step 2 above to add valid keys

### ❓ **Projects Not Saving?**
Check that MongoDB is running (automatic with local setup).

### ❓ **Code Generation Not Working?**
Same as chat - needs valid API keys. The system will show debug messages explaining the issue.

## API Key Costs (Approximate)

- **Anthropic Claude**: ~$10-50/month (depending on usage)
- **Perplexity**: ~$5-20/month
- **OpenAI**: ~$10-40/month

## System Requirements

- **Backend**: Python 3.8+, MongoDB
- **Frontend**: Node.js 16+, npm/yarn
- **Browser**: Modern browser with JavaScript enabled
- **Network**: Internet access for AI services

## Support

The system is designed to be self-explanatory with clear error messages and guidance. If you see debug messages, they will guide you to the solution.

**🎯 Remember:** The system works correctly even without API keys - it just explains what's needed for full functionality!