# Xionimus AI - Advanced AI Development Platform

## Overview
Xionimus AI is an advanced development platform with multi-agent intelligence, featuring Monaco Editor, file management, and intelligent AI model selection.

## Features
- **AI Chat**: Support for GPT-5, Claude Opus 4.1, and Perplexity
- **Monaco Editor**: VS Code-like development environment
- **File Management**: Upload, organize, and manage files
- **Intelligent Agents**: Automatic AI model selection based on task type
- **Responsive Design**: Works on desktop, tablet, and mobile

## Quick Start
```bash
cd /app/xionimus-ai
./start-dev.sh
```

## Architecture
- **Frontend**: React + TypeScript + Chakra UI
- **Backend**: FastAPI + Python + MongoDB
- **AI Integration**: OpenAI GPT-5, Anthropic Claude Opus 4.1, Perplexity

## Configuration
Add your API keys to `/app/xionimus-ai/backend/.env`:
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
PERPLEXITY_API_KEY=your_perplexity_key
```

## License
MIT License - Xionimus AI Platform
