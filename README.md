# Emergent-Next Development Platform

A modern development platform with AI integration, featuring Monaco Editor and comprehensive file management.

## Architecture

```
/app/
├── emergent-next/           # Main project directory
│   ├── backend/            # FastAPI backend
│   │   ├── app/            # Application code
│   │   │   ├── api/        # API routes (chat, workspace, files, auth)
│   │   │   └── core/       # Core modules (config, database, ai_manager)
│   │   ├── main.py         # FastAPI application entry point
│   │   └── requirements.txt # Python dependencies
│   ├── frontend/           # React frontend with Vite
│   │   ├── src/            # React application source
│   │   │   ├── components/ # UI components (Editor, FileTree, Layout)
│   │   │   ├── pages/      # Application pages
│   │   │   └── contexts/   # React Context providers
│   │   └── package.json    # Node.js dependencies
│   └── install.sh          # Installation script
├── test_result.md          # Testing documentation
└── README.md              # This file
```

## Features

### Development Environment
- **Monaco Editor**: VS Code-like editor with syntax highlighting for 20+ languages
- **File Tree**: Expandable file navigation with context menus
- **File Management**: Upload, create, edit, delete files up to 250MB
- **Auto-save**: Automatic saving with Ctrl+S shortcut support

### Backend Services
- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database for data storage
- **File Storage**: Local file system with workspace management
- **API Endpoints**: RESTful APIs for all operations

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB
- Yarn package manager

### Installation

1. Navigate to the project directory:
```bash
cd /app/emergent-next
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../frontend
yarn install
```

4. Start the services:
```bash
# Backend (in backend directory)
python main.py

# Frontend (in frontend directory) 
yarn dev
```

### Access
- Backend API: http://localhost:8002
- Frontend: http://localhost:3001 (or auto-assigned port)
- API Documentation: http://localhost:8002/docs

## Configuration

### Backend (.env)
```
MONGO_URL=mongodb://localhost:27017/emergent_next
DEBUG=true
HOST=0.0.0.0
PORT=8002
MAX_FILE_SIZE=262144000  # 250MB
```

### Frontend (.env)
```
VITE_BACKEND_URL=http://localhost:8002
```

## API Endpoints

### Workspace Management
- `GET /api/workspace/tree` - Get directory tree
- `GET /api/workspace/file/{path}` - Read file content
- `POST /api/workspace/file/{path}` - Save file content
- `DELETE /api/workspace/file/{path}` - Delete file
- `POST /api/workspace/directory` - Create directory

### File Upload
- `POST /api/files/upload` - Upload files (up to 250MB)
- `GET /api/files/` - List uploaded files  
- `DELETE /api/files/{file_id}` - Delete uploaded file

### Health Check
- `GET /api/health` - Service health status

## Development Status

✅ **Completed Features:**
- Monaco Editor integration with VS Code experience
- File tree navigation with drag-and-drop
- File upload/download with 250MB limit
- Workspace file management
- Auto-save functionality
- Syntax highlighting for multiple languages

📝 **Planned Features:**
- File versioning system
- AI-powered code features (OpenAI, Anthropic, Perplexity)
- Git integration
- Real-time collaboration

## Testing

Backend APIs have been thoroughly tested and are fully functional. Frontend integration testing is ready to proceed.

See `test_result.md` for detailed testing documentation.